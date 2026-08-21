import hashlib
import os
import tempfile
import pytest

from app.services.storage_service import StorageService


def test_storage_service_save_bytes_and_hash():
    test_data = b"Digital Forensic Evidence Sample Data"
    expected_hash = hashlib.sha256(test_data).hexdigest()

    case_id = "test-case-123"
    filename = "suspicious_log.txt"
    evidence_id = "ev-001"

    meta = StorageService.save_bytes(
        case_id=case_id,
        filename=filename,
        content=test_data,
        evidence_id=evidence_id,
    )

    try:
        assert meta["file_hash"] == expected_hash
        assert meta["file_size"] == len(test_data)
        assert os.path.exists(meta["file_path"])
        assert StorageService.verify_integrity(meta["file_path"], expected_hash) is True
    finally:
        StorageService.delete_file(meta["file_path"])


def test_storage_service_sanitize_filename():
    unsafe = "../../../etc/passwd"
    safe = StorageService.sanitize_filename(unsafe)
    assert ".." not in safe
    assert "/" not in safe
    assert "\\" not in safe
    assert "passwd" in safe
