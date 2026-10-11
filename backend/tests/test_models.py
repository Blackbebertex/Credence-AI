import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.credence_gov.models import (
    Artifact,
    AuditEventModel,
    Base,
    Case,
    PolicyDecisionModel,
    ReviewTaskModel,
    Tenant,
    User,
)


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


def test_schema_creation_and_relational_integrity(db_session: Session) -> None:
    # 1. Create Tenant
    tenant = Tenant(id="dept-home", name="Ministry of Home Affairs", classification_tier="SECRET")
    db_session.add(tenant)
    db_session.commit()

    # 2. Create User
    user = User(id="user-01", tenant_id=tenant.id, username="analyst_verma", role="analyst", mfa_enabled=True)
    db_session.add(user)
    db_session.commit()

    # 3. Create Case
    case = Case(
        id="case-1001",
        tenant_id=tenant.id,
        owner_id=user.id,
        classification="SECRET",
        title="Disputed Order Notification",
        purpose="Advisory verification for inter-agency review",
        as_of_date="2026-10-01",
        status="active",
    )
    db_session.add(case)
    db_session.commit()

    # 4. Create Artifact
    artifact = Artifact(
        id="art-01",
        case_id=case.id,
        tenant_id=tenant.id,
        artifact_type="pdf_document",
        sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        mime_type="application/pdf",
        storage_uri="evidence/dept-home/case-1001/doc.pdf",
        is_immutable=True,
    )
    db_session.add(artifact)

    # 5. Create Audit Event
    audit_event = AuditEventModel(
        id="audit-01",
        case_id=case.id,
        action="case_created",
        actor_id=user.id,
        payload_json='{"action": "case_created"}',
        previous_hash=None,
        event_hash="a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90",
    )
    db_session.add(audit_event)

    # 6. Create Policy Decision
    decision = PolicyDecisionModel(
        id="pol-01",
        case_id=case.id,
        rule_id="RULE-01",
        outcome="supported",
        rule_version="v1",
        rationale="Evidence spans strictly match official gazette notification.",
    )
    db_session.add(decision)

    # 7. Create Review Task
    review = ReviewTaskModel(
        id="rev-01",
        case_id=case.id,
        assigned_reviewer_id=user.id,
        status="pending",
        risk_tier="R2",
        reviewer_rationale=None,
    )
    db_session.add(review)
    db_session.commit()

    # Query back and verify relations
    retrieved_case = db_session.scalar(select(Case).where(Case.id == "case-1001"))
    assert retrieved_case is not None
    assert retrieved_case.tenant.name == "Ministry of Home Affairs"
    assert retrieved_case.owner.username == "analyst_verma"
    assert len(retrieved_case.artifacts) == 1
    assert retrieved_case.artifacts[0].sha256 == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert len(retrieved_case.audit_events) == 1
    assert retrieved_case.audit_events[0].action == "case_created"
    assert len(retrieved_case.policy_decisions) == 1
    assert retrieved_case.policy_decisions[0].outcome == "supported"
    assert len(retrieved_case.review_tasks) == 1
    assert retrieved_case.review_tasks[0].risk_tier == "R2"
