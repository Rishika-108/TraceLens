from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.entity_repository import EntityRepository
from app.schemas.entity import EntityCreate, EntityResponse

router = APIRouter()


@router.post(
    "/",
    response_model=EntityResponse,
)
async def create_entity(
    entity: EntityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return EntityRepository.create(
        db,
        entity,
    )


@router.get(
    "/case/{case_id}",
    response_model=list[EntityResponse],
)
async def get_entities(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return EntityRepository.get_by_case(
        db,
        case_id,
    )