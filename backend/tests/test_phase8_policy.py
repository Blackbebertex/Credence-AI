from backend.credence_gov.policy import PolicyDecision, PolicyEngine, PolicyOutcome


def test_policy_engine_classifies_supported_and_insufficient_evidence() -> None:
    engine = PolicyEngine()

    supported = engine.evaluate("Case has clear evidence", evidence_strength=0.9)
    insufficient = engine.evaluate("Case lacks evidence", evidence_strength=0.1)

    assert supported.outcome == PolicyOutcome.SUPPORTED
    assert insufficient.outcome == PolicyOutcome.INSUFFICIENT_EVIDENCE
    assert supported.rule_version == "v1"
    assert "Decision support. Not a finding of fact." in supported.summary


def test_policy_decision_rejects_invalid_state() -> None:
    try:
        PolicyDecision(rule_id="R-99", outcome="fake", rationale="bad", rule_version="v1")
        raise AssertionError("Expected ValueError")
    except ValueError as exc:
        assert "outcome" in str(exc).lower()
