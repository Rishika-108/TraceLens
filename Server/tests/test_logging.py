import logging
from app.core.logging import EvidenceRedactionFilter, sanitize_log_text


def test_sanitize_log_text_redacts_sensitive_evidence():
    sensitive_log = (
        "Processing call from +1 415-555-2671 to +91-9876543210. "
        "User email is suspect_99@protonmail.com. "
        "Crypto payout sent to 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa on Case case-12345."
    )

    sanitized = sanitize_log_text(sensitive_log)

    assert "+1 415-555-2671" not in sanitized
    assert "+91-9876543210" not in sanitized
    assert "suspect_99@protonmail.com" not in sanitized
    assert "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" not in sanitized

    assert "[REDACTED_PHONE]" in sanitized
    assert "[REDACTED_EMAIL]" in sanitized
    assert "[REDACTED_CRYPTO]" in sanitized
    assert "Case case-12345" in sanitized


def test_evidence_redaction_filter_in_logger():
    filter_obj = EvidenceRedactionFilter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Suspect phone +14155559999 observed in log stream",
        args=(),
        exc_info=None,
    )

    filter_obj.filter(record)
    assert "+14155559999" not in record.msg
    assert "[REDACTED_PHONE]" in record.msg
