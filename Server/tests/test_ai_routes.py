import io
from app.services.storage_service import StorageService


def test_ai_routes_end_to_end(client):
    # 1. Create Case
    case_resp = client.post(
        "/api/cases/",
        json={"title": "Project DarkLens", "description": "High-profile narcotics communication case"},
    )
    assert case_resp.status_code == 200
    case_id = case_resp.json()["id"]

    # 2. Upload Chat Evidence with multiline & entities
    chat = """15/08/2023, 10:15 - Walter: Meet near Zurich Bank on MG Road tomorrow at 6 PM.
15/08/2023, 10:17 - Jesse: Transfer the 50000 USD to Account #99881.
15/08/2023, 10:20 - Walter: Confirmed. Sent from phone +14155552671.
"""
    files = {"file": ("darklens_chat.txt", io.BytesIO(chat.encode("utf-8")), "text/plain")}
    upload_resp = client.post("/api/evidence/upload", data={"case_id": case_id, "file_type": "WHATSAPP"}, files=files)
    assert upload_resp.status_code == 201

    # 3. Test Semantic Search Endpoint
    search_resp = client.post(
        "/api/search/",
        json={"case_id": case_id, "query": "Find conversations discussing money transfer and bank accounts", "limit": 5},
    )
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert search_data["case_id"] == case_id
    assert search_data["total_results"] >= 1
    assert any("50000 USD" in str(r["content"]) for r in search_data["results"])

    # 4. Test Investigation Agent Endpoint
    inv_resp = client.post(
        "/api/investigations/",
        json={"case_id": case_id, "question": "Who mentioned the phone number and where is the meeting location?"},
    )
    assert inv_resp.status_code == 200
    inv_data = inv_resp.json()
    assert inv_data["case_id"] == case_id
    assert inv_data["confidence"] > 0.5
    assert len(inv_data["evidence_references"]) >= 1
    assert "Executive Summary" in inv_data["answer"]

    # 5. Test Automated Report Generation Endpoint
    report_resp = client.post(
        f"/api/reports/generate?case_id={case_id}&title=Official%20Case%20Assessment",
    )
    assert report_resp.status_code == 200
    report_data = report_resp.json()
    assert report_data["case_id"] == case_id
    assert "Official Case Assessment" in report_data["title"]
    assert "evidence" in report_data

    # 6. Verify Entities and Timeline endpoints
    entities_resp = client.get(f"/api/entities/case/{case_id}")
    assert entities_resp.status_code == 200
    entities = entities_resp.json()
    assert len(entities) >= 1

    timeline_resp = client.get(f"/api/timelines/case/{case_id}")
    assert timeline_resp.status_code == 200
    timeline = timeline_resp.json()
    assert len(timeline) >= 1

    # Clean up file
    ev_path = upload_resp.json().get("file_path")
    if ev_path:
        StorageService.delete_file(ev_path)
