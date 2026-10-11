from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class StorageMetadata:
    sha256: str
    size_bytes: int
    mime_type: str
    bucket: str
    key: str
    is_immutable: bool = True
    object_lock_mode: str = "COMPLIANCE"


@runtime_checkable
class StorageAdapter(Protocol):
    def put_object(
        self,
        *,
        bucket: str,
        key: str,
        data: bytes,
        mime_type: str,
        object_lock: bool = True,
    ) -> StorageMetadata:
        """Store bytes immutably and return verified metadata."""
        ...

    def get_object(self, *, bucket: str, key: str) -> bytes:
        """Retrieve stored bytes."""
        ...

    def verify_object_integrity(
        self,
        *,
        bucket: str,
        key: str,
        expected_sha256: str,
    ) -> bool:
        """Verify whether stored bytes match expected SHA-256 digest."""
        ...

    def object_exists(self, *, bucket: str, key: str) -> bool:
        """Check whether object exists in storage."""
        ...


class LocalStorageAdapter:
    """In-memory and local filesystem storage adapter for synthetic development and testing."""

    def __init__(self) -> None:
        self._storage: dict[tuple[str, str], tuple[bytes, StorageMetadata]] = {}

    def put_object(
        self,
        *,
        bucket: str,
        key: str,
        data: bytes,
        mime_type: str,
        object_lock: bool = True,
    ) -> StorageMetadata:
        if not data:
            raise ValueError("Cannot store empty data bytes")

        target = (bucket, key)
        if target in self._storage:
            metadata = self._storage[target][1]
            if metadata.is_immutable:
                raise PermissionError(f"Cannot overwrite immutable object at {bucket}/{key}")

        digest = hashlib.sha256(data).hexdigest()
        metadata = StorageMetadata(
            sha256=digest,
            size_bytes=len(data),
            mime_type=mime_type,
            bucket=bucket,
            key=key,
            is_immutable=object_lock,
            object_lock_mode="COMPLIANCE" if object_lock else "NONE",
        )
        self._storage[target] = (data, metadata)
        return metadata

    def get_object(self, *, bucket: str, key: str) -> bytes:
        target = (bucket, key)
        if target not in self._storage:
            raise FileNotFoundError(f"Object {bucket}/{key} not found")
        return self._storage[target][0]

    def verify_object_integrity(
        self,
        *,
        bucket: str,
        key: str,
        expected_sha256: str,
    ) -> bool:
        target = (bucket, key)
        if target not in self._storage:
            return False
        data = self._storage[target][0]
        actual_hash = hashlib.sha256(data).hexdigest()
        return actual_hash.lower() == expected_sha256.lower()

    def object_exists(self, *, bucket: str, key: str) -> bool:
        return (bucket, key) in self._storage
