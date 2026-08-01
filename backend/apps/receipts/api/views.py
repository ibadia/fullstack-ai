"""API views for receipt operations."""

import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from apps.receipts.api.serializers import (
    ReceiptSerializer,
    ReceiptUploadSerializer,
    ReceiptLineItemSerializer,
)
from apps.receipts.models import Receipt, ReceiptLineItem
from apps.receipts.services.processor import ReceiptProcessor
from utils.pagination import CorePagination
from utils.response.resp import APIResponse

logger = logging.getLogger(__name__)


class ReceiptUploadAPIView(APIView):
    """Upload receipt image for analysis."""

    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        request_body=ReceiptUploadSerializer,
        responses={
            200: openapi.Response(
                description="Receipt uploaded and analyzed successfully (sync mode). "
                "Status code may be 200 (sync) or 202 (async pending) depending on RECEIPT_PROCESSING_MODE.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "receipt": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    description="Receipt object with analysis results",
                                ),
                            },
                        ),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            202: openapi.Response(
                description="Receipt uploaded and queued for analysis (async mode). "
                "Poll /receipts/{id}/ to check status.",
            ),
            400: openapi.Response(description="Validation error or invalid file."),
            401: openapi.Response(description="Authentication required."),
            500: openapi.Response(description="Analysis processing error."),
        },
        tags=["Receipts"],
    )
    def post(self, request):
        """
        Upload receipt image for AI analysis.

        - **Sync mode (default)**: Analysis happens immediately. Returns 200 with results.
        - **Async mode**: Receipt queued for background processing. Returns 202 (Accepted).
          Use receipt ID to poll status via GET /api/receipts/{id}/.
        """
        serializer = ReceiptUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                APIResponse.get_response(
                    message="Validation error",
                    error=serializer.errors,
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Create receipt record
            file = serializer.validated_data["file"]
            receipt = Receipt.objects.create(
                file=file,
                file_name=file.name,
                file_size_bytes=file.size,
                analysis_status="pending",
            )

            logger.info(f"Receipt {receipt.id} created, starting analysis")

            # Process receipt (sync or async based on settings)
            processor = ReceiptProcessor()
            success, error_msg = processor.process_receipt(receipt)

            receipt_serializer = ReceiptSerializer(receipt)

            if success:
                # Sync mode: analysis complete
                return Response(
                    APIResponse.get_response(
                        message="Receipt analyzed successfully",
                        data={"receipt": receipt_serializer.data},
                    ),
                    status=status.HTTP_200_OK,
                )
            elif receipt.analysis_status == "pending":
                # Async mode: queued for processing
                return Response(
                    APIResponse.get_response(
                        message="Receipt queued for analysis. Check status via GET /api/receipts/{id}/",
                        data={"receipt": receipt_serializer.data},
                    ),
                    status=status.HTTP_202_ACCEPTED,
                )
            else:
                # Sync mode: analysis failed
                return Response(
                    APIResponse.get_response(
                        message=f"Analysis failed: {error_msg}",
                        error={"error_code": receipt.error_code, "detail": error_msg},
                        data={"receipt": receipt_serializer.data},
                    ),
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            logger.error(f"Failed to upload receipt: {e}", exc_info=True)
            return Response(
                APIResponse.get_response(
                    message="Failed to upload receipt",
                    error={"detail": str(e)},
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ReceiptDetailAPIView(APIView):
    """Get receipt details and analysis results."""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="receipt_id",
                in_=openapi.IN_PATH,
                description="Receipt ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Receipt details retrieved.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "receipt": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                ),
                            },
                        ),
                    },
                ),
            ),
            404: openapi.Response(description="Receipt not found."),
        },
        tags=["Receipts"],
    )
    def get(self, request, receipt_id):
        """Get receipt details including analysis results and status."""
        try:
            receipt = Receipt.objects.get(id=receipt_id)
        except Receipt.DoesNotExist:
            return Response(
                APIResponse.get_response(
                    message="Receipt not found",
                ),
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReceiptSerializer(receipt)
        return Response(
            APIResponse.get_response(
                data={"receipt": serializer.data},
            )
        )


class ReceiptListAPIView(ListAPIView):
    """List all receipts for the authenticated user."""

    permission_classes = [IsAuthenticated]
    queryset = Receipt.objects.all().order_by("-created_at")
    serializer_class = ReceiptSerializer
    pagination_class = CorePagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="analysis_status",
                in_=openapi.IN_QUERY,
                description="Filter by analysis status (pending, processing, completed, failed)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                name="page",
                in_=openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(description="List of receipts."),
            401: openapi.Response(description="Authentication required."),
        },
        tags=["Receipts"],
    )
    def get(self, request, *args, **kwargs):
        """List receipts with optional filtering by status."""
        status_filter = request.query_params.get("analysis_status")
        if status_filter:
            self.queryset = self.queryset.filter(analysis_status=status_filter)

        return super().get(request, *args, **kwargs)


class ReceiptLineItemsAPIView(ListAPIView):
    """List line items for a receipt."""

    permission_classes = [IsAuthenticated]
    serializer_class = ReceiptLineItemSerializer
    pagination_class = CorePagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="receipt_id",
                in_=openapi.IN_PATH,
                description="Receipt ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        tags=["Receipts"],
    )
    def get_queryset(self):
        """Get line items for specific receipt."""
        receipt_id = self.kwargs.get("receipt_id")
        return ReceiptLineItem.objects.filter(receipt_id=receipt_id).order_by("created_at")

    def get(self, request, *args, **kwargs):
        """Get line items for a receipt."""
        receipt_id = self.kwargs.get("receipt_id")
        try:
            Receipt.objects.get(id=receipt_id)
        except Receipt.DoesNotExist:
            return Response(
                APIResponse.get_response(message="Receipt not found"),
                status=status.HTTP_404_NOT_FOUND,
            )

        return super().get(request, *args, **kwargs)