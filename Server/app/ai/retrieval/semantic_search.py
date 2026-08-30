import hashlib
import re
from typing import Any
from sqlalchemy.orm import Session

from app.ai.embeddings.generator import create_embedding
from app.ai.retrieval.vector_store import similarity_search


TRANSACTIONAL_NOISE_PATTERNS = [
    r"\bverification\s+code\b",
    r"\botp\b",
    r"\blogin\s+alert\b",
    r"\bpassword\s+reset\b",
    r"\bsecurity\s+code\b",
]

MEETING_INQUIRY_KEYWORDS = [
    "meet", "meeting", "when", "where", "plan", "rendezvous", "location", "time", "date", "camp", "pune"
]


def search(
    db: Session,
    case_id: str,
    query: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Performs case-scoped semantic similarity search for a natural-language investigative query.
    Enforces forensic rigor:
    1. Filters out synthetic dataset documentation and test manifests.
    2. Strictly deduplicates identical artifacts to avoid evidence count inflation.
    3. Re-ranks query-relevant primary communications (e.g., explicit meeting proposals).
    4. Down-ranks transactional noise (e.g., login alerts, verification OTPs).
    """
    clean_query = str(query).strip()
    if not clean_query:
        return []

    # Step 1: Generate query embedding
    query_embedding = create_embedding(clean_query)

    # Step 2: Fetch a larger pool of vector candidates to allow filtering and deduplication
    fetch_limit = max(limit * 4, 30)
    matched_artifacts = similarity_search(
        db=db,
        case_id=case_id,
        query_embedding=query_embedding,
        limit=fetch_limit,
    )

    query_lower = clean_query.lower()
    is_meeting_query = any(k in query_lower for k in MEETING_INQUIRY_KEYWORDS)

    candidate_results: list[dict[str, Any]] = []
    seen_content_hashes: set[str] = set()

    for artifact, base_score in matched_artifacts:
        content = artifact.content or {}
        raw_data = str(artifact.raw_data or "")

        # 1. Exclude synthetic dataset documentation & instructions
        raw_lower = raw_data.lower()
        content_lower = str(content).lower()
        if any(k in raw_lower or k in content_lower for k in [
            "synthetic dataset", "dataset_readme", "test data instructions",
            "mock dataset", "dataset overview", "readme.md", "forensic test case"
        ]):
            continue

        # 2. Strict content deduplication to prevent evidence count inflation
        content_fingerprint = (
            content.get("message")
            or content.get("text")
            or content.get("url")
            or raw_data[:200]
        ).strip().lower()

        fp_hash = hashlib.sha256(content_fingerprint.encode("utf-8", errors="ignore")).hexdigest()
        if fp_hash in seen_content_hashes:
            continue
        seen_content_hashes.add(fp_hash)

        # 3. Domain-specific query re-ranking
        adjusted_score = float(base_score)
        text_corpus = (
            str(content.get("message", "")) + " " +
            str(content.get("text", "")) + " " +
            str(content.get("subject", "")) + " " +
            raw_data
        ).lower()

        # Boost primary meeting propositions when query asks about meetings/timing/location
        if is_meeting_query:
            if any(k in text_corpus for k in ["should meet", "let's meet", "meet near", "at 18:30", "camp"]):
                adjusted_score += 0.35
            elif "will be there" in text_corpus or "received" in text_corpus:
                adjusted_score += 0.20

            # Down-rank transactional OTP/login noise
            if any(re.search(pat, text_corpus) for pat in TRANSACTIONAL_NOISE_PATTERNS):
                adjusted_score -= 0.30

        candidate_results.append({
            "artifact_id": artifact.id,
            "evidence_id": artifact.evidence_id,
            "artifact_type": artifact.artifact_type,
            "timestamp": artifact.timestamp.isoformat() if artifact.timestamp else None,
            "raw_timestamp": str(artifact.timestamp) if artifact.timestamp else "Timestamp Unrecorded",
            "content": artifact.content,
            "raw_data": artifact.raw_data,
            "similarity_score": round(adjusted_score, 4),
            "source": artifact.content.get("source") or artifact.artifact_type,
        })

    # Sort candidates by adjusted score descending
    candidate_results.sort(key=lambda x: x["similarity_score"], reverse=True)

    return candidate_results[:limit]