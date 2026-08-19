from sqlalchemy.orm import Session

from app.ai.retrieval.semantic_search import (
    search,
)


def retrieve_context(
    db: Session,
    question: str,
):

    artifacts = search(
        db,
        question,
    )

    return "\n".join(
        str(
            artifact.content
        )
        for artifact in artifacts
    )