# CredenceAI-Gov

CredenceAI-Gov is an evidence-first, advisory digital evidence platform prototype. It organizes traceable evidence and human review; it does not issue a universal trust score, a real/fake verdict, or an autonomous enforcement action.

## Current status

This checkout contains the product blueprint and a synthetic-only local prototype. Its dashboard connects to authenticated local endpoints for case listing and creation, artifact upload and metadata listing, and human-review task creation, claiming, and completion. The development server seeds five clearly labeled example cases, eight synthetic evidence records, and review tasks in pending, in-progress, and completed states. Analytical trends, provenance relationships, integrity outcomes, and activity remain clearly labeled deterministic illustrative fixtures. The development server keeps cases, artifact metadata, and review tasks in memory; do not use it with real or sensitive evidence.

See [master development prompt](docs/MASTER_PROMPT.md), [requirements](docs/requirements/implementation-spec.md), [architecture](docs/architecture/architecture.md), [assumptions](docs/ASSUMPTIONS.md), and [threat model](docs/THREAT_MODEL.md).

## Prerequisites

- Python 3.12 or newer.
- Git repository metadata is recommended for contribution history and CI provenance.

## Dockerless local API demo

The current checkout has no frontend or application service in Docker Compose. To run the dashboard and synthetic API together without Docker, install the Python project and start its loopback-only development server:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m backend.credence_gov.dev_server
```

Open `http://127.0.0.1:8000` for the browser dashboard or `http://127.0.0.1:8000/docs` for the API. The dashboard receives an ephemeral analyst/reviewer token from a development-only endpoint available to loopback clients; the token expires after 15 minutes and is not printed. The five demonstration cases are reseeded on each launch; new cases, uploads, and workflow changes are in memory and reset when the server stops. This is a local synthetic demo, not a durable application or a substitute for the approved identity, database, object storage, malware scanning, and worker services.

Stop the server with `Ctrl+C`.

## P0 checkpoint

`docker compose --profile dev up -d --wait` remains an optional infrastructure stack for local development. The Dockerless API demo above does not require it. Dependency image digests and license allowlist remain pending.

## Safety boundary

All fixtures and demo content must carry `SIMULATED`. External model calls and live search must remain disabled by default. Production/pilot handling is blocked pending the charter, hosting, identity, retention, key custody, legal and security decisions in `docs/COMPLIANCE_REGISTER.md`.
