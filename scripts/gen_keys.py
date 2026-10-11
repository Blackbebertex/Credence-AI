"""Generate local development key material; never use for production."""

from __future__ import annotations

import os
import secrets
from pathlib import Path


def main() -> None:
    key_dir = Path(".local-keys")
    key_dir.mkdir(mode=0o700, exist_ok=True)
    key = key_dir / "dev-kek.bin"
    if key.exists():
        raise SystemExit("Refusing to overwrite existing .local-keys/dev-kek.bin")
    key.write_bytes(secrets.token_bytes(32))
    try:
        os.chmod(key, 0o600)
    except OSError:
        pass
    print("Generated local-only KEK at .local-keys/dev-kek.bin; do not commit or use in production.")


if __name__ == "__main__":
    main()
