from sqlalchemy.orm import Session, joinedload

from app.models.relationship import Relationship
from app.schemas.relationship import RelationshipCreate


class RelationshipRepository:

    @staticmethod
    def create(db: Session, relationship_data: RelationshipCreate) -> Relationship:
        data = relationship_data.model_dump()
        relationship = Relationship(**data)
        db.add(relationship)
        db.commit()
        db.refresh(relationship)
        return relationship

    @staticmethod
    def bulk_create(db: Session, relationships_data: list[dict]) -> list[Relationship]:
        if not relationships_data:
            return []

        # Deduplicate incoming relationships
        seen = set()
        to_insert = []
        for data in relationships_data:
            clean_data = {
                "id": data.get("id"),
                "case_id": data.get("case_id"),
                "source_entity_id": data.get("source_entity_id"),
                "target_entity_id": data.get("target_entity_id"),
                "relationship_type": data.get("relationship_type"),
                "confidence": str(data.get("confidence", "1.0")),
            }
            key = (
                clean_data["source_entity_id"],
                clean_data["target_entity_id"],
                clean_data["relationship_type"],
            )
            if key not in seen:
                seen.add(key)
                to_insert.append(Relationship(**clean_data))

        if to_insert:
            db.add_all(to_insert)
            db.commit()
            for r in to_insert:
                db.refresh(r)

        return to_insert

    @staticmethod
    def get_by_case(db: Session, case_id: str) -> list[Relationship]:
        return (
            db.query(Relationship)
            .options(
                joinedload(Relationship.source_entity),
                joinedload(Relationship.target_entity),
            )
            .filter(Relationship.case_id == case_id)
            .all()
        )

    @staticmethod
    def get_all(db: Session) -> list[Relationship]:
        return (
            db.query(Relationship)
            .options(
                joinedload(Relationship.source_entity),
                joinedload(Relationship.target_entity),
            )
            .all()
        )
