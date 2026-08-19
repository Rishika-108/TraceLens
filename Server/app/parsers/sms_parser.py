import csv

from app.parsers.base_parser import BaseParser


class SMSParser(BaseParser):

    def parse(
        self,
        file_path: str,
    ) -> list[dict]:

        artifacts = []

        with open(
            file_path,
            encoding="utf-8",
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                artifacts.append(
                    {
                        "artifact_type": "SMS",
                        "timestamp": row["timestamp"],
                        "source": "SMS",
                        "content": {
                            "sender": row["sender"],
                            "recipient": row["recipient"],
                            "message": row["message"],
                        },
                    }
                )

        return artifacts