from app.pipelines.ingestion import ingest
from app.pipelines.normalization import normalize
from app.tasks.celery_app import celery


@celery.task
def parse_evidence(
    file_path: str,
):

    artifacts = ingest(file_path)

    normalized_artifacts = normalize(
        artifacts
    )

    return normalized_artifacts