from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.evidence_repository import (
    EvidenceRepository,
)
from app.schemas.evidence import (
    EvidenceCreate,
    EvidenceResponse,
)

router = APIRouter()


@router.post(
    "/",
    response_model=EvidenceResponse,
)
async def upload_evidence(
    evidence: EvidenceCreate,
    db: Session = Depends(get_db),
):
    return EvidenceRepository.create(
        db,
        evidence,
    )


@router.get(
    "/case/{case_id}",
    response_model=list[EvidenceResponse],
)
async def get_evidence(
    case_id: str,
    db: Session = Depends(get_db),
):
    return EvidenceRepository.get_by_case(
        db,
        case_id,
    )