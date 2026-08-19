from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class ReportBase(BaseModel):
    title: str
    summary: str
    evidence: dict


class ReportCreate(ReportBase):
    case_id: str


class ReportResponse(ReportBase):
    id: str
    case_id: str
    generated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )