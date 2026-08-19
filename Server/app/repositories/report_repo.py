from sqlalchemy.orm import Session

from app.models.report import Report
from app.schemas.report import ReportCreate


class ReportRepository:

    @staticmethod
    def create(
        db: Session,
        report_data: ReportCreate,
    ):
        report = Report(
            **report_data.model_dump()
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        return report

    @staticmethod
    def get_by_case(
        db: Session,
        case_id: str,
    ):
        return (
            db.query(Report)
            .filter(Report.case_id == case_id)
            .all()
        )