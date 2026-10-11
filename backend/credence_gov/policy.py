from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PolicyOutcome(str, Enum):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    MIXED = "mixed"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    OUT_OF_SCOPE = "out_of_scope"


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
