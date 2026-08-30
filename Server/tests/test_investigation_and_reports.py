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


def test_report_agent_deduplicated_unique_metrics(db_session):
    """Verify that report does not claim duplicates are unique entities."""
    from app.models.entity import Entity

    case = Case(title="Cartel Wiretap")
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    # 3 duplicate Masterminds and 2 duplicate phones (5 rows total, 2 unique)
    entities = [
        Entity(case_id=case.id, entity_type="PERSON", value="Mastermind"),
        Entity(case_id=case.id, entity_type="PERSON", value="Mastermind"),
        Entity(case_id=case.id, entity_type="PERSON", value="Mastermind"),
        Entity(case_id=case.id, entity_type="PHONE", value="+1 415 555 2671"),
        Entity(case_id=case.id, entity_type="PHONE", value="+1 415 555 2671"),
    ]
    db_session.add_all(entities)
    db_session.commit()

    report_data = generate_case_report(db=db_session, case_id=case.id)
    metrics = report_data["evidence"]["metrics"]

    # Must accurately report 2 unique entities
    assert metrics["entities_count"] == 2
    assert metrics["total_entity_mentions"] == 5

    narrative = report_data["evidence"]["narrative_report"]
    assert "2 distinct forensic entities" in narrative
    assert "across 5 observed mentions" in narrative
    # Must NOT claim 5 unique entities
    assert "5 unique forensic entities" not in narrative


def test_relationship_endpoints_exposure(db_session):
    """Verify that Relationship model and repository expose endpoint types and values."""
    from app.models.entity import Entity
    from app.models.relationship import Relationship
    from app.repositories.relationship_repository import RelationshipRepository
    from app.schemas.relationship import RelationshipResponse

    case = Case(title="Endpoint Test Case")
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    e1 = Entity(case_id=case.id, entity_type="PERSON", value="Alice Vance")
    e2 = Entity(case_id=case.id, entity_type="ORG", value="Zurich Vault")
    db_session.add_all([e1, e2])
    db_session.commit()
    db_session.refresh(e1)
    db_session.refresh(e2)

    rel = Relationship(
        case_id=case.id,
        source_entity_id=e1.id,
        target_entity_id=e2.id,
        relationship_type="MEMBER_OF",
        confidence="0.95",
    )
    db_session.add(rel)
    db_session.commit()
    db_session.refresh(rel)

    # Test model properties
    assert rel.source_entity_value == "Alice Vance"
    assert rel.source_entity_type == "PERSON"
    assert rel.target_entity_value == "Zurich Vault"
    assert rel.target_entity_type == "ORG"

    # Test repository eager loading
    fetched = RelationshipRepository.get_by_case(db_session, case.id)
    assert len(fetched) == 1
    assert fetched[0].source_entity.value == "Alice Vance"

    # Test schema serialization
    response = RelationshipResponse.model_validate(fetched[0])
    assert response.source_entity_value == "Alice Vance"
    assert response.source_entity_type == "PERSON"
    assert response.target_entity_value == "Zurich Vault"
    assert response.target_entity_type == "ORG"

