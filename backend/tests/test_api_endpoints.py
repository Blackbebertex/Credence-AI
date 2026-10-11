import pytest
import base64
from backend.credence_gov import api as api_module
from fastapi.testclient import TestClient

from backend.credence_gov.app import create_app
from backend.credence_gov.auth import create_access_token


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_create_case_unauthenticated_fails(client: TestClient) -> None:
    response = client.post(
        "/api/v1/cases",
        json={
            "title": "Unauthenticated Case",
            "classification": "CONFIDENTIAL",
            "purpose": "Test",
            "as_of_date": "2026-10-01",
        },
    )
    assert response.status_code == 401


def test_create_case_authenticated_succeeds(client: TestClient) -> None:
    token = create_access_token(
        user_id="analyst-501",
        tenant_id="tenant-punjab",
        username="punjab_analyst",
        roles=["analyst"],
    )

    response = client.post(
        "/api/v1/cases",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Disputed Subsidy Gazette",
            "classification": "SECRET",
            "purpose": "Authenticity audit",
            "as_of_date": "2026-10-01",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Disputed Subsidy Gazette"
    assert data["tenant_id"] == "tenant-punjab"
    assert data["owner_id"] == "analyst-501"
    assert data["banner"] == "Decision support. Not a finding of fact."
    assert "id" in data


def test_case_list_is_scoped_to_authenticated_owner(client: TestClient) -> None:
    owner = create_access_token(user_id="owner-list", tenant_id="tenant-list", username="owner", roles=["analyst"])
    peer = create_access_token(user_id="peer-list", tenant_id="tenant-list", username="peer", roles=["analyst"])
    created = client.post("/api/v1/cases", headers={"Authorization": f"Bearer {owner}"}, json={
        "title": "Owner case", "classification": "OFFICIAL", "purpose": "test", "as_of_date": "2026-10-01"
    })
    owner_cases = client.get("/api/v1/cases", headers={"Authorization": f"Bearer {owner}"})
    peer_cases = client.get("/api/v1/cases", headers={"Authorization": f"Bearer {peer}"})
    assert owner_cases.status_code == 200
    assert [case["id"] for case in owner_cases.json()] == [created.json()["id"]]
    assert peer_cases.json() == []


def test_upload_artifact_and_verify_immutability(client: TestClient) -> None:
    token = create_access_token(
        user_id="analyst-501",
        tenant_id="tenant-punjab",
        username="punjab_analyst",
        roles=["analyst"],
    )

    # 1. Create Case
    create_resp = client.post(
        "/api/v1/cases",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Artifact Intake Case",
            "classification": "CONFIDENTIAL",
            "purpose": "Artifact upload test",
            "as_of_date": "2026-10-01",
        },
    )
    case_id = create_resp.json()["id"]

    # 2. Upload Artifact
    upload_resp = client.post(
        f"/api/v1/cases/{case_id}/artifacts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "artifact_type": "official_pdf",
            "content_b64": "JVBERi0xLjQKJVRlc3QgUERGIFBheWxvYWQ=",
            "mime_type": "application/pdf",
        },
    )
    assert upload_resp.status_code == 201
    art_data = upload_resp.json()
    assert art_data["case_id"] == case_id
    assert art_data["tenant_id"] == "tenant-punjab"
    assert art_data["is_immutable"] is True
    assert len(art_data["sha256"]) == 64


def test_cross_tenant_artifact_upload_blocked(client: TestClient) -> None:
    punjab_token = create_access_token(
        user_id="analyst-punjab",
        tenant_id="tenant-punjab",
        username="punjab_analyst",
        roles=["analyst"],
    )
    haryana_token = create_access_token(
        user_id="analyst-haryana",
        tenant_id="tenant-haryana",
        username="haryana_analyst",
        roles=["analyst"],
    )

    # Punjab analyst creates case
    create_resp = client.post(
        "/api/v1/cases",
        headers={"Authorization": f"Bearer {punjab_token}"},
        json={
            "title": "Punjab Private Case",
            "classification": "TOP_SECRET",
            "purpose": "State matters",
            "as_of_date": "2026-10-01",
        },
    )
    case_id = create_resp.json()["id"]

    # Haryana analyst attempts to upload artifact to Punjab case
    cross_upload = client.post(
        f"/api/v1/cases/{case_id}/artifacts",
        headers={"Authorization": f"Bearer {haryana_token}"},
        json={
            "artifact_type": "pdf",
            "content_b64": "illegal_cross_tenant_bytes",
            "mime_type": "application/pdf",
        },
    )
    assert cross_upload.status_code == 404


def test_same_tenant_non_owner_cannot_upload(client: TestClient) -> None:
    owner = create_access_token(user_id="owner", tenant_id="tenant-a", username="owner", roles=["analyst"])
    peer = create_access_token(user_id="peer", tenant_id="tenant-a", username="peer", roles=["analyst"])
    created = client.post("/api/v1/cases", headers={"Authorization": f"Bearer {owner}"}, json={
        "title": "Private", "classification": "OFFICIAL", "purpose": "test", "as_of_date": "2026-10-01"
    })
    response = client.post(f"/api/v1/cases/{created.json()['id']}/artifacts", headers={"Authorization": f"Bearer {peer}"}, json={
        "artifact_type": "pdf", "content_b64": base64.b64encode(b"%PDF-1.4 fixture").decode(), "mime_type": "application/pdf"
    })
    assert response.status_code == 404


def test_upload_rejects_invalid_base64_and_mime_mismatch(client: TestClient) -> None:
    token = create_access_token(user_id="uploader", tenant_id="tenant-upload", username="uploader", roles=["analyst"])
    created = client.post("/api/v1/cases", headers={"Authorization": f"Bearer {token}"}, json={
        "title": "Upload", "classification": "OFFICIAL", "purpose": "test", "as_of_date": "2026-10-01"
    })
    url = f"/api/v1/cases/{created.json()['id']}/artifacts"
    headers = {"Authorization": f"Bearer {token}"}
    invalid = client.post(url, headers=headers, json={"artifact_type": "pdf", "content_b64": "%%%", "mime_type": "application/pdf"})
    mismatch = client.post(url, headers=headers, json={"artifact_type": "pdf", "content_b64": base64.b64encode(b"not pdf").decode(), "mime_type": "application/pdf"})
    assert invalid.status_code == 400
    assert mismatch.status_code == 415


def test_upload_enforces_decoded_byte_limit(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    token = create_access_token(user_id="limited", tenant_id="tenant-limit", username="limited", roles=["analyst"])
    created = client.post("/api/v1/cases", headers={"Authorization": f"Bearer {token}"}, json={
        "title": "Limit", "classification": "OFFICIAL", "purpose": "test", "as_of_date": "2026-10-01"
    })
    monkeypatch.setattr(api_module, "MAX_UPLOAD_BYTES", 4)
    response = client.post(f"/api/v1/cases/{created.json()['id']}/artifacts", headers={"Authorization": f"Bearer {token}"}, json={
        "artifact_type": "pdf", "content_b64": base64.b64encode(b"%PDF-1.4").decode(), "mime_type": "application/pdf"
    })
    assert response.status_code == 413


def test_create_case_requires_analyst_role(client: TestClient) -> None:
    token = create_access_token(user_id="auditor", tenant_id="tenant-audit", username="auditor", roles=["auditor"])
    response = client.post("/api/v1/cases", headers={"Authorization": f"Bearer {token}"}, json={
        "title": "Audit", "classification": "OFFICIAL", "purpose": "test", "as_of_date": "2026-10-01"
    })
    assert response.status_code == 403
