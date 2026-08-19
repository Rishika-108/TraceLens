from datetime import datetime


def build_timeline(
    artifacts: list[dict],
) -> list[dict]:

    events = []

    for artifact in artifacts:

        timestamp = artifact.get(
            "timestamp"
        )

        if not timestamp:
            continue

        events.append(
            {
                "timestamp": timestamp,
                "event_type":
                    artifact["artifact_type"],
                "description":
                    str(
                        artifact["content"]
                    ),
            }
        )

    return sorted(
        events,
        key=lambda event:
            event["timestamp"],
    )