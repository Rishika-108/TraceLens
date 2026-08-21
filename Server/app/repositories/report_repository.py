from sqlalchemy.orm import Session

from app.models.report import Report
from app.schemas.report import ReportCreate


class ReportRepository:

    @staticmethod
    def create(db: Session, report_data: ReportCreate) -> Report:
        report = Report(**report_data.model_dump())
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def get_by_id(db: Session, report_id: str) -> Report | None:
        return (
            db.query(Report)
            .filter(Report.id == report_id)
            .first()
        )

    @staticmethod
    def get_by_case(db: Session, case_id: str) -> list[Report]:
        return (
            db.query(Report)
            .filter(Report.case_id == case_id)
            .order_by(Report.generated_at.desc())
            .all()
        )
