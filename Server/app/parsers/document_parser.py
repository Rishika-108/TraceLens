from app.parsers.base_parser import BaseParser


class DocumentParser(BaseParser):

    def parse(
        self,
        file_path: str,
    ) -> list[dict]:

        with open(
            file_path,
            encoding="utf-8",
        ) as file:

            text = file.read()

        return [
            {
                "artifact_type": "DOCUMENT",
                "timestamp": None,
                "source": "DOCUMENT",
                "content": {
                    "text": text,
                },
            }
        ]