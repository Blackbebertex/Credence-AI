from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from .audit import AuditLedger
from .models import Artifact, AuditEventModel
from .storage_adapter import StorageAdapter


@dataclass(frozen=True)
class IntegrityReport:
    case_id: str
    audit_chain_valid: bool
    total_events: int
    artifacts_scanned: int
    corrupted_artifacts: tuple[str, ...]
    is_intact: bool
    scanned_at: str


class IntegrityScanner:
    @staticmethod
    def scan_case(
        session: Session,
        storage: StorageAdapter,
        case_id: str,
    ) -> IntegrityReport:
        # 1. Verify Audit Chain
        audit_valid = AuditLedger.verify_db_chain(session, case_id)

        event_count = len(
            session.scalars(
                select(AuditEventModel).where(AuditEventModel.case_id == case_id)
            ).all()
        )

        # 2. Verify Stored Artifact Digests
        artifacts = session.scalars(
            select(Artifact).where(Artifact.case_id == case_id)
        ).all()

        corrupted: list[str] = []
        for art in artifacts:
            parts = art.storage_uri.split("/", 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else art.id
            is_valid = storage.verify_object_integrity(
                bucket=bucket,
                key=key,
                expected_sha256=art.sha256,
            )
            if not is_valid:
                corrupted.append(art.id)

        is_intact = audit_valid and (len(corrupted) == 0)
        return IntegrityReport(
            case_id=case_id,
            audit_chain_valid=audit_valid,
            total_events=event_count,
            artifacts_scanned=len(artifacts),
            corrupted_artifacts=tuple(corrupted),
            is_intact=is_intact,
            scanned_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )
