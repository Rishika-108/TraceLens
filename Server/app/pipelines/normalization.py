import re
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

PLAN_PATTERNS = [
    r"\bmeet\s+(?:tomorrow|later|at|on|tonight|next\s+\w+)\b",
    r"\blet'?s\s+meet\b",
    r"\bplan(?:ning)?\s+to\b",
    r"\bscheduled\s+for\b",
    r"\brendezvous\b",
    r"\bcan\s+you\s+come\b",
    r"\bhoping\s+to\s+see\b",
    r"\bproposed\b",
]

EXECUTION_PATTERNS = [
    r"\b(?:i'?m|am)\s+(?:here|outside|waiting|at\s+the)\b",
    r"\barrived\b",
    r"\breached\b",
    r"\btransferred\b",
    r"\bsent\s+(?:the\s+funds|payment|money|btc|eth)\b",
    r"\bgood\s+seeing\s+you\b",
    r"\bthanks\s+for\s+meeting\b",
    r"\bmeeting\s+concluded\b",
]


def normalize_event(artifact: dict[str, Any], case_id: str | None = None) -> dict[str, Any] | None:
    """
    Normalizes a single parsed artifact into a standard event store item.
    Enforces forensic integrity:
    1. Drops system-generated READMEs, repo manifests, and setup files from timeline.
    2. Requires verified capture timestamps for image captures and documents.
    3. Distinguishes INTENDED / PLANNED events from VERIFIED / OCCURRED events.
    """
    raw_type = artifact.get("artifact_type", "UNKNOWN")
    metadata = artifact.get("metadata") or {}
    content = artifact.get("content", {})
    raw_ts = artifact.get("timestamp")

    # Exclude system documentation or explicitly excluded artifacts
    if metadata.get("exclude_from_timeline") or metadata.get("is_system_doc"):
        return None

    # Check filename for documentation terms if present
    filename = str(content.get("filename") or metadata.get("file_name") or "").lower()
    if any(k in filename for k in ["readme", "setup", "license", "requirements", "instruction", ".gitignore"]):
        return None

    # Standardize timestamp
    parsed_ts = None
    if isinstance(raw_ts, datetime):
        parsed_ts = raw_ts
    elif raw_ts:
        try:
            parsed_ts = date_parser.parse(str(raw_ts))
        except Exception:
            parsed_ts = None

    # For DOCUMENTS: Only include in timeline if document text has an internal date
    if raw_type == "DOCUMENT":
        if not parsed_ts:
            text_content = content.get("text", "")
            date_match = re.search(r"\b(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})\b", text_content)
            if date_match:
                try:
                    parsed_ts = date_parser.parse(date_match.group(1))
                except Exception:
                    pass
        # If no verified historical date in document, do not pollute chronological timeline
        if not parsed_ts:
            return None

    # For IMAGES: Only include in timeline if image has actual EXIF camera capture timestamp
    if raw_type == "IMAGE_METADATA":
        if not parsed_ts:
            return None

    # For communications / navigation: If missing timestamp, use ingestion timestamp
    if not parsed_ts:
        parsed_ts = artifact.get("created_at") or datetime.utcnow()

    event_type = EVENT_TYPE_MAP.get(raw_type, raw_type)
    actor = None
    target = None
    base_description = ""

    if raw_type == "CALL":
        actor = content.get("caller") or "UNKNOWN"
        target = content.get("receiver") or "UNKNOWN"
        duration = content.get("duration_seconds", 0)
        call_type = content.get("call_type", "CALL")
        base_description = f"{call_type} call between {actor} and {target} ({duration}s)"

    elif raw_type == "SMS":
        actor = content.get("sender") or "UNKNOWN"
        target = content.get("recipient") or "UNKNOWN"
        direction = content.get("direction", "SMS")
        msg = content.get("message", "")
        msg_preview = (msg[:90] + "...") if len(msg) > 90 else msg
        base_description = f"{direction} SMS from {actor} to {target}: \"{msg_preview}\""

    elif raw_type == "WHATSAPP_MESSAGE":
        actor = content.get("sender") or "UNKNOWN"
        target = "CHAT_RECIPIENTS"
        msg = content.get("message", "")
        msg_preview = (msg[:90] + "...") if len(msg) > 90 else msg
        if content.get("is_system"):
            base_description = f"WhatsApp System Event: {msg_preview}"
        else:
            base_description = f"WhatsApp Message from {actor}: \"{msg_preview}\""

    elif raw_type == "EMAIL":
        actor = content.get("sender") or "UNKNOWN"
        target = content.get("recipient") or "UNKNOWN"
        subject = content.get("subject", "No Subject")
        base_description = f"Email from {actor} to {target} | Subject: \"{subject}\""

    elif raw_type == "BROWSER_HISTORY":
        actor = "USER"
        target = content.get("url") or "UNKNOWN"
        title = content.get("title") or target
        base_description = f"Visited URL: {title} ({target})"

    elif raw_type == "DOCUMENT":
        actor = content.get("author") or "AUTHOR"
        target = content.get("title") or "DOCUMENT"
        section = content.get("page_number") or content.get("section") or 1
        text_preview = (content.get("text", "")[:90] + "...") if len(content.get("text", "")) > 90 else content.get("text", "")
        base_description = f"Document excerpt (p.{section}): \"{text_preview}\""

    elif raw_type == "IMAGE_METADATA":
        actor = content.get("camera_make", "CAMERA")
        target = content.get("filename", "IMAGE")
        base_description = f"Image capture: {target} ({content.get('exif_summary', '')})"

    else:
        base_description = f"Artifact record of type {raw_type}"

    # Analyze temporal modality: Planned vs Actually Occurred
    text_corpus = (
        str(content.get("message", "")) + " " +
        str(content.get("text", "")) + " " +
        str(content.get("subject", "")) + " " +
        str(content.get("body", ""))
    ).lower()

    is_plan = any(re.search(pat, text_corpus) for pat in PLAN_PATTERNS)
    is_execution = any(re.search(pat, text_corpus) for pat in EXECUTION_PATTERNS)

    if raw_type == "CALL" and content.get("duration_seconds", 0) > 0:
        modality = "VERIFIED_OCCURRENCE"
        description = f"[VERIFIED] {base_description}"
    elif raw_type == "IMAGE_METADATA":
        modality = "VERIFIED_OCCURRENCE"
        description = f"[VERIFIED] {base_description}"
    elif is_plan and not is_execution:
        modality = "INTENDED_PLAN"
        description = f"[PLAN / PROPOSED] {base_description} (Unverified whether meeting/action occurred)"
    elif is_execution:
        modality = "VERIFIED_OCCURRENCE"
        description = f"[VERIFIED] {base_description}"
    else:
        modality = "RECORDED_COMMUNICATION"
        description = f"[RECORDED] {base_description}"

    return {
        "artifact_id": artifact.get("id"),
        "evidence_id": artifact.get("evidence_id"),
        "case_id": case_id,
        "raw_artifact_type": raw_type,
        "event_type": event_type,
        "actor": actor,
        "target": target,
        "description": description,
        "modality": modality,
        "event_timestamp": parsed_ts,
        "source": artifact.get("source", "UNKNOWN"),
        "content": content,
        "raw_data": artifact.get("raw_data"),
        "normalized_at": datetime.utcnow(),
    }


def normalize(artifacts: list[dict[str, Any]], case_id: str | None = None) -> list[dict[str, Any]]:
    """
    Normalizes a list of parsed artifacts into standardized event store items,
    filtering out non-forensic documents and unanchored metadata.
    """
    events = []
    for artifact in artifacts:
        norm = normalize_event(artifact, case_id)
        if norm:
            events.append(norm)
    return events