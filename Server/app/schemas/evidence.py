from datetime import datetime
from pydantic import BaseModel
from pydantic import ConfigDict


class EvidenceBase(BaseModel):
    filename: str
    file_type: str
    file_path: str | None = None
    file_hash: str | None = None
    file_size: int | None = None
    status: str = "PENDING"
    error_message: str | None = None


class EvidenceCreate(EvidenceBase):
    case_id: str


class EvidenceResponse(EvidenceBase):
    id: str
    case_id: str
    uploaded_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )