from sqlalchemy.orm import Session

from app.models.case import Case
from app.schemas.case import CaseCreate


class CaseRepository:

    @staticmethod
    def create(db: Session, case_data: CaseCreate) -> Case:
        case = Case(**case_data.model_dump())
        db.add(case)
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def get_all(db: Session) -> list[Case]:
        return db.query(Case).all()

    @staticmethod
    def get_by_id(db: Session, case_id: str) -> Case | None:
        return (
            db.query(Case)
            .filter(Case.id == case_id)
            .first()
        )

    @staticmethod
    def delete(db: Session, case_id: str) -> Case | None:
        case = (
            db.query(Case)
            .filter(Case.id == case_id)
            .first()
        )
        if case:
            db.delete(case)
            db.commit()
        return case
