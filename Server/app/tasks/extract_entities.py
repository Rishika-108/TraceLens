from app.pipelines.entity_extraction import (
    extract_entities,
)
from app.tasks.celery_app import celery


@celery.task
def extract_entities_task(
    artifacts: list[dict],
):

    return extract_entities(
        artifacts
    )