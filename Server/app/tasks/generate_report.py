from app.ai.agents.report_agent import generate_case_report
from app.db.session import SessionLocal
from app.repositories.report_repository import ReportRepository
from app.schemas.report import ReportCreate
from app.tasks.celery_app import celery


@celery.task(name="tasks.generate_report_task")
def generate_report_task(case_id: str, title: str | None = None):
    db = SessionLocal()
    try:
        report_data = generate_case_report(db, case_id, title)
        report = ReportRepository.create(
            db,
            ReportCreate(
                case_id=case_id,
                title=report_data["title"],
                summary=report_data["summary"],
                evidence=report_data["evidence"],
            ),
        )
        return {"status": "success", "report_id": report.id}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()