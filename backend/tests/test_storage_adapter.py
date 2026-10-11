import pytest

from backend.credence_gov.storage_adapter import (
    LocalStorageAdapter,
    StorageAdapter,
    StorageMetadata,
)


def test_local_storage_adapter_implements_protocol() -> None:
    adapter = LocalStorageAdapter()
    assert isinstance(adapter, StorageAdapter)


def test_put_and_get_object_with_immutability() -> None:
    adapter = LocalStorageAdapter()
    data = b"Government Evidence Payload 123"

    meta = adapter.put_object(
        bucket="evidence",
        key="cases/case-001/doc.pdf",
        data=data,
        mime_type="application/pdf",
        object_lock=True,
    )

    assert meta.bucket == "evidence"
    assert meta.key == "cases/case-001/doc.pdf"
    assert meta.size_bytes == len(data)
    assert meta.is_immutable is True
    assert meta.object_lock_mode == "COMPLIANCE"
    assert len(meta.sha256) == 64

    retrieved = adapter.get_object(bucket="evidence", key="cases/case-001/doc.pdf")
    assert retrieved == data

    # Proves immutable overwrite protection
    with pytest.raises(PermissionError, match="immutable"):
        adapter.put_object(
            bucket="evidence",
            key="cases/case-001/doc.pdf",
            data=b"Tampered payload",
            mime_type="application/pdf",
            object_lock=True,
        )


def test_verify_object_integrity() -> None:
    adapter = LocalStorageAdapter()
    data = b"Authentic Circular Bytes"
    meta = adapter.put_object(
        bucket="evidence",
        key="circular.pdf",
        data=data,
        mime_type="application/pdf",
    )

    assert adapter.verify_object_integrity(
        bucket="evidence",
        key="circular.pdf",
        expected_sha256=meta.sha256,
    ) is True

    assert adapter.verify_object_integrity(
        bucket="evidence",
        key="circular.pdf",
        expected_sha256="0000000000000000000000000000000000000000000000000000000000000000",
    ) is False

    assert adapter.verify_object_integrity(
        bucket="evidence",
        key="non_existent.pdf",
        expected_sha256=meta.sha256,
    ) is False


def test_reject_empty_bytes() -> None:
    adapter = LocalStorageAdapter()
    with pytest.raises(ValueError, match="empty data"):
        adapter.put_object(
            bucket="evidence",
            key="empty.txt",
            data=b"",
            mime_type="text/plain",
        )
