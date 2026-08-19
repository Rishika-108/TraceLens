from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.relationship_repository import (
    RelationshipRepository,
)
from app.schemas.relationship import (
    RelationshipCreate,
    RelationshipResponse,
)

router = APIRouter()


@router.post(
    "/",
    response_model=RelationshipResponse,
)
async def create_relationship(
    relationship: RelationshipCreate,
    db: Session = Depends(get_db),
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
):
    return RelationshipRepository.get_all(db)