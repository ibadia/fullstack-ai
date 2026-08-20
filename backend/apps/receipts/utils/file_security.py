"""File upload security utilities."""

import hashlib
import logging
from pathlib import Path
from typing import Tuple, Optional

from django.core.files.uploadedfile import UploadedFile
from django.conf import settings

logger = logging.getLogger(__name__)

# Configuration from settings
RECEIPT_CONFIG = settings.RECEIPT_UPLOAD


class FileSecurityValidator:
    """Validate uploaded files for security."""

    @staticmethod
    def validate_receipt_file(file: UploadedFile) -> Tuple[bool, Optional[str]]:
        """
        Validate receipt file for security.

        Args:
            file: Uploaded file from Django

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if file.size > RECEIPT_CONFIG["MAX_FILE_SIZE"]:
            max_mb = RECEIPT_CONFIG["MAX_FILE_SIZE"] / (1024 * 1024)
            error = f"File size ({file.size / (1024*1024):.1f}MB) exceeds limit ({max_mb:.1f}MB)"
            logger.warning(f"File upload rejected: {error}, file_name={file.name}")
            return False, error

        # Check MIME type
        if file.content_type not in RECEIPT_CONFIG["ALLOWED_MIME_TYPES"]:
            error = f"File type '{file.content_type}' not allowed. Allowed: {', '.join(RECEIPT_CONFIG['ALLOWED_MIME_TYPES'])}"
            logger.warning(f"File upload rejected: {error}, file_name={file.name}")
            return False, error

        # Check file extension
        file_ext = Path(file.name).suffix.lstrip(".").lower()
        if file_ext not in RECEIPT_CONFIG["ALLOWED_EXTENSIONS"]:
            error = f"File extension '.{file_ext}' not allowed"
            logger.warning(f"File upload rejected: {error}, file_name={file.name}")
            return False, error

        # Additional check: verify file magic bytes (prevent spoofed MIME types)
        valid, error = FileSecurityValidator._verify_file_magic(file)
        if not valid:
            logger.warning(f"File upload rejected: {error}, file_name={file.name}")
            return False, error

        logger.info(
            f"File upload validation passed",
            extra={
                "file_name": file.name,
                "file_size_bytes": file.size,
                "file_type": file.content_type,
            },
        )
        return True, None

    @staticmethod
    def _verify_file_magic(file: UploadedFile) -> Tuple[bool, Optional[str]]:
        """
        Verify file magic bytes to prevent spoofed MIME types.

        Args:
            file: Uploaded file

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Read first few bytes for magic number check
        file.seek(0)
        header = file.read(12)
        file.seek(0)

        # Magic bytes for JPEG
        if header[:2] == b"\xff\xd8":
            return True, None

        # Magic bytes for PNG
        if header[:8] == b"\x89PNG\r\n\x1a\n":
            return True, None

        # Magic bytes for WebP
        if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
            return True, None

        return False, "File magic bytes do not match declared type"

    @staticmethod
    def generate_file_hash(file: UploadedFile) -> str:
        """
        Generate SHA256 hash of file for integrity checking.

        Args:
            file: Uploaded file

        Returns:
            Hex-encoded SHA256 hash
        """
        file.seek(0)
        file_hash = hashlib.sha256()
        for chunk in file.chunks():
            file_hash.update(chunk)
        file.seek(0)
        return file_hash.hexdigest()