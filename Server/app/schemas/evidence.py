from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class EvidenceBase(BaseModel):
    filename: str
    file_type: str


class EvidenceCreate(EvidenceBase):
    case_id: str


class EvidenceResponse(EvidenceBase):
    id: str
    case_id: str
    uploaded_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )