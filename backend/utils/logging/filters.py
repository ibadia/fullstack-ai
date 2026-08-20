"""Custom logging filters for security."""

import json
import logging
import re
from typing import Any, Dict

SENSITIVE_PATTERNS = {
    "api_key": re.compile(r"(?i)(api[_-]?key|apikey|access[_-]?token|token)['\"]?\s*[:=]\s*['\"]?([^'\"]+)['\"]?"),
    "secret": re.compile(r"(?i)(secret|password)['\"]?\s*[:=]\s*['\"]?([^'\"]+)['\"]?"),
    "auth": re.compile(r"(?i)(authorization|bearer)['\"]?\s*[:=]\s*['\"]?([^'\"]+)['\"]?"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
}


class SanitizeCredentialsFilter(logging.Filter):
    """
    Filter to sanitize sensitive credentials from log messages.

    Removes:
    - API keys and tokens
    - Passwords and secrets
    - Authorization headers
    - Email addresses (optional)
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize sensitive information from log record."""
        if isinstance(record.msg, str):
            record.msg = self._sanitize(record.msg)

        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self._sanitize(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self._sanitize(str(arg)) for arg in record.args)

        return True

    @staticmethod
    def _sanitize(text: str) -> str:
        """Replace sensitive values with placeholder."""
        for pattern_name, pattern in SENSITIVE_PATTERNS.items():
            text = pattern.sub(rf"\1=***REDACTED***", text)
        return text


class JsonFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""

    def __init__(self, fmt_keys: Dict[str, str] = None):
        """
        Initialize formatter.

        Args:
            fmt_keys: Mapping of log field names to LogRecord attributes
        """
        super().__init__()
        self.fmt_keys = fmt_keys or {}

    def format(self, record: logging.LogRecord) -> str:
        """Format record as JSON."""
        log_data = {
            self.fmt_keys.get("timestamp", "timestamp"): self.formatTime(record),
            self.fmt_keys.get("level", "level"): record.levelname,
            self.fmt_keys.get("logger", "logger"): record.name,
            self.fmt_keys.get("message", "message"): record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data)