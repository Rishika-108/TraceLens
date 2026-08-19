from sqlalchemy.orm import Session

from app.models.artifact import Artifact


def similarity_search(
    db: Session,
    query_embedding,
    limit: int = 10,
):

    return (
        db.query(Artifact)
        .order_by(
            Artifact.embedding.cosine_distance(
                query_embedding
            )
        )
        .limit(limit)
        .all()
    )