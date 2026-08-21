from app.db.session import SessionLocal
from app.pipelines.embedding_generation import prepare_artifact_text
from app.ai.embeddings.generator import create_embedding
from app.repositories.artifact_repository import ArtifactRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.tasks.celery_app import celery


@celery.task(name="tasks.generate_embeddings_task")
def generate_embeddings_task(evidence_id: str, case_id: str):
    db = SessionLocal()
    try:
        artifacts = ArtifactRepository.get_by_evidence(db, evidence_id)
        count = 0
        for a in artifacts:
            text = prepare_artifact_text({
                "artifact_type": a.artifact_type,
                "content": a.content,
                "timestamp": a.timestamp,
                "raw_data": a.raw_data,
            })
            a.embedding = create_embedding(text)
            count += 1

        db.commit()
        EvidenceRepository.update_status(db, evidence_id, "COMPLETED")
        return {"status": "success", "embeddings_generated": count}
    except Exception as e:
        EvidenceRepository.update_status(db, evidence_id, "FAILED", str(e))
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()