import csv
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from app.parsers.base_parser import BaseParser


# WebKit epoch starts on Jan 1, 1601 UTC
WEBKIT_EPOCH = datetime(1601, 1, 1)


class BrowserParser(BaseParser):
    """
    Forensic Browser History Parser.
    Supports CSV/JSON history exports and direct Chrome/Edge/Firefox SQLite database files.
    """

    URL_KEYS = ["url", "link", "page_url", "address", "uri", "site"]
    TITLE_KEYS = ["title", "page_title", "name", "subject", "query"]
    TIMESTAMP_KEYS = ["timestamp", "date", "visit_time", "time", "last_visit_time", "datetime", "created_at"]
    VISIT_COUNT_KEYS = ["visit_count", "visits", "count", "frequency"]

    def parse(self, file_path: str) -> list[dict[str, Any]]:
        # Check if file is a SQLite database
        if self._is_sqlite_db(file_path):
            return self._parse_sqlite_history(file_path)

        ext = Path(file_path).suffix.lower()
        if ext == ".json":
            return self._parse_json(file_path)
        return self._parse_delimited(file_path)

    @staticmethod
    def _is_sqlite_db(file_path: str) -> bool:
        try:
            with open(file_path, "rb") as f:
                header = f.read(16)
                return header.startswith(b"SQLite format 3")
        except Exception:
            return False

    def _parse_sqlite_history(self, file_path: str) -> list[dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []

        try:
            # Use URI with immutable/read-only mode to prevent locking or writing
            conn = sqlite3.connect(f"file:{Path(file_path).resolve().as_posix()}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Check for Chrome / Chromium / Edge schema ('urls' table)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='urls'")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT 
                        urls.id, 
                        urls.url, 
                        urls.title, 
                        urls.visit_count, 
                        urls.typed_count, 
                        urls.last_visit_time,
                        visits.visit_time,
                        visits.transition
                    FROM urls
                    LEFT JOIN visits ON urls.id = visits.url
                    ORDER BY COALESCE(visits.visit_time, urls.last_visit_time) DESC
                """)
                rows = cursor.fetchall()
                for row in rows:
                    raw_time = row["visit_time"] or row["last_visit_time"]
                    parsed_ts = self._webkit_to_datetime(raw_time)

                    artifacts.append({
                        "artifact_type": "BROWSER_HISTORY",
                        "timestamp": parsed_ts,
                        "source": "CHROME_SQLITE",
                        "content": {
                            "url": row["url"],
                            "title": row["title"] or "No Title",
                            "visit_count": row["visit_count"],
                            "typed_count": row["typed_count"],
                            "transition": row["transition"],
                        },
                        "raw_data": f"URL: {row['url']} | Title: {row['title']} | Time: {parsed_ts}",
                        "metadata": {
                            "browser_engine": "CHROMIUM",
                            "webkit_timestamp": raw_time,
                        },
                    })
                conn.close()
                return artifacts

            # Check for Firefox schema ('moz_places' table)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='moz_places'")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT 
                        moz_places.id, 
                        moz_places.url, 
                        moz_places.title, 
                        moz_places.visit_count, 
                        moz_places.last_visit_date,
                        moz_historyvisits.visit_date
                    FROM moz_places
                    LEFT JOIN moz_historyvisits ON moz_places.id = moz_historyvisits.place_id
                    ORDER BY COALESCE(moz_historyvisits.visit_date, moz_places.last_visit_date) DESC
                """)
                rows = cursor.fetchall()
                for row in rows:
                    raw_time = row["visit_date"] or row["last_visit_date"]
                    parsed_ts = self._firefox_to_datetime(raw_time)

                    artifacts.append({
                        "artifact_type": "BROWSER_HISTORY",
                        "timestamp": parsed_ts,
                        "source": "FIREFOX_SQLITE",
                        "content": {
                            "url": row["url"],
                            "title": row["title"] or "No Title",
                            "visit_count": row["visit_count"],
                        },
                        "raw_data": f"URL: {row['url']} | Title: {row['title']} | Time: {parsed_ts}",
                        "metadata": {
                            "browser_engine": "GECKO_FIREFOX",
                            "raw_timestamp": raw_time,
                        },
                    })
                conn.close()
                return artifacts

            conn.close()
        except Exception as e:
            # If SQLite querying fails, fallback or rethrow
            raise ValueError(f"Failed to parse SQLite browser history: {str(e)}")

        return artifacts

    def _parse_delimited(self, file_path: str) -> list[dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []

        with open(file_path, "r", encoding="utf-8", errors="replace") as file:
            sample = file.read(4096)
            file.seek(0)
            delimiter = "\t" if "\t" in sample and sample.count("\t") > sample.count(",") else ","

            reader = csv.DictReader(file, delimiter=delimiter)
            if not reader.fieldnames:
                return []

            field_map = self._map_fields(reader.fieldnames)

            for row_idx, row in enumerate(reader, start=2):
                url = self._get_value(row, field_map.get("url")) or "about:blank"
                title = self._get_value(row, field_map.get("title")) or url
                raw_ts = self._get_value(row, field_map.get("timestamp"))
                parsed_ts = self.parse_datetime(raw_ts)
                visit_count = self._get_int(self._get_value(row, field_map.get("visit_count")), 1)

                artifacts.append({
                    "artifact_type": "BROWSER_HISTORY",
                    "timestamp": parsed_ts,
                    "source": "BROWSER_CSV",
                    "content": {
                        "url": url,
                        "title": title,
                        "visit_count": visit_count,
                    },
                    "raw_data": json.dumps(row),
                    "metadata": {
                        "row_number": row_idx,
                        "raw_timestamp": raw_ts,
                    },
                })

        return artifacts

    def _parse_json(self, file_path: str) -> list[dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []

        with open(file_path, "r", encoding="utf-8", errors="replace") as file:
            data = json.load(file)

        records = data if isinstance(data, list) else data.get("history", data.get("urls", [data]))

        for idx, item in enumerate(records, start=1):
            if not isinstance(item, dict):
                continue
            field_map = self._map_fields(list(item.keys()))
            url = self._get_value(item, field_map.get("url")) or "about:blank"
            title = self._get_value(item, field_map.get("title")) or url
            raw_ts = self._get_value(item, field_map.get("timestamp"))
            parsed_ts = self.parse_datetime(raw_ts)
            visit_count = self._get_int(self._get_value(item, field_map.get("visit_count")), 1)

            artifacts.append({
                "artifact_type": "BROWSER_HISTORY",
                "timestamp": parsed_ts,
                "source": "BROWSER_JSON",
                "content": {
                    "url": url,
                    "title": title,
                    "visit_count": visit_count,
                },
                "raw_data": json.dumps(item),
                "metadata": {
                    "record_index": idx,
                    "raw_timestamp": raw_ts,
                },
            })

        return artifacts

    def _map_fields(self, fieldnames: list[str]) -> dict[str, str]:
        mapping = {}
        lower_names = {f.lower().strip(): f for f in fieldnames}

        for category, candidates in [
            ("url", self.URL_KEYS),
            ("title", self.TITLE_KEYS),
            ("timestamp", self.TIMESTAMP_KEYS),
            ("visit_count", self.VISIT_COUNT_KEYS),
        ]:
            for cand in candidates:
                if cand in lower_names:
                    mapping[category] = lower_names[cand]
                    break
        return mapping

    @staticmethod
    def _webkit_to_datetime(webkit_timestamp: Any) -> datetime | None:
        if not webkit_timestamp:
            return None
        try:
            micros = int(webkit_timestamp)
            return WEBKIT_EPOCH + timedelta(microseconds=micros)
        except Exception:
            return None

    @staticmethod
    def _firefox_to_datetime(firefox_timestamp: Any) -> datetime | None:
        if not firefox_timestamp:
            return None
        try:
            micros = int(firefox_timestamp)
            return datetime.utcfromtimestamp(micros / 1_000_000.0)
        except Exception:
            return None

    @staticmethod
    def _get_value(row: dict, field: str | None) -> str | None:
        if field and field in row:
            val = str(row[field]).strip()
            return val if val else None
        return None

    @staticmethod
    def _get_int(val: Any, default: int = 1) -> int:
        if val is None:
            return default
        try:
            return int(float(str(val).strip()))
        except Exception:
            return default