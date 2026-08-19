from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.schemas.evidence import EvidenceCreate


class EvidenceRepository:

    @staticmethod
    def create(
        db: Session,
        evidence_data: EvidenceCreate,
    ):
        evidence = Evidence(
            **evidence_data.model_dump()
        )

        db.add(evidence)
        db.commit()
        db.refresh(evidence)

        return evidence

    @staticmethod
    def get_by_case(
        db: Session,
        case_id: str,
    ):
        return (
            db.query(Evidence)
            .filter(Evidence.case_id == case_id)
            .all()
        )