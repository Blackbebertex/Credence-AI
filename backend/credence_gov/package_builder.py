from __future__ import annotations

import datetime
import hashlib
import io
import json
import posixpath
import zipfile
from dataclasses import dataclass
from typing import Any, Sequence

from .crypto_signer import Ed25519Signer


@dataclass(frozen=True)
class PackageDossier:
    case_id: str
    zip_bytes: bytes
    manifest_dict: dict[str, Any]
    signature_hex: str
    manifest_sha256: str


class EvidencePackageBuilder:
    ADVISORY_BANNER = "Decision support. Not a finding of fact."

    @staticmethod
    def _safe_artifact_name(name: str) -> str:
        if not name or "\\" in name or "\x00" in name:
            raise ValueError("Artifact name must be a safe relative ZIP path")
        if ".." in name.split("/"):
            raise ValueError("Artifact name must be a safe relative ZIP path")
        normalized = posixpath.normpath(name)
        if normalized in {".", ".."} or normalized.startswith("../") or normalized.startswith("/"):
            raise ValueError("Artifact name must be a safe relative ZIP path")
        return normalized

    @classmethod
    def build_package(
        cls,
        *,
        case_id: str,
        case_title: str,
        classification: str,
        evidence_state: str,
        summary: str,
        artifacts: Sequence[dict[str, Any]],  # list of {name, bytes, sha256}
        audit_events: Sequence[dict[str, Any]],
        private_key_bytes: bytes,
    ) -> PackageDossier:
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Hash payload bytes ourselves. Caller-provided digests are assertions,
        # not trusted input; reject disagreement before signing anything.
        artifact_entries = []
        artifact_names: set[str] = set()
        for art in artifacts:
            name = cls._safe_artifact_name(str(art["name"]))
            if name in artifact_names:
                raise ValueError(f"Duplicate artifact name: {name}")
            artifact_names.add(name)
            data = bytes(art["bytes"])
            digest = hashlib.sha256(data).hexdigest()
            if art.get("sha256", "").lower() != digest:
                raise ValueError(f"Artifact digest mismatch for {name}")
            artifact_entries.append({"name": name, "sha256": digest, "bytes": data})

        audit_bytes = json.dumps(list(audit_events), indent=2, sort_keys=True).encode("utf-8")
        findings_bytes = json.dumps(
            {
                "case_id": case_id,
                "evidence_state": evidence_state,
                "summary": summary,
                "banner": cls.ADVISORY_BANNER,
            },
            indent=2,
            sort_keys=True,
        ).encode("utf-8")
        manifest_payload = {
            "case_id": case_id,
            "case_title": case_title,
            "classification": classification,
            "evidence_state": evidence_state,
            "summary": summary,
            "banner": cls.ADVISORY_BANNER,
            "generated_at": timestamp,
            "artifacts": [
                {"name": art["name"], "sha256": art["sha256"]} for art in artifact_entries
            ],
            "files": {
                "audit_trail.json": hashlib.sha256(audit_bytes).hexdigest(),
                "findings.json": hashlib.sha256(findings_bytes).hexdigest(),
            },
            "audit_event_count": len(audit_events),
        }
        manifest_bytes = json.dumps(manifest_payload, sort_keys=True).encode("utf-8")
        manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()

        # Sign manifest
        signature = Ed25519Signer.sign_bytes(private_key_bytes, manifest_bytes)
        signature_hex = signature.hex()

        # Assemble ZIP dossier
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", manifest_bytes)
            zf.writestr("manifest.sig", signature)
            zf.writestr("audit_trail.json", audit_bytes)
            zf.writestr("findings.json", findings_bytes)
            for art in artifact_entries:
                zf.writestr(f"artifacts/{art['name']}", art["bytes"])

        zip_bytes = zip_buffer.getvalue()
        return PackageDossier(
            case_id=case_id,
            zip_bytes=zip_bytes,
            manifest_dict=manifest_payload,
            signature_hex=signature_hex,
            manifest_sha256=manifest_sha256,
        )
