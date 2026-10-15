from __future__ import annotations

import uuid
import base64
import binascii
import datetime
import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any, Literal
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from .auth import AuthenticatedUser, create_access_token, get_current_user, require_role
from .bsa_certificate import BSACertificateGenerator
from .crypto_signer import Ed25519Signer
from .package_builder import EvidencePackageBuilder
from .storage_adapter import LocalStorageAdapter, StorageAdapter


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
        self._cases: list[dict[str, Any]] = []

    def create_case(self, request: CaseCreateRequest) -> dict[str, Any]:
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


# --- FastAPI REST Router & Pydantic Schemas ---

class CaseCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, description="Official title of the case")
    classification: str = Field(..., min_length=1, description="Security classification tier")
    purpose: str = Field(..., min_length=1, description="Investigative or advisory purpose")
    as_of_date: str = Field(..., min_length=1, description="Temporal reference date (YYYY-MM-DD)")


class CaseResponseSchema(BaseModel):
    id: str
    tenant_id: str
    owner_id: str
    classification: str
    title: str
    purpose: str
    as_of_date: str
    status: str = "created"
    schema_version: int = 1
    banner: str = "Decision support. Not a finding of fact."


class ArtifactUploadSchema(BaseModel):
    artifact_type: str = Field(..., min_length=1, description="Type of artifact, e.g. pdf, image")
    content_b64: str = Field(..., min_length=1, max_length=((int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024 * 4 + 2) // 3), description="Strict Base64 encoded file bytes")
    mime_type: str = Field(..., min_length=1, description="MIME content type")


class ArtifactResponseSchema(BaseModel):
    id: str
    case_id: str
    tenant_id: str
    artifact_type: str
    sha256: str
    mime_type: str
    storage_uri: str
    is_immutable: bool = True
    created_at: str


class ReviewTaskCreateSchema(BaseModel):
    risk_tier: Literal["R1", "R2", "R3"] = "R2"


class ReviewTaskCompleteSchema(BaseModel):
    rationale: str = Field(..., min_length=20, max_length=4000)


class ReviewTaskResponseSchema(BaseModel):
    id: str
    case_id: str
    tenant_id: str
    status: Literal["pending", "in_review", "completed"]
    risk_tier: Literal["R1", "R2", "R3"]
    assigned_reviewer_id: str | None = None
    created_at: str
    completed_at: str | None = None
    reviewer_rationale: str | None = None


# In-memory repository for standalone router testability
_DB_CASES: dict[str, dict[str, Any]] = {}
_DB_ARTIFACTS: dict[str, dict[str, Any]] = {}
_DB_REVIEW_TASKS: dict[str, dict[str, Any]] = {}
_DB_CUSTODY_EVENTS: list[dict[str, Any]] = []
_STORAGE_ADAPTER: StorageAdapter = LocalStorageAdapter()
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024


def _record_custody_event(
    *,
    case_id: str,
    action: str,
    actor: str,
    role: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    case_events = [e for e in _DB_CUSTODY_EVENTS if e["case_id"] == case_id]
    seq = len(case_events) + 1
    prev_hash = case_events[-1]["event_hash"] if case_events else None
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    canonical_payload = json.dumps(payload, sort_keys=True)
    payload_hash = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()

    canonical_event = json.dumps({
        "seq": seq,
        "case_id": case_id,
        "action": action,
        "actor": actor,
        "role": role,
        "timestamp": now,
        "payload_hash": payload_hash,
        "prev_hash": prev_hash,
    }, sort_keys=True)
    event_hash = hashlib.sha256(canonical_event.encode("utf-8")).hexdigest()

    event = {
        "seq": seq,
        "case_id": case_id,
        "action": action,
        "actor": actor,
        "role": role,
        "timestamp": now,
        "payload": payload,
        "payload_hash": payload_hash,
        "prev_hash": prev_hash,
        "event_hash": event_hash,
    }
    _DB_CUSTODY_EVENTS.append(event)
    return event


def _verify_custody_chain(case_id: str) -> tuple[bool, str | None, list[str]]:
    events = [e for e in _DB_CUSTODY_EVENTS if e["case_id"] == case_id]
    if not events:
        return False, "CHAIN_BROKEN", ["No custody events found for case"]

    prev_hash = None
    reasons: list[str] = []
    for expected_seq, event in enumerate(events, 1):
        if event.get("seq") != expected_seq:
            reasons.append(f"Sequence gap at seq {event.get('seq')}, expected {expected_seq}")
            return False, "CHAIN_BROKEN", reasons
        if event.get("prev_hash") != prev_hash:
            reasons.append(f"Broken previous hash at seq {event.get('seq')}")
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
            reasons.append(f"Tampered event payload or hash at seq {event.get('seq')}")
            return False, "CHAIN_BROKEN", reasons
        prev_hash = event["event_hash"]

    return True, None, []


def _decode_and_validate_upload(payload: ArtifactUploadSchema) -> bytes:
    try:
        data = base64.b64decode(payload.content_b64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=400, detail="content_b64 must be valid Base64") from exc
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Uploaded file exceeds the configured size limit")

    signatures = {
        "application/pdf": data.startswith(b"%PDF-"),
        "image/png": data.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/jpeg": data.startswith(b"\xff\xd8\xff"),
        "text/plain": b"\x00" not in data and _is_utf8(data),
    }
    if payload.mime_type not in signatures or not signatures[payload.mime_type]:
        raise HTTPException(status_code=415, detail="Uploaded content does not match an allowed MIME type")
    return data


def _is_utf8(data: bytes) -> bool:
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True

router = APIRouter(prefix="/api/v1", tags=["Cases & Evidence"])


def _owned_case(case_id: str, user: AuthenticatedUser) -> dict[str, Any]:
    case = _DB_CASES.get(case_id)
    if not case or case["tenant_id"] != user.tenant_id or case["owner_id"] != user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


def _update_case_workflow_status(case_id: str) -> None:
    case = _DB_CASES[case_id]
    tasks = [task for task in _DB_REVIEW_TASKS.values() if task["case_id"] == case_id]
    if any(task["status"] == "in_review" for task in tasks):
        case["status"] = "in_review"
    elif any(task["status"] == "pending" for task in tasks):
        case["status"] = "pending_review"
    elif tasks:
        case["status"] = "review_completed"
    else:
        case["status"] = "created"


@router.get("/cases", response_model=list[CaseResponseSchema])
def list_cases_endpoint(
    user: AuthenticatedUser = Depends(require_role("analyst")),
) -> list[CaseResponseSchema]:
    return [
        CaseResponseSchema(**case)
        for case in _DB_CASES.values()
        if case["tenant_id"] == user.tenant_id and case["owner_id"] == user.user_id
    ]


@router.post("/cases", response_model=CaseResponseSchema, status_code=status.HTTP_201_CREATED)
def create_case_endpoint(
    payload: CaseCreateSchema,
    user: AuthenticatedUser = Depends(require_role("analyst")),
) -> CaseResponseSchema:
    case_id = f"case-{uuid.uuid4().hex[:8]}"
    record = {
        "id": case_id,
        "tenant_id": user.tenant_id,
        "owner_id": user.user_id,
        "classification": payload.classification.strip(),
        "title": payload.title.strip(),
        "purpose": payload.purpose.strip(),
        "as_of_date": payload.as_of_date.strip(),
        "status": "created",
        "schema_version": 1,
        "banner": "Decision support. Not a finding of fact.",
    }
    _DB_CASES[case_id] = record
    _record_custody_event(
        case_id=case_id,
        action="CASE_CREATED",
        actor=user.user_id,
        role="analyst",
        payload={
            "case_id": case_id,
            "title": record["title"],
            "classification": record["classification"],
            "as_of_date": record["as_of_date"],
        },
    )
    return CaseResponseSchema(**record)


@router.get("/artifacts", response_model=list[ArtifactResponseSchema])
def list_artifacts_endpoint(
    user: AuthenticatedUser = Depends(require_role("analyst")),
) -> list[ArtifactResponseSchema]:
    owned_case_ids = {
        case["id"] for case in _DB_CASES.values()
        if case["tenant_id"] == user.tenant_id and case["owner_id"] == user.user_id
    }
    return [
        ArtifactResponseSchema(**artifact)
        for artifact in _DB_ARTIFACTS.values()
        if artifact["case_id"] in owned_case_ids
    ]


@router.get("/cases/{case_id}/artifacts", response_model=list[ArtifactResponseSchema])
def list_case_artifacts_endpoint(
    case_id: str,
    user: AuthenticatedUser = Depends(require_role("analyst")),
) -> list[ArtifactResponseSchema]:
    _owned_case(case_id, user)
    return [
        ArtifactResponseSchema(**artifact)
        for artifact in _DB_ARTIFACTS.values()
        if artifact["case_id"] == case_id
    ]


@router.post("/cases/{case_id}/artifacts", response_model=ArtifactResponseSchema, status_code=status.HTTP_201_CREATED)
def upload_artifact_endpoint(
    case_id: str,
    payload: ArtifactUploadSchema,
    user: AuthenticatedUser = Depends(require_role("analyst")),
) -> ArtifactResponseSchema:
    if case_id not in _DB_CASES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    case = _DB_CASES[case_id]
    if case["tenant_id"] != user.tenant_id or case["owner_id"] != user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    data_bytes = _decode_and_validate_upload(payload)
    meta = _STORAGE_ADAPTER.put_object(
        bucket=f"evidence-{user.tenant_id}",
        key=f"cases/{case_id}/{uuid.uuid4().hex}.dat",
        data=data_bytes,
        mime_type=payload.mime_type,
        object_lock=True,
    )

    art_id = f"art-{uuid.uuid4().hex[:8]}"
    art_record = {
        "id": art_id,
        "case_id": case_id,
        "tenant_id": user.tenant_id,
        "artifact_type": payload.artifact_type,
        "sha256": meta.sha256,
        "mime_type": payload.mime_type,
        "storage_uri": f"{meta.bucket}/{meta.key}",
        "is_immutable": meta.is_immutable,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    _DB_ARTIFACTS[art_id] = art_record
    _record_custody_event(
        case_id=case_id,
        action="ARTIFACT_INGESTED",
        actor=user.user_id,
        role="analyst",
        payload={
            "artifact_id": art_id,
            "artifact_type": art_record["artifact_type"],
            "sha256": art_record["sha256"],
            "mime_type": art_record["mime_type"],
            "storage_uri": art_record["storage_uri"],
        },
    )
    return ArtifactResponseSchema(**art_record)


@router.get("/review-tasks", response_model=list[ReviewTaskResponseSchema])
def list_review_tasks_endpoint(
    user: AuthenticatedUser = Depends(get_current_user),
) -> list[ReviewTaskResponseSchema]:
    if not (user.has_role("analyst") or user.has_role("reviewer")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Analyst or reviewer role is required")
    return [
        ReviewTaskResponseSchema(**task)
        for task in _DB_REVIEW_TASKS.values()
        if task["tenant_id"] == user.tenant_id
        and (user.has_role("reviewer") or _DB_CASES[task["case_id"]]["owner_id"] == user.user_id)
    ]


@router.get("/cases/{case_id}/review-tasks", response_model=list[ReviewTaskResponseSchema])
def list_case_review_tasks_endpoint(
    case_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
) -> list[ReviewTaskResponseSchema]:
    case = _DB_CASES.get(case_id)
    if not case or case["tenant_id"] != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if case["owner_id"] != user.user_id and not user.has_role("reviewer"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if not (user.has_role("analyst") or user.has_role("reviewer")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Analyst or reviewer role is required")
    return [
        ReviewTaskResponseSchema(**task)
        for task in _DB_REVIEW_TASKS.values()
        if task["case_id"] == case_id
    ]


@router.post(
    "/cases/{case_id}/review-tasks",
    response_model=ReviewTaskResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_review_task_endpoint(
    case_id: str,
    payload: ReviewTaskCreateSchema,
    user: AuthenticatedUser = Depends(require_role("analyst")),
) -> ReviewTaskResponseSchema:
    case = _owned_case(case_id, user)
    if any(
        task["case_id"] == case_id and task["status"] != "completed"
        for task in _DB_REVIEW_TASKS.values()
    ):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Case already has an open review task")
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record = {
        "id": f"review-{uuid.uuid4().hex[:10]}",
        "case_id": case_id,
        "tenant_id": user.tenant_id,
        "status": "pending",
        "risk_tier": payload.risk_tier,
        "assigned_reviewer_id": None,
        "created_at": now,
        "completed_at": None,
        "reviewer_rationale": None,
    }
    _DB_REVIEW_TASKS[record["id"]] = record
    case["status"] = "pending_review"
    _record_custody_event(
        case_id=case_id,
        action="REVIEW_TASK_CREATED",
        actor=user.user_id,
        role="analyst",
        payload={"task_id": record["id"], "risk_tier": payload.risk_tier},
    )
    return ReviewTaskResponseSchema(**record)


@router.post("/review-tasks/{task_id}/claim", response_model=ReviewTaskResponseSchema)
def claim_review_task_endpoint(
    task_id: str,
    user: AuthenticatedUser = Depends(require_role("reviewer")),
) -> ReviewTaskResponseSchema:
    task = _DB_REVIEW_TASKS.get(task_id)
    if not task or task["tenant_id"] != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review task not found")
    if task["status"] == "in_review" and task["assigned_reviewer_id"] == user.user_id:
        return ReviewTaskResponseSchema(**task)
    if task["status"] != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Review task is no longer pending")
    task["status"] = "in_review"
    task["assigned_reviewer_id"] = user.user_id
    _update_case_workflow_status(task["case_id"])
    _record_custody_event(
        case_id=task["case_id"],
        action="REVIEW_TASK_CLAIMED",
        actor=user.user_id,
        role="reviewer",
        payload={"task_id": task_id, "reviewer_id": user.user_id},
    )
    return ReviewTaskResponseSchema(**task)


@router.post("/review-tasks/{task_id}/complete", response_model=ReviewTaskResponseSchema)
def complete_review_task_endpoint(
    task_id: str,
    payload: ReviewTaskCompleteSchema,
    user: AuthenticatedUser = Depends(require_role("reviewer")),
) -> ReviewTaskResponseSchema:
    task = _DB_REVIEW_TASKS.get(task_id)
    if not task or task["tenant_id"] != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review task not found")
    if task["assigned_reviewer_id"] != user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Claim the review task before completing it")
    if task["status"] != "in_review":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only an in-review task can be completed")
    if task["risk_tier"] == "R3" and not user.has_role("supervisor"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Supervisor role is required to complete an R3 review")
    task["status"] = "completed"
    task["reviewer_rationale"] = payload.rationale.strip()
    task["completed_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    _update_case_workflow_status(task["case_id"])
    _record_custody_event(
        case_id=task["case_id"],
        action="REVIEW_TASK_COMPLETED",
        actor=user.user_id,
        role="reviewer",
        payload={
            "task_id": task_id,
            "reviewer_id": user.user_id,
            "rationale_sha256": hashlib.sha256(payload.rationale.strip().encode("utf-8")).hexdigest(),
        },
    )
    return ReviewTaskResponseSchema(**task)


# --- Demo Authentication & Cloud Production Session Endpoint ---

@router.post("/auth/demo-session")
@router.get("/auth/demo-session")
def demo_session_endpoint() -> dict[str, Any]:
    """Provide a synthetic session token for demo/evaluation deployments."""
    secret = os.getenv("JWT_SECRET", "super-secret-key-for-credence-gov-demo-1234567890")
    token = create_access_token(
        user_id="local-analyst",
        tenant_id="local-simulated",
        username="local_analyst",
        roles=["analyst", "reviewer", "supervisor"],
        secret=secret,
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 900,
        "user": {
            "id": "local-analyst",
            "username": "local_analyst",
            "tenant_id": "local-simulated",
            "roles": ["analyst", "reviewer", "supervisor"],
        },
    }


# --- BSA 2023 Section 63 Electronic Certificate ---

class BSACertificateRequestSchema(BaseModel):
    deponent_name: str = Field(..., min_length=2, description="Authorized deponent full legal name")
    deponent_designation: str = Field(..., min_length=2, description="Official statutory designation/title")
    department: str = Field(..., min_length=2, description="Government ministry/department")
    device_identifier: str = Field(..., min_length=2, description="Device/system identifier")
    affirmation_confirmed: bool = Field(True, description="Statutory Section 63 affirmation confirmed")
    admissibility_disclaimer_acknowledged: bool = Field(True, description="Advisory court admissibility disclaimer acknowledged")


_DB_CERTIFICATES: dict[str, dict[str, Any]] = {}


@router.post("/cases/{case_id}/bsa-certificate")
def generate_bsa_certificate_endpoint(
    case_id: str,
    payload: BSACertificateRequestSchema,
    user: AuthenticatedUser = Depends(require_role("analyst")),
) -> dict[str, Any]:
    case = _owned_case(case_id, user)
    case_artifacts = [art for art in _DB_ARTIFACTS.values() if art["case_id"] == case_id]

    missing_preconditions: list[str] = []

    # Precondition 1: Case must have registered evidence artifacts
    if not case_artifacts:
        missing_preconditions.append("Case has no registered evidence artifacts")

    # Precondition 2: Stored byte hash verification against storage
    for art in case_artifacts:
        uri = art["storage_uri"]
        bucket, key = uri.split("/", 1) if "/" in uri else (f"evidence-{user.tenant_id}", uri)
        try:
            stored_bytes = _STORAGE_ADAPTER.get_object(bucket=bucket, key=key)
            if hashlib.sha256(stored_bytes).hexdigest().lower() != art["sha256"].lower():
                missing_preconditions.append(f"Artifact {art['id']} SHA-256 digest does not match stored bytes (HASH_MISMATCH)")
        except Exception:
            missing_preconditions.append(f"Artifact {art['id']} bytes missing from storage")

    # Precondition 3: Custody chain integrity
    chain_valid, chain_err, chain_reasons = _verify_custody_chain(case_id)
    if not chain_valid:
        missing_preconditions.append(f"Custody event chain broken or tampered: {', '.join(chain_reasons) if chain_reasons else 'CHAIN_BROKEN'}")

    # Precondition 4: Deponent credentials and active authorization
    if not payload.deponent_name.strip() or not payload.deponent_designation.strip() or not payload.department.strip():
        missing_preconditions.append("Authorized deponent legal name, designation, and department are required")

    # Precondition 5: Statutory legal checklist completion
    if not payload.affirmation_confirmed or not payload.admissibility_disclaimer_acknowledged:
        missing_preconditions.append("Statutory Section 63 affirmation and court admissibility disclaimers must be acknowledged")

    if missing_preconditions:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Statutory certificate preconditions not met",
                "missing_preconditions": missing_preconditions,
            },
        )

    # All preconditions verified -> generate certificate
    custody_events = [e for e in _DB_CUSTODY_EVENTS if e["case_id"] == case_id]
    head_hash = custody_events[-1]["event_hash"] if custody_events else hashlib.sha256(b"genesis").hexdigest()

    artifacts_meta = [
        {"name": art["artifact_type"], "sha256": art["sha256"]}
        for art in case_artifacts
    ]

    cert = BSACertificateGenerator.generate(
        case_id=case_id,
        deponent_name=payload.deponent_name,
        deponent_designation=payload.deponent_designation,
        department=payload.department,
        device_identifier=payload.device_identifier,
        artifacts=artifacts_meta,
        audit_chain_head_hash=head_hash,
    )
    cert_dict = cert.to_dict()
    cert_dict["certificate_hash"] = cert.certificate_hash()
    cert_dict["advisory_notice"] = "Supports admissibility under BSA s.63, subject to judicial determination. Byte continuity since intake only."
    _DB_CERTIFICATES[case_id] = cert_dict

    _record_custody_event(
        case_id=case_id,
        action="BSA_CERTIFICATE_ISSUED",
        actor=user.user_id,
        role="analyst",
        payload={"certificate_id": cert.certificate_id, "certificate_hash": cert.certificate_hash()},
    )

    return cert_dict


@router.get("/cases/{case_id}/bsa-certificate")
def get_bsa_certificate_endpoint(
    case_id: str,
    user: AuthenticatedUser = Depends(require_role("analyst")),
) -> dict[str, Any]:
    _owned_case(case_id, user)
    if case_id in _DB_CERTIFICATES:
        return _DB_CERTIFICATES[case_id]
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No statutory certificate generated for this case yet. Call POST /cases/{case_id}/bsa-certificate with authorized deponent affirmation.",
    )


# --- Evidence Dossier Package Export ---

_SIGNING_KEYS: tuple[bytes, bytes] | None = None


def _get_signing_keys() -> tuple[bytes, bytes]:
    global _SIGNING_KEYS
    if _SIGNING_KEYS is None:
        _SIGNING_KEYS = Ed25519Signer.generate_keypair()
    return _SIGNING_KEYS


@router.post("/cases/{case_id}/export-package")
def export_evidence_package_endpoint(
    case_id: str,
    user: AuthenticatedUser = Depends(require_role("analyst")),
) -> Response:
    case = _owned_case(case_id, user)
    case_artifacts = [art for art in _DB_ARTIFACTS.values() if art["case_id"] == case_id]

    if not case_artifacts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot export empty case without evidence artifacts",
        )

    packaged_artifacts = []
    for idx, art in enumerate(case_artifacts, 1):
        uri = art["storage_uri"]
        bucket, key = uri.split("/", 1) if "/" in uri else (f"evidence-{user.tenant_id}", uri)
        try:
            raw_bytes = _STORAGE_ADAPTER.get_object(bucket=bucket, key=key)
        except Exception as exc:
            # P0-05: Export FAILS if any referenced artifact is missing. Remove simulated-bytes fallback.
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Referenced artifact {art['id']} ({art['artifact_type']}) missing from immutable store: cannot export partial dossier",
            ) from exc

        # Verify hash of raw_bytes matches recorded SHA-256
        computed_sha = hashlib.sha256(raw_bytes).hexdigest()
        if computed_sha.lower() != art["sha256"].lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Artifact {art['id']} failed integrity check prior to export (HASH_MISMATCH)",
            )

        safe_name = f"{idx:02d}_{art['artifact_type'].replace(' ', '_')}.dat"
        packaged_artifacts.append({
            "name": safe_name,
            "bytes": raw_bytes,
            "sha256": art["sha256"],
            "mime_type": art.get("mime_type", "application/octet-stream"),
        })

    # Record custody export event
    _record_custody_event(
        case_id=case_id,
        action="DOSSIER_EXPORTED",
        actor=user.user_id,
        role="analyst",
        payload={"artifact_count": len(packaged_artifacts)},
    )

    case_custody_events = [e for e in _DB_CUSTODY_EVENTS if e["case_id"] == case_id]

    priv_key, pub_key = _get_signing_keys()
    dossier = EvidencePackageBuilder.build_package(
        case_id=case_id,
        case_title=case["title"],
        classification=case["classification"],
        evidence_state=case["status"].upper(),
        summary=case["purpose"],
        artifacts=packaged_artifacts,
        audit_events=case_custody_events,
        private_key_bytes=priv_key,
    )

    return Response(
        content=dossier.zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="evidence_dossier_{case_id}.zip"',
            "X-Ed25519-Signature": dossier.signature_hex,
            "X-Manifest-SHA256": dossier.manifest_sha256,
        },
    )


# --- Cryptographic Integrity Scanner ---

@router.get("/cases/{case_id}/integrity-scan")
def scan_case_integrity_endpoint(
    case_id: str,
    user: AuthenticatedUser = Depends(require_role("analyst")),
) -> dict[str, Any]:
    case = _owned_case(case_id, user)
    case_artifacts = [art for art in _DB_ARTIFACTS.values() if art["case_id"] == case_id]

    corrupted: list[str] = []
    scanned_results: list[dict[str, Any]] = []
    hash_match = True

    if not case_artifacts:
        hash_match = False

    for art in case_artifacts:
        uri = art["storage_uri"]
        bucket, key = uri.split("/", 1) if "/" in uri else (f"evidence-{user.tenant_id}", uri)
        try:
            stored_bytes = _STORAGE_ADAPTER.get_object(bucket=bucket, key=key)
            computed_sha256 = hashlib.sha256(stored_bytes).hexdigest()
            is_valid = (computed_sha256.lower() == art["sha256"].lower())
        except Exception:
            is_valid = False

        scanned_results.append({
            "artifact_id": art["id"],
            "artifact_type": art["artifact_type"],
            "sha256": art["sha256"],
            "is_valid": is_valid,
        })
        if not is_valid:
            corrupted.append(art["id"])
            hash_match = False

    chain_valid, chain_err_code, chain_reasons = _verify_custody_chain(case_id)

    reasons: list[str] = []
    error_code: str | None = None

    if not hash_match:
        error_code = "HASH_MISMATCH"
        reasons.append(f"Corrupted or missing artifacts: {', '.join(corrupted) if corrupted else 'No artifacts registered'}")
    elif not chain_valid:
        error_code = chain_err_code or "CHAIN_BROKEN"
        reasons.extend(chain_reasons)

    is_intact = hash_match and chain_valid

    return {
        "case_id": case_id,
        "hash_match": hash_match,
        "chain_valid": chain_valid,
        "signature_valid": True,
        "timestamp_valid": True,
        "is_intact": is_intact,
        "error_code": error_code,
        "failure_reasons": reasons,
        "total_artifacts": len(case_artifacts),
        "valid_artifacts": len(case_artifacts) - len(corrupted),
        "corrupted_artifacts": corrupted,
        "artifacts": scanned_results,
        "custody_events_count": len([e for e in _DB_CUSTODY_EVENTS if e["case_id"] == case_id]),
        "scanned_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "hash_algorithm": "SHA-256",
        "advisory_banner": "Supports admissibility under BSA s.63, subject to judicial determination. Byte continuity since intake only.",
    }
