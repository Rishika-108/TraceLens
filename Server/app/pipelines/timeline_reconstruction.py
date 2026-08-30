from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
from dateutil import parser as date_parser

from app.pipelines.normalization import normalize_event


def build_timeline(artifacts: list[dict[str, Any]], case_id: str | None = None) -> list[dict[str, Any]]:
    """
    Reconstructs chronological timeline events from parsed/normalized artifacts.
    Preserves all forensic fields: event_state, modality, actor, target,
    referenced times, locations, and synthetic timestamp flags.
    """
    events: list[dict[str, Any]] = []

    for artifact in artifacts:
        norm = normalize_event(artifact, case_id)
        if not norm:
            continue

        ts = norm.get("event_timestamp")
        if not ts:
            ts = artifact.get("created_at") or datetime.now(timezone.utc).replace(tzinfo=None)

        if not isinstance(ts, datetime):
            try:
                parsed = date_parser.parse(str(ts))
                if parsed.tzinfo is not None:
                    ts = parsed.astimezone(timezone.utc).replace(tzinfo=None)
                else:
                    ts = parsed
            except Exception:
                ts = datetime.now(timezone.utc).replace(tzinfo=None)

        events.append({
            "id": str(uuid4()),
            "case_id": case_id or artifact.get("case_id"),
            "artifact_id": artifact.get("id"),
            "event_type": norm["event_type"],
            "event_state": norm.get("event_state"),
            "modality": norm.get("modality"),
            "actor": norm.get("actor"),
            "target": norm.get("target"),
            "description": norm["description"],
            "referenced_time": norm.get("referenced_time"),
            "referenced_location": norm.get("referenced_location"),
            "is_synthetic_timestamp": bool(norm.get("is_synthetic_timestamp", False)),
            "event_timestamp": ts,
        })

    # Sort strictly by timestamp ascending
    return sorted(events, key=lambda e: e["event_timestamp"])