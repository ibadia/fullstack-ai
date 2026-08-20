"""
Receipt processing service with comprehensive logging and error handling.
"""

import logging
import os
import time
from typing import Optional, Tuple

from apps.receipts.models import Receipt, ReceiptLineItem
from apps.receipts.services.analyzer_factory import AnalyzerFactory
from apps.receipts.utils.validators import validate_receipt_data

logger = logging.getLogger(__name__)


class ReceiptProcessor:
    """Process receipt images through AI analysis with logging."""

    def __init__(self):
        """Initialize processor with configuration."""
        self.processing_mode = os.getenv("RECEIPT_PROCESSING_MODE", "sync").lower()
        self.provider = os.getenv("RECEIPT_ANALYZER_PROVIDER", "mock")
        # Note: API key is not logged
        self.api_key = os.getenv(f"{self.provider.upper()}_API_KEY")

    def process_receipt(self, receipt: Receipt) -> Tuple[bool, Optional[str]]:
        """
        Process receipt based on configured mode.

        Args:
            receipt: Receipt instance to process

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        logger.info(
            f"Starting receipt processing",
            extra={
                "receipt_id": receipt.id,
                "mode": self.processing_mode,
                "provider": self.provider,
                "file_size_bytes": receipt.file_size_bytes,
            },
        )

        if self.processing_mode == "async":
            return self._queue_async_processing(receipt)
        else:
            return self._process_synchronously(receipt)

    def _process_synchronously(self, receipt: Receipt) -> Tuple[bool, Optional[str]]:
        """
        Process receipt immediately with comprehensive logging.

        Args:
            receipt: Receipt to analyze

        Returns:
            Tuple of (success, error_message)
        """
        start_time = time.time()

        try:
            logger.info(
                f"[SYNC] Starting synchronous analysis",
                extra={"receipt_id": receipt.id},
            )

            receipt.analysis_status = "processing"
            receipt.save(update_fields=["analysis_status"])

            # Create analyzer
            try:
                analyzer = AnalyzerFactory.create_analyzer(
                    provider=self.provider,
                    api_key=self.api_key,
                )
                logger.debug(
                    f"Analyzer created successfully",
                    extra={"receipt_id": receipt.id, "provider": self.provider},
                )
            except ImportError as e:
                error_msg = f"Analyzer provider not available: {str(e)}"
                logger.error(
                    error_msg,
                    exc_info=True,
                    extra={"receipt_id": receipt.id},
                )
                receipt.analysis_status = "failed"
                receipt.error_message = error_msg
                receipt.error_code = "provider_not_available"
                receipt.save()
                return False, error_msg

            # Analyze receipt
            result = analyzer.analyze(receipt.file.path)
            processing_time_ms = int((time.time() - start_time) * 1000)

            if not result.success:
                # Log analysis failure
                logger.warning(
                    f"[SYNC] Analysis failed",
                    extra={
                        "receipt_id": receipt.id,
                        "error_code": result.error_code,
                        "processing_time_ms": processing_time_ms,
                        "provider": result.provider,
                        "model": result.model,
                    },
                )

                receipt.analysis_status = "failed"
                receipt.error_message = result.error_message
                receipt.error_code = result.error_code
                receipt.analysis_provider = result.provider
                receipt.analysis_model = result.model
                receipt.processing_time_ms = processing_time_ms
                receipt.save()

                return False, result.error_message

            # Validate extracted data
            valid, validation_error = validate_receipt_data(result.data)
            if not valid:
                logger.warning(
                    f"[SYNC] Validation failed",
                    extra={
                        "receipt_id": receipt.id,
                        "error": validation_error,
                        "processing_time_ms": processing_time_ms,
                    },
                )

                receipt.analysis_status = "failed"
                receipt.error_message = f"Validation error: {validation_error}"
                receipt.error_code = "validation_error"
                receipt.analysis_provider = result.provider
                receipt.analysis_model = result.model
                receipt.processing_time_ms = processing_time_ms
                receipt.save()

                return False, validation_error

            # Save analysis results
            receipt.analysis_status = "completed"
            receipt.extracted_data = result.data
            receipt.analysis_provider = result.provider
            receipt.analysis_model = result.model
            receipt.processing_time_ms = processing_time_ms
            receipt.save()

            # Create line items
            try:
                self._create_line_items(receipt, result.data)
                logger.info(
                    f"[SYNC] Analysis completed successfully",
                    extra={
                        "receipt_id": receipt.id,
                        "processing_time_ms": processing_time_ms,
                        "provider": result.provider,
                        "model": result.model,
                        "line_items_count": len(result.data.get("line_items", [])),
                    },
                )
            except Exception as e:
                logger.error(
                    f"Failed to create line items",
                    exc_info=True,
                    extra={"receipt_id": receipt.id},
                )
                # Don't fail the whole receipt if line items fail
                return True, None

            return True, None

        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            logger.error(
                f"[SYNC] Unexpected error during processing",
                exc_info=True,
                extra={
                    "receipt_id": receipt.id,
                    "error_type": type(e).__name__,
                    "processing_time_ms": processing_time_ms,
                },
            )

            receipt.analysis_status = "failed"
            receipt.error_message = f"Processing error: {str(e)}"
            receipt.error_code = "processing_error"
            receipt.processing_time_ms = processing_time_ms
            receipt.save()

            return False, str(e)

    def _queue_async_processing(self, receipt: Receipt) -> Tuple[bool, Optional[str]]:
        """
        Queue receipt for async processing via Celery.

        Args:
            receipt: Receipt to queue

        Returns:
            Tuple of (success, error_message)
        """
        try:
            from apps.receipts.tasks import analyze_receipt_async

            logger.info(
                f"[ASYNC] Queuing receipt for analysis",
                extra={"receipt_id": receipt.id},
            )

            receipt.analysis_status = "pending"
            receipt.save(update_fields=["analysis_status"])

            # Queue task
            analyze_receipt_async.delay(receipt.id)

            logger.info(
                f"[ASYNC] Receipt queued successfully",
                extra={"receipt_id": receipt.id},
            )
            return True, None

        except ImportError:
            logger.error(
                "[ASYNC] Celery not available, falling back to sync mode"
            )
            return self._process_synchronously(receipt)
        except Exception as e:
            logger.error(
                f"[ASYNC] Failed to queue receipt",
                exc_info=True,
                extra={"receipt_id": receipt.id},
            )

            receipt.analysis_status = "failed"
            receipt.error_message = f"Failed to queue: {str(e)}"
            receipt.error_code = "queue_error"
            receipt.save()

            return False, str(e)

    @staticmethod
    def _create_line_items(receipt: Receipt, extracted_data: dict) -> None:
        """Create line item records from extracted data."""
        if "line_items" not in extracted_data or not extracted_data["line_items"]:
            return

        line_items_to_create = []
        for item in extracted_data["line_items"]:
            line_items_to_create.append(
                ReceiptLineItem(
                    receipt=receipt,
                    description=item.get("description", ""),
                    quantity=float(item.get("quantity", 0)),
                    unit_price=float(item.get("unit_price", 0)),
                    total_price=float(item.get("total_price", 0)),
                    category=item.get("category"),
                )
            )

        if line_items_to_create:
            ReceiptLineItem.objects.bulk_create(line_items_to_create)
            logger.debug(
                f"Created line items",
                extra={
                    "receipt_id": receipt.id,
                    "count": len(line_items_to_create),
                },
            )