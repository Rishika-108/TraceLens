from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.retrieval.semantic_search import search as run_semantic_search
from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.case_repository import CaseRepository
from app.schemas.search import SearchRequest, SearchResponse

router = APIRouter()


@router.post(
    "/",
    response_model=SearchResponse,
    summary="Case-scoped semantic similarity search across digital evidence",
)
async def semantic_search(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = CaseRepository.get_by_id(db, request.case_id)
    if not case:
        raise HTTPException(
            status_code=404,
            detail=f"Case with ID '{request.case_id}' not found.",
        )

    results = run_semantic_search(
        db=db,
        case_id=request.case_id,
        query=request.query,
        limit=request.limit,
    )

    return {
        "case_id": request.case_id,
        "query": request.query,
        "total_results": len(results),
        "results": results,
    }