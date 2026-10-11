import sys
from types import ModuleType

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


def test_dockerless_launcher_rejects_invalid_port(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["credence-dev", "--port", "70000"])
    try:
        dev_server.main()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("invalid port should be rejected")
