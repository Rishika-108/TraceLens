import re


PHONE_PATTERN = re.compile(
    r"\+?\d[\d\s\-]{8,}"
)

EMAIL_PATTERN = re.compile(
    r"[\w\.-]+@[\w\.-]+\.\w+"
)


def extract_entities(
    artifacts: list[dict],
) -> list[dict]:

    entities = []

    for artifact in artifacts:

        content = str(
            artifact["content"]
        )

        phones = PHONE_PATTERN.findall(
            content
        )

        emails = EMAIL_PATTERN.findall(
            content
        )

        for phone in phones:

            entities.append(
                {
                    "entity_type": "PHONE",
                    "value": phone,
                }
            )

        for email in emails:

            entities.append(
                {
                    "entity_type": "EMAIL",
                    "value": email,
                }
            )

    return entities