import csv
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote_plus, urlparse
from app.parsers.base_parser import BaseParser


# WebKit epoch starts on Jan 1, 1601 UTC
WEBKIT_EPOCH = datetime(1601, 1, 1)


def extract_search_query(url: str | None) -> str | None:
    """
    Extracts investigative search keywords from popular search engine URLs.
    """
    if not url:
        return None
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        query_params = parse_qs(parsed.query)

        # Google, DuckDuckGo, Bing
        if any(d in netloc for d in ["google.", "duckduckgo.", "bing."]):
            if "q" in query_params:
                return unquote_plus(query_params["q"][0]).strip()
        # Yahoo
        if "yahoo." in netloc and "p" in query_params:
            return unquote_plus(query_params["p"][0]).strip()
        # YouTube
        if "youtube." in netloc and "search_query" in query_params:
            return unquote_plus(query_params["search_query"][0]).strip()
        # Baidu
        if "baidu." in netloc and "wd" in query_params:
            return unquote_plus(query_params["wd"][0]).strip()
        # Yandex
        if "yandex." in netloc and "text" in query_params:
            return unquote_plus(query_params["text"][0]).strip()
    except Exception:
        pass
    return None


class BrowserParser(BaseParser):
    """
    Forensic Browser History & Search Intent Parser.
    Supports CSV/JSON history exports and direct Chrome/Edge/Firefox/Safari SQLite database files.
    """

    URL_KEYS = [
        "url", "link", "page_url", "address", "uri", "site", "website",
        "target_url", "destination_url", "visited_url", "location"
    ]
    TITLE_KEYS = [
        "title", "page_title", "name", "subject", "query", "site_name",
        "topic", "search_term"
    ]
    TIMESTAMP_KEYS = [
        "timestamp", "date", "visit_time", "time", "last_visit_time",
        "datetime", "created_at", "visited_on", "last_visit_date", "visit_date"
    ]
    VISIT_COUNT_KEYS = [
        "visit_count", "visits", "count", "frequency", "typed_count"
    ]

    def parse(self, file_path: str) -> list[dict[str, Any]]:
        # Check if file is an SQLite database
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
            resolved_path = Path(file_path).resolve()
            # Try standard connection with read-only pragma for maximum cross-platform compatibility
            try:
                conn = sqlite3.connect(f"{resolved_path.as_uri()}?mode=ro", uri=True)
            except Exception:
                conn = sqlite3.connect(str(resolved_path))

            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Query all tables in database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0].lower() for row in cursor.fetchall()]

            # 1. Chrome / Chromium / Edge schema ('urls' table)
            if "urls" in tables:
                has_visits = "visits" in tables
                if has_visits:
                    query = """
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
                    """
                else:
                    query = """
                        SELECT 
                            urls.id, 
                            urls.url, 
                            urls.title, 
                            urls.visit_count, 
                            urls.typed_count, 
                            urls.last_visit_time,
                            NULL as visit_time,
                            NULL as transition
                        FROM urls
                        ORDER BY urls.last_visit_time DESC
                    """

                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    raw_time = row["visit_time"] or row["last_visit_time"]
                    parsed_ts = self._webkit_to_datetime(raw_time)
                    url_val = row["url"] or ""
                    search_q = extract_search_query(url_val)

                    content = {
                        "url": url_val,
                        "title": row["title"] or "No Title",
                        "visit_count": row["visit_count"] or 1,
                        "typed_count": row["typed_count"] or 0,
                    }
                    if search_q:
                        content["search_query"] = search_q
                        content["is_search"] = True

                    artifacts.append({
                        "artifact_type": "BROWSER_HISTORY",
                        "timestamp": parsed_ts,
                        "source": "CHROME_SQLITE",
                        "content": content,
                        "raw_data": f"URL: {url_val} | Title: {row['title']} | Time: {parsed_ts}",
                        "metadata": {
                            "browser_engine": "CHROMIUM",
                            "webkit_timestamp": raw_time,
                            "has_search_query": search_q is not None,
                        },
                    })
                conn.close()
                return artifacts

            # 2. Firefox schema ('moz_places' table)
            if "moz_places" in tables:
                has_history_visits = "moz_historyvisits" in tables
                if has_history_visits:
                    query = """
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
                    """
                else:
                    query = """
                        SELECT 
                            moz_places.id, 
                            moz_places.url, 
                            moz_places.title, 
                            moz_places.visit_count, 
                            moz_places.last_visit_date,
                            NULL as visit_date
                        FROM moz_places
                        ORDER BY moz_places.last_visit_date DESC
                    """

                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    raw_time = row["visit_date"] or row["last_visit_date"]
                    parsed_ts = self._firefox_to_datetime(raw_time)
                    url_val = row["url"] or ""
                    search_q = extract_search_query(url_val)

                    content = {
                        "url": url_val,
                        "title": row["title"] or "No Title",
                        "visit_count": row["visit_count"] or 1,
                    }
                    if search_q:
                        content["search_query"] = search_q
                        content["is_search"] = True

                    artifacts.append({
                        "artifact_type": "BROWSER_HISTORY",
                        "timestamp": parsed_ts,
                        "source": "FIREFOX_SQLITE",
                        "content": content,
                        "raw_data": f"URL: {url_val} | Title: {row['title']} | Time: {parsed_ts}",
                        "metadata": {
                            "browser_engine": "GECKO_FIREFOX",
                            "raw_timestamp": raw_time,
                            "has_search_query": search_q is not None,
                        },
                    })
                conn.close()
                return artifacts

            # 3. Dynamic fallback: Scan all tables for a column named 'url' or 'link'
            for table_name in tables:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1].lower() for col in cursor.fetchall()]
                url_col = next((c for c in columns if "url" in c or "link" in c or "uri" in c), None)
                if url_col:
                    title_col = next((c for c in columns if "title" in c or "name" in c), None)
                    time_col = next((c for c in columns if "time" in c or "date" in c), None)

                    select_cols = f"{url_col}"
                    if title_col:
                        select_cols += f", {title_col}"
                    if time_col:
                        select_cols += f", {time_col}"

                    cursor.execute(f"SELECT {select_cols} FROM {table_name} LIMIT 500")
                    rows = cursor.fetchall()
                    for row in rows:
                        url_val = row[0]
                        if not url_val:
                            continue
                        title_val = row[1] if title_col else url_val
                        raw_time = row[2] if time_col else None
                        parsed_ts = self.parse_datetime(raw_time) if raw_time else None
                        search_q = extract_search_query(url_val)

                        content = {
                            "url": str(url_val),
                            "title": str(title_val) if title_val else "No Title",
                            "visit_count": 1,
                        }
                        if search_q:
                            content["search_query"] = search_q
                            content["is_search"] = True

                        artifacts.append({
                            "artifact_type": "BROWSER_HISTORY",
                            "timestamp": parsed_ts,
                            "source": f"SQLITE_{table_name.upper()}",
                            "content": content,
                            "raw_data": f"Table: {table_name} | URL: {url_val} | Title: {title_val}",
                            "metadata": {
                                "browser_table": table_name,
                                "has_search_query": search_q is not None,
                            },
                        })
                    if artifacts:
                        conn.close()
                        return artifacts

            conn.close()
        except Exception as e:
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
                search_q = extract_search_query(url)

                content = {
                    "url": url,
                    "title": title,
                    "visit_count": visit_count,
                }
                if search_q:
                    content["search_query"] = search_q
                    content["is_search"] = True

                artifacts.append({
                    "artifact_type": "BROWSER_HISTORY",
                    "timestamp": parsed_ts,
                    "source": "BROWSER_CSV",
                    "content": content,
                    "raw_data": json.dumps(row),
                    "metadata": {
                        "row_number": row_idx,
                        "raw_timestamp": raw_ts,
                        "has_search_query": search_q is not None,
                    },
                })

        return artifacts

    def _parse_json(self, file_path: str) -> list[dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []

        with open(file_path, "r", encoding="utf-8", errors="replace") as file:
            data = json.load(file)

        records = data if isinstance(data, list) else data.get("history", data.get("records", [data]))

        for idx, item in enumerate(records, start=1):
            if not isinstance(item, dict):
                continue
            field_map = self._map_fields(list(item.keys()))
            url = self._get_value(item, field_map.get("url")) or "about:blank"
            title = self._get_value(item, field_map.get("title")) or url
            raw_ts = self._get_value(item, field_map.get("timestamp"))
            parsed_ts = self.parse_datetime(raw_ts)
            visit_count = self._get_int(self._get_value(item, field_map.get("visit_count")), 1)
            search_q = extract_search_query(url)

            content = {
                "url": url,
                "title": title,
                "visit_count": visit_count,
            }
            if search_q:
                content["search_query"] = search_q
                content["is_search"] = True

            artifacts.append({
                "artifact_type": "BROWSER_HISTORY",
                "timestamp": parsed_ts,
                "source": "BROWSER_JSON",
                "content": content,
                "raw_data": json.dumps(item),
                "metadata": {
                    "record_index": idx,
                    "raw_timestamp": raw_ts,
                    "has_search_query": search_q is not None,
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
    def _webkit_to_datetime(webkit_microseconds: int | float | None) -> datetime | None:
        if not webkit_microseconds or webkit_microseconds <= 0:
            return None
        try:
            return WEBKIT_EPOCH + timedelta(microseconds=int(webkit_microseconds))
        except Exception:
            return None

    @staticmethod
    def _firefox_to_datetime(firefox_microseconds: int | float | None) -> datetime | None:
        if not firefox_microseconds or firefox_microseconds <= 0:
            return None
        try:
            return datetime.utcfromtimestamp(int(firefox_microseconds) / 1000000.0)
        except Exception:
            return None

    @staticmethod
    def _get_value(row: dict, field: str | None) -> str | None:
        if field and field in row:
            val = str(row[field]).strip()
            return val if val and val.lower() != "null" else None
        return None

    @staticmethod
    def _get_int(val: str | None, default: int = 1) -> int:
        if not val:
            return default
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return default