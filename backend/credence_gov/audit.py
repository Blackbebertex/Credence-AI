from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


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
