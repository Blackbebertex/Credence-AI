from backend.credence_gov.audit import AuditEvent, AuditLedger, EventHashChain


def test_audit_ledger_appends_hash_chained_events() -> None:
    ledger = AuditLedger()

    event1 = ledger.record_event(case_id="case-200", action="created", actor_id="analyst-1", payload={"kind": "case"})
    event2 = ledger.record_event(case_id="case-200", action="artifact_stored", actor_id="analyst-1", payload={"sha256": "abc123"})

    assert event1.previous_hash is None
    assert event2.previous_hash == event1.event_hash
    assert event2.event_hash != event1.event_hash
    assert isinstance(event2, AuditEvent)


def test_hash_chain_rejects_tampering() -> None:
    chain = EventHashChain()
    chain.append("first", payload={"v": 1})
    chain.append("second", payload={"v": 2})

    tampered = list(chain.entries)
    tampered[0] = {"event": "changed", "payload": {"v": 9}}

    assert chain.verify_entries(tampered) is False
