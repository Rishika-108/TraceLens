from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class TimelineBase(BaseModel):
    event_type: str
    description: str
    event_timestamp: datetime


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