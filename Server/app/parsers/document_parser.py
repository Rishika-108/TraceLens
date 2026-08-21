import os
from pathlib import Path
from typing import Any
from app.parsers.base_parser import BaseParser


class DocumentParser(BaseParser):
    """
    Forensic Document Parser.
    Extracts text and metadata from PDF, Markdown, Plain Text, and structured document files.
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

            for page_idx, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                if not page_text.strip():
                    continue

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

            if not artifacts:
                # If all pages were empty or image-based
                artifacts.append({
                    "artifact_type": "DOCUMENT",
                    "timestamp": parsed_ts,
                    "source": "PDF_DOCUMENT",
                    "content": {
                        "text": f"PDF document {Path(file_path).name} contains {total_pages} pages (no raw text extracted).",
                        "page_number": 1,
                        "total_pages": total_pages,
                    },
                    "raw_data": "",
                    "metadata": {"total_pages": total_pages},
                })

        except ImportError:
            # Fallback if pypdf is not yet installed in runtime
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

        with open(file_path, "r", encoding="utf-8", errors="replace") as file:
            full_text = file.read()

        # Split into logical sections if large (>2000 chars)
        paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]

        if not paragraphs:
            return [{
                "artifact_type": "DOCUMENT",
                "timestamp": None,
                "source": "TEXT_DOCUMENT",
                "content": {"text": ""},
                "raw_data": "",
                "metadata": {"file_name": Path(file_path).name},
            }]

        # Group short paragraphs into chunks of ~1500 chars
        current_chunk = []
        current_len = 0
        chunk_idx = 1

        for para in paragraphs:
            current_chunk.append(para)
            current_len += len(para)

            if current_len >= 1500:
                chunk_text = "\n\n".join(current_chunk)
                artifacts.append({
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
                })
                current_chunk = []
                current_len = 0
                chunk_idx += 1

        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            artifacts.append({
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
            })

        return artifacts