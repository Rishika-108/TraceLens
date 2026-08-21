from uuid import uuid4
from app.db.session import SessionLocal
from app.models.evidence import Evidence
from app.models.artifact import Artifact
from app.pipelines.ingestion import ingest
from app.repositories.artifact_repository import ArtifactRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.tasks.celery_app import celery


@celery.task(name="tasks.parse_evidence_task")
def parse_evidence_task(evidence_id: str, case_id: str):
    db = SessionLocal()
    try:
        evidence = EvidenceRepository.get_by_id(db, evidence_id)
        if not evidence or not evidence.file_path:
            return {"status": "error", "message": "Evidence record or file not found"}

        EvidenceRepository.update_status(db, evidence_id, "PROCESSING")

        parsed_items = ingest(evidence.file_path, evidence.file_type)

        artifact_records = []
        for item in parsed_items:
            artifact_records.append({
                "id": str(uuid4()),
                "evidence_id": evidence_id,
                "artifact_type": item.get("artifact_type", "UNKNOWN"),
                "content": item.get("content", {}),
                "raw_data": item.get("raw_data"),
                "timestamp": item.get("timestamp"),
                "parser_stage": "PARSED",
            })

        if artifact_records:
            ArtifactRepository.bulk_create(db, artifact_records)

        EvidenceRepository.update_status(db, evidence_id, "PARSED")
        return {"status": "success", "artifact_count": len(artifact_records)}
    except Exception as e:
        EvidenceRepository.update_status(db, evidence_id, "FAILED", str(e))
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()