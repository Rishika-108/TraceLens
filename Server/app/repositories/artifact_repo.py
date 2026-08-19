from sqlalchemy.orm import Session

from app.models.artifact import Artifact
from app.schemas.artifact import ArtifactCreate


class ArtifactRepository:

    @staticmethod
    def create(
        db: Session,
        artifact_data: ArtifactCreate,
    ):
        artifact = Artifact(
            **artifact_data.model_dump()
        )

        db.add(artifact)
        db.commit()
        db.refresh(artifact)

        return artifact

    @staticmethod
    def get_by_evidence(
        db: Session,
        evidence_id: str,
    ):
        return (
            db.query(Artifact)
            .filter(
                Artifact.evidence_id == evidence_id
            )
            .all()
        )