import pytest

from backend.credence_gov.policy import PolicyEngine, PolicyOutcome, RiskTier


def test_routine_r1_routing() -> None:
    engine = PolicyEngine()
    routing = engine.determine_risk_tier(PolicyOutcome.SUPPORTED, is_high_impact=False, is_contested=False)

    assert routing.risk_tier == RiskTier.R1
    assert routing.requires_supervisor is False
    assert routing.requires_recorded_rationale is False

    # Disposing R1 succeeds even without rationale
    assert engine.validate_disposition(routing, rationale=None, is_supervisor_authorized=False) is True


def test_elevated_r2_requires_rationale() -> None:
    engine = PolicyEngine()
    routing = engine.determine_risk_tier(PolicyOutcome.MIXED, is_high_impact=False, is_contested=True)

    assert routing.risk_tier == RiskTier.R2
    assert routing.requires_recorded_rationale is True

    # Missing rationale raises ValueError
    with pytest.raises(ValueError, match="Rationale is mandatory"):
        engine.validate_disposition(routing, rationale="", is_supervisor_authorized=False)

    # Providing rationale succeeds
    assert engine.validate_disposition(
        routing,
        rationale="Analyst inspected conflicting gazette versions and reconciled effective dates.",
        is_supervisor_authorized=False,
    ) is True


def test_critical_r3_requires_supervisor() -> None:
    engine = PolicyEngine()
    routing = engine.determine_risk_tier(PolicyOutcome.CONTRADICTED, is_high_impact=True)

    assert routing.risk_tier == RiskTier.R3
    assert routing.requires_supervisor is True
    assert routing.requires_recorded_rationale is True

    # Unauthorized analyst attempting sign-off raises PermissionError
    with pytest.raises(PermissionError, match="Supervisor authorization is mandatory"):
        engine.validate_disposition(
            routing,
            rationale="Analyst summary",
            is_supervisor_authorized=False,
        )

    # Authorized supervisor succeeds
    assert engine.validate_disposition(
        routing,
        rationale="Supervisor reviewed contradictory findings and authorized advisory dispatch.",
        is_supervisor_authorized=True,
    ) is True
