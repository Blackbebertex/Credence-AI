from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence


class Plane(str, Enum):
    CONTROL = "control"
    EVIDENCE = "evidence"
    REVIEW = "review"
    INTELLIGENCE = "intelligence"


@dataclass(frozen=True)
class ModuleBoundary:
    module_name: str
    plane: Plane
    may_write_decisions: bool = False
    may_write_artifacts: bool = False

    @property
    def is_control_plane(self) -> bool:
        return self.plane == Plane.CONTROL

    @property
    def can_write_decisions(self) -> bool:
        return self.may_write_decisions

    @property
    def can_write_artifacts(self) -> bool:
        return self.may_write_artifacts


@dataclass(frozen=True)
class ArchitecturePlan:
    name: str
    planes: Sequence[Plane] = field(default_factory=lambda: [
        Plane.CONTROL,
        Plane.EVIDENCE,
        Plane.REVIEW,
        Plane.INTELLIGENCE,
    ])

    def plane_names(self) -> set[str]:
        return {plane.value for plane in self.planes}

    def has_plane(self, plane: Plane) -> bool:
        return plane in self.planes
