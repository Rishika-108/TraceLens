from app.ai.embeddings.generator import create_embedding, create_embeddings_batch
from app.ai.retrieval.semantic_search import search
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.artifact import Artifact
from app.repositories.case_repository import CaseRepository


def test_embedding_generation_dimension():
    text = "Suspect communication regarding Swiss bank account transfer"
    vec = create_embedding(text)

    assert isinstance(vec, list)
    assert len(vec) == 384
    assert any(v != 0.0 for v in vec)

    batch_vecs = create_embeddings_batch([text, "Secondary query"])
    assert len(batch_vecs) == 2
    assert len(batch_vecs[0]) == 384


def test_case_isolated_semantic_search(db_session):
    # Case 1
    case1 = Case(title="Case Alpha")
    db_session.add(case1)
    db_session.commit()
    db_session.refresh(case1)

    ev1 = Evidence(case_id=case1.id, filename="email1.eml", file_type="EMAIL", status="COMPLETED")
    db_session.add(ev1)
    db_session.commit()
    db_session.refresh(ev1)

    art1 = Artifact(
        evidence_id=ev1.id,
        artifact_type="EMAIL",
        content={"sender": "alice@alpha.com", "recipient": "bob@alpha.com", "subject": "Financial transfer funds"},
        embedding=create_embedding("Financial transfer funds"),
    )
    db_session.add(art1)

    # Case 2 (Strict isolation check)
    case2 = Case(title="Case Beta")
    db_session.add(case2)
    db_session.commit()
    db_session.refresh(case2)

    ev2 = Evidence(case_id=case2.id, filename="email2.eml", file_type="EMAIL", status="COMPLETED")
    db_session.add(ev2)
    db_session.commit()
    db_session.refresh(ev2)

    art2 = Artifact(
        evidence_id=ev2.id,
        artifact_type="EMAIL",
        content={"sender": "other@beta.com", "subject": "Financial transfer in Beta"},
        embedding=create_embedding("Financial transfer in Beta"),
    )
    db_session.add(art2)
    db_session.commit()

    # Search in Case 1 must ONLY return Case 1 artifacts
    results = search(db=db_session, case_id=case1.id, query="Financial funds")
    assert len(results) >= 1
    assert all(r["evidence_id"] == ev1.id for r in results)
    assert not any(r["evidence_id"] == ev2.id for r in results)
