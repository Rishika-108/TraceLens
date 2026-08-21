import hashlib
import os
import re
from pathlib import Path
from typing import BinaryIO
from fastapi import UploadFile

from app.core.config import settings


class StorageService:
    """
    Forensic Evidence Storage Service.
    Handles secure, case-isolated storage of raw evidence with SHA-256 integrity verification.
    """

    @classmethod
    def get_case_storage_dir(cls, case_id: str) -> Path:
        base_dir = Path(settings.STORAGE_PATH)
        case_dir = base_dir / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        return case_dir

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        # Strip path components and unsafe characters
        clean_name = Path(filename).name
        clean_name = re.sub(r'[^\w\.\-\_ ]', '_', clean_name)
        return clean_name.strip() or "unnamed_evidence.bin"

    @classmethod
    async def save_upload_file(
        cls,
        case_id: str,
        upload_file: UploadFile,
        evidence_id: str,
    ) -> dict:
        case_dir = cls.get_case_storage_dir(case_id)
        safe_filename = cls.sanitize_filename(upload_file.filename or "evidence.bin")
        target_path = case_dir / f"{evidence_id}_{safe_filename}"

        sha256_hash = hashlib.sha256()
        total_size = 0
        chunk_size = 64 * 1024  # 64KB chunks

        with open(target_path, "wb") as destination:
            while chunk := await upload_file.read(chunk_size):
                sha256_hash.update(chunk)
                total_size += len(chunk)
                destination.write(chunk)

        # Reset cursor for subsequent reads if needed
        await upload_file.seek(0)

        return {
            "file_path": str(target_path),
            "file_hash": sha256_hash.hexdigest(),
            "file_size": total_size,
            "filename": safe_filename,
        }

    @classmethod
    def save_bytes(
        cls,
        case_id: str,
        filename: str,
        content: bytes,
        evidence_id: str,
    ) -> dict:
        case_dir = cls.get_case_storage_dir(case_id)
        safe_filename = cls.sanitize_filename(filename)
        target_path = case_dir / f"{evidence_id}_{safe_filename}"

        sha256_hash = hashlib.sha256(content).hexdigest()
        total_size = len(content)

        with open(target_path, "wb") as destination:
            destination.write(content)

        return {
            "file_path": str(target_path),
            "file_hash": sha256_hash,
            "file_size": total_size,
            "filename": safe_filename,
        }

    @classmethod
    def calculate_file_hash(cls, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(64 * 1024):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    @classmethod
    def verify_integrity(cls, file_path: str, expected_hash: str) -> bool:
        if not os.path.exists(file_path):
            return False
        return cls.calculate_file_hash(file_path).lower() == expected_hash.lower()

    @classmethod
    def delete_file(cls, file_path: str) -> bool:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
