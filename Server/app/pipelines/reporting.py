def generate_report(
    timeline: list[dict],
    entities: list[dict],
    relationships: list[dict],
):

    return {
        "summary":
            (
                f"{len(timeline)} events, "
                f"{len(entities)} entities, "
                f"{len(relationships)} relationships discovered."
            ),
        "evidence": {
            "timeline": timeline,
            "entities": entities,
            "relationships":
                relationships,
        },
    }