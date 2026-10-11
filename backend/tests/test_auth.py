import pytest
import datetime
import jwt
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.credence_gov.auth import (
    AuthenticatedUser,
    create_access_token,
    get_current_user,
    require_role,
)

app = FastAPI()


@app.get("/protected")
def protected_route(user: AuthenticatedUser = Depends(get_current_user)):
    return {"user_id": user.user_id, "tenant_id": user.tenant_id}


@app.get("/supervisor-only")
def supervisor_route(user: AuthenticatedUser = Depends(require_role("supervisor"))):
    return {"message": "Supervisor access granted"}


client = TestClient(app)


def test_missing_auth_header_returns_401() -> None:
    response = client.get("/protected")
    assert response.status_code == 401
    assert "Missing or malformed" in response.json()["detail"]


def test_invalid_token_returns_401() -> None:
    response = client.get("/protected", headers={"Authorization": "Bearer invalid.jwt.string"})
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]


def test_valid_token_authenticates_user() -> None:
    token = create_access_token(
        user_id="analyst-99",
        tenant_id="tenant-delhi",
        username="delhi_analyst",
        roles=["analyst"],
    )
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "analyst-99"
    assert data["tenant_id"] == "tenant-delhi"


def test_token_without_expiry_is_rejected() -> None:
    secret = "test-only-secret-that-is-at-least-32-bytes"
    token = jwt.encode({
        "sub": "analyst-99",
        "tenant_id": "tenant-delhi",
        "iss": "http://keycloak:8080/realms/credence-dev",
        "aud": "credence-api",
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }, secret, algorithm="HS256")
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_missing_jwt_secret_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JWT_SECRET")
    response = client.get("/protected", headers={"Authorization": "Bearer anything"})
    assert response.status_code == 503


def test_rbac_denies_unauthorized_role() -> None:
    analyst_token = create_access_token(
        user_id="analyst-99",
        tenant_id="tenant-delhi",
        username="delhi_analyst",
        roles=["analyst"],
    )
    # Analyst attempting to access supervisor endpoint
    response = client.get("/supervisor-only", headers={"Authorization": f"Bearer {analyst_token}"})
    assert response.status_code == 403
    assert "supervisor" in response.json()["detail"]

    # Supervisor token
    supervisor_token = create_access_token(
        user_id="sup-01",
        tenant_id="tenant-delhi",
        username="delhi_supervisor",
        roles=["analyst", "supervisor"],
    )
    response = client.get("/supervisor-only", headers={"Authorization": f"Bearer {supervisor_token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Supervisor access granted"
