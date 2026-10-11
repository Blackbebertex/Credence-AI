from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


PRIORITY_ORDER = {
    "MUST HAVE": 1,
    "SHOULD HAVE": 2,
    "COULD HAVE": 3,
    "FUTURE": 4,
    "UNCLEAR": 5,
    "CONFLICTING": 6,
    "NOT IMPLEMENTABLE AS WRITTEN": 7,
}

PHASE_ORDER = {
    "Phase 0": 0,
    "Phase 1": 1,
    "Phase 2": 2,
    "Phase 3": 3,
    "G0": 4,
    "Phase 4+": 5,
}


@dataclass(frozen=True)
class Requirement:
    id: str
    title: str
    priority: str
    phase: str
    owner: str
    traceability: str

    @property
    def normalized_id(self) -> str:
        normalized = self.id.strip().upper()
        return normalized.replace(" ", "")

    @property
    def summary(self) -> str:
        return f"{self.normalized_id} | {self.priority} | {self.phase} | {self.title}"


class RequirementCatalog:
    def __init__(self, requirements: Sequence[Requirement] | Iterable[Requirement]):
        self.requirements = list(requirements)

    @staticmethod
    def priority_rank(priority: str) -> int:
        return PRIORITY_ORDER.get(priority.strip(), len(PRIORITY_ORDER) + 1)

    @staticmethod
    def phase_order(phase: str) -> int:
        return PHASE_ORDER.get(phase.strip(), len(PHASE_ORDER) + 1)

    def order_by_priority_and_phase(self) -> list[Requirement]:
        return sorted(
            self.requirements,
            key=lambda requirement: (
                self.phase_order(requirement.phase),
                self.priority_rank(requirement.priority),
                requirement.normalized_id,
            ),
        )
