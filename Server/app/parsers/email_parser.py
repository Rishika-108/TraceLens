import email
import json
import re
from email import policy
from pathlib import Path
from typing import Any
from app.parsers.base_parser import BaseParser


class EmailParser(BaseParser):
    """
    Forensic Email Parser.
    Supports RFC 822 (.eml), MBOX, and structured JSON email archives.
    """

    def parse(self, file_path: str) -> list[dict[str, Any]]:
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == ".json":
            return self._parse_json(file_path)
        elif ext in [".eml", ".msg", ".txt", ".mbox"]:
            return self._parse_eml_file(file_path)
        else:
            # Fallback: try EML parsing, if fails try JSON
            try:
                return self._parse_eml_file(file_path)
            except Exception:
                return self._parse_json(file_path)

    def _parse_eml_file(self, file_path: str) -> list[dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []

        with open(file_path, "rb") as file:
            msg = email.message_from_binary_file(file, policy=policy.default)

        sender = str(msg.get("From", "UNKNOWN"))
        recipient = str(msg.get("To", "UNKNOWN"))
        cc = str(msg.get("Cc", "")) if msg.get("Cc") else None
        bcc = str(msg.get("Bcc", "")) if msg.get("Bcc") else None
        subject = str(msg.get("Subject", "No Subject"))
        message_id = str(msg.get("Message-ID", ""))
        raw_date = str(msg.get("Date", ""))
        parsed_ts = self.parse_datetime(raw_date)

        body_text = ""
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in content_disposition:
                    filename = part.get_filename() or "unnamed_attachment"
                    payload = part.get_payload(decode=True) or b""
                    attachments.append({
                        "filename": filename,
                        "content_type": content_type,
                        "size_bytes": len(payload),
                    })
                elif content_type == "text/plain" and not body_text:
                    try:
                        body_text = part.get_content()
                    except Exception:
                        pass
                elif content_type == "text/html" and not body_text:
                    try:
                        raw_html = part.get_content()
                        # Simple tag stripper
                        body_text = re.sub(r"<[^>]+>", " ", raw_html)
                    except Exception:
                        pass
        else:
            try:
                body_text = msg.get_content()
            except Exception:
                payload = msg.get_payload(decode=True)
                body_text = payload.decode("utf-8", errors="replace") if payload else ""

        artifacts.append(
            {
                "artifact_type": "EMAIL",
                "timestamp": parsed_ts,
                "source": "EMAIL",
                "content": {
                    "sender": sender,
                    "recipient": recipient,
                    "cc": cc,
                    "bcc": bcc,
                    "subject": subject,
                    "body": body_text.strip(),
                    "message_id": message_id,
                    "attachments": attachments,
                },
                "raw_data": f"From: {sender}\nTo: {recipient}\nDate: {raw_date}\nSubject: {subject}\n\n{body_text[:1000]}",
                "metadata": {
                    "raw_date": raw_date,
                    "attachment_count": len(attachments),
                },
            }
        )

        return artifacts

    def _parse_json(self, file_path: str) -> list[dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []

        with open(file_path, "r", encoding="utf-8", errors="replace") as file:
            data = json.load(file)

        records = data if isinstance(data, list) else data.get("emails", data.get("messages", [data]))

        for idx, item in enumerate(records, start=1):
            if not isinstance(item, dict):
                continue

            sender = item.get("from") or item.get("sender") or "UNKNOWN"
            recipient = item.get("to") or item.get("recipient") or "UNKNOWN"
            subject = item.get("subject", "No Subject")
            body = item.get("body") or item.get("content") or item.get("text") or ""
            raw_ts = item.get("timestamp") or item.get("date") or item.get("time")
            parsed_ts = self.parse_datetime(raw_ts)

            artifacts.append(
                {
                    "artifact_type": "EMAIL",
                    "timestamp": parsed_ts,
                    "source": "EMAIL",
                    "content": {
                        "sender": str(sender),
                        "recipient": str(recipient),
                        "cc": str(item.get("cc", "")) if item.get("cc") else None,
                        "subject": str(subject),
                        "body": str(body).strip(),
                    },
                    "raw_data": json.dumps(item),
                    "metadata": {
                        "record_index": idx,
                        "raw_timestamp": raw_ts,
                    },
                }
            )

        return artifacts