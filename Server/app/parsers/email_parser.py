import json

from app.parsers.base_parser import BaseParser


class EmailParser(BaseParser):

    def parse(
        self,
        file_path: str,
    ) -> list[dict]:

        with open(
            file_path,
            encoding="utf-8",
        ) as file:

            emails = json.load(file)

        artifacts = []

        for email in emails:

            artifacts.append(
                {
                    "artifact_type": "EMAIL",
                    "timestamp": email["timestamp"],
                    "source": "EMAIL",
                    "content": {
                        "sender": email["from"],
                        "recipient": email["to"],
                        "subject": email["subject"],
                        "body": email["body"],
                    },
                }
            )

        return artifacts