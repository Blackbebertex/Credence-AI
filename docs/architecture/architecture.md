# CredenceAI-Gov architecture proposal

**Status:** Proposed, based on `CredenceAI-Gov_Master_Blueprint.md`; not deployment-approved.  
**Primary constraint:** Do not accept real or sensitive pilot evidence until R0 decisions and security/legal approvals are complete.

## System shape

Start with a modular monolith and isolated workers. Keep four logical planes within clear module/API boundaries:

```text
Browser ── OIDC/SAML identity ── FastAPI API
                                  │
               ┌──────────────────┼─────────────────┐
          Control             Evidence          Review
       tenant/RBAC/policy   cases/artifacts     matrix/queue
                                  │
                         Intelligence workers
                   retrieval/provenance/sandboxed tools
                                  │
       PostgreSQL ── S3-compatible object store ── Redis/Celery
```

The API owns authorization, validation, lifecycle transitions, and policy invocation. Workers receive scoped immutable references, have bounded resources and no network by default, and return versioned findings; they do not write decisions directly. PostgreSQL is authoritative for relational state. Object storage holds originals and derived artifacts. Redis/Celery is a replaceable job transport, not the record of truth.

## Candidate technology

| Area | Candidate | Qualification |
|---|---|---|
| UI | React + TypeScript | Confirm actual repo and GIGW/WCAG procurement needs. |
| API | FastAPI modular monolith | Preferred if existing backend checkout can be recovered and passes audit; otherwise create conventional Python package. |
| Identity | Keycloak via OIDC/SAML | Pilot identity authority and hosting not selected. Do not implement custom password IAM. |
| Relational data | PostgreSQL; pgvector only if retrieval evaluation supports it | Start with relational/full-text capabilities; vector extension is not mandatory. |
| Jobs | Celery + Redis | Use only for real asynchronous work; define idempotency, timeout, retry, cancellation, and dead-letter handling. |
| Evidence store | S3-compatible object storage with object lock | Select based on approved hosting/procurement and tested retention semantics. |
| File safety | ClamAV and sandboxed parsers | Versions/licenses and isolation must be reviewed. |
| Provenance | ExifTool, C2PA-compatible tooling, PDF signature validation | Findings describe indicators and limitations, never proof of authenticity. |
| Observability | OpenTelemetry with Prometheus/Grafana/Loki or existing government stack | Avoid duplicating approved central logging/monitoring. |
| Local deployment | Docker Compose | Development only; production topology follows measured HA and security needs. |

No microservices, Kubernetes, broker, GPU, hosted model, or external cloud service is assumed. Every dependency requires license, maintenance, security, and data-flow review.

## Core data model (logical, pending workflow decision)

- **Tenant, User, Role, Permission:** identity and scoped access.
- **Case, CaseAccessGrant:** owner, tenant, classification, workflow type, status, retention class, timestamps.
- **Artifact, DerivedArtifact:** object reference, media type, byte length, SHA-256, encryption/key reference, parent artifact, tool/version.
- **CustodyEvent, AuditEvent:** actor/service, action, time, source context where approved, reason, prior event hash, event hash; avoid retaining unnecessary personal/network data.
- **Source, SourceSnapshot:** canonical identity, tier/flags, publication/effective/supersession dates, fetched time, content hash and immutable object reference.
- **Claim, EvidenceSpan, Finding:** claim text/as-of date, source snapshot and exact span offsets, stance/state, limitations, analyzer and model version.
- **AnalysisJob, AnalyzerManifest:** lifecycle, idempotency key, resource/time limits, schema version, model hash and validity envelope.
- **PolicyPack, PolicyDecision, ReviewTask, ReviewerDisposition:** versioned rule inputs/outcome, assigned reviewer, rationale, override and supervisor approval.
- **EvidencePackage, RetentionClass, LegalHold:** export manifest/signature reference, approved retention schedule, hold authority and lifecycle.

Database constraints must enforce tenant ownership and referential integrity. Do not rely solely on application filters. PostgreSQL row-level security is a candidate defense-in-depth control, not a substitute for endpoint authorization and cross-tenant tests.

## Security and evidence flow

1. Authenticate and authorize user; establish tenant, case access, classification, and approved retention class.
2. Validate URL or file type, size, signature, dimensions, and parser safety. Quarantine and scan hostile uploads.
3. Create artifact record, compute SHA-256, encrypt and store original immutably, then append custody event. Analysis is forbidden until these steps succeed.
4. Enqueue a scoped job with idempotency key. Worker reads only the referenced artifact, runs within resource/time limits, and emits schema-validated findings plus provenance.
5. API verifies findings and citation spans, applies versioned deterministic policy, creates review task if required, and records all transitions.
6. Human disposition and rationale are linked to the exact findings and policy version.
7. Export package with hashes, findings, policy/review history, audit excerpt, and signed manifest once key custody is approved.

Sensitive identity and case data are encrypted in transit and at rest. Secrets are external to source control. Logs use identifiers and operational fields, not raw evidence or prompts. Egress is denied by default. Hosted inference is disabled until approved. Audit and retention behavior must be reconciled with records law before real data.

## API boundary

Initial resource families after G0: `/api/v1/cases`, `/artifacts`, `/analyses`, `/evidence`, `/reviews`, `/audit`, `/packages`, `/health`. Every endpoint must document authentication, permission, tenant scope, request/response schema, validation, error format, rate limit, audit event, and tests. Use consistent RFC-style problem details, cursor pagination where needed, idempotency for submissions, and additive schema evolution. Never expose raw filesystem paths or object-store credentials.

## Operations and observability

- Environments: development, staging, production with independent credentials and data.
- Local setup: Compose, explicit `.env.example`, migration and synthetic seed commands; no production data in fixtures.
- Health: liveness/readiness, database/object-store/queue dependency checks, worker heartbeat.
- Metrics: request latency/error rate, queue age/depth, worker failures, storage, analyzer version, cost-per-case inputs. Do not label metrics with sensitive/case-identifying values.
- Backup: encrypted backups, recovery keys, documented restore runbook, measured RPO/RTO. Blueprint's 15-minute/4-hour targets are proposals pending owner approval.
- Deployment: reviewed migrations, staging smoke/evaluation, controlled production release and rollback. Government-specific hosting, audit log export, incident response and CERT-In obligations need security-owner confirmation.

## Architecture decisions still open

1. Reuse versus replace an existing CredenceAI codebase: this checkout has no source; locate/audit the claimed original repository before deciding.
2. Lead workflow and language: G0 answer-availability test and pilot owner decision.
3. Hosting/air-gap and whether any case content can leave the network.
4. Identity integration and tenant topology.
5. Object storage, key management, signing-key custody, and backup operator.
6. Retention classes, legal hold, audit retention and package legal status.
7. Register availability and approved source corpus ownership.
8. Pilot workload, latency/availability objectives, staffing, budget, procurement and support model.

## Phase 4 implementation entry criteria

Before implementing production-like pilot flows, record decisions for items 2–8 above, complete a threat/data-classification review, secure a counsel-cleared advisory charter, and approve acceptance thresholds. A synthetic-data-only local skeleton can follow earlier only if it does not encode unresolved workflows or claim production readiness.
