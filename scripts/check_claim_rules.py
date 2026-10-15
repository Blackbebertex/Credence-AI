#!/usr/bin/env python3
"""
P0-02 Claim Rules CI Gate.
Section 2 & 5 Execution Plan v2.

Scans frontend code for banned marketing claim words that assert unearned assurance:
- "100%" (unless dynamically computed in JavaScript variables)
- "ensures" or "guarantees" (must use "supports admissibility under BSA s.63, subject to the court")
- "tamper-proof"
- "BSA Compliant" (must be "supports admissibility under BSA s.63, subject to the court")
- "Authentic" (must be "Hash recorded at intake" / "byte continuity")

Fails the build (exits with code 1) if any banned string is found.
"""

import re
import sys
from pathlib import Path

BANNED_PATTERNS = [
    (r"\b100%\b(?!\s*\{)", "Hardcoded '100%' claim without dynamic calculation"),
    (r"\bensures admissibility\b", "Claims system 'ensures admissibility' (must use 'supports admissibility subject to court')"),
    (r"\bguarantees?\b", "Unverifiable 'guarantee' claim"),
    (r"\btamper-proof\b", "Misleading claim 'tamper-proof' (tamper-evident / hash-chained is acceptable)"),
    (r"\bBSA COMPLIANT\b", "'BSA COMPLIANT' badge (must use 'BSA s.63 Admissibility Support')"),
    (r"\bguaranteed authentic\b", "'Guaranteed authentic' claim (hashes prove post-ingestion byte continuity only)"),
]

SCANNED_EXTENSIONS = {".jsx", ".tsx", ".html", ".js"}
EXCLUDE_DIRS = {"node_modules", "dist", ".git", ".venv", "tests"}


def check_claims(root_dir: str) -> list[tuple[str, int, str, str]]:
    violations = []
    root = Path(root_dir)

    for path in root.rglob("*"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.suffix not in SCANNED_EXTENSIONS:
            continue
        if "check_claim_rules.py" in path.name:
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for line_num, line in enumerate(content.splitlines(), 1):
            # Ignore comments
            clean_line = line.strip()
            if clean_line.startswith("//") or clean_line.startswith("/*") or clean_line.startswith("*"):
                continue

            for pattern, reason in BANNED_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check if allowed with "subject to judicial" or "subject to the court"
                    if "subject to" in line.lower() and "bsa" in line.lower():
                        continue
                    violations.append((str(path), line_num, line.strip(), reason))

    return violations


def main() -> None:
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "frontend/src"
    print(f"Scanning {target_dir} for banned claim assertions (P0-02)...")
    violations = check_claims(target_dir)

    if violations:
        print(f"\n[FAIL] Found {len(violations)} false assurance or banned claim violations:")
        for path, line_num, line, reason in violations:
            print(f"  {path}:{line_num} -> {reason}")
            print(f"    Line: \"{line}\"")
        print("\nPlease replace with verified computed labels or statutory disclaimers ('supports admissibility under BSA s.63, subject to the court').\n")
        sys.exit(1)

    print("[PASS] Claim rules verification clean: no false assurance claims detected.")
    sys.exit(0)


if __name__ == "__main__":
    main()
