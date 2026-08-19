from pydantic import BaseModel
from pydantic import ConfigDict


class EntityBase(BaseModel):
    entity_type: str
    value: str


class EntityCreate(EntityBase):
    case_id: str


class EntityResponse(EntityBase):
    id: str
    case_id: str

    model_config = ConfigDict(
        from_attributes=True
    )