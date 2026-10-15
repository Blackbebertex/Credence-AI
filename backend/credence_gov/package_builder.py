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
    ADVISORY_BANNER = "Decision support. Not a finding of fact. Supports admissibility under BSA s.63, subject to judicial determination."

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
        artifacts: Sequence[dict[str, Any]],  # list of {name, bytes, sha256, [mime_type]}
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
            sha256_digest = hashlib.sha256(data).hexdigest()
            sha512_digest = hashlib.sha512(data).hexdigest()
            if art.get("sha256", "").lower() != sha256_digest:
                raise ValueError(f"Artifact digest mismatch for {name}")
            artifact_entries.append({
                "name": name,
                "sha256": sha256_digest,
                "sha512": sha512_digest,
                "size_bytes": len(data),
                "mime_type": art.get("mime_type", "application/octet-stream"),
                "bytes": data,
            })

        # Format custody events line by line as custody.jsonl (Section 4 spec)
        custody_lines = [json.dumps(event, sort_keys=True) for event in audit_events]
        custody_jsonl_bytes = ("\n".join(custody_lines) + ("\n" if custody_lines else "")).encode("utf-8")
        audit_bytes = json.dumps(list(audit_events), indent=2, sort_keys=True).encode("utf-8")
        findings_bytes = json.dumps(
            {
                "case_id": case_id,
                "evidence_state": evidence_state,
                "summary": summary,
                "banner": cls.ADVISORY_BANNER,
                "disclaimer": "Trust starts at ingestion. Hashes prove byte continuity since upload only, not pre-ingestion authenticity.",
            },
            indent=2,
            sort_keys=True,
        ).encode("utf-8")

        verify_md_content = f"""# Evidence Package Verification Instructions
Case ID: {case_id}
Generated: {timestamp}

## Independent Verification (No Server Trust Required)
To verify this package offline on an air-gapped machine:
1. Extract this package.
2. Run the open-source verifier:
   ```bash
   python scripts/verifier.py --package evidence_dossier_{case_id}.zip
   ```
3. Checks performed in order:
   - File hashes (SHA-256 and SHA-512) against manifest.json
   - Ed25519 cryptographic signature of manifest.json
   - Sequential integrity and hash continuity of custody.jsonl
   - Separation-of-duties rules
"""
        verify_md_bytes = verify_md_content.encode("utf-8")

        # Custody head hash
        custody_head_hash = audit_events[-1].get("event_hash") if audit_events else hashlib.sha256(b"genesis").hexdigest()

        # Canonical manifest payload (RFC 8785 sorting)
        manifest_payload = {
            "schema_version": "2.0.0",
            "case_id": case_id,
            "case_title": case_title,
            "classification": classification,
            "evidence_state": evidence_state,
            "summary": summary,
            "banner": cls.ADVISORY_BANNER,
            "trust_principle": "Trust starts at ingestion. A hash proves bytes did not change post-upload, not pre-upload authenticity.",
            "generated_at": timestamp,
            "custody_head_hash": custody_head_hash,
            "artifacts": [
                {
                    "name": art["name"],
                    "sha256": art["sha256"],
                    "sha512": art["sha512"],
                    "size_bytes": art["size_bytes"],
                    "mime_type": art["mime_type"],
                }
                for art in artifact_entries
            ],
            "files": {
                "audit_trail.json": hashlib.sha256(audit_bytes).hexdigest(),
                "custody.jsonl": hashlib.sha256(custody_jsonl_bytes).hexdigest(),
                "findings.json": hashlib.sha256(findings_bytes).hexdigest(),
                "VERIFY.md": hashlib.sha256(verify_md_bytes).hexdigest(),
            },
            "audit_event_count": len(audit_events),
        }
        manifest_bytes = json.dumps(manifest_payload, sort_keys=True).encode("utf-8")
        manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()

        # Sign manifest with Ed25519
        signature = Ed25519Signer.sign_bytes(private_key_bytes, manifest_bytes)
        signature_hex = signature.hex()

        # Assemble ZIP dossier (Layout conforming to Section 4)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", manifest_bytes)
            zf.writestr("manifest.sig", signature)
            zf.writestr("custody.jsonl", custody_jsonl_bytes)
            zf.writestr("audit_trail.json", audit_bytes)
            zf.writestr("findings.json", findings_bytes)
            zf.writestr("VERIFY.md", verify_md_bytes)
            for art in artifact_entries:
                # Layout Section 4: evidence/ untouched bytes
                zf.writestr(f"evidence/{art['name']}", art["bytes"])
                # Also include alias in artifacts/ for backwards compatibility
                zf.writestr(f"artifacts/{art['name']}", art["bytes"])

        zip_bytes = zip_buffer.getvalue()
        return PackageDossier(
            case_id=case_id,
            zip_bytes=zip_bytes,
            manifest_dict=manifest_payload,
            signature_hex=signature_hex,
            manifest_sha256=manifest_sha256,
        )
