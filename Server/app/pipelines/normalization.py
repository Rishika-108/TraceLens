from datetime import datetime
from typing import Any
from dateutil import parser as date_parser


EVENT_TYPE_MAP = {
    "CALL": "PHONE_COMMUNICATION",
    "SMS": "SMS_COMMUNICATION",
    "WHATSAPP_MESSAGE": "CHAT_COMMUNICATION",
    "EMAIL": "EMAIL_COMMUNICATION",
    "BROWSER_HISTORY": "WEB_NAVIGATION",
    "DOCUMENT": "DOCUMENT_RECORD",
    "IMAGE_METADATA": "IMAGE_CAPTURE",
}


def normalize_event(artifact: dict[str, Any], case_id: str | None = None) -> dict[str, Any]:
    """
    Normalizes a single parsed artifact into a standard event store item.
    Extracts actor, target, standardized event type, and human-readable description.
    """
    raw_type = artifact.get("artifact_type", "UNKNOWN")
    event_type = EVENT_TYPE_MAP.get(raw_type, raw_type)
    content = artifact.get("content", {})
    raw_ts = artifact.get("timestamp")

    # Standardize timestamp
    parsed_ts = None
    if isinstance(raw_ts, datetime):
        parsed_ts = raw_ts
    elif raw_ts:
        try:
            parsed_ts = date_parser.parse(str(raw_ts))
        except Exception:
            parsed_ts = None

    actor = None
    target = None
    description = ""

    if raw_type == "CALL":
        actor = content.get("caller") or "UNKNOWN"
        target = content.get("receiver") or "UNKNOWN"
        duration = content.get("duration_seconds", 0)
        call_type = content.get("call_type", "CALL")
        description = f"{call_type} call between {actor} and {target} ({duration}s)"

    elif raw_type == "SMS":
        actor = content.get("sender") or "UNKNOWN"
        target = content.get("recipient") or "UNKNOWN"
        direction = content.get("direction", "SMS")
        msg_preview = (content.get("message", "")[:80] + "...") if len(content.get("message", "")) > 80 else content.get("message", "")
        description = f"{direction} SMS from {actor} to {target}: \"{msg_preview}\""

    elif raw_type == "WHATSAPP_MESSAGE":
        actor = content.get("sender") or "UNKNOWN"
        target = "CHAT_RECIPIENTS"
        msg = content.get("message", "")
        msg_preview = (msg[:80] + "...") if len(msg) > 80 else msg
        if content.get("is_system"):
            description = f"WhatsApp System Event: {msg_preview}"
        else:
            description = f"WhatsApp Message from {actor}: \"{msg_preview}\""

    elif raw_type == "EMAIL":
        actor = content.get("sender") or "UNKNOWN"
        target = content.get("recipient") or "UNKNOWN"
        subject = content.get("subject", "No Subject")
        description = f"Email from {actor} to {target} | Subject: \"{subject}\""

    elif raw_type == "BROWSER_HISTORY":
        actor = "USER"
        target = content.get("url") or "UNKNOWN"
        title = content.get("title") or target
        description = f"Visited URL: {title} ({target})"

    elif raw_type == "DOCUMENT":
        actor = content.get("author") or "AUTHOR"
        target = content.get("title") or "DOCUMENT"
        section = content.get("page_number") or content.get("section") or 1
        text_preview = (content.get("text", "")[:80] + "...") if len(content.get("text", "")) > 80 else content.get("text", "")
        description = f"Document excerpt (p.{section}): \"{text_preview}\""

    elif raw_type == "IMAGE_METADATA":
        actor = content.get("camera_make", "CAMERA")
        target = content.get("filename", "IMAGE")
        description = f"Image capture: {target} ({content.get('exif_summary', '')})"

    else:
        description = f"Artifact record of type {raw_type}"

    return {
        "artifact_id": artifact.get("id"),
        "evidence_id": artifact.get("evidence_id"),
        "case_id": case_id,
        "raw_artifact_type": raw_type,
        "event_type": event_type,
        "actor": actor,
        "target": target,
        "description": description,
        "event_timestamp": parsed_ts,
        "source": artifact.get("source", "UNKNOWN"),
        "content": content,
        "raw_data": artifact.get("raw_data"),
        "normalized_at": datetime.utcnow(),
    }


def normalize(artifacts: list[dict[str, Any]], case_id: str | None = None) -> list[dict[str, Any]]:
    """
    Normalizes a list of parsed artifacts into standardized event store items.
    """
    return [normalize_event(artifact, case_id) for artifact in artifacts]