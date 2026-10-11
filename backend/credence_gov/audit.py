from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from .models import AuditEventModel


@dataclass(frozen=True)
class AuditEvent:
    case_id: str
    action: str
    actor_id: str
    payload: dict[str, Any]
    previous_hash: str | None
    event_hash: str


class EventHashChain:
    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []

    def append(self, event_name: str, *, payload: dict[str, Any]) -> dict[str, Any]:
        previous_hash = self.entries[-1]["event_hash"] if self.entries else None
        canonical = json.dumps({"event": event_name, "payload": payload, "previous_hash": previous_hash}, sort_keys=True)
        event_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        entry = {"event": event_name, "payload": payload, "previous_hash": previous_hash, "event_hash": event_hash}
        self.entries.append(entry)
        return entry

    def verify_entries(self, entries: list[dict[str, Any]]) -> bool:
        previous_hash = None
        for entry in entries:
            canonical = json.dumps({
                "event": entry.get("event"),
                "payload": entry.get("payload", {}),
                "previous_hash": previous_hash,
            }, sort_keys=True)
            expected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            if entry.get("event_hash") != expected_hash:
                return False
            previous_hash = entry.get("event_hash")
        return True


class AuditLedger:
    def __init__(self) -> None:
        self._chain = EventHashChain()

    def record_event(
        self,
        *,
        case_id: str,
        action: str,
        actor_id: str,
        payload: dict[str, Any],
    ) -> AuditEvent:
        previous_hash = self._chain.entries[-1]["event_hash"] if self._chain.entries else None
        canonical = json.dumps({
            "case_id": case_id,
            "action": action,
            "actor_id": actor_id,
            "payload": payload,
            "previous_hash": previous_hash,
        }, sort_keys=True)
        event_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        event = AuditEvent(
            case_id=case_id,
            action=action,
            actor_id=actor_id,
            payload=payload,
            previous_hash=previous_hash,
            event_hash=event_hash,
        )
        self._chain.entries.append({
            "case_id": case_id,
            "action": action,
            "actor_id": actor_id,
            "payload": payload,
            "previous_hash": previous_hash,
            "event_hash": event_hash,
        })
        return event

    @staticmethod
    def record_event_to_db(
        session: Session,
        *,
        case_id: str,
        action: str,
        actor_id: str,
        payload: dict[str, Any],
    ) -> Any:
        from sqlalchemy import select
        from .models import AuditEventModel

        stmt = (
            select(AuditEventModel)
            .where(AuditEventModel.case_id == case_id)
            .order_by(AuditEventModel.recorded_at.desc(), AuditEventModel.id.desc())
            .limit(1)
        )
        latest_event = session.scalars(stmt).first()
        previous_hash = latest_event.event_hash if latest_event else None

        canonical = json.dumps({
            "case_id": case_id,
            "action": action,
            "actor_id": actor_id,
            "payload": payload,
            "previous_hash": previous_hash,
        }, sort_keys=True)
        event_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        db_event = AuditEventModel(
            id=f"audit-{uuid.uuid4().hex[:12]}",
            case_id=case_id,
            action=action,
            actor_id=actor_id,
            payload_json=json.dumps(payload, sort_keys=True),
            previous_hash=previous_hash,
            event_hash=event_hash,
        )
        session.add(db_event)
        return db_event

    @staticmethod
    def verify_db_chain(session: Session, case_id: str) -> bool:
        from sqlalchemy import select
        from .models import AuditEventModel

        stmt = (
            select(AuditEventModel)
            .where(AuditEventModel.case_id == case_id)
            .order_by(AuditEventModel.recorded_at.asc(), AuditEventModel.id.asc())
        )
        events = session.scalars(stmt).all()
        previous_hash = None

        for event in events:
            payload = json.loads(event.payload_json)
            canonical = json.dumps({
                "case_id": event.case_id,
                "action": event.action,
                "actor_id": event.actor_id,
                "payload": payload,
                "previous_hash": previous_hash,
            }, sort_keys=True)
            expected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            if event.event_hash != expected_hash or event.previous_hash != previous_hash:
                return False
            previous_hash = event.event_hash

        return True
