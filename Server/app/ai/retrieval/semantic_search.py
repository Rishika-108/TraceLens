from typing import Any
from sqlalchemy.orm import Session

from app.ai.embeddings.generator import create_embedding
from app.ai.retrieval.vector_store import similarity_search


def search(
    db: Session,
    case_id: str,
    query: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Performs case-scoped semantic similarity search for a natural-language investigative query.
    Returns ranked evidence artifacts with relevance scores and source traceability.
    """
    clean_query = str(query).strip()
    if not clean_query:
        return []

    # Step 1: Generate query embedding
    query_embedding = create_embedding(clean_query)

    # Step 2: Vector similarity search scoped to case
    matched_artifacts = similarity_search(
        db=db,
        case_id=case_id,
        query_embedding=query_embedding,
        limit=limit,
    )

    # Step 3: Format results preserving source provenance
    results: list[dict[str, Any]] = []
    for artifact, score in matched_artifacts:
        results.append({
            "artifact_id": artifact.id,
            "evidence_id": artifact.evidence_id,
            "artifact_type": artifact.artifact_type,
            "timestamp": artifact.timestamp.isoformat() if artifact.timestamp else None,
            "content": artifact.content,
            "raw_data": artifact.raw_data,
            "similarity_score": round(score, 4),
            "source": artifact.content.get("source") or artifact.artifact_type,
        })

    return results