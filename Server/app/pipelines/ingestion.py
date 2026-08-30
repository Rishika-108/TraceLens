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


WHATSAPP_SNIFF_REGEX = re.compile(
    r"^\s*(\[?\d{1,4}[/\-\.]\d{1,2}[/\-\.]\d{1,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[apAP][mM])?)[\]\s-]+([^:]+?):"
)

SYSTEM_DOC_PATTERNS = [
    r"^readme(\..*)?$",
    r"^license(\..*)?$",
    r"^requirements(\..*)?$",
    r"^setup(\..*)?$",
    r"^instructions?(\..*)?$",
    r"^\.gitignore$",
    r".*dataset_readme.*",
]


def is_system_documentation(file_path: str) -> bool:
    """
    Identifies setup files, READMEs, instructions, and non-forensic repository metadata.
    """
    filename = Path(file_path).name.lower().strip()
    return any(re.match(pattern, filename, re.IGNORECASE) for pattern in SYSTEM_DOC_PATTERNS)


def detect_parser(file_path: str, evidence_type_hint: str | None = None) -> BaseParser:
    """
    Intelligently select the appropriate parser based on type hint, file extension, and deep content sniffing.
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

    # Text files: Sniff for WhatsApp vs Plain Document (check first 50 non-empty lines)
    if ext in [".txt", ".log", ".chat"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines_checked = 0
                for line in f:
                    clean_line = (
                        line.strip()
                        .replace("\u200e", "")
                        .replace("\u200f", "")
                        .replace("\ufeff", "")
                        .replace("\u202f", " ")
                        .replace("\xa0", " ")
                    )
                    if not clean_line:
                        continue
                    lines_checked += 1
                    if WHATSAPP_SNIFF_REGEX.search(clean_line) or (
                        re.search(r"\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}", clean_line)
                        and (" - " in clean_line or ":" in clean_line)
                    ):
                        return WhatsAppParser()
                    if lines_checked >= 50:
                        break
        except Exception:
            pass
        return DocumentParser()

    # Delimited files (CSV / TSV): Sniff header and delimiter
    if ext in [".csv", ".tsv"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                sample = f.read(4096)
                f.seek(0)
                delimiter = "\t" if ext == ".tsv" or sample.count("\t") > sample.count(",") else (
                    ";" if sample.count(";") > sample.count(",") else ","
                )
                reader = csv.reader(f, delimiter=delimiter)
                header = next(reader, [])
                header_str = " ".join(header).lower()

                call_keys = ["caller", "duration", "callee", "call_type", "dialed", "origin", "calling", "destination"]
                sms_keys = ["sms", "message", "msg", "sms_body", "recipient", "sender", "receiver", "thread_id"]
                browser_keys = ["url", "title", "visit", "typed_count", "history", "search_term", "domain"]
                email_keys = ["from", "to", "subject", "cc", "bcc", "email", "body", "headers"]

                if any(k in header_str for k in call_keys):
                    return CallParser()
                if any(k in header_str for k in sms_keys):
                    return SMSParser()
                if any(k in header_str for k in browser_keys):
                    return BrowserParser()
                if any(k in header_str for k in email_keys):
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
                if any(k in keys_str for k in ["caller", "duration", "call_type", "dialed"]):
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
    Main ingestion entrypoint. Detects parser, processes evidence, and flags system documentation.
    """
    is_sys_doc = is_system_documentation(file_path)
    parser = detect_parser(file_path, evidence_type_hint)
    artifacts = parser.parse(file_path)

    for art in artifacts:
        if not art.get("metadata"):
            art["metadata"] = {}
        if is_sys_doc:
            art["metadata"]["is_system_doc"] = True
            art["metadata"]["exclude_from_timeline"] = True
            art["metadata"]["exclude_from_primary_evidence"] = True

    return artifacts