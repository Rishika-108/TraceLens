from datetime import datetime
from typing import Any
from pydantic import BaseModel
from pydantic import ConfigDict


class ArtifactBase(BaseModel):
    artifact_type: str
    content: dict[str, Any]
    raw_data: str | None = None
    parser_stage: str = "PARSED"
    timestamp: datetime | None = None


class ArtifactCreate(ArtifactBase):
    evidence_id: str


class ArtifactResponse(ArtifactBase):
    id: str
    evidence_id: str

    model_config = ConfigDict(
        from_attributes=True
    )