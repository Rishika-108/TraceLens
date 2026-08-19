from app.pipelines.embedding_generation import (
    generate_embeddings,
)
from app.tasks.celery_app import celery


@celery.task
def generate_embeddings_task(
    artifacts: list[dict],
):

    return generate_embeddings(
        artifacts
    )