from backend.credence_gov.storage import ArtifactStore, ArtifactRecord


def test_artifact_store_hashes_and_preserves_originals() -> None:
    store = ArtifactStore()
    record = store.store_artifact(
        case_id="case-0001",
        tenant_id="tenant-100",
        artifact_type="original",
        content=b"SIMULATED: evidence packet",
        mime_type="application/octet-stream",
    )

    assert isinstance(record, ArtifactRecord)
    assert record.sha256
    assert record.sha256 != ""
    assert record.original_is_immutable is True
    assert record.bucket == "evidence"


def test_artifact_store_rejects_empty_payloads() -> None:
    store = ArtifactStore()

    try:
        store.store_artifact(
            case_id="case-0002",
            tenant_id="tenant-100",
            artifact_type="original",
            content=b"",
            mime_type="application/octet-stream",
        )
        raise AssertionError("Expected ValueError")
    except ValueError as exc:
        assert "content" in str(exc).lower()
