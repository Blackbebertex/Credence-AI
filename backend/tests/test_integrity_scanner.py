import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.credence_gov.audit import AuditLedger
from backend.credence_gov.integrity_scanner import IntegrityScanner
from backend.credence_gov.models import Artifact, AuditEventModel, Base, Case, Tenant, User
from backend.credence_gov.storage_adapter import LocalStorageAdapter


@pytest.fixture
def test_env() -> tuple[Session, LocalStorageAdapter]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    storage = LocalStorageAdapter()

    # Seed Tenant, User, Case
    t = Tenant(id="dept-fin", name="Ministry of Finance", classification_tier="SECRET")
    u = User(id="user-fin", tenant_id="dept-fin", username="fin_analyst", role="analyst")
    c = Case(
        id="case-fin-01",
        tenant_id="dept-fin",
        owner_id="user-fin",
        classification="SECRET",
        title="Fiscal Notice Verification",
        purpose="Integrity audit",
        as_of_date="2026-10-01",
    )
    session.add_all([t, u, c])
    session.commit()

    # Store genuine artifact
    data = b"Authentic Fiscal Circular 2026"
    meta = storage.put_object(
        bucket="evidence-dept-fin",
        key="cases/case-fin-01/doc.pdf",
        data=data,
        mime_type="application/pdf",
    )

    art = Artifact(
        id="art-fin-01",
        case_id="case-fin-01",
        tenant_id="dept-fin",
        artifact_type="pdf",
        sha256=meta.sha256,
        mime_type="application/pdf",
        storage_uri="evidence-dept-fin/cases/case-fin-01/doc.pdf",
        is_immutable=True,
    )
    session.add(art)
    session.commit()

    # Add audit events
    AuditLedger.record_event_to_db(
        session,
        case_id="case-fin-01",
        action="case_created",
        actor_id="user-fin",
        payload={"stage": "intake"},
    )
    AuditLedger.record_event_to_db(
        session,
        case_id="case-fin-01",
        action="artifact_stored",
        actor_id="user-fin",
        payload={"sha256": meta.sha256},
    )
    session.commit()

    yield session, storage
    Base.metadata.drop_all(engine)


def test_scanner_confirms_intact_case(test_env: tuple[Session, LocalStorageAdapter]) -> None:
    session, storage = test_env
    report = IntegrityScanner.scan_case(session, storage, "case-fin-01")

    assert report.is_intact is True
    assert report.audit_chain_valid is True
    assert report.artifacts_scanned == 1
    assert len(report.corrupted_artifacts) == 0
    assert report.total_events == 2


def test_scanner_detects_tampered_artifact(test_env: tuple[Session, LocalStorageAdapter]) -> None:
    session, storage = test_env

    # Directly tamper with the stored artifact bytes in storage
    storage._storage[("evidence-dept-fin", "cases/case-fin-01/doc.pdf")] = (
        b"Tampered Bytes In Storage",
        storage._storage[("evidence-dept-fin", "cases/case-fin-01/doc.pdf")][1],
    )

    report = IntegrityScanner.scan_case(session, storage, "case-fin-01")
    assert report.is_intact is False
    assert "art-fin-01" in report.corrupted_artifacts


def test_scanner_detects_tampered_audit_event(test_env: tuple[Session, LocalStorageAdapter]) -> None:
    session, storage = test_env

    # Tamper with audit event payload in DB
    event = session.query(AuditEventModel).filter(AuditEventModel.action == "case_created").one()
    event.payload_json = json.dumps({"tampered": True})
    session.commit()

    report = IntegrityScanner.scan_case(session, storage, "case-fin-01")
    assert report.is_intact is False
    assert report.audit_chain_valid is False
