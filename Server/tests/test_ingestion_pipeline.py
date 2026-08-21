import os
import tempfile
from app.parsers.whatsapp_parser import WhatsAppParser
from app.parsers.call_parser import CallParser
from app.parsers.sms_parser import SMSParser
from app.parsers.email_parser import EmailParser
from app.parsers.document_parser import DocumentParser
from app.pipelines.ingestion import detect_parser, ingest


def test_detect_parser_by_extension_and_content():
    # WhatsApp Sniffing
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as f:
        f.write("15/08/2023, 10:15 - Officer: Beginning search operation.\n")
        wa_path = f.name

    # Document Plain Text
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as f:
        f.write("Standard investigation document report overview.\n")
        doc_path = f.name

    # Call CSV
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".csv", delete=False) as f:
        f.write("caller,receiver,duration,timestamp\n111,222,60,2023-01-01\n")
        call_path = f.name

    # SMS CSV
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".csv", delete=False) as f:
        f.write("sender,recipient,message,timestamp\n111,222,hello,2023-01-01\n")
        sms_path = f.name

    try:
        assert isinstance(detect_parser(wa_path), WhatsAppParser)
        assert isinstance(detect_parser(doc_path), DocumentParser)
        assert isinstance(detect_parser(call_path), CallParser)
        assert isinstance(detect_parser(sms_path), SMSParser)
    finally:
        for p in [wa_path, doc_path, call_path, sms_path]:
            if os.path.exists(p):
                os.unlink(p)
