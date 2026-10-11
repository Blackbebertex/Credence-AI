from __future__ import annotations

import socket
import struct
from dataclasses import dataclass
from enum import Enum


class ScanStatus(str, Enum):
    CLEAN = "clean"
    INFECTED = "infected"
    ERROR = "error"


EICAR_TEST_SIGNATURE = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


@dataclass(frozen=True)
class AntivirusScanResult:
    status: ScanStatus
    virus_name: str | None
    is_quarantined: bool
    details: str

    @property
    def is_safe(self) -> bool:
        return self.status == ScanStatus.CLEAN


class ClamAVScanner:
    def __init__(self, host: str = "127.0.0.1", port: int = 3310, timeout: float = 2.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def scan_bytes(self, data: bytes) -> AntivirusScanResult:
        if not data:
            return AntivirusScanResult(
                status=ScanStatus.ERROR,
                virus_name=None,
                is_quarantined=False,
                details="Empty payload cannot be scanned.",
            )

        # 1. Built-in immediate check for EICAR standard test signature
        if EICAR_TEST_SIGNATURE in data:
            return AntivirusScanResult(
                status=ScanStatus.INFECTED,
                virus_name="EICAR-Test-Signature",
                is_quarantined=True,
                details="Malware signature identified: EICAR-Test-Signature. File quarantined.",
            )

        # 2. Attempt live ClamAV daemon socket if reachable
        try:
            with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
                sock.sendall(b"zINSTREAM\0")
                chunk_size = 2048
                for i in range(0, len(data), chunk_size):
                    chunk = data[i : i + chunk_size]
                    sock.sendall(struct.pack("!I", len(chunk)) + chunk)
                sock.sendall(struct.pack("!I", 0))

                response = sock.recv(4096).decode("utf-8", errors="replace").strip().rstrip("\x00")
                if "FOUND" in response:
                    virus_name = response.split(":")[1].replace("FOUND", "").strip() if ":" in response else "Unknown-Threat"
                    return AntivirusScanResult(
                        status=ScanStatus.INFECTED,
                        virus_name=virus_name,
                        is_quarantined=True,
                        details=f"Live ClamAV daemon detected threat: {virus_name}",
                    )
                if response.endswith("OK"):
                    return AntivirusScanResult(
                        status=ScanStatus.CLEAN,
                        virus_name=None,
                        is_quarantined=False,
                        details="Live ClamAV scan clean.",
                    )
                return AntivirusScanResult(
                    status=ScanStatus.ERROR,
                    virus_name=None,
                    is_quarantined=False,
                    details="ClamAV returned an unrecognized scan response.",
                )
        except (OSError, TimeoutError) as exc:
            return AntivirusScanResult(
                status=ScanStatus.ERROR,
                virus_name=None,
                is_quarantined=False,
                details=f"ClamAV scan unavailable: {type(exc).__name__}.",
            )

        return AntivirusScanResult(
            status=ScanStatus.ERROR,
            virus_name=None,
            is_quarantined=False,
            details="ClamAV returned no complete scan result.",
        )
