from datetime import datetime


def normalize(
    artifacts: list[dict],
) -> list[dict]:

    normalized = []

    for artifact in artifacts:

        normalized.append(
            {
                "artifact_type":
                    artifact.get(
                        "artifact_type"
                    ),
                "timestamp":
                    artifact.get(
                        "timestamp"
                    ),
                "content":
                    artifact.get(
                        "content",
                        {},
                    ),
                "normalized_at":
                    datetime.utcnow(),
            }
        )

    return normalized