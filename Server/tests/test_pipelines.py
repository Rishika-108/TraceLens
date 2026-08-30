from datetime import datetime
from app.pipelines.normalization import normalize_event, normalize
from app.pipelines.entity_extraction import extract_entities, is_valid_phone_number, classify_structured_party
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


def test_false_phone_filtering():
    """Verify that dates, timestamps, IPs, pure currency amounts, and suspect names are NEVER tagged as PHONE."""
    assert is_valid_phone_number("2023-08-15") is False
    assert is_valid_phone_number("15/08/2023") is False
    assert is_valid_phone_number("2024.01.22") is False
    assert is_valid_phone_number("14:30:00") is False
    assert is_valid_phone_number("192.168.1.1") is False
    assert is_valid_phone_number("250000") is False
    assert is_valid_phone_number("99881") is False
    assert is_valid_phone_number("Suspect 1") is False

    assert is_valid_phone_number("+1 415 555 2671") is True
    assert is_valid_phone_number("+91-9876543210") is True
    assert is_valid_phone_number("(415) 555-2671") is True
    assert is_valid_phone_number("9876543210") is True

    # Check party classification for names with numbers
    assert classify_structured_party("Officer 42") == ("PERSON", "Officer 42")
    assert classify_structured_party("Suspect 7") == ("PERSON", "Suspect 7")
    assert classify_structured_party("+1 415 555 2671") == ("PHONE", "+1 415 555 2671")
    assert classify_structured_party("agent@corp.com") == ("EMAIL", "agent@corp.com")

    # Artifact containing dates, amounts, and IP addresses
    artifact = {
        "id": "art-false-test",
        "artifact_type": "DOCUMENT",
        "case_id": "case-test",
        "content": {
            "text": "Meeting occurred on 2023-08-15 at 14:30:00. Payout was 250000 USD from IP 192.168.1.1. Contact +1 415 555 2671."
        },
    }
    extracted = extract_entities([artifact], case_id="case-test")
    phone_entities = [e["value"] for e in extracted if e["entity_type"] == "PHONE"]

    # Only genuine phone number should be present
    assert "2023-08-15" not in phone_entities
    assert "14:30:00" not in phone_entities
    assert "250000" not in phone_entities
    assert "192.168.1.1" not in phone_entities
    assert any("415" in p for p in phone_entities)


def test_entity_deduplication_across_artifacts():
    """Verify that identical entities across multiple artifacts are strictly deduplicated with observation counts."""
    artifacts = [
        {
            "id": f"art-{i}",
            "artifact_type": "WHATSAPP_MESSAGE",
            "case_id": "case-dedup",
            "content": {
                "sender": "Mastermind",
                "message": f"Message {i}: Call me back at +1 415 555 2671.",
            },
        }
        for i in range(5)
    ]

    entities = extract_entities(artifacts, case_id="case-dedup")

    # There should only be 1 Mastermind PERSON and 1 PHONE entity
    person_entities = [e for e in entities if e["entity_type"] == "PERSON" and "Mastermind" in e["value"]]
    phone_entities = [e for e in entities if e["entity_type"] == "PHONE" and "415" in e["value"]]

    assert len(person_entities) == 1
    assert len(phone_entities) == 1
    assert person_entities[0]["mentions_count"] == 5
    assert phone_entities[0]["mentions_count"] == 5
    assert len(phone_entities[0]["artifact_ids"]) == 5


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


def test_timeline_reconstruction_all_artifact_types():
    """Verify that all artifact types including documents and images without timestamps are included."""
    artifacts = [
        {"id": "a1", "artifact_type": "CALL", "timestamp": "2023-08-15 10:00:00", "content": {"caller": "A", "receiver": "B", "duration_seconds": 10}},
        {"id": "a2", "artifact_type": "SMS", "timestamp": "2023-08-15 12:00:00", "content": {"sender": "A", "recipient": "B", "message": "Second"}},
        {"id": "a3", "artifact_type": "DOCUMENT", "content": {"text": "Plain text forensic document with no explicit timestamp"}},
        {"id": "a4", "artifact_type": "IMAGE_METADATA", "content": {"filename": "crime_scene.jpg", "camera_make": "Sony"}},
    ]

    timeline = build_timeline(artifacts, case_id="c1")
    # All 4 artifacts must produce timeline events!
    assert len(timeline) == 4
    artifact_ids_in_timeline = {ev["artifact_id"] for ev in timeline}
    assert artifact_ids_in_timeline == {"a1", "a2", "a3", "a4"}
