from sqlalchemy.orm import Session

from app.models.artifact import Artifact
from app.models.evidence import Evidence
from app.schemas.artifact import ArtifactCreate


class ArtifactRepository:

    @staticmethod
    def create(db: Session, artifact_data: ArtifactCreate) -> Artifact:
        artifact = Artifact(**artifact_data.model_dump())
        db.add(artifact)
        db.commit()
        db.refresh(artifact)
        return artifact

    @staticmethod
    def bulk_create(db: Session, artifacts_data: list[dict]) -> list[Artifact]:
        artifacts = [Artifact(**data) for data in artifacts_data]
        db.add_all(artifacts)
        db.commit()
        for a in artifacts:
            db.refresh(a)
        return artifacts

    @staticmethod
    def get_by_evidence(db: Session, evidence_id: str) -> list[Artifact]:
        return (
            db.query(Artifact)
            .filter(Artifact.evidence_id == evidence_id)
            .order_by(Artifact.timestamp.asc().nulls_last())
            .all()
        )

    @staticmethod
    def get_by_case(db: Session, case_id: str) -> list[Artifact]:
        return (
            db.query(Artifact)
            .join(Evidence, Artifact.evidence_id == Evidence.id)
            .filter(Evidence.case_id == case_id)
            .order_by(Artifact.timestamp.asc().nulls_last())
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, artifact_id: str) -> Artifact | None:
        return (
            db.query(Artifact)
            .filter(Artifact.id == artifact_id)
            .first()
        )
