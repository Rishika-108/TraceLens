import re

from app.parsers.base_parser import BaseParser


PATTERN = re.compile(
    r"(.+?),\s(.+?)\s-\s(.+?):\s(.+)"
)


class WhatsAppParser(BaseParser):

    def parse(
        self,
        file_path: str,
    ) -> list[dict]:

        artifacts = []

        with open(
            file_path,
            encoding="utf-8",
        ) as file:

            for line in file:

                match = PATTERN.match(
                    line.strip()
                )

                if not match:
                    continue

                date, time, sender, message = (
                    match.groups()
                )

                artifacts.append(
                    {
                        "artifact_type":
                            "WHATSAPP_MESSAGE",
                        "timestamp":
                            f"{date} {time}",
                        "source":
                            "WHATSAPP",
                        "content": {
                            "sender": sender,
                            "message": message,
                        },
                    }
                )

        return artifacts