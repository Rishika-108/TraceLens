import re
from typing import Any
from app.parsers.base_parser import BaseParser


# Regex patterns for WhatsApp chat export formats
ANDROID_PATTERN = re.compile(
    r"^\[?(\d{1,4}[/\-\.]\d{1,2}[/\-\.]\d{1,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[apAP][mM])?)\]?\s*(?:-|\s)\s*(.+)$"
)

IOS_PATTERN = re.compile(
    r"^\[(\d{1,4}[/\-\.]\d{1,2}[/\-\.]\d{1,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[apAP][mM])?)\]\s+(.+)$"
)

SENDER_MESSAGE_PATTERN = re.compile(r"^([^:]+?):\s+(.*)$", re.DOTALL)

SYSTEM_NOTICE_KEYWORDS = [
    "messages and calls are end-to-end encrypted",
    "changed the subject to",
    "changed the group description",
    "changed this group's icon",
    "added",
    "left",
    "removed",
    "created group",
    "you're now an admin",
    "security code changed",
    "missed voice call",
    "missed video call",
]


class WhatsAppParser(BaseParser):
    """
    Robust WhatsApp Chat Export Parser.
    Handles Android/iOS formats, 12h/24h timestamps, multiline messages, media classification, and system audit events.
    """

    def parse(self, file_path: str) -> list[dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []

        # Auto-detect encoding
        encoding = "utf-8"
        try:
            with open(file_path, "rb") as bf:
                header = bf.read(4)
                if header.startswith(b"\xff\xfe"):
                    encoding = "utf-16-le"
                elif header.startswith(b"\xfe\xff"):
                    encoding = "utf-16-be"
                elif header.startswith(b"\xef\xbb\xbf"):
                    encoding = "utf-8-sig"
        except Exception:
            pass

        try:
            with open(file_path, "r", encoding=encoding, errors="replace") as file:
                lines = file.readlines()
        except Exception as e:
            raise ValueError(f"Failed to read WhatsApp export file: {str(e)}")

        current_message: dict[str, Any] | None = None

        for line_idx, line in enumerate(lines, start=1):
            line_str = (
                line.rstrip("\r\n")
                .replace("\u200e", "")
                .replace("\u200f", "")
                .replace("\ufeff", "")
                .replace("\u202f", " ")
                .replace("\xa0", " ")
            )
            if not line_str.strip():
                continue

            # Check if line begins a new message (Android or iOS format)
            match = ANDROID_PATTERN.match(line_str) or IOS_PATTERN.match(line_str)

            if match:
                # Flush previous message if present
                if current_message:
                    self._finalize_and_append(artifacts, current_message)

                date_part, time_part, remainder = match.groups()
                raw_ts = f"{date_part} {time_part}"
                parsed_ts = self.parse_datetime(raw_ts)

                # Check if remainder is "Sender: Message" or a system event
                sender_match = SENDER_MESSAGE_PATTERN.match(remainder)
                if sender_match:
                    sender = sender_match.group(1).strip()
                    message_text = sender_match.group(2).strip()
                    is_system = any(kw in message_text.lower() for kw in SYSTEM_NOTICE_KEYWORDS)
                else:
                    sender = "SYSTEM"
                    message_text = remainder.strip()
                    is_system = True

                current_message = {
                    "raw_timestamp": raw_ts,
                    "parsed_timestamp": parsed_ts,
                    "sender": sender,
                    "message_lines": [message_text],
                    "raw_lines": [line_str],
                    "start_line": line_idx,
                    "is_system": is_system,
                }
            else:
                # Continuation of multiline message
                if current_message:
                    current_message["message_lines"].append(line_str)
                    current_message["raw_lines"].append(line_str)
                else:
                    # Text before first valid timestamp (e.g. export header)
                    current_message = {
                        "raw_timestamp": None,
                        "parsed_timestamp": None,
                        "sender": "SYSTEM",
                        "message_lines": [line_str],
                        "raw_lines": [line_str],
                        "start_line": line_idx,
                        "is_system": True,
                    }

        # Flush final message
        if current_message:
            self._finalize_and_append(artifacts, current_message)

        return artifacts

    def _finalize_and_append(
        self,
        artifacts: list[dict[str, Any]],
        msg_data: dict[str, Any],
    ) -> None:
        full_message = "\n".join(msg_data["message_lines"]).strip()
        raw_text = "\n".join(msg_data["raw_lines"])
        msg_lower = full_message.lower()

        # Classify media attachments
        attachment_type = None
        is_media = False
        if "<media omitted>" in msg_lower or "attachment omitted" in msg_lower:
            is_media = True
            attachment_type = "MEDIA_FILE"
        elif "image omitted" in msg_lower or "photo omitted" in msg_lower or ".jpg" in msg_lower or ".png" in msg_lower:
            is_media = True
            attachment_type = "IMAGE"
        elif "video omitted" in msg_lower or ".mp4" in msg_lower:
            is_media = True
            attachment_type = "VIDEO"
        elif "audio omitted" in msg_lower or "voice message" in msg_lower or ".opus" in msg_lower or ".m4a" in msg_lower:
            is_media = True
            attachment_type = "AUDIO"
        elif "document omitted" in msg_lower or ".pdf" in msg_lower or ".doc" in msg_lower:
            is_media = True
            attachment_type = "DOCUMENT"
        elif "contact card omitted" in msg_lower or ".vcf" in msg_lower:
            is_media = True
            attachment_type = "CONTACT_CARD"

        is_deleted = "this message was deleted" in msg_lower or "you deleted this message" in msg_lower
        is_system = msg_data["is_system"] or any(kw in msg_lower for kw in SYSTEM_NOTICE_KEYWORDS)

        artifact_type = "SYSTEM_AUDIT_EVENT" if is_system else "WHATSAPP_MESSAGE"

        artifacts.append(
            {
                "artifact_type": artifact_type,
                "timestamp": msg_data["parsed_timestamp"],
                "source": "WHATSAPP",
                "content": {
                    "sender": msg_data["sender"],
                    "message": full_message,
                    "is_system": is_system,
                    "is_media": is_media,
                    "attachment_type": attachment_type,
                    "is_deleted": is_deleted,
                },
                "raw_data": raw_text,
                "metadata": {
                    "line_number": msg_data["start_line"],
                    "raw_timestamp": msg_data["raw_timestamp"],
                    "is_system_audit": is_system,
                },
            }
        )