import io
from app.services.storage_service import StorageService


def test_evidence_upload_and_artifact_generation(client):
    # Step 1: Create a case
    case_resp = client.post(
        "/api/cases/",
        json={"title": "Operation Blackout", "description": "Financial fraud and communications investigation"},
    )
    assert case_resp.status_code == 200
    case_data = case_resp.json()
    case_id = case_data["id"]

    # Step 2: Upload WhatsApp chat evidence file
    chat_content = """15/08/2023, 10:15 - John Doe: Meet me at the station at 8 PM.
15/08/2023, 10:17 - Jane Smith: I will bring the payment ledger.
"""
    file_bytes = chat_content.encode("utf-8")
    files = {"file": ("whatsapp_chat.txt", io.BytesIO(file_bytes), "text/plain")}
    data = {"case_id": case_id, "file_type": "WHATSAPP"}

    upload_resp = client.post("/api/evidence/upload", data=data, files=files)
    assert upload_resp.status_code == 201
    evidence = upload_resp.json()

    assert evidence["case_id"] == case_id
    assert evidence["filename"] == "whatsapp_chat.txt"
    assert evidence["status"] == "COMPLETED"
    assert evidence["file_hash"] is not None
    assert len(evidence["file_hash"]) == 64  # SHA-256 length
    assert evidence["file_size"] == len(file_bytes)

    evidence_id = evidence["id"]

    # Step 3: Query parsed artifacts for this evidence
    artifacts_resp = client.get(f"/api/evidence/{evidence_id}/artifacts")
    assert artifacts_resp.status_code == 200
    artifacts = artifacts_resp.json()

    assert len(artifacts) == 2
    assert artifacts[0]["artifact_type"] == "WHATSAPP_MESSAGE"
    assert artifacts[0]["content"]["sender"] == "John Doe"
    assert "station at 8 PM" in artifacts[0]["content"]["message"]

    assert artifacts[1]["artifact_type"] == "WHATSAPP_MESSAGE"
    assert artifacts[1]["content"]["sender"] == "Jane Smith"
    assert "payment ledger" in artifacts[1]["content"]["message"]

    # Step 4: Query evidence list by case
    case_evidence_resp = client.get(f"/api/evidence/case/{case_id}")
    assert case_evidence_resp.status_code == 200
    evidence_list = case_evidence_resp.json()
    assert len(evidence_list) == 1
    assert evidence_list[0]["id"] == evidence_id

    # Clean up stored test file
    if evidence.get("file_path"):
        StorageService.delete_file(evidence["file_path"])


def test_evidence_upload_invalid_case(client):
    files = {"file": ("test.txt", io.BytesIO(b"sample"), "text/plain")}
    data = {"case_id": "non-existent-case-id-12345"}

    resp = client.post("/api/evidence/upload", data=data, files=files)
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()
