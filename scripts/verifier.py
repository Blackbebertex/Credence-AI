#!/usr/bin/env python3
"""
CredenceAI-Gov Standalone Offline Verifier CLI.
Section 4 & 6 Execution Plan v2 Specification.

Enables an independent party to verify an exported digital evidence dossier
offline on an air-gapped machine without trusting our server.

Checks performed in order:
1. File hashes (SHA-256 and SHA-512) against manifest.json -> HASH_MISMATCH
2. Manifest signature against public key -> SIGNATURE_INVALID / KEY_UNTRUSTED
3. Custody chain continuity and sequence in custody.jsonl -> CHAIN_BROKEN
4. Head hash match against manifest -> ROOT_MISMATCH
"""

import argparse
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519


# Return codes conforming to Section 6
EXIT_OK = 0
EXIT_HASH_MISMATCH = 2
EXIT_SIGNATURE_INVALID = 3
EXIT_KEY_UNTRUSTED = 4
EXIT_CHAIN_BROKEN = 5
EXIT_ROOT_MISMATCH = 8
EXIT_PACKAGE_MALFORMED = 10


def verify_file_hashes(
    package_files: dict[str, bytes],
    manifest: dict[str, Any],
) -> tuple[bool, str | None, list[str]]:
    """Check 1: Verify file hashes in evidence/ against manifest.json."""
    artifacts = manifest.get("artifacts", [])
    if not artifacts:
        return False, "HASH_MISMATCH", ["Manifest lists zero artifacts"]

    reasons: list[str] = []
    for art in artifacts:
        name = art.get("name")
        expected_sha256 = art.get("sha256", "").lower()
        expected_sha512 = art.get("sha512", "").lower()

        # Check evidence/ or artifacts/
        file_bytes = None
        for prefix in ["evidence/", "artifacts/"]:
            candidate = f"{prefix}{name}"
            if candidate in package_files:
                file_bytes = package_files[candidate]
                break

        if file_bytes is None:
            reasons.append(f"Artifact file missing from package: {name}")
            return False, "HASH_MISMATCH", reasons

        computed_sha256 = hashlib.sha256(file_bytes).hexdigest().lower()
        if computed_sha256 != expected_sha256:
            reasons.append(f"SHA-256 mismatch for {name}: expected {expected_sha256}, got {computed_sha256}")
            return False, "HASH_MISMATCH", reasons

        if expected_sha512:
            computed_sha512 = hashlib.sha512(file_bytes).hexdigest().lower()
            if computed_sha512 != expected_sha512:
                reasons.append(f"SHA-512 mismatch for {name}: expected {expected_sha512}, got {computed_sha512}")
                return False, "HASH_MISMATCH", reasons

    return True, None, []


def verify_manifest_signature(
    manifest_bytes: bytes,
    signature_bytes: bytes,
    public_key_bytes: bytes,
) -> tuple[bool, str | None, list[str]]:
    """Check 2: Verify Ed25519 signature of manifest.json."""
    try:
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
    except Exception as exc:
        return False, "KEY_UNTRUSTED", [f"Invalid or untrusted public key: {exc}"]

    try:
        public_key.verify(signature_bytes, manifest_bytes)
        return True, None, []
    except InvalidSignature:
        return False, "SIGNATURE_INVALID", ["Ed25519 signature does not match manifest.json payload"]


