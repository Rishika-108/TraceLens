from typing import Any
from pydantic import BaseModel, Field


class InvestigationRequest(BaseModel):
    case_id: str = Field(..., description="Target Case ID to investigate")
    question: str = Field(..., min_length=2, description="Investigative query or question")
    limit: int = Field(8, ge=1, le=50, description="Max supporting evidence items to retrieve")


class InvestigationResponse(BaseModel):
    case_id: str
    question: str
    answer: str
    confidence: float
    citations_count: int
    evidence_references: list[dict[str, Any]]
