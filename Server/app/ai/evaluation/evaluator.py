def evaluate(
    answer: str,
):

    checks = {
        "contains_evidence":
            "Evidence" in answer,
        "contains_timeline":
            "Timeline" in answer,
    }

    return checks