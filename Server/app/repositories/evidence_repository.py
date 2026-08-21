from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.schemas.evidence import EvidenceCreate


class EvidenceRepository:

    @staticmethod
    def create(db: Session, evidence_data: EvidenceCreate) -> Evidence:
        evidence = Evidence(**evidence_data.model_dump())
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        return evidence

    @staticmethod
    def create_with_metadata(
        db: Session,
        case_id: str,
        filename: str,
        file_type: str,
        file_path: str | None = None,
        file_hash: str | None = None,
        file_size: int | None = None,
        status: str = "PENDING",
    ) -> Evidence:
        evidence = Evidence(
            case_id=case_id,
            filename=filename,
            file_type=file_type,
            file_path=file_path,
            file_hash=file_hash,
            file_size=file_size,
            status=status,
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        return evidence

    @staticmethod
    def update_status(
        db: Session,
        evidence_id: str,
        status: str,
        error_message: str | None = None,
    ) -> Evidence | None:
        evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if evidence:
            evidence.status = status
            if error_message is not None:
                evidence.error_message = error_message
            db.commit()
            db.refresh(evidence)
        return evidence

    @staticmethod
    def get_by_id(db: Session, evidence_id: str) -> Evidence | None:
        return (
            db.query(Evidence)
            .filter(Evidence.id == evidence_id)
            .first()
        )

    @staticmethod
    def get_by_case(db: Session, case_id: str) -> list[Evidence]:
        return (
            db.query(Evidence)
            .filter(Evidence.case_id == case_id)
            .order_by(Evidence.uploaded_at.desc())
            .all()
        )
