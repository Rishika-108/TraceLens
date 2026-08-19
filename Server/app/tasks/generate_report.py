from app.pipelines.relationship_discovery import (
    discover_relationships,
)
from app.pipelines.reporting import (
    generate_report,
)
from app.tasks.celery_app import celery


@celery.task
def generate_report_task(
    timeline: list[dict],
    entities: list[dict],
):

    relationships = discover_relationships(
        entities
    )

    return generate_report(
        timeline,
        entities,
        relationships,
    )