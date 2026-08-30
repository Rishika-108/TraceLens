from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TimelineBase(BaseModel):
    event_type: str
    description: str
    event_timestamp: datetime
    event_state: str | None = None
    modality: str | None = None
    actor: str | None = None
    target: str | None = None
    referenced_time: str | None = None
    referenced_location: str | None = None
    is_synthetic_timestamp: bool = False


class TimelineCreate(TimelineBase):
    case_id: str
    artifact_id: str


class TimelineResponse(TimelineBase):
    id: str
    case_id: str
    artifact_id: str

    model_config = ConfigDict(
        from_attributes=True
    )