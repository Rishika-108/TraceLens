from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.timeline_repository import TimelineRepository
from app.schemas.timeline import TimelineCreate, TimelineResponse

router = APIRouter()


@router.post(
    "/",
    response_model=TimelineResponse,
)
async def create_event(
    timeline: TimelineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TimelineRepository.create(
        db,
        timeline,
    )


@router.get(
    "/case/{case_id}",
    response_model=list[TimelineResponse],
)
async def get_timeline(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TimelineRepository.get_by_case(
        db,
        case_id,
    )