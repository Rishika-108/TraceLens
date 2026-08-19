from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.report_repository import (
    ReportRepository,
)
from app.schemas.report import (
    ReportCreate,
    ReportResponse,
)

router = APIRouter()


@router.post(
    "/",
    response_model=ReportResponse,
)
async def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db),
):
    return ReportRepository.create(
        db,
        report,
    )


@router.get(
    "/case/{case_id}",
    response_model=list[ReportResponse],
)
async def get_reports(
    case_id: str,
    db: Session = Depends(get_db),
):
    return ReportRepository.get_by_case(
        db,
        case_id,
    )