from app.ai.agents.investigator import investigate
from app.ai.agents.report_agent import generate_case_report
from app.ai.evaluation.evaluator import evaluate
from app.ai.retrieval.retriever import build_evidence_context
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.artifact import Artifact
from app.ai.embeddings.generator import create_embedding


def test_context_builder_formatting():
    artifacts = [
        {
            "id": "art-99",
            "artifact_type": "SMS",
            "timestamp": "2023-08-15 19:30:00",
            "content": {"sender": "+112233", "recipient": "+445566", "message": "Funds ready at Swiss Bank"},
        }
    ]

    context = build_evidence_context(artifacts)
    assert "[EVIDENCE_REF #1" in context
    assert "ID: art-99" in context
    assert "Funds ready at Swiss Bank" in context


def test_investigation_agent_grounded_answer(db_session):
    case = Case(title="Cyber Extortion")
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    ev = Evidence(case_id=case.id, filename="chat.txt", file_type="WHATSAPP", status="COMPLETED")
    db_session.add(ev)
    db_session.commit()
    db_session.refresh(ev)

    art = Artifact(
        evidence_id=ev.id,
        artifact_type="WHATSAPP_MESSAGE",
        content={"sender": "BlackHat", "message": "Pay 5 BTC to wallet 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa by midnight"},
        embedding=create_embedding("Pay 5 BTC to wallet by midnight"),
    )
    db_session.add(art)
    db_session.commit()

    inv_result = investigate(db=db_session, case_id=case.id, question="Who requested the BTC payment?")
    assert inv_result["case_id"] == case.id
    assert inv_result["confidence"] > 0.5
    assert len(inv_result["evidence_references"]) >= 1

    eval_result = evaluate(inv_result["answer"], inv_result["evidence_references"])
    assert eval_result["is_grounded"] is True
    assert eval_result["has_fact_tags"] is True


def test_investigation_insufficient_evidence(db_session):
    case = Case(title="Empty Case")
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    inv_result = investigate(db=db_session, case_id=case.id, question="Where was the meeting located?")
    assert "INSUFFICIENT EVIDENCE" in inv_result["answer"].upper()
    assert inv_result["confidence"] == 0.0


def test_report_agent_synthesis(db_session):
    case = Case(title="Financial Fraud Investigation")
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    report_data = generate_case_report(db=db_session, case_id=case.id)
    assert report_data["case_id"] == case.id
    assert "Financial Fraud" in report_data["title"]
    assert "narrative_report" in report_data["evidence"]
    assert "Executive Summary" in report_data["evidence"]["narrative_report"]
