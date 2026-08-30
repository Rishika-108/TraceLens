from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.agents.investigator import investigate as run_investigation
from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.case_repository import CaseRepository
from app.schemas.investigation import InvestigationRequest, InvestigationResponse

router = APIRouter()


@router.post(
    "/",
    response_model=InvestigationResponse,
    summary="Natural language AI-assisted case investigation with grounded citations",
)
async def investigate_case(
    request: InvestigationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = CaseRepository.get_by_id(db, request.case_id)
    if not case:
        raise HTTPException(
            status_code=404,
            detail=f"Case with ID '{request.case_id}' not found.",
        )

    result = run_investigation(
        db=db,
        case_id=request.case_id,
        question=request.question,
        limit=request.limit,
    )
    return result