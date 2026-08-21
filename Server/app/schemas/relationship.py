from pydantic import BaseModel
from pydantic import ConfigDict


class RelationshipBase(BaseModel):
    relationship_type: str
    confidence: str = "1.0"


class RelationshipCreate(RelationshipBase):
    case_id: str
    source_entity_id: str
    target_entity_id: str


class RelationshipResponse(RelationshipBase):
    id: str
    case_id: str
    source_entity_id: str
    target_entity_id: str

    model_config = ConfigDict(
        from_attributes=True
    )