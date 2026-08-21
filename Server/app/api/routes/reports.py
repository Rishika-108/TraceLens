from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.ai.agents.report_agent import generate_case_report
from app.db.session import get_db
from app.repositories.case_repository import CaseRepository
from app.repositories.report_repository import ReportRepository
from app.schemas.report import ReportCreate, ReportResponse

router = APIRouter()


@router.post(
    "/generate",
    response_model=ReportResponse,
    summary="Generate an evidence-backed case intelligence report via Report Agent",
)
async def generate_report_endpoint(
    case_id: str = Query(..., description="Target Case ID"),
    title: str | None = Query(None, description="Optional custom report title"),
    db: Session = Depends(get_db),
):
    case = CaseRepository.get_by_id(db, case_id)
    if not case:
        raise HTTPException(
            status_code=404,
            detail=f"Case with ID '{case_id}' not found.",
        )

    report_data = generate_case_report(db, case_id, title)
    created_report = ReportRepository.create(
        db,
        ReportCreate(
            case_id=case_id,
            title=report_data["title"],
            summary=report_data["summary"],
            evidence=report_data["evidence"],
        ),
    )
    return created_report


@router.post(
    "/",
    response_model=ReportResponse,
    summary="Manually save a report record",
)
async def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db),
):
    case = CaseRepository.get_by_id(db, report.case_id)
    if not case:
        raise HTTPException(
            status_code=404,
            detail=f"Case with ID '{report.case_id}' not found.",
        )
    return ReportRepository.create(
        db,
        report,
    )


@router.get(
    "/case/{case_id}",
    response_model=list[ReportResponse],
    summary="Get all reports for a case",
)
async def get_reports(
    case_id: str,
    db: Session = Depends(get_db),
):
    return ReportRepository.get_by_case(
        db,
        case_id,
    )


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get a report by ID",
)
async def get_report(
    report_id: str,
    db: Session = Depends(get_db),
):
    report = ReportRepository.get_by_id(db, report_id)
    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )
    return report