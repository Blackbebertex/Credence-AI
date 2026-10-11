from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class ArtifactRecord:
    case_id: str
    tenant_id: str
    artifact_type: str
    sha256: str
    mime_type: str
    bucket: str
    original_is_immutable: bool = True


class ArtifactStore:
    def store_artifact(
        self,
        *,
        case_id: str,
        tenant_id: str,
        artifact_type: str,
        content: bytes,
        mime_type: str,
    ) -> ArtifactRecord:
        if not content:
            raise ValueError("content is required")

        digest = hashlib.sha256(content).hexdigest()
        return ArtifactRecord(
            case_id=case_id,
            tenant_id=tenant_id,
            artifact_type=artifact_type,
            sha256=digest,
            mime_type=mime_type,
            bucket="evidence",
            original_is_immutable=True,
        )
