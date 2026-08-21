from datetime import datetime
from app.pipelines.normalization import normalize_event, normalize
from app.pipelines.entity_extraction import extract_entities
from app.pipelines.relationship_discovery import discover_relationships
from app.pipelines.timeline_reconstruction import build_timeline


def test_normalization_pipeline():
    call_artifact = {
        "id": "art-1",
        "evidence_id": "ev-1",
        "artifact_type": "CALL",
        "timestamp": "2023-08-15 14:30:00",
        "content": {"caller": "+1234567890", "receiver": "+9876543210", "duration_seconds": 90, "call_type": "INCOMING"},
    }

    norm = normalize_event(call_artifact, case_id="case-101")
    assert norm["event_type"] == "PHONE_COMMUNICATION"
    assert norm["actor"] == "+1234567890"
    assert norm["target"] == "+9876543210"
    assert norm["event_timestamp"] is not None
    assert "90s" in norm["description"]


def test_entity_extraction_multi_type():
    artifacts = [
        {
            "id": "art-wa",
            "artifact_type": "WHATSAPP_MESSAGE",
            "case_id": "case-1",
            "content": {
                "sender": "John Miller",
                "message": "Call agent Smith at +1 415-555-2671 or email smith@intelligence.gov. Send BTC to 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa or ETH to 0x71C7656EC7ab88b098defB751B7401B5f6d8976F. Server IP is 198.51.100.42 near Zurich Bank on MG Road.",
            },
        }
    ]

    entities = extract_entities(artifacts, case_id="case-1")
    types_found = {e["entity_type"] for e in entities}

    assert "PERSON" in types_found
    assert "PHONE" in types_found
    assert "EMAIL" in types_found
    assert "IP_ADDRESS" in types_found
    assert "CRYPTO_ADDRESS" in types_found

    phone_vals = [e["value"] for e in entities if e["entity_type"] == "PHONE"]
    assert any("415" in p for p in phone_vals)

    email_vals = [e["value"] for e in entities if e["entity_type"] == "EMAIL"]
    assert "smith@intelligence.gov" in email_vals


def test_relationship_discovery_direct_and_cooccurrence():
    entities = [
        {"id": "ent-1", "case_id": "c1", "artifact_id": "art-1", "entity_type": "PHONE", "value": "+1111111111"},
        {"id": "ent-2", "case_id": "c1", "artifact_id": "art-1", "entity_type": "PHONE", "value": "+2222222222"},
        {"id": "ent-3", "case_id": "c1", "artifact_id": "art-1", "entity_type": "PERSON", "value": "Bob Vance"},
    ]
    artifacts = [
        {
            "id": "art-1",
            "artifact_type": "CALL",
            "case_id": "c1",
            "content": {"caller": "+1111111111", "receiver": "+2222222222", "duration_seconds": 60},
        }
    ]

    relationships = discover_relationships(entities, artifacts, case_id="c1")
    assert len(relationships) >= 1

    rel_types = {r["relationship_type"] for r in relationships}
    assert "CALLS" in rel_types or "CO_OCCURS_WITH" in rel_types


def test_timeline_reconstruction_ordering():
    artifacts = [
        {"id": "a3", "artifact_type": "EMAIL", "timestamp": "2023-08-15 15:00:00", "content": {"sender": "A", "recipient": "B", "subject": "Third"}},
        {"id": "a1", "artifact_type": "CALL", "timestamp": "2023-08-15 10:00:00", "content": {"caller": "A", "receiver": "B", "duration_seconds": 10}},
        {"id": "a2", "artifact_type": "SMS", "timestamp": "2023-08-15 12:00:00", "content": {"sender": "A", "recipient": "B", "message": "Second"}},
    ]

    timeline = build_timeline(artifacts, case_id="c1")
    assert len(timeline) == 3

    # Must be ordered strictly chronologically
    assert timeline[0]["artifact_id"] == "a1"
    assert timeline[1]["artifact_id"] == "a2"
    assert timeline[2]["artifact_id"] == "a3"
