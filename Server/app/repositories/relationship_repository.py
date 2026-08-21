from sqlalchemy.orm import Session

from app.models.relationship import Relationship
from app.schemas.relationship import RelationshipCreate


class RelationshipRepository:

    @staticmethod
    def create(db: Session, relationship_data: RelationshipCreate) -> Relationship:
        relationship = Relationship(**relationship_data.model_dump())
        db.add(relationship)
        db.commit()
        db.refresh(relationship)
        return relationship

    @staticmethod
    def bulk_create(db: Session, relationships_data: list[dict]) -> list[Relationship]:
        relationships = [Relationship(**data) for data in relationships_data]
        db.add_all(relationships)
        db.commit()
        for r in relationships:
            db.refresh(r)
        return relationships

    @staticmethod
    def get_by_case(db: Session, case_id: str) -> list[Relationship]:
        return (
            db.query(Relationship)
            .filter(Relationship.case_id == case_id)
            .all()
        )

    @staticmethod
    def get_all(db: Session) -> list[Relationship]:
        return db.query(Relationship).all()
