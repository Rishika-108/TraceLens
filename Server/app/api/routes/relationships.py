from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.relationship_repository import RelationshipRepository
from app.schemas.relationship import RelationshipCreate, RelationshipResponse

router = APIRouter()


@router.post(
    "/",
    response_model=RelationshipResponse,
)
async def create_relationship(
    relationship: RelationshipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RelationshipRepository.create(
        db,
        relationship,
    )


@router.get(
    "/",
    response_model=list[RelationshipResponse],
)
async def get_relationships(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RelationshipRepository.get_all(db)


@router.get(
    "/case/{case_id}",
    response_model=list[RelationshipResponse],
)
async def get_relationships_by_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RelationshipRepository.get_by_case(
        db,
        case_id,
    )