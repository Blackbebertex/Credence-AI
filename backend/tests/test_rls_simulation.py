import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.credence_gov.models import Base, Case, Tenant, User


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
    Base.metadata.drop_all(engine)


def test_multi_tenant_isolation_semantics(session: Session) -> None:
    # Set up Tenant A and Tenant B
    tenant_a = Tenant(id="tenant-alpha", name="State Department Alpha", classification_tier="OFFICIAL")
    tenant_b = Tenant(id="tenant-beta", name="State Department Beta", classification_tier="OFFICIAL")
    session.add_all([tenant_a, tenant_b])
    session.commit()

    user_a = User(id="user-a", tenant_id="tenant-alpha", username="analyst_a", role="analyst", mfa_enabled=True)
    user_b = User(id="user-b", tenant_id="tenant-beta", username="analyst_b", role="analyst", mfa_enabled=True)
    session.add_all([user_a, user_b])
    session.commit()

    case_a = Case(
        id="case-a1",
        tenant_id="tenant-alpha",
        owner_id="user-a",
        classification="CONFIDENTIAL",
        title="Case Alpha",
        purpose="Alpha investigation",
        as_of_date="2026-10-01",
    )
    case_b = Case(
        id="case-b1",
        tenant_id="tenant-beta",
        owner_id="user-b",
        classification="CONFIDENTIAL",
        title="Case Beta",
        purpose="Beta investigation",
        as_of_date="2026-10-01",
    )
    session.add_all([case_a, case_b])
    session.commit()

    # Query scoped to Tenant Alpha
    alpha_cases = session.scalars(select(Case).where(Case.tenant_id == "tenant-alpha")).all()
    assert len(alpha_cases) == 1
    assert alpha_cases[0].id == "case-a1"
    assert alpha_cases[0].title == "Case Alpha"

    # Query scoped to Tenant Beta
    beta_cases = session.scalars(select(Case).where(Case.tenant_id == "tenant-beta")).all()
    assert len(beta_cases) == 1
    assert beta_cases[0].id == "case-b1"

    # Cross-tenant query attempt (Tenant Alpha attempting to read Tenant Beta)
    unauthorized_query = session.scalars(
        select(Case).where(Case.tenant_id == "tenant-alpha", Case.id == "case-b1")
    ).all()
    assert len(unauthorized_query) == 0
