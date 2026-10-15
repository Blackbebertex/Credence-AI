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
    artifacts = client.get(
        f"/api/v1/cases/{case_id}/artifacts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert artifacts.status_code == 200
    assert [item["id"] for item in artifacts.json()] == [art_data["id"]]


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


def test_artifact_listing_is_scoped_to_case_owner(client: TestClient) -> None:
    owner = create_access_token(user_id="artifact-owner", tenant_id="artifact-tenant", username="owner", roles=["analyst"])
    peer = create_access_token(user_id="artifact-peer", tenant_id="artifact-tenant", username="peer", roles=["analyst"])
    created = client.post("/api/v1/cases", headers={"Authorization": f"Bearer {owner}"}, json={
        "title": "Private evidence", "classification": "OFFICIAL", "purpose": "scope test", "as_of_date": "2026-10-12"
    })
    case_id = created.json()["id"]
    uploaded = client.post(f"/api/v1/cases/{case_id}/artifacts", headers={"Authorization": f"Bearer {owner}"}, json={
        "artifact_type": "pdf", "content_b64": "JVBERi0xLjQ=", "mime_type": "application/pdf"
    })
    assert uploaded.status_code == 201
    assert client.get("/api/v1/artifacts", headers={"Authorization": f"Bearer {owner}"}).json()[0]["id"] == uploaded.json()["id"]
    assert client.get("/api/v1/artifacts", headers={"Authorization": f"Bearer {peer}"}).json() == []
    assert client.get(f"/api/v1/cases/{case_id}/artifacts", headers={"Authorization": f"Bearer {peer}"}).status_code == 404


def test_human_review_workflow_enforces_roles_scope_and_transitions(client: TestClient) -> None:
    owner = create_access_token(user_id="review-owner", tenant_id="review-tenant", username="owner", roles=["analyst"])
    reviewer = create_access_token(user_id="reviewer-1", tenant_id="review-tenant", username="reviewer", roles=["reviewer"])
    other_reviewer = create_access_token(user_id="reviewer-2", tenant_id="review-tenant", username="other", roles=["reviewer"])
    outsider = create_access_token(user_id="review-outsider", tenant_id="elsewhere", username="outsider", roles=["reviewer"])
    owner_headers = {"Authorization": f"Bearer {owner}"}
    reviewer_headers = {"Authorization": f"Bearer {reviewer}"}
    created = client.post("/api/v1/cases", headers=owner_headers, json={
        "title": "Review workflow case", "classification": "OFFICIAL", "purpose": "workflow test", "as_of_date": "2026-10-12"
    })
    case_id = created.json()["id"]
    requested = client.post(f"/api/v1/cases/{case_id}/review-tasks", headers=owner_headers, json={"risk_tier": "R2"})
    assert requested.status_code == 201
    task_id = requested.json()["id"]
    assert requested.json()["status"] == "pending"
    assert client.get("/api/v1/review-tasks", headers={"Authorization": f"Bearer {outsider}"}).json() == []
    assert client.get(f"/api/v1/cases/{case_id}/review-tasks", headers=owner_headers).json()[0]["id"] == task_id
    assert client.post(f"/api/v1/review-tasks/{task_id}/claim", headers=owner_headers).status_code == 403

    claimed = client.post(f"/api/v1/review-tasks/{task_id}/claim", headers=reviewer_headers)
    assert claimed.status_code == 200
    assert claimed.json()["status"] == "in_review"
    case = client.get("/api/v1/cases", headers=owner_headers).json()[0]
    assert case["status"] == "in_review"
    assert client.post(f"/api/v1/review-tasks/{task_id}/complete", headers={"Authorization": f"Bearer {other_reviewer}"}, json={
        "rationale": "This reviewer did not claim the task."
    }).status_code == 403
    assert client.post(f"/api/v1/review-tasks/{task_id}/complete", headers=reviewer_headers, json={"rationale": "too short"}).status_code == 422
    completed = client.post(f"/api/v1/review-tasks/{task_id}/complete", headers=reviewer_headers, json={
        "rationale": "Reviewed the synthetic record and documented the workflow disposition."
    })
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    assert client.get("/api/v1/cases", headers=owner_headers).json()[0]["status"] == "review_completed"
    assert client.post(f"/api/v1/review-tasks/{task_id}/claim", headers=reviewer_headers).status_code == 409


def test_r3_review_completion_requires_supervisor_role(client: TestClient) -> None:
    owner = create_access_token(user_id="r3-owner", tenant_id="r3-tenant", username="owner", roles=["analyst"])
    reviewer = create_access_token(user_id="r3-reviewer", tenant_id="r3-tenant", username="reviewer", roles=["reviewer"])
    owner_headers = {"Authorization": f"Bearer {owner}"}
    reviewer_headers = {"Authorization": f"Bearer {reviewer}"}
    case = client.post("/api/v1/cases", headers=owner_headers, json={
        "title": "Critical review", "classification": "SECRET", "purpose": "R3 workflow test", "as_of_date": "2026-10-12"
    }).json()
    task = client.post(f"/api/v1/cases/{case['id']}/review-tasks", headers=owner_headers, json={"risk_tier": "R3"}).json()
    assert client.post(f"/api/v1/review-tasks/{task['id']}/claim", headers=reviewer_headers).status_code == 200
    response = client.post(f"/api/v1/review-tasks/{task['id']}/complete", headers=reviewer_headers, json={
        "rationale": "The synthetic high impact case was reviewed and rationale recorded."
    })
    assert response.status_code == 403


def test_demo_session_endpoint(client: TestClient) -> None:
    response = client.post("/api/v1/auth/demo-session")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "local_analyst"


def test_bsa_certificate_and_integrity_and_export(client: TestClient) -> None:
    token = create_access_token(user_id="cert-analyst", tenant_id="cert-tenant", username="cert_user", roles=["analyst"])
    headers = {"Authorization": f"Bearer {token}"}

    case = client.post("/api/v1/cases", headers=headers, json={
        "title": "Certificate & Export Test Case",
        "classification": "OFFICIAL",
        "purpose": "Verifying BSA s.63 certificate and dossier export",
        "as_of_date": "2026-10-15",
    }).json()

    # Upload an artifact
    upload = client.post(
        f"/api/v1/cases/{case['id']}/artifacts",
        headers=headers,
        json={
            "artifact_type": "inspection_report",
            "content_b64": base64.b64encode(b"%PDF-1.4 simulated document").decode(),
            "mime_type": "application/pdf",
        },
    )
    assert upload.status_code == 201

    # Generate BSA Section 63 certificate
    cert_res = client.post(f"/api/v1/cases/{case['id']}/bsa-certificate", headers=headers, json={
        "deponent_name": "Test Officer",
        "deponent_designation": "Forensic Custodian",
        "department": "Evidence Cyber Cell",
        "device_identifier": "SECURE-BOX-01",
    })
    assert cert_res.status_code == 200
    cert_data = cert_res.json()
    assert cert_data["case_id"] == case["id"]
    assert "Section 63" in cert_data["affirmation_statement"]
    assert "certificate_hash" in cert_data

    # Integrity scan
    scan_res = client.get(f"/api/v1/cases/{case['id']}/integrity-scan", headers=headers)
    assert scan_res.status_code == 200
    scan_data = scan_res.json()
    assert scan_data["is_intact"] is True
    assert scan_data["total_artifacts"] == 1

    # Export signed package
    export_res = client.post(f"/api/v1/cases/{case['id']}/export-package", headers=headers)
    assert export_res.status_code == 200
    assert export_res.headers["content-type"] == "application/zip"
    assert "X-Ed25519-Signature" in export_res.headers
    assert len(export_res.content) > 100
