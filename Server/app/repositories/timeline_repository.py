from sqlalchemy.orm import Session

from app.models.timeline import Timeline
from app.schemas.timeline import TimelineCreate


class TimelineRepository:

    @staticmethod
    def create(db: Session, timeline_data: TimelineCreate) -> Timeline:
        event = Timeline(**timeline_data.model_dump())
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def bulk_create(db: Session, events_data: list[dict]) -> list[Timeline]:
        events = [Timeline(**data) for data in events_data]
        db.add_all(events)
        db.commit()
        for e in events:
            db.refresh(e)
        return events

    @staticmethod
    def get_by_case(db: Session, case_id: str) -> list[Timeline]:
        return (
            db.query(Timeline)
            .filter(Timeline.case_id == case_id)
            .order_by(Timeline.event_timestamp.asc())
            .all()
        )
