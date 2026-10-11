# Dependency and image proposal

**Status:** P0 proposal, not yet resolved or vulnerability-cleared. Exact pins must be written to lockfiles and container references by digest after a working Docker/registry environment is available. Do not deploy this proposal to production.

## Runtime and build tools

| Component | Proposed pin | P0 use | Notes |
|---|---|---|---|
| CPython | 3.12.15 | API and workers | Required minor version; this workstation currently has Python 3.14.8, so host execution is not representative. |
| FastAPI | 0.143.0 | API | Candidate release observed on PyPI on 2026-10-09; resolve compatibility lock before use. |
| Pydantic | 2.13.0 | Schemas | Candidate current v2 release; compatibility must be checked with FastAPI. |
| SQLAlchemy | 2.1.4 | Async ORM | Candidate release observed 2026-10-07; prompt requires SQLAlchemy 2. |
| Alembic | 1.20.0 | Migrations | Candidate docs version; pin and resolve with SQLAlchemy before application schema work. |
| PostgreSQL | 16.15-bookworm | Database | Pin to `sha256:b59011e348abadc71f141c547299377f5e37420b65f609f2518caf8569940212` only for linux/amd64; verify registry manifest before use. |
| pgvector | 0.8.1 | PostgreSQL extension | Proposed exact tag; image digest/build provenance pending. |
| Redis | 7.4.11-alpine | Queue/cache | Proposed exact tag; image digest pending. |
| Celery | 5.5.3 | Background work | Exact candidate; resolve with current Python 3.12 dependency tree. |
| Keycloak | 26.7.4 | OIDC development identity | Exact server release; image digest pending. Dev realm only. |
| MinIO | RELEASE.2025-10-15T17-29-55Z | S3-compatible local development | **Not production-approved:** upstream OSS repository archived 2026-04-25; image availability and license/maintenance review required. |
| ClamAV | 1.4.6-debian13-slim | Malware scanning | Exact candidate; digest/platform verification pending. |
| Node.js | 22.23.2 | Frontend build | Exact Node version proposed; frontend will use React 18 per fixed prompt. |
| React | 18.3.1 | UI | Exact React 18 pin. |
| Vite | 7.1.12 | UI build | Candidate exact pin; resolve with Node 22 and plugin versions. |
| TypeScript | 5.9.3 | UI typing | Exact candidate. |
| GitHub Actions checkout | 3d3c42e5aac5ba805825da76410c181273ba90b1 (v7.0.1) | CI source checkout | Full commit SHA pin; repository is not configured here. |

## Deferred pinned dependencies

The remaining prompt components must be pinned before the phase that introduces them: `python-magic`, `cryptography`, `httpx`, `structlog`, `prometheus-client`, OpenTelemetry packages, pytest/pytest-asyncio/Hypothesis/testcontainers/Playwright/axe, `pyHanko`, `pikepdf`, `pdfminer.six`, `pypdfium2`, `imagehash`, `sentence-transformers`, ExifTool, C2PA tooling, Prometheus/Grafana/Loki/OTel Collector, proxy, fetcher, and sandbox base images. P0 will not claim their pins or licenses are resolved without lockfile resolution, upstream checks, and image-digest verification.

## License and supply-chain gates

- Add every direct/transitive runtime dependency and license to the generated inventory; maintain `infra/licence-allowlist.txt` with review reason.
- Run `pip-licenses`, `license-checker`, `pip-audit`, `npm audit`, and an image scanner in CI after lockfiles and container images exist.
- Pin Python/npm lockfiles and image digests; record SBOMs for release artifacts.
- MinIO's upstream project is AGPL-3.0 and archived; obtain counsel/procurement review and decide whether to build from source, procure supported terms, or choose a different S3-compatible object store before production.
