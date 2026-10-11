"""Loopback-only, synthetic-data API launcher for Dockerless development."""

from __future__ import annotations

import argparse
import os
import secrets

from .app import create_app
from .auth import create_access_token


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the synthetic CredenceAI-Gov API locally")
    parser.add_argument("--port", type=int, default=8000, help="Local HTTP port (default: 8000)")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")

    # This entry point is explicitly for disposable local demos. Never load a
    # configured/deployment secret into it or bind it beyond loopback.
    jwt_secret = secrets.token_urlsafe(48)
    os.environ["JWT_SECRET"] = jwt_secret
    token = create_access_token(
        user_id="local-analyst",
        tenant_id="local-simulated",
        username="local_analyst",
        roles=["analyst"],
        secret=jwt_secret,
    )

    print("CredenceAI-Gov synthetic API: http://127.0.0.1:%s" % args.port)
    print("Interactive API docs: http://127.0.0.1:%s/docs" % args.port)
    print("Local demo token is available only to loopback clients and expires in 15 minutes.")
    print("Data is in memory and will be lost when this process stops. Do not use real evidence.")

    import uvicorn

    uvicorn.run(
        create_app(dev_token=token),
        host="127.0.0.1",
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
