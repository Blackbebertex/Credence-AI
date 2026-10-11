from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EvidenceState(str, Enum):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    MIXED = "mixed"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    OUT_OF_SCOPE = "out_of_scope"


@dataclass(frozen=True)
class G0Decision:
    pilot_owner: str
    charter_approved: bool
    language_selected: str
    egress_approved: bool
    key_custody_approved: bool
    retention_approved: bool
    register_available: bool
    workload_defined: bool

    @property
    def is_ready(self) -> bool:
        required_values = [
            self.pilot_owner,
            self.charter_approved,
            self.language_selected,
            self.egress_approved,
            self.key_custody_approved,
            self.retention_approved,
            self.register_available,
            self.workload_defined,
        ]

        if not self.pilot_owner.strip():
            return False
        if not self.language_selected.strip():
            return False
        return all(bool(value) for value in required_values[2:])


@dataclass(frozen=True)
class CaseRecord:
    tenant_id: str
    owner_id: str
    classification: str
    title: str

    def __post_init__(self) -> None:
        if not self.tenant_id.strip():
            raise ValueError("tenant_id is required")
        if not self.owner_id.strip():
            raise ValueError("owner_id is required")
        if not self.classification.strip():
            raise ValueError("classification is required")
        if not self.title.strip():
            raise ValueError("title is required")


@dataclass(frozen=True)
class MVPChecklist:
    g0_decision: G0Decision

    def requires_human_review(self, evidence_state: str) -> bool:
        if evidence_state in {"mixed", EvidenceState.MIXED.value}:
            return False
        return True
