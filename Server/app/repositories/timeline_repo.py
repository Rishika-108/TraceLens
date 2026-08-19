from sqlalchemy.orm import Session

from app.models.timeline import Timeline
from app.schemas.timeline import TimelineCreate


class TimelineRepository:

    @staticmethod
    def create(
        db: Session,
        timeline_data: TimelineCreate,
    ):
        event = Timeline(
            **timeline_data.model_dump()
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return event

    @staticmethod
    def get_by_case(
        db: Session,
        case_id: str,
    ):
        return (
            db.query(Timeline)
            .filter(Timeline.case_id == case_id)
            .order_by(
                Timeline.event_timestamp
            )
            .all()
        )