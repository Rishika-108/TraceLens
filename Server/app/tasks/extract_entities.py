from app.db.session import SessionLocal
from app.pipelines.entity_extraction import extract_entities
from app.pipelines.relationship_discovery import discover_relationships
from app.repositories.artifact_repository import ArtifactRepository
from app.repositories.entity_repository import EntityRepository
from app.repositories.relationship_repository import RelationshipRepository
from app.tasks.celery_app import celery


@celery.task(name="tasks.extract_entities_task")
def extract_entities_task(evidence_id: str, case_id: str):
    db = SessionLocal()
    try:
        artifacts = ArtifactRepository.get_by_evidence(db, evidence_id)
        artifact_dicts = [
            {
                "id": a.id,
                "evidence_id": a.evidence_id,
                "case_id": case_id,
                "artifact_type": a.artifact_type,
                "content": a.content,
                "raw_data": a.raw_data,
                "timestamp": a.timestamp,
            }
            for a in artifacts
        ]

        extracted = extract_entities(artifact_dicts, case_id)
        if extracted:
            EntityRepository.bulk_create(db, extracted)

        # Discover relationships from new entities & artifacts
        relationships = discover_relationships(extracted, artifact_dicts, case_id)
        if relationships:
            RelationshipRepository.bulk_create(db, relationships)

        return {
            "status": "success",
            "entities_count": len(extracted),
            "relationships_count": len(relationships),
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()