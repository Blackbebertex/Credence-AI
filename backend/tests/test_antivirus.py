import pytest
from unittest.mock import Mock

from backend.credence_gov.antivirus import (
    ClamAVScanner,
    EICAR_TEST_SIGNATURE,
    ScanStatus,
)


def test_clean_payload_passes_only_after_daemon_confirms(monkeypatch: pytest.MonkeyPatch) -> None:
    sock = Mock()
    sock.recv.return_value = b"stream: OK\x00"
    sock.__enter__ = Mock(return_value=sock)
    sock.__exit__ = Mock(return_value=None)
    monkeypatch.setattr("backend.credence_gov.antivirus.socket.create_connection", lambda *_args, **_kwargs: sock)
    scanner = ClamAVScanner()
    clean_bytes = b"Official Department PDF Content"

    result = scanner.scan_bytes(clean_bytes)
    assert result.is_safe is True
    assert result.status == ScanStatus.CLEAN
    assert result.virus_name is None
    assert result.is_quarantined is False


def test_unavailable_scanner_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("backend.credence_gov.antivirus.socket.create_connection", Mock(side_effect=OSError("offline")))
    result = ClamAVScanner().scan_bytes(b"%PDF-1.4 fixture")
    assert result.status == ScanStatus.ERROR
    assert result.is_safe is False


def test_empty_payload_is_not_reported_clean() -> None:
    result = ClamAVScanner().scan_bytes(b"")
    assert result.status == ScanStatus.ERROR
    assert result.is_safe is False


def test_eicar_signature_triggers_quarantine() -> None:
    scanner = ClamAVScanner()
    malicious_bytes = b"Preceding normal content..." + EICAR_TEST_SIGNATURE + b"...tail bytes"

    result = scanner.scan_bytes(malicious_bytes)
    assert result.is_safe is False
    assert result.status == ScanStatus.INFECTED
    assert result.virus_name == "EICAR-Test-Signature"
    assert result.is_quarantined is True
    assert "quarantined" in result.details.lower()
