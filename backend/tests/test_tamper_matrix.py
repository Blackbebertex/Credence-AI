import copy
import hashlib
import json
import pytest
from fastapi.testclient import TestClient

from backend.credence_gov.app import create_app
from backend.credence_gov.auth import create_access_token
from backend.credence_gov.crypto_signer import Ed25519Signer
from backend.credence_gov.package_builder import EvidencePackageBuilder
from scripts.verifier import verify_package, verify_file_hashes, verify_manifest_signature, verify_custody_chain


@pytest.fixture
def auth_client() -> tuple[TestClient, dict[str, str]]:
    app = create_app()
    token = create_access_token(
        user_id="tamper-analyst",
        tenant_id="tamper-tenant",
        username="tamper_analyst",
        roles=["analyst", "reviewer", "supervisor"],
    )
    headers = {"Authorization": f"Bearer {token}"}
    return TestClient(app), headers


# --- Section 6: Tamper Test Matrix ---

def test_tamper_matrix_1_flip_byte_in_artifact_triggers_hash_mismatch() -> None:
    """1. Flip one byte in an artifact -> HASH_MISMATCH."""
    manifest = {
        "artifacts": [
            {
                "name": "sample.pdf",
                "sha256": hashlib.sha256(b"original authentic content").hexdigest(),
                "sha512": hashlib.sha512(b"original authentic content").hexdigest(),
            }
        ]
    }
    # Tamper with the bytes (flipped byte)
    tampered_files = {
        "evidence/sample.pdf": b"original autxntic content",  # flipped byte
    }
    ok, error_code, reasons = verify_file_hashes(tampered_files, manifest)
    assert ok is False
    assert error_code == "HASH_MISMATCH"
    assert "SHA-256 mismatch" in reasons[0]


def test_tamper_matrix_2_edit_manifest_triggers_signature_invalid() -> None:
    """2. Edit one manifest field -> SIGNATURE_INVALID."""
    priv, pub = Ed25519Signer.generate_keypair()
    original_manifest = json.dumps({"case_id": "CASE-001", "classification": "OFFICIAL"}, sort_keys=True).encode()
    signature = Ed25519Signer.sign_bytes(priv, original_manifest)

    # Edit one field in the manifest
    tampered_manifest = json.dumps({"case_id": "CASE-001", "classification": "SECRET"}, sort_keys=True).encode()

    ok, error_code, reasons = verify_manifest_signature(tampered_manifest, signature, pub)
    assert ok is False
    assert error_code == "SIGNATURE_INVALID"


def test_tamper_matrix_3_edit_custody_event_triggers_chain_broken() -> None:
    """3. Edit a custody event -> CHAIN_BROKEN."""
    events = [
        {
            "seq": 1,
            "case_id": "CASE-01",
            "action": "CASE_CREATED",
            "actor": "user-1",
            "role": "analyst",
            "timestamp": "2026-10-15T10:00:00Z",
            "payload_hash": hashlib.sha256(b"payload1").hexdigest(),
            "prev_hash": None,
        }
    ]
    # compute valid event hash
    canonical = json.dumps(events[0], sort_keys=True)
    events[0]["event_hash"] = hashlib.sha256(canonical.encode()).hexdigest()

    # Tamper with the event actor
    events[0]["actor"] = "malicious-actor"
    jsonl_bytes = json.dumps(events[0]).encode() + b"\n"

    manifest = {"custody_head_hash": events[0]["event_hash"]}
    ok, error_code, reasons = verify_custody_chain(jsonl_bytes, manifest)
    assert ok is False
    assert error_code == "CHAIN_BROKEN"


def test_tamper_matrix_4_delete_custody_event_triggers_chain_broken_sequence_gap() -> None:
    """4. Delete a custody event -> CHAIN_BROKEN (sequence gap)."""
    # Event 1
    ev1 = {
        "seq": 1, "case_id": "C-1", "action": "A", "actor": "u", "role": "r",
        "timestamp": "T1", "payload_hash": "p1", "prev_hash": None,
    }
    ev1["event_hash"] = hashlib.sha256(json.dumps(ev1, sort_keys=True).encode()).hexdigest()

    # Event 3 (Event 2 deleted!)
    ev3 = {
        "seq": 3, "case_id": "C-1", "action": "B", "actor": "u", "role": "r",
        "timestamp": "T2", "payload_hash": "p2", "prev_hash": ev1["event_hash"],
    }
    ev3["event_hash"] = hashlib.sha256(json.dumps(ev3, sort_keys=True).encode()).hexdigest()

    jsonl_bytes = (json.dumps(ev1) + "\n" + json.dumps(ev3) + "\n").encode()
    manifest = {"custody_head_hash": ev3["event_hash"]}

    ok, error_code, reasons = verify_custody_chain(jsonl_bytes, manifest)
    assert ok is False
    assert error_code == "CHAIN_BROKEN"
    assert "Sequence break" in reasons[0]


