"""Loopback-only, synthetic-data API launcher for Dockerless development."""

from __future__ import annotations

import argparse
import base64
import datetime
import os
import secrets
import struct
import zlib

from .app import create_app
from .auth import AuthenticatedUser, create_access_token


def _make_simulated_pdf(title: str) -> bytes:
    """Build a tiny single-page PDF containing only labeled synthetic text."""
    safe_title = title.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 32 150 Td (SIMULATED - {safe_title}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 360 200] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = bytearray(b"%PDF-1.4\n% SIMULATED\n")
    offsets = [0]
    for number, body in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii") + body + b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii"))
    return bytes(pdf)


def _make_simulated_png() -> bytes:
    """Build a valid one-pixel image fixture without external image assets."""
    def chunk(kind: bytes, data: bytes) -> bytes:
        payload = kind + data
        return struct.pack(">I", len(data)) + payload + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    pixel = b"\x00\x37\x8b\xff\xff"  # Filter byte + synthetic blue RGBA pixel.
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(pixel)) + chunk(b"IEND", b"")


def _seed_demo_data() -> int:
    """Populate only the disposable development server with repeatable fixtures."""
    from . import api

    tenant_id = "local-simulated"
    owner_id = "local-analyst"
    if any(case["tenant_id"] == tenant_id and case["owner_id"] == owner_id for case in api._DB_CASES.values()):
        return 0

    user = AuthenticatedUser(
        user_id=owner_id,
        tenant_id=tenant_id,
        username="local_analyst",
        roles=("analyst", "reviewer", "supervisor"),
    )
    # Case dates are date-only values, so generate them in the host's local
    # timezone to match the browser's Today filter.
    today = datetime.datetime.now().astimezone().date().isoformat()
    examples = [
        {
            "title": "[SIMULATED] Gazette notice provenance review",
            "classification": "OFFICIAL",
            "purpose": "Demonstrate source capture, document hashing, provenance notes, and reviewer disposition using a fictional public notice.",
            "evidence": [
                ("SIMULATED notice PDF", "application/pdf", _make_simulated_pdf("Fictional public notice - provenance sample")),
                ("SIMULATED source notes", "text/plain", b"SIMULATED\nFictional source: Example Gazette\nPurpose: demonstrate intake metadata and provenance review.\nNo real agency or record is represented.\n"),
            ],
            "review": ("R2", "completed", "Reviewed the synthetic source notes and document metadata; provenance remains illustrative."),
        },
        {
            "title": "[SIMULATED] Procurement invoice evidence intake",
            "classification": "OFFICIAL",
            "purpose": "Demonstrate case creation, multiple evidence items, metadata inventory, and a pending human-review queue entry.",
            "evidence": [
                ("SIMULATED invoice PDF", "application/pdf", _make_simulated_pdf("Fictional procurement invoice - sample 0042")),
                ("SIMULATED intake notes", "text/plain", b"SIMULATED\nFictional vendor: Example Supplies\nInvoice: DEMO-0042\nPurpose: demonstrate evidence inventory only.\n"),
            ],
            "review": ("R2", "pending", None),
        },
        {
            "title": "[SIMULATED] Public works inspection media",
            "classification": "OFFICIAL",
            "purpose": "Demonstrate image evidence metadata, integrity hash display, and an in-progress reviewer assignment.",
            "evidence": [
                ("SIMULATED inspection image", "image/png", _make_simulated_png()),
                ("SIMULATED field notes", "text/plain", b"SIMULATED\nFictional inspection site: Sample District 00\nPurpose: demonstrate related evidence items.\n"),
            ],
            "review": ("R1", "in_review", None),
        },
        {
            "title": "[SIMULATED] Service bulletin version comparison",
            "classification": "OFFICIAL",
            "purpose": "Demonstrate a completed human-review task with a recorded synthetic rationale.",
            "evidence": [
                ("SIMULATED bulletin excerpt", "text/plain", b"SIMULATED\nVersion A: sample wording alpha.\nVersion B: sample wording beta.\nThis is invented content for demonstrating comparison workflows.\n"),
                ("SIMULATED comparison memo", "text/plain", b"SIMULATED\nTwo invented text snippets are catalogued; no authenticity conclusion is made.\n"),
            ],
            "review": ("R2", "completed", "Compared the two synthetic excerpts and recorded a demonstration disposition; no finding of fact was made."),
        },
        {
            "title": "[SIMULATED] Case awaiting evidence submission",
            "classification": "OFFICIAL",
            "purpose": "Demonstrate the new-case empty state and the add-evidence workflow before any files are attached.",
            "evidence": [],
            "review": None,
        },
    ]

    for example in examples:
        case = api.create_case_endpoint(
            api.CaseCreateSchema(
                title=example["title"],
                classification=example["classification"],
                purpose=example["purpose"],
                as_of_date=today,
            ),
            user,
        )
        for label, mime_type, content in example["evidence"]:
            api.upload_artifact_endpoint(
                case.id,
                api.ArtifactUploadSchema(
                    artifact_type=label,
                    content_b64=base64.b64encode(content).decode("ascii"),
                    mime_type=mime_type,
                ),
                user,
            )
        if example["review"]:
            risk_tier, workflow_status, rationale = example["review"]
            task = api.create_review_task_endpoint(
                case.id, api.ReviewTaskCreateSchema(risk_tier=risk_tier), user
            )
            if workflow_status in {"in_review", "completed"}:
                api.claim_review_task_endpoint(task.id, user)
            if workflow_status == "completed":
                api.complete_review_task_endpoint(
                    task.id, api.ReviewTaskCompleteSchema(rationale=rationale), user
                )
    return len(examples)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the synthetic CredenceAI-Gov API locally")
    parser.add_argument("--port", type=int, default=8000, help="Local HTTP port (default: 8000)")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")

    # This entry point is explicitly for disposable local demos. Never load a
    # configured/deployment secret into it or bind it beyond loopback.
    jwt_secret = secrets.token_urlsafe(48)
    os.environ["JWT_SECRET"] = jwt_secret
    token = create_access_token(
        user_id="local-analyst",
        tenant_id="local-simulated",
        username="local_analyst",
        # The local token can exercise all human-review transitions in the
        # synthetic demo. These roles are never loaded by production startup.
        roles=["analyst", "reviewer", "supervisor"],
        secret=jwt_secret,
    )
    seeded_cases = _seed_demo_data()

    print("CredenceAI-Gov synthetic API: http://127.0.0.1:%s" % args.port)
    print("Interactive API docs: http://127.0.0.1:%s/docs" % args.port)
    print("Local demo analyst/reviewer token is available only to loopback clients and expires in 15 minutes.")
    print("Loaded %s clearly labeled synthetic demonstration cases." % seeded_cases)
    print("Data is in memory and will be lost when this process stops. Do not use real evidence.")

    import uvicorn

    uvicorn.run(
        create_app(dev_token=token),
        host="127.0.0.1",
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
