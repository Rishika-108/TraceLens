import os
import re
from pathlib import Path
from typing import Any
from app.parsers.base_parser import BaseParser


class DocumentParser(BaseParser):
    """
    Forensic Document Parser.
    Extracts text and metadata from PDF, Markdown, Plain Text, and structured document files
    with semantic paragraph and sentence boundary preservation.
    """

    def parse(self, file_path: str) -> list[dict[str, Any]]:
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == ".pdf":
            return self._parse_pdf(file_path)
        return self._parse_text(file_path)

    def _parse_pdf(self, file_path: str) -> list[dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []

        try:
            from pypdf import PdfReader

            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            doc_metadata = reader.metadata or {}

            creation_date = doc_metadata.get("/CreationDate", "")
            parsed_ts = self.parse_datetime(str(creation_date).replace("D:", "")[:14] if creation_date else None)

            has_extracted_text = False

            for page_idx, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                if not page_text.strip():
                    continue

                has_extracted_text = True
                artifacts.append(
                    {
                        "artifact_type": "DOCUMENT",
                        "timestamp": parsed_ts,
                        "source": "PDF_DOCUMENT",
                        "content": {
                            "text": page_text.strip(),
                            "page_number": page_idx,
                            "total_pages": total_pages,
                            "title": str(doc_metadata.get("/Title", Path(file_path).name)),
                            "author": str(doc_metadata.get("/Author", "UNKNOWN")),
                        },
                        "raw_data": page_text[:1000],
                        "metadata": {
                            "file_name": Path(file_path).name,
                            "page": page_idx,
                            "creation_date": str(creation_date),
                        },
                    }
                )

            if not has_extracted_text:
                # Scanned or image-based PDF
                artifacts.append({
                    "artifact_type": "DOCUMENT",
                    "timestamp": parsed_ts,
                    "source": "PDF_DOCUMENT",
                    "content": {
                        "text": f"Scanned PDF document '{Path(file_path).name}' ({total_pages} pages) has no selectable text layer.",
                        "page_number": 1,
                        "total_pages": total_pages,
                        "is_scanned_raster": True,
                    },
                    "raw_data": "",
                    "metadata": {
                        "total_pages": total_pages,
                        "is_scanned": True,
                    },
                })

        except ImportError:
            with open(file_path, "rb") as f:
                content = f.read().decode("latin1", errors="ignore")
            artifacts.append({
                "artifact_type": "DOCUMENT",
                "timestamp": None,
                "source": "PDF_FALLBACK",
                "content": {
                    "text": content[:5000],
                    "note": "pypdf not available, raw text extracted",
                },
                "raw_data": content[:1000],
                "metadata": {"file_name": Path(file_path).name},
            })
        except Exception as e:
            raise ValueError(f"Failed to parse PDF document: {str(e)}")

        return artifacts

    def _parse_text(self, file_path: str) -> list[dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []

        # Auto-detect encoding
        encoding = "utf-8"
        try:
            with open(file_path, "rb") as bf:
                header = bf.read(4)
                if header.startswith(b"\xff\xfe"):
                    encoding = "utf-16-le"
                elif header.startswith(b"\xfe\xff"):
                    encoding = "utf-16-be"
                elif header.startswith(b"\xef\xbb\xbf"):
                    encoding = "utf-8-sig"
        except Exception:
            pass

        with open(file_path, "r", encoding=encoding, errors="replace") as file:
            full_text = file.read()

        # Split into semantic paragraphs
        raw_paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]

        if not raw_paragraphs:
            return [{
                "artifact_type": "DOCUMENT",
                "timestamp": None,
                "source": "TEXT_DOCUMENT",
                "content": {"text": ""},
                "raw_data": "",
                "metadata": {"file_name": Path(file_path).name},
            }]

        # Group paragraphs semantically into coherent chunks of ~1500 chars
        current_chunk: list[str] = []
        current_len = 0
        chunk_idx = 1

        for para in raw_paragraphs:
            # If paragraph is very long, split by sentences rather than slicing mid-word
            if len(para) > 2000:
                sentences = re.split(r"(?<=[.?!])\s+", para)
                for sent in sentences:
                    current_chunk.append(sent)
                    current_len += len(sent)
                    if current_len >= 1500:
                        chunk_text = " ".join(current_chunk)
                        artifacts.append(self._build_chunk_artifact(file_path, chunk_text, chunk_idx))
                        current_chunk = []
                        current_len = 0
                        chunk_idx += 1
            else:
                current_chunk.append(para)
                current_len += len(para)
                if current_len >= 1500:
                    chunk_text = "\n\n".join(current_chunk)
                    artifacts.append(self._build_chunk_artifact(file_path, chunk_text, chunk_idx))
                    current_chunk = []
                    current_len = 0
                    chunk_idx += 1

        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            artifacts.append(self._build_chunk_artifact(file_path, chunk_text, chunk_idx))

        return artifacts

    def _build_chunk_artifact(self, file_path: str, chunk_text: str, chunk_idx: int) -> dict[str, Any]:
        return {
            "artifact_type": "DOCUMENT",
            "timestamp": None,
            "source": "TEXT_DOCUMENT",
            "content": {
                "text": chunk_text,
                "section": chunk_idx,
            },
            "raw_data": chunk_text[:1000],
            "metadata": {
                "file_name": Path(file_path).name,
                "section": chunk_idx,
            },
        }