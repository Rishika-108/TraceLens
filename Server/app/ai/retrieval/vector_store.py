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
    Executes a case-isolated semantic vector similarity search against case artifacts.
    Returns list of (Artifact, similarity_score) tuples ordered by relevance descending.
    """
    bind = db.get_bind()
    dialect = bind.dialect.name if bind else "postgresql"

    # PostgreSQL with pgvector extension
    if dialect == "postgresql":
        try:
            # Query Artifacts joined with Evidence strictly scoped to case_id
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
            # Fallback to in-memory cosine similarity if pgvector native op fails
            pass

    # In-memory cosine calculation fallback (for SQLite, testing, or unindexed vectors)
    artifacts = (
        db.query(Artifact)
        .join(Evidence, Artifact.evidence_id == Evidence.id)
        .filter(Evidence.case_id == case_id)
        .all()
    )

    scored: list[tuple[Artifact, float]] = []
    for art in artifacts:
        if art.embedding:
            # Handle list or string vector representation
            emb = art.embedding if isinstance(art.embedding, list) else list(art.embedding)
            score = cosine_similarity(query_embedding, emb)
            scored.append((art, score))
        else:
            # Keyword / substring fallback score
            content_str = str(art.content).lower()
            scored.append((art, 0.5 if len(content_str) > 0 else 0.0))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:limit]