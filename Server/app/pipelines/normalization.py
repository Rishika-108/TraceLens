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
    "IMAGE_METADATA": "IMAGE_RECORD",
}

PLAN_PATTERNS = [
    r"\b(?:should|can|could|will|let'?s)\s+meet\b",
    r"\bmeet\s+(?:near|at|in|by|around|outside|tomorrow|later|tonight|next\s+\w+)\b",
    r"\bmeet(?:ing)?\s+near\b",
    r"\bwe\s+should\s+meet\b",
    r"\bplan(?:ning)?\s+(?:to\s+meet|to\s+come|for)\b",
    r"\bscheduled\s+(?:for|at)\b",
    r"\brendezvous\b",
    r"\bproposed\s+meeting\b",
    r"\bcan\s+you\s+come\b",
    r"\bhoping\s+to\s+see\b",
]

ACKNOWLEDGMENT_PATTERNS = [
    r"\breceived[.,!]?\s*(?:i\s+will|i'll)\s+be\s+there\b",
    r"\bi\s+will\s+be\s+there\b",
    r"\bi'll\s+be\s+there\b",
    r"\bsee\s+you\s+there\b",
    r"\bgot\s+it,\s*(?:will|see)\b",
    r"\bwill\s+reach\b",
]

EXECUTION_PATTERNS = [
    r"\b(?:i'?m|am)\s+(?:here|outside|waiting|at\s+the)\b",
    r"\barrived\b",
    r"\breached\s+the\s+spot\b",
    r"\btransferred\b",
    r"\bsent\s+(?:the\s+funds|payment|money|btc|eth)\b",
    r"\bgood\s+seeing\s+you\b",
    r"\bthanks\s+for\s+meeting\b",
    r"\bmeeting\s+concluded\b",
]

TIME_REGEX = re.compile(r"\b(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[apAP][mM])?|\d{1,2}\s*[apAP][mM])\b")
LOCATION_NEAR_REGEX = re.compile(r"\b(?:near|at|around|outside|in)\s+([A-Z][a-z0-9]+(?:\s+[A-Z][a-z0-9]+)?)")


def normalize_event(artifact: dict[str, Any], case_id: str | None = None) -> dict[str, Any] | None:
    """
    Normalizes a single parsed artifact into a standard event store item.
    Enforces forensic integrity:
    1. Drops system-generated READMEs, repo manifests, and synthetic test documentation.
    2. Separates message transmission timestamp from referenced future event time.
    3. Distinguishes event states: PLANNED, ACKNOWLEDGED, OCCURRED, UNVERIFIED.
    4. Prohibits treating image capture or subsequent photos as meeting occurrence.
    """
    raw_type = artifact.get("artifact_type", "UNKNOWN")
    metadata = artifact.get("metadata") or {}
    content = artifact.get("content", {})
    raw_ts = artifact.get("timestamp")

    # Exclude system documentation or explicitly excluded artifacts
    if metadata.get("exclude_from_timeline") or metadata.get("is_system_doc"):
        return None

    filename = str(content.get("filename") or metadata.get("file_name") or "").lower()
    if any(k in filename for k in ["readme", "setup", "license", "requirements", "instruction", ".gitignore", "synthetic"]):
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
        if not parsed_ts:
            return None

    # For IMAGES: Only include in timeline if image has actual EXIF camera capture timestamp
    if raw_type == "IMAGE_METADATA":
        if not parsed_ts:
            return None

    # Fallback to ingestion timestamp for communications lacking timestamp
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
        search_q = content.get("search_query")
        if search_q:
            base_description = f"Web Search: \"{search_q}\" ({title})"
            event_type = "WEB_SEARCH_QUERY"
        else:
            base_description = f"Visited URL: {title} ({target})"

    elif raw_type == "DOCUMENT":
        actor = content.get("author") or "AUTHOR"
        target = content.get("title") or "DOCUMENT"
        section = content.get("page_number") or content.get("section") or 1
        text_preview = (content.get("text", "")[:90] + "...") if len(content.get("text", "")) > 90 else content.get("text", "")
        base_description = f"Document excerpt (p.{section}): \"{text_preview}\""

    elif raw_type == "IMAGE_METADATA":
        actor = content.get("camera_make") or content.get("camera_display") or "CAMERA"
        target = content.get("filename", "IMAGE")
        exif_sum = content.get("exif_summary", "Image EXIF")
        base_description = f"Image file record: {target} ({exif_sum})"

    else:
        base_description = f"Artifact record of type {raw_type}"

    # Analyze temporal modality and extract referenced future times
    text_corpus = (
        str(content.get("message", "")) + " " +
        str(content.get("text", "")) + " " +
        str(content.get("subject", "")) + " " +
        str(content.get("body", ""))
    ).lower()

    is_plan = any(re.search(pat, text_corpus, re.IGNORECASE) for pat in PLAN_PATTERNS)
    is_ack = any(re.search(pat, text_corpus, re.IGNORECASE) for pat in ACKNOWLEDGMENT_PATTERNS)
    is_execution = any(re.search(pat, text_corpus, re.IGNORECASE) for pat in EXECUTION_PATTERNS)

    referenced_time = None
    referenced_location = None
    time_match = TIME_REGEX.search(text_corpus)
    if time_match:
        referenced_time = time_match.group(1).upper()
    loc_match = LOCATION_NEAR_REGEX.search(str(content.get("message", "") or content.get("text", "")))
    if loc_match:
        referenced_location = loc_match.group(0)

    # Classify event state
    if is_plan and not is_execution:
        event_state = "PLANNED"
        modality = "INTENDED_PLAN"
        time_spec = f" at {referenced_time}" if referenced_time else ""
        loc_spec = f" ({referenced_location})" if referenced_location else ""
        description = f"[PLANNED EVENT{time_spec}{loc_spec}] {base_description} — Physical occurrence UNVERIFIED"

    elif is_ack and not is_execution:
        event_state = "ACKNOWLEDGED"
        modality = "PROPOSED_ACKNOWLEDGMENT"
        description = f"[ACKNOWLEDGED] Response indicating intent to attend: \"{base_description}\" — Physical occurrence UNVERIFIED"

    elif raw_type == "CALL" and content.get("duration_seconds", 0) > 0:
        event_state = "OCCURRED"
        modality = "VERIFIED_OCCURRENCE"
        description = f"[OCCURRED] {base_description}"

    elif raw_type == "IMAGE_METADATA":
        event_state = "IMAGE_CAPTURE"
        modality = "MEDIA_RECORD"
        capture_str = parsed_ts.strftime("%b %d, %H:%M") if parsed_ts else "Date Unrecorded"
        description = f"[MEDIA RECORD] {base_description} (Captured: {capture_str} — Independent media capture)"

    elif is_execution:
        event_state = "OCCURRED"
        modality = "VERIFIED_OCCURRENCE"
        description = f"[OCCURRED] {base_description}"

    else:
        event_state = "RECORDED"
        modality = "RECORDED_COMMUNICATION"
        description = f"[RECORDED] {base_description}"

    return {
        "artifact_id": artifact.get("id"),
        "evidence_id": artifact.get("evidence_id"),
        "case_id": case_id,
        "raw_artifact_type": raw_type,
        "event_type": event_type,
        "event_state": event_state,
        "actor": actor,
        "target": target,
        "description": description,
        "modality": modality,
        "event_timestamp": parsed_ts,
        "referenced_time": referenced_time,
        "referenced_location": referenced_location,
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