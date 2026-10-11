# CredenceAI-Gov

CredenceAI-Gov is a proposed evidence-first, advisory digital evidence platform. It organizes traceable evidence and human review; it does not issue a universal trust score, a real/fake verdict, or an autonomous enforcement action.

## Current status

This checkout contains the product blueprint, a draft requirements baseline, and a P0 foundation proposal. No application feature is currently implemented or validated. P0 is synthetic-data-only. Do not use it with real or sensitive evidence.

See [master development prompt](docs/MASTER_PROMPT.md), [requirements](docs/requirements/implementation-spec.md), [architecture](docs/architecture/architecture.md), [assumptions](docs/ASSUMPTIONS.md), and [threat model](docs/THREAT_MODEL.md).

## Prerequisites

- Docker Desktop with its Linux engine running and accessible to the current user.
- Git repository metadata for contribution history and CI provenance.
- After P0: Python 3.12, Node 22, and package tooling pinned in project lockfiles.

## P0 checkpoint

The intended local P0 commands are `docker compose --profile dev up -d --wait` and `make licences`. They have not been verified in this environment: the Docker client cannot access the Docker Desktop engine pipe, and this workspace is not currently a Git repository. Dependency image digests and license allowlist remain pending.

## Safety boundary

All fixtures and demo content must carry `SIMULATED`. External model calls and live search must remain disabled by default. Production/pilot handling is blocked pending the charter, hosting, identity, retention, key custody, legal and security decisions in `docs/COMPLIANCE_REGISTER.md`.
