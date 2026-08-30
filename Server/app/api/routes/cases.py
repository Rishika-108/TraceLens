from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.case import Case
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
    case_dict = case.model_dump()
    new_case = Case(
        title=case_dict["title"],
        description=case_dict.get("description"),
        owner_id=current_user.id,
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case


@router.get(
    "/",
    response_model=list[CaseResponse],
)
async def get_cases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "ADMIN":
        return db.query(Case).order_by(Case.created_at.desc()).all()

    # Isolate cases to the authenticated investigator
    return (
        db.query(Case)
        .filter((Case.owner_id == current_user.id) | (Case.owner_id.is_(None)))
        .order_by(Case.created_at.desc())
        .all()
    )


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

    if current_user.role != "ADMIN" and case.owner_id and case.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: this case belongs to another investigator account.",
        )

    return case


@router.delete("/{case_id}")
async def delete_case(
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

    if current_user.role != "ADMIN" and case.owner_id and case.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: you cannot delete another investigator's case.",
        )

    CaseRepository.delete(
        db,
        case_id,
    )

    return {
        "message": "Case deleted"
    }