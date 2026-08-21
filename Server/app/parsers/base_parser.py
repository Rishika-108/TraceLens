from abc import ABC
from abc import abstractmethod
from datetime import datetime
from typing import Any
from dateutil import parser as date_parser


class BaseParser(ABC):
    """
    Base abstract class for digital forensics evidence parsers.
    Each parser transforms source-specific evidence into structured artifact dictionaries.
    """

    @abstractmethod
    def parse(self, file_path: str) -> list[dict[str, Any]]:
        """
        Parses evidence file and returns a list of standardized artifact dictionaries.
        Each item should contain:
        - artifact_type: str (e.g. 'CALL', 'SMS', 'WHATSAPP_MESSAGE', 'EMAIL', 'BROWSER_HISTORY', 'DOCUMENT', 'IMAGE_METADATA')
        - timestamp: datetime | None
        - source: str (source identifier)
        - content: dict (structured domain fields)
        - raw_data: str | None (original raw text or record for auditability)
        - metadata: dict (line numbers, offsets, EXIF tags, etc.)
        """
        pass

    @staticmethod
    def parse_datetime(raw_timestamp: Any) -> datetime | None:
        """
        Robust datetime parser supporting multiple formats, Unix timestamps, and ISO strings.
        """
        if raw_timestamp is None:
            return None

        if isinstance(raw_timestamp, datetime):
            return raw_timestamp

        # Handle numeric timestamps (Unix seconds or milliseconds)
        if isinstance(raw_timestamp, (int, float)):
            try:
                # If timestamp is in milliseconds (e.g. > 100 billion)
                if raw_timestamp > 1e11:
                    return datetime.utcfromtimestamp(raw_timestamp / 1000.0)
                return datetime.utcfromtimestamp(raw_timestamp)
            except Exception:
                return None

        ts_str = str(raw_timestamp).strip()
        if not ts_str:
            return None

        # Try parsing via dateutil
        try:
            return date_parser.parse(ts_str)
        except Exception:
            pass

        # Try custom common forensic formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%d/%m/%Y, %H:%M:%S",
            "%d/%m/%Y, %H:%M",
            "%d/%m/%y, %H:%M:%S",
            "%d/%m/%y, %H:%M",
            "%m/%d/%Y %I:%M:%S %p",
            "%m/%d/%Y, %I:%M %p",
            "%Y/%m/%d %H:%M:%S",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(ts_str, fmt)
            except ValueError:
                continue

        return None