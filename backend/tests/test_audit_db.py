import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.credence_gov.audit import AuditLedger
from backend.credence_gov.models import AuditEventModel, Base, Case, Tenant, User


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        # Prepopulate Tenant, User, Case
        t = Tenant(id="dept-law", name="Ministry of Law", classification_tier="SECRET")
        u = User(id="user-law", tenant_id="dept-law", username="counsel_sharma", role="supervisor")
        c = Case(
            id="case-9001",
            tenant_id="dept-law",
            owner_id="user-law",
            classification="SECRET",
            title="Legal Notice Evidence",
            purpose="Authenticity validation",
            as_of_date="2026-10-01",
        )
        s.add_all([t, u, c])
        s.commit()
        yield s
    Base.metadata.drop_all(engine)


def test_audit_ledger_records_to_db_and_chains(session: Session) -> None:
    # Record event 1
    ev1 = AuditLedger.record_event_to_db(
        session,
        case_id="case-9001",
        action="case_created",
        actor_id="user-law",
        payload={"stage": "intake"},
    )
    session.commit()

    assert ev1.previous_hash is None
    assert len(ev1.event_hash) == 64

    # Record event 2
    ev2 = AuditLedger.record_event_to_db(
        session,
        case_id="case-9001",
        action="artifact_uploaded",
        actor_id="user-law",
        payload={"sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"},
    )
    session.commit()

    assert ev2.previous_hash == ev1.event_hash
    assert ev2.event_hash != ev1.event_hash

    # Verify chain
    assert AuditLedger.verify_db_chain(session, "case-9001") is True


def test_audit_ledger_detects_db_tampering(session: Session) -> None:
    AuditLedger.record_event_to_db(
        session,
        case_id="case-9001",
        action="event_1",
        actor_id="user-law",
        payload={"data": "original_1"},
    )
    session.commit()

    AuditLedger.record_event_to_db(
        session,
        case_id="case-9001",
        action="event_2",
        actor_id="user-law",
        payload={"data": "original_2"},
    )
    session.commit()

    assert AuditLedger.verify_db_chain(session, "case-9001") is True

    # Tamper with row 1's payload in database directly
    row1 = session.query(AuditEventModel).filter(AuditEventModel.action == "event_1").one()
    row1.payload_json = json.dumps({"data": "tampered_by_malicious_actor"})
    session.commit()

    # Chain verification MUST fail
    assert AuditLedger.verify_db_chain(session, "case-9001") is False
