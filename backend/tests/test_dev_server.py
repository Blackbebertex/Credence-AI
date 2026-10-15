import sys
from types import ModuleType

from fastapi.testclient import TestClient

from backend.credence_gov import dev_server


def test_dockerless_launcher_uses_loopback_and_ephemeral_analyst_token(monkeypatch, capsys):
    captured = {}
    fake_uvicorn = ModuleType("uvicorn")
    fake_uvicorn.run = lambda app, **kwargs: captured.update(app=app, **kwargs)
    monkeypatch.setitem(sys.modules, "uvicorn", fake_uvicorn)
    monkeypatch.setattr(sys, "argv", ["credence-dev", "--port", "8765"])
    monkeypatch.delenv("JWT_SECRET", raising=False)

    dev_server.main()

    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 8765
    assert captured["log_level"] == "info"
    assert captured["app"].title == "CredenceAI-Gov API"
    output = capsys.readouterr().out
    assert "127.0.0.1:8765/docs" in output
    assert "Synthetic analyst token" not in output
    assert "127.0.0.1:8765" in output
    assert "Loaded 5 clearly labeled synthetic demonstration cases." in output

    with TestClient(captured["app"]) as client:
        token = client.get("/api/v1/dev-session").json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        cases = client.get("/api/v1/cases", headers=headers).json()
        artifacts = client.get("/api/v1/artifacts", headers=headers).json()
        tasks = client.get("/api/v1/review-tasks", headers=headers).json()
    assert len(cases) == 5
    assert all("[SIMULATED]" in case["title"] for case in cases)
    assert len(artifacts) == 8
    assert {artifact["mime_type"] for artifact in artifacts} == {"application/pdf", "image/png", "text/plain"}
    assert {task["status"] for task in tasks} == {"pending", "in_review", "completed"}


def test_dockerless_launcher_rejects_invalid_port(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["credence-dev", "--port", "70000"])
    try:
        dev_server.main()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("invalid port should be rejected")
