from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CaseRecord:
    id: str
    tenant_id: str
    owner_id: str
    classification: str
    title: str


@dataclass(frozen=True)
class EvidencePackage:
    case_id: str
    case_title: str
    evidence_state: str
    banner: str
    summary: str


class CaseService:
    def __init__(self) -> None:
        self._cases: dict[str, CaseRecord] = {}

    @staticmethod
    def _sanitize_claim(claim: str) -> str:
        sanitized = claim.strip()
        verdict_words = {
            "authentic": "synthetic assertion",
            "real": "synthetic assertion",
            "fake": "synthetic assertion",
            "genuine": "synthetic assertion",
            "verified": "synthetic assertion",
            "trustworthy": "synthetic assertion",
        }
        lowered = sanitized.lower()
        for word, replacement in verdict_words.items():
            lowered = lowered.replace(word, replacement)
        return lowered.title() if lowered else "Synthetic claim text"

    def create_case(
        self,
        *,
        tenant_id: str,
        owner_id: str,
        classification: str,
        title: str,
    ) -> CaseRecord:
        case_id = f"case-{len(self._cases) + 1:04d}"
        case = CaseRecord(
            id=case_id,
            tenant_id=tenant_id,
            owner_id=owner_id,
            classification=classification,
            title=title,
        )
        self._cases[case_id] = case
        return case

    def build_evidence_package(
        self,
        *,
        case_id: str,
        case_title: str,
        claim: str,
        evidence_state: str,
        caveat: str,
    ) -> EvidencePackage:
        safe_claim = self._sanitize_claim(claim)
        summary = (
            f"Case {case_id}: {case_title}. "
            f"Claim reviewed: {safe_claim}. "
            f"Evidence state: {evidence_state}. "
            f"Caveat: {caveat.strip()}. "
            "Decision support. Not a finding of fact."
        )
        return EvidencePackage(
            case_id=case_id,
            case_title=case_title,
            evidence_state=evidence_state,
            banner="Decision support. Not a finding of fact.",
            summary=summary,
        )
