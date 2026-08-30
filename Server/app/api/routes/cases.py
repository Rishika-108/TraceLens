from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.case_repository import CaseRepository
from app.schemas.case import CaseCreate, CaseResponse

router = APIRouter()


@router.post(
    "/",
    response_model=CaseResponse,
)
async def create_case(
    case: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CaseRepository.create(
        db,
        case,
    )


@router.get(
    "/",
    response_model=list[CaseResponse],
)
async def get_cases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CaseRepository.get_all(db)


@router.get(
    "/{case_id}",
    response_model=CaseResponse,
)
async def get_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = CaseRepository.get_by_id(
        db,
        case_id,
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    return case


@router.delete("/{case_id}")
async def delete_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = CaseRepository.delete(
        db,
        case_id,
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    return {
        "message": "Case deleted"
    }