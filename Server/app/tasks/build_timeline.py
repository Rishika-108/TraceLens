from app.pipelines.timeline_reconstruction import (
    build_timeline,
)
from app.tasks.celery_app import celery


@celery.task
def build_timeline_task(
    artifacts: list[dict],
):

    return build_timeline(
        artifacts
    )