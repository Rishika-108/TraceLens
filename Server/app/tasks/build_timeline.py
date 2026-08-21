from app.db.session import SessionLocal
from app.pipelines.timeline_reconstruction import build_timeline
from app.repositories.artifact_repository import ArtifactRepository
from app.repositories.timeline_repository import TimelineRepository
from app.tasks.celery_app import celery


@celery.task(name="tasks.build_timeline_task")
def build_timeline_task(evidence_id: str, case_id: str):
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

        timeline_events = build_timeline(artifact_dicts, case_id)
        if timeline_events:
            TimelineRepository.bulk_create(db, timeline_events)

        return {"status": "success", "timeline_events_count": len(timeline_events)}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()