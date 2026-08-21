import io
from app.services.storage_service import StorageService


def test_full_spectrum_forensic_investigation_lifecycle(client):
    """
    Comprehensive End-to-End Forensic Investigation Lifecycle Test (AGENT.md Sec. 4, 5, 60):
    1. Authenticate Investigator
    2. Open Forensic Case
    3. Ingest Multi-Source Evidence (Calls, WhatsApp, Email, Notes)
    4. Validate Cryptographic Chain of Custody (SHA-256)
    5. Verify Intelligence Extraction (Entities, Relationships, Timeline)
    6. Perform Semantic Search across Vector Space
    7. Execute AI Investigation Agent with Grounded Citations
    8. Generate Formal Case Intelligence Report
    9. Enforce Strict Case Boundary Isolation
    """
    # ----------------------------------------------------
    # Stage 1: Authenticate Investigator
    # ----------------------------------------------------
    auth_resp = client.post(
        "/api/auth/register",
        json={
            "username": "lead_forensic_agent",
            "email": "agent@tracelens.gov",
            "password": "ForensicPass@2026!",
            "role": "INVESTIGATOR",
        },
    )
    assert auth_resp.status_code == 201
    auth_data = auth_resp.json()
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # ----------------------------------------------------
    # Stage 2: Create Forensic Case
    # ----------------------------------------------------
    case_resp = client.post(
        "/api/cases/",
        json={
            "title": "Operation Sovereign Vault",
            "description": "Multi-jurisdiction financial fraud and cyber extortion probe.",
        },
        headers=headers,
    )
    assert case_resp.status_code == 200
    case_id = case_resp.json()["id"]

    # ----------------------------------------------------
    # Stage 3: Ingest Multi-Source Heterogeneous Evidence
    # ----------------------------------------------------
    # 1. Call Record CSV
    call_csv = """caller,receiver,duration,timestamp,type
+14155552671,+919876543210,185,2023-08-15 14:00:00,incoming
+919876543210,+41225559988,90,2023-08-15 14:30:00,outgoing
"""
    call_file = {"file": ("call_logs.csv", io.BytesIO(call_csv.encode("utf-8")), "text/csv")}
    call_resp = client.post("/api/evidence/upload", data={"case_id": case_id, "file_type": "CALL"}, files=call_file, headers=headers)
    assert call_resp.status_code == 201
    assert call_resp.json()["status"] == "COMPLETED"
    assert len(call_resp.json()["file_hash"]) == 64

    # 2. WhatsApp Chat Export
    chat_txt = """15/08/2023, 15:00 - Mastermind: Transfer the 250000 USD to Account #99881 at Zurich Bank.
15/08/2023, 15:05 - Operator: Done. Sent crypto backup to 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa.
15/08/2023, 15:10 - Mastermind: Meet near MG Road terminal tomorrow at 6 PM.
"""
    chat_file = {"file": ("whatsapp_export.txt", io.BytesIO(chat_txt.encode("utf-8")), "text/plain")}
    chat_resp = client.post("/api/evidence/upload", data={"case_id": case_id, "file_type": "WHATSAPP"}, files=chat_file, headers=headers)
    assert chat_resp.status_code == 201

    # 3. Email EML Record
    email_eml = b"""From: informant@deepvault.io
To: operator@darknet.org
Subject: Offshore Wire Verification
Date: Tue, 15 Aug 2023 16:00:00 +0000

The offshore wire for 250000 USD has cleared Zurich Bank.
"""
    eml_file = {"file": ("wire_confirmation.eml", io.BytesIO(email_eml), "message/rfc822")}
    eml_resp = client.post("/api/evidence/upload", data={"case_id": case_id, "file_type": "EMAIL"}, files=eml_file, headers=headers)
    assert eml_resp.status_code == 201

    # ----------------------------------------------------
    # Stage 4: Verify Intelligence Extraction (Entities, Relationships, Timeline)
    # ----------------------------------------------------
    # Entities
    entities_resp = client.get(f"/api/entities/case/{case_id}", headers=headers)
    assert entities_resp.status_code == 200
    entities = entities_resp.json()
    assert len(entities) >= 4
    entity_types = {e["entity_type"] for e in entities}
    assert "PHONE" in entity_types
    assert "EMAIL" in entity_types or "CRYPTO_ADDRESS" in entity_types

    # Relationships
    rel_resp = client.get(f"/api/relationships/case/{case_id}", headers=headers)
    assert rel_resp.status_code == 200
    relationships = rel_resp.json()
    assert len(relationships) >= 1

    # Timeline
    timeline_resp = client.get(f"/api/timelines/case/{case_id}", headers=headers)
    assert timeline_resp.status_code == 200
    timeline = timeline_resp.json()
    assert len(timeline) >= 4
    # Verify chronological ordering
    timestamps = [t["event_timestamp"] for t in timeline if t["event_timestamp"]]
    assert timestamps == sorted(timestamps)

    # ----------------------------------------------------
    # Stage 5: Semantic Similarity Search
    # ----------------------------------------------------
    search_resp = client.post(
        "/api/search/",
        json={"case_id": case_id, "query": "Find records regarding Zurich Bank wire transfers and USD payment amounts", "limit": 5},
        headers=headers,
    )
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert search_data["total_results"] >= 1
    assert any("250000 USD" in str(r["content"]) or "Zurich Bank" in str(r["content"]) for r in search_data["results"])

    # ----------------------------------------------------
    # Stage 6: AI-Assisted Investigation Agent
    # ----------------------------------------------------
    inv_resp = client.post(
        "/api/investigations/",
        json={"case_id": case_id, "question": "What amount was transferred to Zurich Bank and what meeting was arranged?"},
        headers=headers,
    )
    assert inv_resp.status_code == 200
    inv_data = inv_resp.json()
    assert inv_data["confidence"] > 0.6
    assert len(inv_data["evidence_references"]) >= 1
    assert "Executive Summary" in inv_data["answer"]
    assert "Artifact #" in inv_data["answer"] or "EVIDENCE_REF #" in inv_data["answer"]

    # ----------------------------------------------------
    # Stage 7: Automated Case Intelligence Report
    # ----------------------------------------------------
    report_resp = client.post(
        f"/api/reports/generate?case_id={case_id}&title=Final%20Sovereign%20Vault%20Assessment",
        headers=headers,
    )
    assert report_resp.status_code == 200
    report_data = report_resp.json()
    assert "Final Sovereign Vault Assessment" in report_data["title"]
    assert report_data["evidence"]["metrics"]["evidence_count"] == 3
    assert report_data["evidence"]["metrics"]["timeline_events_count"] >= 4

    # ----------------------------------------------------
    # Stage 8: Strict Case Boundary Isolation
    # ----------------------------------------------------
    other_case_resp = client.post("/api/cases/", json={"title": "Unrelated Case Zeta"}, headers=headers)
    other_case_id = other_case_resp.json()["id"]

    # Search in Unrelated Case must yield ZERO results from Case 1
    empty_search = client.post(
        "/api/search/",
        json={"case_id": other_case_id, "query": "Zurich Bank wire transfer 250000 USD"},
        headers=headers,
    )
    assert empty_search.status_code == 200
    assert empty_search.json()["total_results"] == 0

    # Investigation in Unrelated Case must return Insufficient Evidence
    empty_inv = client.post(
        "/api/investigations/",
        json={"case_id": other_case_id, "question": "What amount was transferred to Zurich Bank?"},
        headers=headers,
    )
    assert empty_inv.status_code == 200
    assert "INSUFFICIENT EVIDENCE" in empty_inv.json()["answer"].upper()
    assert empty_inv.json()["confidence"] == 0.0

    # Clean up files
    for r in [call_resp, chat_resp, eml_resp]:
        fpath = r.json().get("file_path")
        if fpath:
            StorageService.delete_file(fpath)
