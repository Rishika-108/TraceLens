from sqlalchemy.orm import Session

from app.models.entity import Entity
from app.schemas.entity import EntityCreate


class EntityRepository:

    @staticmethod
    def create(
        db: Session,
        entity_data: EntityCreate,
    ):
        entity = Entity(
            **entity_data.model_dump()
        )

        db.add(entity)
        db.commit()
        db.refresh(entity)

        return entity

    @staticmethod
    def get_by_case(
        db: Session,
        case_id: str,
    ):
        return (
            db.query(Entity)
            .filter(Entity.case_id == case_id)
            .all()
        )