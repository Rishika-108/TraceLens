from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class CaseBase(BaseModel):
    title: str
    description: str | None = None


class CaseCreate(CaseBase):
    pass


class CaseResponse(CaseBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )