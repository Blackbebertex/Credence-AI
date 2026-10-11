from __future__ import annotations

import datetime
import hashlib
import json
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Sequence


@dataclass(frozen=True)
class BSACertificate:
    certificate_id: str
    case_id: str
    deponent_name: str
    deponent_designation: str
    department: str
    device_system_identifier: str
    hash_algorithm: str
    artifact_hashes: tuple[dict[str, str], ...]
    audit_chain_head_hash: str
    statutory_reference: str
    advisory_notice: str
    affirmation_statement: str
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    def certificate_hash(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


class BSACertificateGenerator:
    STATUTORY_REF = "Bharatiya Sakshya Adhiniyam, 2023, Section 63 (Admissibility of Electronic Records)"
    ADVISORY_NOTICE = "Decision support. Not a finding of fact. Establishes byte continuity since intake only."

    @classmethod
    def generate(
        cls,
        *,
        case_id: str,
        deponent_name: str,
        deponent_designation: str,
        department: str,
        device_identifier: str,
        artifacts: Sequence[dict[str, str]],
        audit_chain_head_hash: str,
    ) -> BSACertificate:
        if not deponent_name.strip():
            raise ValueError("deponent_name is required for statutory certificate")
        if not deponent_designation.strip():
            raise ValueError("deponent_designation is required")
        if not department.strip():
            raise ValueError("department is required")

        affirmation = (
            f"I, {deponent_name}, {deponent_designation}, hereby certify under Section 63 of the "
            f"Bharatiya Sakshya Adhiniyam, 2023, that the computer output and digital records listed "
            f"herein were produced by the secure computer system '{device_identifier}' during its lawful, "
            f"ordinary operation, and the cryptographic hash values accurately represent byte continuity "
            f"without unauthorized alteration since intake."
        )

        return BSACertificate(
            certificate_id=f"bsa-{uuid.uuid4().hex[:12]}",
            case_id=case_id,
            deponent_name=deponent_name.strip(),
            deponent_designation=deponent_designation.strip(),
            department=department.strip(),
            device_system_identifier=device_identifier.strip(),
            hash_algorithm="SHA-256",
            artifact_hashes=tuple(artifacts),
            audit_chain_head_hash=audit_chain_head_hash,
            statutory_reference=cls.STATUTORY_REF,
            advisory_notice=cls.ADVISORY_NOTICE,
            affirmation_statement=affirmation,
            generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )
