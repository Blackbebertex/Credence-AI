import pytest
from fastapi.testclient import TestClient

from backend.credence_gov.app import create_app
from backend.credence_gov.auth import create_access_token


@pytest.fixture
def client() -> TestClient:
    app = create_app()

    # Route to trigger test exceptions
    @app.get("/test/value-error")
    def trigger_value_error():
        raise ValueError("Invalid case parameter provided")

    @app.get("/test/permission-error")
    def trigger_permission_error():
        raise PermissionError("User lacks elevation clearance")

    return TestClient(app)


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "credence-gov"
    assert "timestamp" in data


def test_value_error_rfc7807_handler(client: TestClient) -> None:
    response = client.get("/test/value-error")
    assert response.status_code == 400
    assert response.headers["content-type"] == "application/problem+json"
    data = response.json()
    assert data["title"] == "Bad Request"
    assert data["status"] == 400
    assert "Invalid case parameter" in data["detail"]
    assert data["instance"] == "/test/value-error"


def test_permission_error_rfc7807_handler(client: TestClient) -> None:
    response = client.get("/test/permission-error")
    assert response.status_code == 403
    assert response.headers["content-type"] == "application/problem+json"
    data = response.json()
    assert data["title"] == "Forbidden"
    assert data["status"] == 403
    assert "elevation clearance" in data["detail"]


def test_cors_does_not_allow_arbitrary_origin(client: TestClient) -> None:
    response = client.options("/api/v1/cases", headers={
        "Origin": "https://attacker.invalid",
        "Access-Control-Request-Method": "POST",
    })
    assert "access-control-allow-origin" not in response.headers
    assert response.headers.get("access-control-allow-credentials") != "true"


def test_cors_rejects_wildcard_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "*")
    with pytest.raises(ValueError, match="explicit origins"):
        create_app()


def test_frontend_and_backend_work_together_in_dev_mode() -> None:
    token = create_access_token(
        user_id="browser-analyst",
        tenant_id="browser-demo",
        username="browser_analyst",
        roles=["analyst"],
    )
    client = TestClient(create_app(dev_token=token))

    page = client.get("/")
    session = client.get("/api/v1/dev-session")
    assert page.status_code == 200
    assert "Create a case" in page.text
    assert "Add a synthetic artifact" in page.text
    assert session.json()["access_token"] == token

    headers = {"Authorization": f"Bearer {session.json()['access_token']}"}
    created = client.post("/api/v1/cases", headers=headers, json={
        "title": "Browser integration fixture",
        "classification": "OFFICIAL",
        "purpose": "synthetic integration check",
        "as_of_date": "2026-10-12",
    })
    listed = client.get("/api/v1/cases", headers=headers)
    assert created.status_code == 201
    assert any(case["id"] == created.json()["id"] for case in listed.json())

    artifact = client.post(
        f"/api/v1/cases/{created.json()['id']}/artifacts",
        headers=headers,
        json={
            "artifact_type": "synthetic_pdf",
            "content_b64": "JVBERi0xLjQKJSBEZW1vIGZpbGU=",
            "mime_type": "application/pdf",
        },
    )
    assert artifact.status_code == 201
    assert artifact.json()["case_id"] == created.json()["id"]


def test_dashboard_has_reference_layout_and_supported_workflow_controls() -> None:
    page = TestClient(create_app()).get("/")
    assert page.status_code == 200
    assert page.text.count('class="kpi"') == 5
    assert "Cases & recent activity" in page.text
    assert "Evidence provenance graph" in page.text
    assert "Add evidence" in page.text
    assert "LIVE API" in page.text
    assert "SIMULATED" in page.text
    assert "@media(max-width:700px)" in page.text
