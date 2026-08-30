from pydantic import BaseModel, ConfigDict


class RelationshipBase(BaseModel):
    relationship_type: str
    confidence: str = "1.0"
    supporting_artifact_id: str | None = None
    evidence_snippet: str | None = None


class RelationshipCreate(RelationshipBase):
    case_id: str
    source_entity_id: str
    target_entity_id: str


class RelationshipResponse(RelationshipBase):
    id: str
    case_id: str
    source_entity_id: str
    target_entity_id: str
    source_entity_value: str | None = None
    source_entity_type: str | None = None
    target_entity_value: str | None = None
    target_entity_type: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )