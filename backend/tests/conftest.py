import pytest


@pytest.fixture(autouse=True)
def configure_test_jwt_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    # Authentication deliberately has no built-in development signing key.
    monkeypatch.setenv("JWT_SECRET", "test-only-secret-that-is-at-least-32-bytes")
