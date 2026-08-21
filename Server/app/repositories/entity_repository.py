from sqlalchemy.orm import Session

from app.models.entity import Entity
from app.schemas.entity import EntityCreate


class EntityRepository:

    @staticmethod
    def create(db: Session, entity_data: EntityCreate) -> Entity:
        entity = Entity(**entity_data.model_dump())
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def bulk_create(db: Session, entities_data: list[dict]) -> list[Entity]:
        entities = [Entity(**data) for data in entities_data]
        db.add_all(entities)
        db.commit()
        for e in entities:
            db.refresh(e)
        return entities

    @staticmethod
    def get_by_case(db: Session, case_id: str) -> list[Entity]:
        return (
            db.query(Entity)
            .filter(Entity.case_id == case_id)
            .all()
        )

    @staticmethod
    def get_by_type(db: Session, case_id: str, entity_type: str) -> list[Entity]:
        return (
            db.query(Entity)
            .filter(Entity.case_id == case_id, Entity.entity_type == entity_type)
            .all()
        )
