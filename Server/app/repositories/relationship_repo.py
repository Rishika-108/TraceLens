from sqlalchemy.orm import Session

from app.models.relationship import Relationship
from app.schemas.relationship import (
    RelationshipCreate,
)


class RelationshipRepository:

    @staticmethod
    def create(
        db: Session,
        relationship_data: RelationshipCreate,
    ):
        relationship = Relationship(
            **relationship_data.model_dump()
        )

        db.add(relationship)
        db.commit()
        db.refresh(relationship)

        return relationship

    @staticmethod
    def get_all(db: Session):
        return db.query(Relationship).all()