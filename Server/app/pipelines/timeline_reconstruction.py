from datetime import datetime
from typing import Any
from uuid import uuid4
from dateutil import parser as date_parser

from app.pipelines.normalization import normalize_event


def build_timeline(artifacts: list[dict[str, Any]], case_id: str | None = None) -> list[dict[str, Any]]:
    """
    Reconstructs chronological timeline events from parsed/normalized artifacts.
    """
    events: list[dict[str, Any]] = []

    for artifact in artifacts:
        norm = normalize_event(artifact, case_id)
        ts = norm.get("event_timestamp")

        if not ts:
            ts = artifact.get("created_at") or datetime.utcnow()

        if not isinstance(ts, datetime):
            try:
                ts = date_parser.parse(str(ts))
            except Exception:
                ts = datetime.utcnow()

        events.append({
            "id": str(uuid4()),
            "case_id": case_id or artifact.get("case_id"),
            "artifact_id": artifact.get("id"),
            "event_type": norm["event_type"],
            "description": norm["description"],
            "event_timestamp": ts,
        })

    # Sort strictly by timestamp ascending
    return sorted(events, key=lambda e: e["event_timestamp"])