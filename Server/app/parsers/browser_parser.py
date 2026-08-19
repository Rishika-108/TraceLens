import csv

from app.parsers.base_parser import BaseParser


class BrowserParser(BaseParser):

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
                        "artifact_type":
                            "BROWSER_HISTORY",
                        "timestamp":
                            row["timestamp"],
                        "source":
                            "BROWSER",
                        "content": {
                            "url": row["url"],
                            "title": row["title"],
                        },
                    }
                )

        return artifacts