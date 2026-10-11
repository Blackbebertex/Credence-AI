from __future__ import annotations

import uuid
import base64
import binascii
import os
from dataclasses import dataclass
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from .auth import AuthenticatedUser, require_role
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


# In-memory repository for standalone router testability
_DB_CASES: dict[str, dict[str, Any]] = {}
_DB_ARTIFACTS: dict[str, dict[str, Any]] = {}
_STORAGE_ADAPTER: StorageAdapter = LocalStorageAdapter()
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024


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
        "schema_version": 1,
        "banner": "Decision support. Not a finding of fact.",
    }
    _DB_CASES[case_id] = record
    return CaseResponseSchema(**record)


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
    }
    _DB_ARTIFACTS[art_id] = art_record
    return ArtifactResponseSchema(**art_record)
