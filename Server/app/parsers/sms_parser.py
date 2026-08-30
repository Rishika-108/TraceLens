import csv
import json
from pathlib import Path
from typing import Any
from app.parsers.base_parser import BaseParser


class SMSParser(BaseParser):
    """
    Forensic SMS / MMS Message Parser.
    Supports CSV, TSV, and JSON formats with header discovery, integer direction decoding,
    and concatenated SMS (CSMS) handling.
    """

    SENDER_KEYS = [
        "sender", "from", "source", "address", "phone_number", "sender_number",
        "origin", "source_address", "oa"
    ]
    RECIPIENT_KEYS = [
        "recipient", "to", "destination", "target", "receiver", "callee",
        "destination_address", "da"
    ]
    MESSAGE_KEYS = [
        "message", "body", "text", "msg", "content", "sms_body", "message_text",
        "snippet", "payload"
    ]
    TIMESTAMP_KEYS = [
        "timestamp", "date", "time", "datetime", "sent_date", "received_date",
        "created_at", "msg_date"
    ]
    TYPE_KEYS = [
        "type", "direction", "status", "folder", "box", "msg_box"
    ]
    THREAD_KEYS = [
        "thread_id", "conversation_id", "conv_id", "session_id"
    ]
    PART_KEYS = [
        "part_id", "part_index", "sequence", "seq", "segment"
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
                sender = self._get_value(row, field_map.get("sender")) or "UNKNOWN"
                recipient = self._get_value(row, field_map.get("recipient")) or "UNKNOWN"
                message = self._get_value(row, field_map.get("message")) or ""
                direction = self._normalize_direction(self._get_value(row, field_map.get("type")))
                raw_ts = self._get_value(row, field_map.get("timestamp"))
                parsed_ts = self.parse_datetime(raw_ts)

                thread_id = self._get_value(row, field_map.get("thread_id"))
                part_id = self._get_value(row, field_map.get("part_id"))

                content = {
                    "sender": sender,
                    "recipient": recipient,
                    "message": message,
                    "direction": direction,
                }
                if thread_id:
                    content["thread_id"] = thread_id
                if part_id:
                    content["part_id"] = part_id

                artifacts.append(
                    {
                        "artifact_type": "SMS",
                        "timestamp": parsed_ts,
                        "source": "SMS",
                        "content": content,
                        "raw_data": json.dumps(row),
                        "metadata": {
                            "row_number": row_idx,
                            "raw_timestamp": raw_ts,
                        },
                    }
                )

        return artifacts

    def _parse_json(self, file_path: str) -> list[dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []

        with open(file_path, "r", encoding="utf-8", errors="replace") as file:
            data = json.load(file)

        records = data if isinstance(data, list) else data.get("messages", data.get("sms", [data]))

        for idx, item in enumerate(records, start=1):
            if not isinstance(item, dict):
                continue
            field_map = self._map_fields(list(item.keys()))
            sender = self._get_value(item, field_map.get("sender")) or "UNKNOWN"
            recipient = self._get_value(item, field_map.get("recipient")) or "UNKNOWN"
            message = self._get_value(item, field_map.get("message")) or ""
            direction = self._normalize_direction(self._get_value(item, field_map.get("type")))
            raw_ts = self._get_value(item, field_map.get("timestamp"))
            parsed_ts = self.parse_datetime(raw_ts)

            thread_id = self._get_value(item, field_map.get("thread_id"))
            part_id = self._get_value(item, field_map.get("part_id"))

            content = {
                "sender": sender,
                "recipient": recipient,
                "message": message,
                "direction": direction,
            }
            if thread_id:
                content["thread_id"] = thread_id
            if part_id:
                content["part_id"] = part_id

            artifacts.append(
                {
                    "artifact_type": "SMS",
                    "timestamp": parsed_ts,
                    "source": "SMS",
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
            ("sender", self.SENDER_KEYS),
            ("recipient", self.RECIPIENT_KEYS),
            ("message", self.MESSAGE_KEYS),
            ("timestamp", self.TIMESTAMP_KEYS),
            ("type", self.TYPE_KEYS),
            ("thread_id", self.THREAD_KEYS),
            ("part_id", self.PART_KEYS),
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
            return val if val and val.lower() != "null" else None
        return None

    @staticmethod
    def _normalize_direction(val: str | None) -> str:
        if not val:
            return "UNKNOWN"
        v = val.lower().strip()
        # Telecommunications & Android numeric codes
        if v in ["1", "in", "inbox", "incoming"]:
            return "INCOMING"
        if v in ["2", "out", "sent", "outgoing"]:
            return "OUTGOING"
        if v in ["3", "draft"]:
            return "DRAFT"
        if v in ["4", "outbox"]:
            return "OUTBOX"
        if v in ["5", "failed"]:
            return "FAILED"
        if v in ["6", "queued"]:
            return "QUEUED"
        return val.upper()