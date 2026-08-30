from sqlalchemy.orm import Session

from app.models.entity import Entity
from app.schemas.entity import EntityCreate


class EntityRepository:

    @staticmethod
    def create(db: Session, entity_data: EntityCreate) -> Entity:
        data = entity_data.model_dump()
        # Check if already exists in this case
        existing = (
            db.query(Entity)
            .filter(
                Entity.case_id == data["case_id"],
                Entity.entity_type == data["entity_type"],
                Entity.value == data["value"],
            )
            .first()
        )
        if existing:
            return existing

        entity = Entity(**data)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def bulk_create(db: Session, entities_data: list[dict]) -> list[Entity]:
        if not entities_data:
            return []

        case_id = entities_data[0].get("case_id")
        existing_keys = set()
        if case_id:
            existing = (
                db.query(Entity.entity_type, Entity.value)
                .filter(Entity.case_id == case_id)
                .all()
            )
            existing_keys = {(t, str(v).strip().lower()) for t, v in existing}

        to_insert = []
        for data in entities_data:
            ent_type = data.get("entity_type", "")
            val = str(data.get("value", "")).strip()
            key = (ent_type, val.lower())

            if key not in existing_keys:
                existing_keys.add(key)
                clean_data = {
                    "id": data.get("id"),
                    "case_id": data.get("case_id"),
                    "artifact_id": data.get("artifact_id"),
                    "entity_type": ent_type,
                    "value": val,
                }
                to_insert.append(Entity(**clean_data))

        if to_insert:
            db.add_all(to_insert)
            db.commit()
            for e in to_insert:
                db.refresh(e)

        return to_insert

    @staticmethod
    def get_by_case(db: Session, case_id: str) -> list[Entity]:
        raw_entities = (
            db.query(Entity)
            .filter(Entity.case_id == case_id)
            .all()
        )
        # Deduplicate across any legacy rows
        seen = set()
        deduped: list[Entity] = []
        for e in raw_entities:
            key = (e.entity_type, e.value.strip().lower())
            if key not in seen:
                seen.add(key)
                deduped.append(e)
        return deduped

    @staticmethod
    def get_by_type(db: Session, case_id: str, entity_type: str) -> list[Entity]:
        raw_entities = (
            db.query(Entity)
            .filter(Entity.case_id == case_id, Entity.entity_type == entity_type)
            .all()
        )
        seen = set()
        deduped: list[Entity] = []
        for e in raw_entities:
            key = e.value.strip().lower()
            if key not in seen:
                seen.add(key)
                deduped.append(e)
        return deduped
