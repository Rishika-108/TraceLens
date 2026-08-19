from sqlalchemy.orm import Session

from app.ai.prompts.investigation_prompt import (
    INVESTIGATION_PROMPT,
)
from app.ai.retrieval.retriever import (
    retrieve_context,
)


def investigate(
    db: Session,
    question: str,
):

    context = retrieve_context(
        db,
        question,
    )

    prompt = (
        INVESTIGATION_PROMPT.format(
            context=context,
            question=question,
        )
    )

    return prompt