def test_tamper_matrix_5_reorder_custody_events_triggers_chain_broken() -> None:
    """5. Reorder custody events -> CHAIN_BROKEN."""
    ev1 = {
        "seq": 1, "case_id": "C-1", "action": "A", "actor": "u", "role": "r",
        "timestamp": "T1", "payload_hash": "p1", "prev_hash": None,
    }
    ev1["event_hash"] = hashlib.sha256(json.dumps(ev1, sort_keys=True).encode()).hexdigest()

    ev2 = {
        "seq": 2, "case_id": "C-1", "action": "B", "actor": "u", "role": "r",
        "timestamp": "T2", "payload_hash": "p2", "prev_hash": ev1["event_hash"],
    }
    ev2["event_hash"] = hashlib.sha256(json.dumps(ev2, sort_keys=True).encode()).hexdigest()

    # Reorder: ev2 before ev1
    jsonl_bytes = (json.dumps(ev2) + "\n" + json.dumps(ev1) + "\n").encode()
    manifest = {"custody_head_hash": ev2["event_hash"]}

    ok, error_code, reasons = verify_custody_chain(jsonl_bytes, manifest)
    assert ok is False
    assert error_code == "CHAIN_BROKEN"


def test_tamper_matrix_6_swap_another_key_signature_fails() -> None:
    """6. Swap in another key's signature -> SIGNATURE_INVALID / KEY_UNTRUSTED."""
    key1_priv, key1_pub = Ed25519Signer.generate_keypair()
    key2_priv, key2_pub = Ed25519Signer.generate_keypair()

    manifest_bytes = b'{"case_id": "C-99"}'
    sig_from_key2 = Ed25519Signer.sign_bytes(key2_priv, manifest_bytes)

    # Verifying key2's signature against key1's public key must fail
    ok, error_code, reasons = verify_manifest_signature(manifest_bytes, sig_from_key2, key1_pub)
    assert ok is False
    assert error_code == "SIGNATURE_INVALID"


# --- P0-04: Gate the statutory certificate (4 negative preconditions) ---

def test_p0_04_bsa_cert_fails_when_case_has_no_artifacts(auth_client: tuple[TestClient, dict[str, str]]) -> None:
    """P0-04 Precondition 1: Certificate fails if case has no artifacts."""
    client, headers = auth_client
    case = client.post("/api/v1/cases", headers=headers, json={
        "title": "Empty Case", "classification": "OFFICIAL", "purpose": "Testing gating", "as_of_date": "2026-10-15"
    }).json()

    res = client.post(f"/api/v1/cases/{case['id']}/bsa-certificate", headers=headers, json={
        "deponent_name": "Official Officer",
        "deponent_designation": "Director",
        "department": "Cyber Directorate",
        "device_identifier": "SECURE-BOX",
    })
    assert res.status_code == 409
    assert any("no registered evidence artifacts" in p for p in res.json()["detail"]["missing_preconditions"])


def test_p0_04_bsa_cert_fails_when_deponent_name_blank(auth_client: tuple[TestClient, dict[str, str]]) -> None:
    """P0-04 Precondition 2: Certificate fails if authorized deponent is missing/invalid."""
    client, headers = auth_client
    case = client.post("/api/v1/cases", headers=headers, json={
        "title": "Named Case", "classification": "OFFICIAL", "purpose": "Testing deponent gating", "as_of_date": "2026-10-15"
    }).json()

    # Upload an artifact
    client.post(f"/api/v1/cases/{case['id']}/artifacts", headers=headers, json={
        "artifact_type": "notice",
        "content_b64": "JVBERi0xLjQKJSBkZW1v",
        "mime_type": "application/pdf",
    })

    res = client.post(f"/api/v1/cases/{case['id']}/bsa-certificate", headers=headers, json={
        "deponent_name": " ",
        "deponent_designation": "Director",
        "department": "Cyber Directorate",
        "device_identifier": "SECURE-BOX",
    })
    # Validation error for min_length or 409
    assert res.status_code in [409, 422]


