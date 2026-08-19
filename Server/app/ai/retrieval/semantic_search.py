from sqlalchemy.orm import Session

from app.ai.embeddings.generator import (
    create_embedding,
)
from app.ai.retrieval.vector_store import (
    similarity_search,
)


def search(
    db: Session,
    query: str,
):

    embedding = create_embedding(
        query
    )

    return similarity_search(
        db,
        embedding,
    )