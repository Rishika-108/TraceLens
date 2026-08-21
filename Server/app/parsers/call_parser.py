import csv
import json
from pathlib import Path
from typing import Any
from app.parsers.base_parser import BaseParser


class CallParser(BaseParser):
    """
    Forensic Call Log Parser.
    Supports CSV, TSV, and JSON call detail records with flexible column matching.
    """

    CALLER_KEYS = ["caller", "from", "source", "origin", "caller_number", "outgoing_number", "sender", "phone_number"]
    RECEIVER_KEYS = ["receiver", "to", "destination", "recipient", "callee", "dialed_number", "target"]
    DURATION_KEYS = ["duration", "duration_sec", "call_duration", "duration_seconds", "length", "seconds"]
    TIMESTAMP_KEYS = ["timestamp", "date", "call_date", "time", "datetime", "start_time", "created_at"]
    TYPE_KEYS = ["type", "call_type", "direction", "status"]

    def parse(self, file_path: str) -> list[dict[str, Any]]:
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == ".json":
            return self._parse_json(file_path)
        return self._parse_delimited(file_path)

    def _parse_delimited(self, file_path: str) -> list[dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []

        with open(file_path, "r", encoding="utf-8", errors="replace") as file:
            sample = file.read(4096)
            file.seek(0)
            delimiter = ","
            if "\t" in sample and sample.count("\t") > sample.count(","):
                delimiter = "\t"
            elif ";" in sample and sample.count(";") > sample.count(","):
                delimiter = ";"

            reader = csv.DictReader(file, delimiter=delimiter)
            if not reader.fieldnames:
                return []

            field_map = self._map_fields(reader.fieldnames)

            for row_idx, row in enumerate(reader, start=2):
                caller = self._get_value(row, field_map.get("caller")) or "UNKNOWN"
                receiver = self._get_value(row, field_map.get("receiver")) or "UNKNOWN"
                duration = self._get_duration(self._get_value(row, field_map.get("duration")))
                call_type = self._normalize_call_type(self._get_value(row, field_map.get("type")))
                raw_ts = self._get_value(row, field_map.get("timestamp"))
                parsed_ts = self.parse_datetime(raw_ts)

                artifacts.append(
                    {
                        "artifact_type": "CALL",
                        "timestamp": parsed_ts,
                        "source": "CALL_LOG",
                        "content": {
                            "caller": caller,
                            "receiver": receiver,
                            "duration_seconds": duration,
                            "call_type": call_type,
                        },
                        "raw_data": json.dumps(row),
                        "metadata": {
                            "row_number": row_idx,
                            "raw_timestamp": raw_ts,
                            "original_fields": dict(row),
                        },
                    }
                )

        return artifacts

    def _parse_json(self, file_path: str) -> list[dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []

        with open(file_path, "r", encoding="utf-8", errors="replace") as file:
            data = json.load(file)

        records = data if isinstance(data, list) else data.get("calls", data.get("records", [data]))

        for idx, item in enumerate(records, start=1):
            if not isinstance(item, dict):
                continue
            field_map = self._map_fields(list(item.keys()))
            caller = self._get_value(item, field_map.get("caller")) or "UNKNOWN"
            receiver = self._get_value(item, field_map.get("receiver")) or "UNKNOWN"
            duration = self._get_duration(self._get_value(item, field_map.get("duration")))
            call_type = self._normalize_call_type(self._get_value(item, field_map.get("type")))
            raw_ts = self._get_value(item, field_map.get("timestamp"))
            parsed_ts = self.parse_datetime(raw_ts)

            artifacts.append(
                {
                    "artifact_type": "CALL",
                    "timestamp": parsed_ts,
                    "source": "CALL_LOG",
                    "content": {
                        "caller": caller,
                        "receiver": receiver,
                        "duration_seconds": duration,
                        "call_type": call_type,
                    },
                    "raw_data": json.dumps(item),
                    "metadata": {
                        "record_index": idx,
                        "raw_timestamp": raw_ts,
                    },
                }
            )

        return artifacts

    def _map_fields(self, fieldnames: list[str]) -> dict[str, str]:
        mapping = {}
        lower_names = {f.lower().strip(): f for f in fieldnames}

        for category, candidates in [
            ("caller", self.CALLER_KEYS),
            ("receiver", self.RECEIVER_KEYS),
            ("duration", self.DURATION_KEYS),
            ("timestamp", self.TIMESTAMP_KEYS),
            ("type", self.TYPE_KEYS),
        ]:
            for cand in candidates:
                if cand in lower_names:
                    mapping[category] = lower_names[cand]
                    break
        return mapping

    @staticmethod
    def _get_value(row: dict, field: str | None) -> str | None:
        if field and field in row:
            val = str(row[field]).strip()
            return val if val else None
        return None

    @staticmethod
    def _get_duration(val: Any) -> int:
        if val is None:
            return 0
        try:
            return int(float(str(val).strip()))
        except Exception:
            return 0

    @staticmethod
    def _normalize_call_type(val: str | None) -> str:
        if not val:
            return "UNKNOWN"
        v = val.lower().strip()
        if "miss" in v:
            return "MISSED"
        if "reject" in v:
            return "REJECTED"
        if v.startswith("out") or "outgoing" in v:
            return "OUTGOING"
        if v.startswith("in") or "incoming" in v:
            return "INCOMING"
        return val.upper()