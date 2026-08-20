"""Security and logging middleware."""

import logging
import time
import uuid
from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

# Paths that don't need logging
SKIP_LOGGING_PATHS = [
    "/healthcheck/",
    "/static/",
    "/media/",
]


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log HTTP requests and responses.

    Logs:
    - Request method, path, status
    - User ID (if authenticated)
    - Processing time
    - Errors (4xx, 5xx responses)

    Does NOT log:
    - Request/response bodies (to avoid logging sensitive data)
    - Full query strings (to avoid logging secrets)
    - File contents (to avoid logging uploaded documents)
    """

    def process_request(self, request: HttpRequest) -> None:
        """Capture request start time and generate request ID."""
        # Skip logging for certain paths
        if any(request.path.startswith(p) for p in SKIP_LOGGING_PATHS):
            return

        # Generate request ID for tracing
        request.id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request._start_time = time.time()

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """Log request/response details."""
        # Skip logging for certain paths
        if any(request.path.startswith(p) for p in SKIP_LOGGING_PATHS):
            return response

        # Calculate processing time
        duration_ms = 0
        if hasattr(request, "_start_time"):
            duration_ms = int((time.time() - request._start_time) * 1000)

        # Extract relevant info
        method = request.method
        path = request.path
        status = response.status_code
        user_id = request.user.id if request.user.is_authenticated else None

        # Log based on status code
        if 400 <= status < 500:
            logger.warning(
                f"Client error: {method} {path} {status}",
                extra={
                    "request_id": getattr(request, "id", "unknown"),
                    "status": status,
                    "user_id": user_id,
                    "duration_ms": duration_ms,
                },
            )
        elif status >= 500:
            logger.error(
                f"Server error: {method} {path} {status}",
                extra={
                    "request_id": getattr(request, "id", "unknown"),
                    "status": status,
                    "user_id": user_id,
                    "duration_ms": duration_ms,
                },
            )
        else:
            logger.debug(
                f"Request: {method} {path} {status}",
                extra={
                    "request_id": getattr(request, "id", "unknown"),
                    "status": status,
                    "user_id": user_id,
                    "duration_ms": duration_ms,
                },
            )

        # Add request ID to response headers
        response["X-Request-ID"] = getattr(request, "id", "unknown")

        return response

    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        """Log unhandled exceptions."""
        logger.error(
            f"Unhandled exception: {type(exception).__name__}: {str(exception)}",
            exc_info=True,
            extra={
                "request_id": getattr(request, "id", "unknown"),
                "user_id": request.user.id if request.user.is_authenticated else None,
                "path": request.path,
            },
        )