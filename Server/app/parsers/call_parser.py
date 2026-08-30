import csv
import json
from pathlib import Path
from typing import Any
from app.parsers.base_parser import BaseParser


class CallParser(BaseParser):
    """
    Forensic Call Detail Record (CDR) Parser.
    Supports CSV, TSV, and JSON carrier CDRs with cell tower, IMEI, and IMSI telemetry.
    """

    CALLER_KEYS = [
        "caller", "from", "source", "origin", "caller_number", "outgoing_number",
        "sender", "phone_number", "calling_party_number", "served_msisdn", "originating_number",
        "src_number", "ani", "calling_no", "a_party", "calling_msisdn"
    ]
    RECEIVER_KEYS = [
        "receiver", "to", "destination", "recipient", "callee", "dialed_number",
        "target", "called_party_number", "destination_number", "dialed_digits",
        "b_party", "target_number", "term_msisdn", "dnis", "called_msisdn"
    ]
    DURATION_KEYS = [
        "duration", "duration_sec", "call_duration", "duration_seconds",
        "length", "seconds", "billsec", "conv_time", "actual_duration"
    ]
    TIMESTAMP_KEYS = [
        "timestamp", "date", "call_date", "time", "datetime", "start_time", "created_at", "call_time"
    ]
    TYPE_KEYS = [
        "type", "call_type", "direction", "status", "call_direction"
    ]
    CELL_ID_KEYS = [
        "cell_id", "first_cgi", "cgi", "base_station", "site_id", "tower_id", "cell_name", "cellid"
    ]
    LAC_KEYS = [
        "lac", "location_area_code", "location_area"
    ]
    IMEI_KEYS = [
        "imei", "imeisv", "device_id", "device_imei", "caller_imei"
    ]
    IMSI_KEYS = [
        "imsi", "subscriber_id", "sim_imsi", "caller_imsi"
    ]

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
            try:
                dialect = csv.Sniffer().sniff(sample)
                delimiter = dialect.delimiter
            except Exception:
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

                cell_id = self._get_value(row, field_map.get("cell_id"))
                lac = self._get_value(row, field_map.get("lac"))
                imei = self._get_value(row, field_map.get("imei"))
                imsi = self._get_value(row, field_map.get("imsi"))

                content = {
                    "caller": caller,
                    "receiver": receiver,
                    "duration_seconds": duration,
                    "call_type": call_type,
                }
                if cell_id:
                    content["cell_id"] = cell_id
                if lac:
                    content["lac"] = lac
                if imei:
                    content["imei"] = imei
                if imsi:
                    content["imsi"] = imsi

                artifacts.append(
                    {
                        "artifact_type": "CALL",
                        "timestamp": parsed_ts,
                        "source": "CALL_LOG",
                        "content": content,
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

            cell_id = self._get_value(item, field_map.get("cell_id"))
            lac = self._get_value(item, field_map.get("lac"))
            imei = self._get_value(item, field_map.get("imei"))
            imsi = self._get_value(item, field_map.get("imsi"))

            content = {
                "caller": caller,
                "receiver": receiver,
                "duration_seconds": duration,
                "call_type": call_type,
            }
            if cell_id:
                content["cell_id"] = cell_id
            if lac:
                content["lac"] = lac
            if imei:
                content["imei"] = imei
            if imsi:
                content["imsi"] = imsi

            artifacts.append(
                {
                    "artifact_type": "CALL",
                    "timestamp": parsed_ts,
                    "source": "CALL_LOG",
                    "content": content,
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
            ("cell_id", self.CELL_ID_KEYS),
            ("lac", self.LAC_KEYS),
            ("imei", self.IMEI_KEYS),
            ("imsi", self.IMSI_KEYS),
        ]:
            for cand in candidates:
                if cand in lower_names:
                    mapping[category] = lower_names[cand]
                    break
        return mapping

    def _get_value(self, row: dict, field_name: str | None) -> str | None:
        if not field_name or field_name not in row:
            return None
        val = str(row[field_name]).strip()
        return val if val and val.lower() != "null" else None

    def _get_duration(self, raw_val: str | None) -> int:
        if not raw_val:
            return 0
        try:
            return int(float(raw_val))
        except (ValueError, TypeError):
            return 0

    def _normalize_call_type(self, raw_val: str | None) -> str:
        if not raw_val:
            return "VOICE"
        val = raw_val.upper()
        if "IN" in val:
            return "INCOMING"
        if "OUT" in val:
            return "OUTGOING"
        if "MISSED" in val:
            return "MISSED"
        if "REJECT" in val:
            return "REJECTED"
        return "VOICE"