from typing import Any
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    case_id: str = Field(..., description="Target Case ID")
    query: str = Field(..., description="Natural language search query")
    limit: int = Field(10, ge=1, le=100, description="Max results to return")


class SearchResultItem(BaseModel):
    artifact_id: str
    evidence_id: str
    artifact_type: str
    timestamp: str | None = None
    content: dict[str, Any]
    raw_data: str | None = None
    similarity_score: float
    source: str


class SearchResponse(BaseModel):
    case_id: str
    query: str
    total_results: int
    results: list[SearchResultItem]
