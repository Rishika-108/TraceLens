from pathlib import Path

from app.parsers.browser_parser import BrowserParser
from app.parsers.call_parser import CallParser
from app.parsers.document_parser import DocumentParser
from app.parsers.email_parser import EmailParser
from app.parsers.sms_parser import SMSParser
from app.parsers.whatsapp_parser import WhatsAppParser


PARSERS = {
    ".csv": CallParser,
    ".txt": WhatsAppParser,
    ".json": EmailParser,
}


def get_parser(file_path: str):
    extension = Path(file_path).suffix.lower()

    parser = PARSERS.get(extension)

    if not parser:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    return parser()


def ingest(file_path: str) -> list[dict]:
    parser = get_parser(file_path)

    return parser.parse(file_path)