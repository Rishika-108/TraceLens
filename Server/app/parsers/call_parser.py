import csv

from app.parsers.base_parser import BaseParser


class CallParser(BaseParser):

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
                        "artifact_type": "CALL",
                        "timestamp": row["timestamp"],
                        "source": "CALL_LOG",
                        "content": {
                            "caller": row["caller"],
                            "receiver": row["receiver"],
                            "duration": row["duration"],
                        },
                    }
                )

        return artifacts