def test_p0_04_bsa_cert_fails_when_affirmation_unconfirmed(auth_client: tuple[TestClient, dict[str, str]]) -> None:
    """P0-04 Precondition 3: Certificate fails if statutory affirmation is not confirmed."""
    client, headers = auth_client
    case = client.post("/api/v1/cases", headers=headers, json={
        "title": "Affirmation Case", "classification": "OFFICIAL", "purpose": "Testing affirmation gating", "as_of_date": "2026-10-15"
    }).json()
    client.post(f"/api/v1/cases/{case['id']}/artifacts", headers=headers, json={
        "artifact_type": "notice", "content_b64": "JVBERi0xLjQKJSBkZW1v", "mime_type": "application/pdf",
    })

    res = client.post(f"/api/v1/cases/{case['id']}/bsa-certificate", headers=headers, json={
        "deponent_name": "Official Officer",
        "deponent_designation": "Director",
        "department": "Cyber Directorate",
        "device_identifier": "SECURE-BOX",
        "affirmation_confirmed": False,  # Missing affirmation!
    })
    assert res.status_code == 409
    assert any("affirmation" in p for p in res.json()["detail"]["missing_preconditions"])


def test_p0_04_bsa_cert_fails_when_artifact_hash_mismatch(auth_client: tuple[TestClient, dict[str, str]]) -> None:
    """P0-04 Precondition 4: Certificate fails if stored artifact bytes do not match SHA-256."""
    client, headers = auth_client
    case = client.post("/api/v1/cases", headers=headers, json={
        "title": "Corrupt Case", "classification": "OFFICIAL", "purpose": "Testing hash gating", "as_of_date": "2026-10-15"
    }).json()
    art = client.post(f"/api/v1/cases/{case['id']}/artifacts", headers=headers, json={
        "artifact_type": "notice", "content_b64": "JVBERi0xLjQKJSBkZW1v", "mime_type": "application/pdf",
    }).json()

    # Intentionally corrupt the artifact's recorded sha256 in DB
    from backend.credence_gov.api import _DB_ARTIFACTS
    _DB_ARTIFACTS[art["id"]]["sha256"] = "corrupted_digest_00000000000000000000000000000000"

    res = client.post(f"/api/v1/cases/{case['id']}/bsa-certificate", headers=headers, json={
        "deponent_name": "Official Officer",
        "deponent_designation": "Director",
        "department": "Cyber Directorate",
        "device_identifier": "SECURE-BOX",
    })
    assert res.status_code == 409
    assert any("HASH_MISMATCH" in p for p in res.json()["detail"]["missing_preconditions"])


# --- P0-05: Fix export (fails if any artifact missing) ---

def test_p0_05_export_fails_if_artifact_missing_from_store(auth_client: tuple[TestClient, dict[str, str]]) -> None:
    """P0-05: Export fails with 409 if referenced artifact missing from storage (no simulated fallback)."""
    client, headers = auth_client
    case = client.post("/api/v1/cases", headers=headers, json={
        "title": "Missing Store Case", "classification": "OFFICIAL", "purpose": "Testing missing export", "as_of_date": "2026-10-15"
    }).json()
    art = client.post(f"/api/v1/cases/{case['id']}/artifacts", headers=headers, json={
        "artifact_type": "notice", "content_b64": "JVBERi0xLjQKJSBkZW1v", "mime_type": "application/pdf",
    }).json()

    # Corrupt storage URI so get_object fails
    from backend.credence_gov.api import _DB_ARTIFACTS
    _DB_ARTIFACTS[art["id"]]["storage_uri"] = "nonexistent_bucket/missing_key.dat"

    res = client.post(f"/api/v1/cases/{case['id']}/export-package", headers=headers)
    assert res.status_code == 409
    assert "missing from immutable store" in res.json()["detail"]


# --- P0-03: Real Integrity API ---

def test_p0_03_integrity_api_recomputes_real_hashes(auth_client: tuple[TestClient, dict[str, str]]) -> None:
    """P0-03: scan_case_integrity_endpoint returns per-check results and real computed flags."""
    client, headers = auth_client
    case = client.post("/api/v1/cases", headers=headers, json={
        "title": "Real Scan Case", "classification": "OFFICIAL", "purpose": "Testing real scan", "as_of_date": "2026-10-15"
    }).json()
    art = client.post(f"/api/v1/cases/{case['id']}/artifacts", headers=headers, json={
        "artifact_type": "doc", "content_b64": "JVBERi0xLjQKJSBkZW1v", "mime_type": "application/pdf",
    }).json()

    res = client.get(f"/api/v1/cases/{case['id']}/integrity-scan", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["hash_match"] is True
    assert data["chain_valid"] is True
    assert data["is_intact"] is True
    assert data["error_code"] is None

    # Corrupt an artifact
    from backend.credence_gov.api import _DB_ARTIFACTS
    _DB_ARTIFACTS[art["id"]]["sha256"] = "tampered_fake_digest"
    tampered_res = client.get(f"/api/v1/cases/{case['id']}/integrity-scan", headers=headers)
    tampered_data = tampered_res.json()
    assert tampered_data["hash_match"] is False
    assert tampered_data["is_intact"] is False
    assert tampered_data["error_code"] == "HASH_MISMATCH"
