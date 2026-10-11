from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CaseCreateRequest:
    tenant_id: str
    owner_id: str
    classification: str
    title: str
    purpose: str
    as_of_date: str

    def __post_init__(self) -> None:
        if not self.tenant_id.strip():
            raise ValueError("tenant_id is required")
        if not self.owner_id.strip():
            raise ValueError("owner_id is required")
        if not self.classification.strip():
            raise ValueError("classification is required")
        if not self.title.strip():
            raise ValueError("title is required")
        if not self.purpose.strip():
            raise ValueError("purpose is required")
        if not self.as_of_date.strip():
            raise ValueError("as_of_date is required")


class CaseAPI:
    def __init__(self) -> None:
        self._cases: list[dict[str, str]] = []

    def create_case(self, request: CaseCreateRequest) -> dict[str, str | int]:
        case_id = f"case-{len(self._cases) + 1:04d}"
        payload = {
            "id": case_id,
            "tenant_id": request.tenant_id,
            "owner_id": request.owner_id,
            "classification": request.classification,
            "title": request.title.strip(),
            "purpose": request.purpose.strip(),
            "as_of_date": request.as_of_date,
            "schema_version": 1,
            "banner": "Decision support. Not a finding of fact.",
        }
        self._cases.append(payload)
        return payload
