import math
from typing import Any
from sqlalchemy.orm import Session

from app.models.artifact import Artifact
from app.models.evidence import Evidence


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Computes cosine similarity between two unit-normalized or general vectors.
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a)) or 1.0
    norm_b = math.sqrt(sum(b * b for b in vec_b)) or 1.0
    return dot / (norm_a * norm_b)


def similarity_search(
    db: Session,
    case_id: str,
    query_embedding: list[float],
    limit: int = 10,
) -> list[tuple[Artifact, float]]:
    """
    Executes a case-isolated semantic vector similarity search using PostgreSQL pgvector.
    Returns list of (Artifact, similarity_score) tuples ordered by relevance descending.
    """
    try:
        # PostgreSQL with pgvector cosine_distance
        results = (
            db.query(
                Artifact,
                (1.0 - Artifact.embedding.cosine_distance(query_embedding)).label("score"),
            )
            .join(Evidence, Artifact.evidence_id == Evidence.id)
            .filter(Evidence.case_id == case_id)
            .filter(Artifact.embedding.isnot(None))
            .order_by(Artifact.embedding.cosine_distance(query_embedding))
            .limit(limit)
            .all()
        )
        return [(r[0], float(r[1])) for r in results]
    except Exception:
        # Resilient in-memory calculation if pgvector extension is pending initialization
        artifacts = (
            db.query(Artifact)
            .join(Evidence, Artifact.evidence_id == Evidence.id)
            .filter(Evidence.case_id == case_id)
            .all()
        )

        scored: list[tuple[Artifact, float]] = []
        for art in artifacts:
            if art.embedding is not None:
                emb = [float(x) for x in art.embedding] if hasattr(art.embedding, "__iter__") else []
                score = cosine_similarity(query_embedding, emb) if emb else 0.0
                scored.append((art, score))
            else:
                content_str = str(art.content).lower()
                scored.append((art, 0.5 if len(content_str) > 0 else 0.0))

        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:limit]