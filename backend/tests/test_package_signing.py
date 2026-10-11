import io
import json
import zipfile
import hashlib
import pytest

from backend.credence_gov.crypto_signer import Ed25519Signer
from backend.credence_gov.package_builder import EvidencePackageBuilder


def test_ed25519_signing_and_verification() -> None:
    priv_bytes, pub_bytes = Ed25519Signer.generate_keypair()
    payload = b"Official Department Evidence Manifest Content"

    sig = Ed25519Signer.sign_bytes(priv_bytes, payload)
    assert len(sig) == 64

    # Verification succeeds
    assert Ed25519Signer.verify_bytes(pub_bytes, payload, sig) is True

    # Tampered payload fails
    assert Ed25519Signer.verify_bytes(pub_bytes, b"Tampered Manifest", sig) is False


def test_build_signed_evidence_package() -> None:
    priv_bytes, pub_bytes = Ed25519Signer.generate_keypair()

    artifacts = [
        {
            "name": "gazette_circular.pdf",
            "bytes": b"%PDF-1.4 Mock Gazette Content",
            "sha256": hashlib.sha256(b"%PDF-1.4 Mock Gazette Content").hexdigest(),
        }
    ]
    audit_events = [
        {"action": "case_created", "event_hash": "hash1"},
        {"action": "artifact_stored", "event_hash": "hash2"},
    ]

    dossier = EvidencePackageBuilder.build_package(
        case_id="case-dossier-01",
        case_title="Dossier Test Case",
        classification="SECRET",
        evidence_state="supported",
        summary="Sourced from official notification.",
        artifacts=artifacts,
        audit_events=audit_events,
        private_key_bytes=priv_bytes,
    )

    assert dossier.case_id == "case-dossier-01"
    assert len(dossier.manifest_sha256) == 64
    assert len(dossier.zip_bytes) > 0

    # Unpack ZIP in memory and inspect files
    with zipfile.ZipFile(io.BytesIO(dossier.zip_bytes), "r") as zf:
        file_list = zf.namelist()
        assert "manifest.json" in file_list
        assert "manifest.sig" in file_list
        assert "audit_trail.json" in file_list
        assert "findings.json" in file_list
        assert "artifacts/gazette_circular.pdf" in file_list

        manifest_raw = zf.read("manifest.json")
        sig_raw = zf.read("manifest.sig")
        findings_dict = json.loads(zf.read("findings.json"))

        # Verify cryptographic signature on manifest
        assert Ed25519Signer.verify_bytes(pub_bytes, manifest_raw, sig_raw) is True

        # Verify mandatory advisory banner
        assert "Decision support. Not a finding of fact." in findings_dict["banner"]
        assert "Decision support. Not a finding of fact." in json.loads(manifest_raw)["banner"]
        manifest = json.loads(manifest_raw)
        assert manifest["artifacts"][0]["sha256"] == hashlib.sha256(zf.read("artifacts/gazette_circular.pdf")).hexdigest()
        assert manifest["files"]["audit_trail.json"] == hashlib.sha256(zf.read("audit_trail.json")).hexdigest()
        assert manifest["files"]["findings.json"] == hashlib.sha256(zf.read("findings.json")).hexdigest()


def test_package_rejects_mismatched_digest_and_unsafe_name() -> None:
    private_key, _ = Ed25519Signer.generate_keypair()
    base = {"case_id": "c", "case_title": "t", "classification": "OFFICIAL", "evidence_state": "insufficient_evidence", "summary": "s", "audit_events": [], "private_key_bytes": private_key}
    with pytest.raises(ValueError, match="digest mismatch"):
        EvidencePackageBuilder.build_package(**base, artifacts=[{"name": "a.pdf", "bytes": b"bytes", "sha256": "0" * 64}])
    digest = hashlib.sha256(b"bytes").hexdigest()
    with pytest.raises(ValueError, match="safe relative ZIP path"):
        EvidencePackageBuilder.build_package(**base, artifacts=[{"name": "../escape", "bytes": b"bytes", "sha256": digest}])
    with pytest.raises(ValueError, match="Duplicate artifact name"):
        EvidencePackageBuilder.build_package(**base, artifacts=[
            {"name": "same.bin", "bytes": b"bytes", "sha256": digest},
            {"name": "same.bin", "bytes": b"bytes", "sha256": digest},
        ])
