import os
import sqlite3
import tempfile
from datetime import datetime
import pytest

from app.parsers.whatsapp_parser import WhatsAppParser
from app.parsers.call_parser import CallParser
from app.parsers.sms_parser import SMSParser
from app.parsers.email_parser import EmailParser
from app.parsers.browser_parser import BrowserParser
from app.parsers.document_parser import DocumentParser
from app.parsers.image_parser import ImageParser


def test_whatsapp_parser_multiline_and_formats():
    content = """15/08/2023, 10:15 - Messages and calls are end-to-end encrypted.
15/08/2023, 10:16 - Alice: Hey Bob, here is the secret file details.
Remember to keep this strictly confidential.
Do not share with anyone else.
15/08/2023, 10:18 - Bob: Understood. Transferring the payment now.
15/08/2023, 10:20 - Bob: <Media omitted>
"""
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        parser = WhatsAppParser()
        artifacts = parser.parse(temp_path)

        assert len(artifacts) >= 3
        # First is system message
        assert artifacts[0]["content"]["sender"] == "SYSTEM"
        assert artifacts[0]["content"]["is_system"] is True

        # Second is multiline message from Alice
        alice_msg = artifacts[1]
        assert alice_msg["content"]["sender"] == "Alice"
        assert "strictly confidential" in alice_msg["content"]["message"]
        assert "Do not share" in alice_msg["content"]["message"]
        assert alice_msg["timestamp"] is not None

        # Third is Bob's reply
        bob_msg = artifacts[2]
        assert bob_msg["content"]["sender"] == "Bob"
        assert "Transferring the payment" in bob_msg["content"]["message"]

        # Fourth is media attachment
        media_msg = artifacts[3]
        assert media_msg["content"]["is_media"] is True
    finally:
        os.unlink(temp_path)


def test_call_parser_csv_and_json():
    csv_content = """caller,receiver,duration,timestamp,type
+1234567890,+9876543210,125,2023-08-15 14:30:00,incoming
+9876543210,+1122334455,45,2023-08-15 15:00:00,outgoing
+5544332211,+1234567890,0,2023-08-15 16:15:00,missed
"""
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        temp_path = f.name

    try:
        parser = CallParser()
        artifacts = parser.parse(temp_path)

        assert len(artifacts) == 3
        assert artifacts[0]["content"]["caller"] == "+1234567890"
        assert artifacts[0]["content"]["receiver"] == "+9876543210"
        assert artifacts[0]["content"]["duration_seconds"] == 125
        assert artifacts[0]["content"]["call_type"] == "INCOMING"
        assert artifacts[2]["content"]["call_type"] == "MISSED"
    finally:
        os.unlink(temp_path)


def test_sms_parser_csv():
    csv_content = """sender,recipient,message,timestamp,direction
+14155552671,+14155559999,Meeting at the warehouse at 9 PM,2023-08-15 19:45:00,incoming
+14155559999,+14155552671,Confirmed. I have the package.,2023-08-15 19:48:00,outgoing
"""
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        temp_path = f.name

    try:
        parser = SMSParser()
        artifacts = parser.parse(temp_path)

        assert len(artifacts) == 2
        assert artifacts[0]["content"]["sender"] == "+14155552671"
        assert artifacts[0]["content"]["direction"] == "INCOMING"
        assert "warehouse" in artifacts[0]["content"]["message"]
        assert artifacts[1]["content"]["direction"] == "OUTGOING"
    finally:
        os.unlink(temp_path)


def test_email_parser_eml():
    eml_content = b"""From: suspect@darknet.org
To: accomplice@protonmail.com
Cc: boss@classified.io
Subject: Updated Account Numbers
Date: Tue, 15 Aug 2023 20:30:00 +0000
Message-ID: <msg12345@darknet.org>
MIME-Version: 1.0
Content-Type: text/plain; charset="utf-8"

Please wire the remaining funds to Account #99281-CH at Zurich Bank.
"""
    with tempfile.NamedTemporaryFile("wb", suffix=".eml", delete=False) as f:
        f.write(eml_content)
        temp_path = f.name

    try:
        parser = EmailParser()
        artifacts = parser.parse(temp_path)

        assert len(artifacts) == 1
        art = artifacts[0]
        assert art["content"]["sender"] == "suspect@darknet.org"
        assert art["content"]["recipient"] == "accomplice@protonmail.com"
        assert art["content"]["subject"] == "Updated Account Numbers"
        assert "Zurich Bank" in art["content"]["body"]
        assert art["timestamp"] is not None
    finally:
        os.unlink(temp_path)


def test_browser_parser_sqlite():
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        temp_db_path = f.name

    try:
        conn = sqlite3.connect(temp_db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE urls (
                id INTEGER PRIMARY KEY,
                url TEXT,
                title TEXT,
                visit_count INTEGER,
                typed_count INTEGER,
                last_visit_time INTEGER
            )
        """)
        cur.execute("""
            CREATE TABLE visits (
                id INTEGER PRIMARY KEY,
                url INTEGER,
                visit_time INTEGER,
                from_visit INTEGER,
                transition INTEGER
            )
        """)
        # 13336588800000000 microseconds since 1601-01-01 corresponds to approx Aug 2023
        cur.execute("""
            INSERT INTO urls (id, url, title, visit_count, typed_count, last_visit_time)
            VALUES (1, 'https://swissbank.ch/login', 'Swiss Bank Portal', 12, 5, 13336588800000000)
        """)
        cur.execute("""
            INSERT INTO visits (id, url, visit_time, from_visit, transition)
            VALUES (1, 1, 13336588800000000, 0, 0)
        """)
        conn.commit()
        conn.close()

        parser = BrowserParser()
        artifacts = parser.parse(temp_db_path)

        assert len(artifacts) >= 1
        assert artifacts[0]["content"]["url"] == "https://swissbank.ch/login"
        assert artifacts[0]["content"]["title"] == "Swiss Bank Portal"
        assert artifacts[0]["source"] == "CHROME_SQLITE"
    finally:
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


def test_document_parser_text():
    text_content = """# Investigation Case Notes

Suspect observed entering building at 18:00 hours.
Vehicle license plate identified as MH-02-CD-4421.

Contact made with secondary person of interest at 18:30.
"""
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as f:
        f.write(text_content)
        temp_path = f.name

    try:
        parser = DocumentParser()
        artifacts = parser.parse(temp_path)

        assert len(artifacts) >= 1
        assert "MH-02-CD-4421" in artifacts[0]["content"]["text"]
    finally:
        os.unlink(temp_path)
