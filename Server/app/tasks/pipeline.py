from app.tasks.parse_evidence import parse_evidence_task
from app.tasks.extract_entities import extract_entities_task
from app.tasks.build_timeline import build_timeline_task
from app.tasks.generate_embeddings import generate_embeddings_task
from app.tasks.celery_app import celery


@celery.task(name="tasks.process_evidence_pipeline")
def process_evidence_pipeline(evidence_id: str, case_id: str):
    """
    Unified end-to-end evidence intelligence processing pipeline (AGENT.md Sec. 4, 35, 60):
    1. Parse Evidence -> Artifacts
    2. Extract Entities & Discover Relationships
    3. Build Chronological Timeline
    4. Generate Semantic Embeddings & Index
    """
    # 1. Parse Evidence
    res_parse = parse_evidence_task(evidence_id, case_id)
    if res_parse.get("status") == "failed":
        return res_parse

    # 2. Extract Entities & Relationships
    res_entities = extract_entities_task(evidence_id, case_id)

    # 3. Build Timeline
    res_timeline = build_timeline_task(evidence_id, case_id)

    # 4. Generate Embeddings
    res_embeddings = generate_embeddings_task(evidence_id, case_id)

    return {
        "status": "completed",
        "evidence_id": evidence_id,
        "case_id": case_id,
        "parse_result": res_parse,
        "entity_result": res_entities,
        "timeline_result": res_timeline,
        "embedding_result": res_embeddings,
    }
