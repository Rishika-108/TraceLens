import logging
import re
import sys
from typing import Any


# Patterns for sensitive forensic evidence redaction in logs
PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b")
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
CRYPTO_REGEX = re.compile(r"\b(?:0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,59})\b")


def sanitize_log_text(text: str) -> str:
    """
    Redacts phone numbers, emails, and crypto addresses from log text (AGENT.md Sec. 23, 69).
    """
    sanitized = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
    sanitized = PHONE_REGEX.sub("[REDACTED_PHONE]", sanitized)
    sanitized = CRYPTO_REGEX.sub("[REDACTED_CRYPTO]", sanitized)
    return sanitized


class EvidenceRedactionFilter(logging.Filter):
    """
    Logging filter that intercepts and sanitizes log records before emission.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = sanitize_log_text(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: (sanitize_log_text(str(v)) if isinstance(v, str) else v) for k, v in record.args.items()}
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(sanitize_log_text(str(arg)) if isinstance(arg, str) else arg for arg in record.args)
        return True


def get_logger(name: str = "tracelens") -> logging.Logger:
    """
    Configures and returns a safe, centralized logger for TraceLens.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.addFilter(EvidenceRedactionFilter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger


logger = get_logger("tracelens")