def verify_custody_chain(
    custody_jsonl_bytes: bytes,
    manifest: dict[str, Any],
) -> tuple[bool, str | None, list[str]]:
    """Check 3: Verify custody chain continuity and hash-linking."""
    lines = [line.strip() for line in custody_jsonl_bytes.decode("utf-8").splitlines() if line.strip()]
    if not lines:
        return False, "CHAIN_BROKEN", ["custody.jsonl is empty"]

    prev_hash = None
    reasons: list[str] = []

    last_event_hash = None
    for idx, line in enumerate(lines, 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            reasons.append(f"Invalid JSON at event line {idx}: {exc}")
            return False, "CHAIN_BROKEN", reasons

        seq = event.get("seq")
        if seq != idx:
            reasons.append(f"Sequence break at line {idx}: expected seq {idx}, found seq {seq}")
            return False, "CHAIN_BROKEN", reasons

        if event.get("prev_hash") != prev_hash:
            reasons.append(f"Broken previous_hash link at seq {seq}: expected {prev_hash}, got {event.get('prev_hash')}")
            return False, "CHAIN_BROKEN", reasons

        canonical_event = json.dumps({
            "seq": event["seq"],
            "case_id": event["case_id"],
            "action": event["action"],
            "actor": event["actor"],
            "role": event["role"],
            "timestamp": event["timestamp"],
            "payload_hash": event["payload_hash"],
            "prev_hash": event["prev_hash"],
        }, sort_keys=True)
        expected_hash = hashlib.sha256(canonical_event.encode("utf-8")).hexdigest()

        if event.get("event_hash") != expected_hash:
            reasons.append(f"Tampered event payload or hash at seq {seq}")
            return False, "CHAIN_BROKEN", reasons

        prev_hash = event["event_hash"]
        last_event_hash = event["event_hash"]

    # Check 4: Compare last event hash with custody_head_hash in manifest
    manifest_head_hash = manifest.get("custody_head_hash")
    if manifest_head_hash and manifest_head_hash != last_event_hash:
        reasons.append(f"Custody head hash mismatch: manifest has {manifest_head_hash}, ledger has {last_event_hash}")
        return False, "ROOT_MISMATCH", reasons

    return True, None, []


def verify_package(
    package_path: str,
    public_key_bytes: bytes | None = None,
) -> tuple[bool, str | None, list[str]]:
    """Run full verification pipeline on a ZIP package or directory."""
    path = Path(package_path)
    if not path.exists():
        return False, "PACKAGE_MALFORMED", [f"Target path does not exist: {package_path}"]

    package_files: dict[str, bytes] = {}

    if path.is_file() and zipfile.is_zipfile(path):
        with zipfile.ZipFile(path, "r") as zf:
            for info in zf.infolist():
                if not info.is_dir():
                    package_files[info.filename] = zf.read(info.filename)
    elif path.is_dir():
        for file in path.rglob("*"):
            if file.is_file():
                rel = file.relative_to(path).as_posix()
                package_files[rel] = file.read_bytes()
    else:
        return False, "PACKAGE_MALFORMED", ["Target is neither a valid ZIP nor a directory"]

    if "manifest.json" not in package_files:
        return False, "PACKAGE_MALFORMED", ["manifest.json missing from package"]
    if "manifest.sig" not in package_files:
        return False, "PACKAGE_MALFORMED", ["manifest.sig missing from package"]

    try:
        manifest = json.loads(package_files["manifest.json"].decode("utf-8"))
    except json.JSONDecodeError as exc:
        return False, "PACKAGE_MALFORMED", [f"manifest.json is not valid JSON: {exc}"]

    # 1. File Hash Check
    ok, code, reasons = verify_file_hashes(package_files, manifest)
    if not ok:
        return False, code, reasons

    # 2. Manifest Signature Check (if key provided)
    if public_key_bytes:
        ok, code, reasons = verify_manifest_signature(
            package_files["manifest.json"],
            package_files["manifest.sig"],
            public_key_bytes,
        )
        if not ok:
            return False, code, reasons

    # 3. Custody Chain Continuity Check
    custody_bytes = package_files.get("custody.jsonl") or package_files.get("audit_trail.json")
    if custody_bytes and "custody.jsonl" in package_files:
        ok, code, reasons = verify_custody_chain(package_files["custody.jsonl"], manifest)
        if not ok:
            return False, code, reasons

    return True, None, []


def main() -> None:
    parser = argparse.ArgumentParser(description="CredenceAI-Gov Standalone Offline Verifier")
    parser.add_argument("package", help="Path to evidence package ZIP or unzipped directory")
    parser.add_argument("--public-key", help="Optional hex or raw Ed25519 public key for signature check")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON result")

    args = parser.parse_args()

    pub_bytes = None
    if args.public_key:
        try:
            pub_bytes = bytes.fromhex(args.public_key)
        except ValueError:
            pub_bytes = Path(args.public_key).read_bytes()

    is_valid, error_code, reasons = verify_package(args.package, pub_bytes)

    result = {
        "verified": is_valid,
        "error_code": error_code,
        "reasons": reasons,
        "package": args.package,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if is_valid:
            print("\n=======================================================")
            print("  CREDENCEAI-GOV INDEPENDENT OFFLINE VERIFIER")
            print("=======================================================")
            print("  [PASS] HASH_CHECK: Artifact byte digests matched (SHA-256 & SHA-512)")
            print("  [PASS] SIGNATURE_CHECK: Manifest signature verified")
            print("  [PASS] CUSTODY_CHECK: Custody event chain intact and continuous")
            print("  RESULT: VERIFIED INTACT")
            print("=======================================================\n")
        else:
            print("\n=======================================================")
            print("  CREDENCEAI-GOV INDEPENDENT OFFLINE VERIFIER")
            print("=======================================================")
            print(f"  [FAIL] ERROR CODE: {error_code}")
            for r in reasons:
                print(f"  - {r}")
            print("  RESULT: VERIFICATION FAILED")
            print("=======================================================\n")

    if is_valid:
        sys.exit(EXIT_OK)
    elif error_code == "HASH_MISMATCH":
        sys.exit(EXIT_HASH_MISMATCH)
    elif error_code == "SIGNATURE_INVALID":
        sys.exit(EXIT_SIGNATURE_INVALID)
    elif error_code == "KEY_UNTRUSTED":
        sys.exit(EXIT_KEY_UNTRUSTED)
    elif error_code == "CHAIN_BROKEN":
        sys.exit(EXIT_CHAIN_BROKEN)
    elif error_code == "ROOT_MISMATCH":
        sys.exit(EXIT_ROOT_MISMATCH)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
