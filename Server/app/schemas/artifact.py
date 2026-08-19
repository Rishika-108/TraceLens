from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class ArtifactBase(BaseModel):
    artifact_type: str
    content: dict
    timestamp: datetime | None = None


class ArtifactCreate(ArtifactBase):
    evidence_id: str


class ArtifactResponse(ArtifactBase):
    id: str
    evidence_id: str

    model_config = ConfigDict(
        from_attributes=True
    )