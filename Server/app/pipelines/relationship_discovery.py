from itertools import combinations


def discover_relationships(
    entities: list[dict],
) -> list[dict]:

    relationships = []

    for source, target in combinations(
        entities,
        2,
    ):

        if source == target:
            continue

        relationships.append(
            {
                "source": source["value"],
                "target": target["value"],
                "relationship":
                    "CO_OCCURRENCE",
                "confidence": 1.0,
            }
        )

    return relationships