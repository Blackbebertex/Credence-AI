from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PolicyOutcome(str, Enum):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    MIXED = "mixed"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    OUT_OF_SCOPE = "out_of_scope"


class RiskTier(str, Enum):
    R1 = "R1"  # Routine advisory
    R2 = "R2"  # Elevated review (mandatory rationale)
    R3 = "R3"  # Critical disposition (mandatory supervisor sign-off)


@dataclass(frozen=True)
class PolicyDecision:
    rule_id: str
    outcome: str
    rationale: str
    rule_version: str

    def __post_init__(self) -> None:
        if self.outcome not in {item.value for item in PolicyOutcome}:
            raise ValueError("outcome must be a valid policy state")
        if not self.rationale.strip():
            raise ValueError("rationale is required")


@dataclass(frozen=True)
class PolicyResult:
    outcome: PolicyOutcome
    summary: str
    rule_version: str


@dataclass(frozen=True)
class ReviewRouting:
    risk_tier: RiskTier
    requires_supervisor: bool
    requires_recorded_rationale: bool
    routing_reason: str


class PolicyEngine:
    def evaluate(self, claim: str, *, evidence_strength: float) -> PolicyResult:
        if evidence_strength >= 0.8:
            outcome = PolicyOutcome.SUPPORTED
        elif evidence_strength <= 0.2:
            outcome = PolicyOutcome.INSUFFICIENT_EVIDENCE
        else:
            outcome = PolicyOutcome.MIXED

        summary = (
            f"Rule {outcome.value}: {claim.strip()}. "
            "Decision support. Not a finding of fact."
        )
        return PolicyResult(outcome=outcome, summary=summary, rule_version="v1")

    @staticmethod
    def determine_risk_tier(
        outcome: PolicyOutcome,
        *,
        is_high_impact: bool = False,
        is_contested: bool = False,
    ) -> ReviewRouting:
        if is_high_impact:
            return ReviewRouting(
                risk_tier=RiskTier.R3,
                requires_supervisor=True,
                requires_recorded_rationale=True,
                routing_reason="High-impact matter requires critical supervisor approval (R3).",
            )
        if outcome in {PolicyOutcome.MIXED, PolicyOutcome.INSUFFICIENT_EVIDENCE} or is_contested:
            return ReviewRouting(
                risk_tier=RiskTier.R2,
                requires_supervisor=False,
                requires_recorded_rationale=True,
                routing_reason="Mixed/insufficient evidence or contested matter requires elevated review with recorded rationale (R2).",
            )
        return ReviewRouting(
            risk_tier=RiskTier.R1,
            requires_supervisor=False,
            requires_recorded_rationale=False,
            routing_reason="Routine finding processed under standard advisory workflow (R1).",
        )

    @staticmethod
    def validate_disposition(
        routing: ReviewRouting,
        *,
        rationale: str | None,
        is_supervisor_authorized: bool,
    ) -> bool:
        if routing.requires_recorded_rationale and (not rationale or not rationale.strip()):
            raise ValueError("Rationale is mandatory for elevated cases (R2/R3)")
        if routing.requires_supervisor and not is_supervisor_authorized:
            raise PermissionError("Supervisor authorization is mandatory for critical cases (R3)")
        return True
