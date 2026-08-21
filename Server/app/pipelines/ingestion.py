import csv
import json
import re
from pathlib import Path
from typing import Any

from app.parsers.base_parser import BaseParser
from app.parsers.browser_parser import BrowserParser
from app.parsers.call_parser import CallParser
from app.parsers.document_parser import DocumentParser
from app.parsers.email_parser import EmailParser
from app.parsers.image_parser import ImageParser
from app.parsers.sms_parser import SMSParser
from app.parsers.whatsapp_parser import WhatsAppParser


WHATSAPP_SNIFF_REGEX = re.compile(r"^\s*(\[?\d{1,4}[/\-\.]\d{1,2}[/\-\.]\d{1,4})")


def detect_parser(file_path: str, evidence_type_hint: str | None = None) -> BaseParser:
    """
    Intelligently select the appropriate parser based on type hint, file extension, and content sniffing.
    """
    if evidence_type_hint:
        hint = evidence_type_hint.upper().strip()
        if "WHATSAPP" in hint or "CHAT" in hint:
            return WhatsAppParser()
        if "CALL" in hint:
            return CallParser()
        if "SMS" in hint or "MMS" in hint:
            return SMSParser()
        if "EMAIL" in hint or "MAIL" in hint:
            return EmailParser()
        if "BROWSER" in hint or "HISTORY" in hint:
            return BrowserParser()
        if "IMAGE" in hint or "PHOTO" in hint:
            return ImageParser()
        if "DOC" in hint or "PDF" in hint or "TEXT" in hint:
            return DocumentParser()

    path = Path(file_path)
    ext = path.suffix.lower()

    # Image extensions
    if ext in [".jpg", ".jpeg", ".png", ".heic", ".webp", ".tiff", ".bmp", ".gif"]:
        return ImageParser()

    # Document formats
    if ext in [".pdf", ".docx", ".doc"]:
        return DocumentParser()

    # Email formats
    if ext in [".eml", ".msg", ".mbox"]:
        return EmailParser()

    # SQLite database files (Browser History)
    if ext in [".sqlite", ".db", ".sqlite3"] or path.name.lower() in ["history", "places.sqlite"]:
        return BrowserParser()

    # Text files: Sniff for WhatsApp vs Plain Document
    if ext in [".txt", ".log", ".chat"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                sample_lines = [f.readline() for _ in range(5)]
                for line in sample_lines:
                    if WHATSAPP_SNIFF_REGEX.search(line) and (" - " in line or ":" in line):
                        return WhatsAppParser()
        except Exception:
            pass
        return DocumentParser()

    # Delimited files (CSV / TSV): Sniff header
    if ext in [".csv", ".tsv"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                header = next(reader, [])
                header_str = " ".join(header).lower()

                if any(k in header_str for k in ["caller", "duration", "callee", "call_type"]):
                    return CallParser()
                if any(k in header_str for k in ["sms", "message", "body", "sms_body", "recipient"]):
                    return SMSParser()
                if any(k in header_str for k in ["url", "title", "visit", "typed_count"]):
                    return BrowserParser()
                if any(k in header_str for k in ["from", "to", "subject"]):
                    return EmailParser()
        except Exception:
            pass
        return CallParser()

    # JSON files: Sniff structure
    if ext == ".json":
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                first_item = data[0] if isinstance(data, list) and data else (data if isinstance(data, dict) else {})
                keys_str = " ".join(first_item.keys()).lower()

                if any(k in keys_str for k in ["subject", "bcc", "cc", "body"]) and "from" in keys_str:
                    return EmailParser()
                if any(k in keys_str for k in ["caller", "duration", "call_type"]):
                    return CallParser()
                if any(k in keys_str for k in ["message", "sms", "recipient", "sms_body"]):
                    return SMSParser()
                if any(k in keys_str for k in ["url", "page_url", "title", "visit_count"]):
                    return BrowserParser()
        except Exception:
            pass
        return EmailParser()

    # Default fallback
    return DocumentParser()


def ingest(file_path: str, evidence_type_hint: str | None = None) -> list[dict[str, Any]]:
    """
    Main ingestion entrypoint. Detects parser, processes evidence, and returns structured artifacts.
    """
    parser = detect_parser(file_path, evidence_type_hint)
    return parser.parse(file_path)