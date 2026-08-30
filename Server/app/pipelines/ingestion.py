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
    r".*synthetic.*",
]


def detect_file_encoding(file_path: str) -> str:
    """
    Detects text encoding supporting UTF-8, UTF-16 LE/BE (with BOM), and Windows-1252.
    """
    try:
        with open(file_path, "rb") as f:
            header = f.read(4)
            if header.startswith(b"\xff\xfe"):
                return "utf-16-le"
            if header.startswith(b"\xfe\xff"):
                return "utf-16-be"
            if header.startswith(b"\xef\xbb\xbf"):
                return "utf-8-sig"

            f.seek(0)
            chunk = f.read(8192)
            try:
                chunk.decode("utf-8")
                return "utf-8"
            except UnicodeDecodeError:
                try:
                    chunk.decode("utf-16-le")
                    return "utf-16-le"
                except UnicodeDecodeError:
                    return "cp1252"
    except Exception:
        return "utf-8"


def sniff_magic_bytes(file_path: str) -> str | None:
    """
    Inspects binary headers (Magic Bytes) to identify file type regardless of filename or extension.
    """
    try:
        with open(file_path, "rb") as f:
            header = f.read(32)
            if header.startswith(b"SQLite format 3\000"):
                return "SQLITE_DB"
            if header.startswith(b"%PDF-"):
                return "PDF"
            if header.startswith(b"\xff\xd8\xff"):
                return "JPEG"
            if header.startswith(b"\x89PNG\r\n\x1a\n"):
                return "PNG"
            if header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
                return "GIF"
            if header.startswith(b"RIFF") and b"WEBP" in header[:16]:
                return "WEBP"
            if header.startswith(b"II*\x00") or header.startswith(b"MM\x00*"):
                return "TIFF"
            if header.startswith(b"From ") or header.startswith(b"Received:") or header.startswith(b"Message-ID:"):
                return "EMAIL"
    except Exception:
        pass
    return None


def is_system_documentation(file_path: str) -> bool:
    """
    Identifies setup files, READMEs, instructions, synthetic dataset docs, and non-forensic repository metadata.
    """
    filename = Path(file_path).name.lower().strip()
    return any(re.match(pattern, filename, re.IGNORECASE) for pattern in SYSTEM_DOC_PATTERNS)


def detect_parser(file_path: str, evidence_type_hint: str | None = None) -> BaseParser:
    """
    Intelligently select the appropriate parser based on magic bytes, type hint,
    file extension, and deep multi-encoding content sniffing.
    """
    path = Path(file_path)
    filename_lower = path.name.lower()

    # 1. Check user-supplied explicit category hint
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

    # 2. Magic bytes binary inspection (file extension independent)
    magic = sniff_magic_bytes(file_path)
    if magic == "SQLITE_DB":
        return BrowserParser()
    if magic == "PDF":
        return DocumentParser()
    if magic in ["JPEG", "PNG", "GIF", "WEBP", "TIFF"]:
        return ImageParser()
    if magic == "EMAIL":
        return EmailParser()

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

    # SQLite database files or browser history files
    if (
        ext in [".sqlite", ".db", ".sqlite3"]
        or filename_lower in ["history", "places.sqlite", "web data", "cookies"]
        or any(k in filename_lower for k in ["browser", "history", "chrome", "firefox", "edge", "safari"])
    ):
        # If it's a database or named history, route to BrowserParser
        if ext in [".sqlite", ".db", ".sqlite3"] or filename_lower in ["history", "places.sqlite"]:
            return BrowserParser()

    # Text files: Multi-encoding Sniff for WhatsApp vs Plain Document
    if ext in [".txt", ".log", ".chat"]:
        encoding = detect_file_encoding(file_path)
        try:
            with open(file_path, "r", encoding=encoding, errors="replace") as f:
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

    # Delimited files (CSV / TSV): Sniff header and delimiter with csv.Sniffer
    if ext in [".csv", ".tsv"]:
        # Filename hint priority
        if any(k in filename_lower for k in ["browser", "history", "chrome", "firefox", "edge", "safari", "web_history", "navigation"]):
            return BrowserParser()

        encoding = detect_file_encoding(file_path)
        try:
            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                sample = f.read(4096)
                f.seek(0)
                delimiter = ","
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    delimiter = dialect.delimiter
                except Exception:
                    if ext == ".tsv" or sample.count("\t") > sample.count(","):
                        delimiter = "\t"
                    elif sample.count(";") > sample.count(","):
                        delimiter = ";"

                reader = csv.reader(f, delimiter=delimiter)
                header = next(reader, [])
                header_str = " ".join(header).lower()

                browser_keys = ["url", "page_url", "visit", "typed_count", "history", "search_term", "domain", "website", "uri", "site_name"]
                call_keys = ["caller", "duration", "callee", "call_type", "dialed", "calling", "served_msisdn", "first_cgi", "cell_id"]
                sms_keys = ["sms", "sms_body", "recipient", "thread_id"]
                email_keys = ["subject", "cc", "bcc", "headers"]

                # Prioritize Browser if URL or visit is present without phone call headers
                if any(k in header_str for k in browser_keys) and not any(k in header_str for k in ["caller", "callee", "call_duration"]):
                    return BrowserParser()
                if any(k in header_str for k in call_keys):
                    return CallParser()
                if any(k in header_str for k in sms_keys):
                    return SMSParser()
                if any(k in header_str for k in email_keys):
                    return EmailParser()
        except Exception:
            pass

        if any(k in filename_lower for k in ["call", "cdr"]):
            return CallParser()
        if any(k in filename_lower for k in ["sms", "message"]):
            return SMSParser()
        return CallParser()

    # JSON files: Sniff structure
    if ext == ".json":
        if any(k in filename_lower for k in ["browser", "history", "chrome", "firefox", "edge"]):
            return BrowserParser()

        encoding = detect_file_encoding(file_path)
        try:
            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                data = json.load(f)
                first_item = data[0] if isinstance(data, list) and data else (data if isinstance(data, dict) else {})
                keys_str = " ".join(first_item.keys()).lower()

                if any(k in keys_str for k in ["url", "page_url", "title", "visit_count", "search_query"]):
                    return BrowserParser()
                if any(k in keys_str for k in ["subject", "bcc", "cc", "body"]) and "from" in keys_str:
                    return EmailParser()
                if any(k in keys_str for k in ["caller", "duration", "call_type", "dialed", "served_msisdn"]):
                    return CallParser()
                if any(k in keys_str for k in ["message", "sms", "recipient", "sms_body"]):
                    return SMSParser()
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