# 02-PHASES.md
**Project:** CredenceAI-Gov (`Blackbebertex/Credence-AI`)  
**Scope:** Phased Implementation Roadmap, Quality Gates, Rollback Plans, and Validation Protocols  
**Traceability:** Linked directly to `00-MASTER-ASSESSMENT-AND-ARCHITECTURE.md` and `01-TODO.md`  
**Status:** Baseline Established  

---

## Phase Execution Strategy
Implementation must proceed sequentially from Phase 0 to Phase 5. Under no circumstances may a subsequent phase begin until all Exit Criteria of the preceding phase are independently proven and verified by automated test output.

---

### Phase 0: Discovery, Environment Alignment & Packaging Hygiene

#### 1. Goal
Establish a reliable, reproducible Python 3.12 developer and build environment with explicit package definitions and an abstract storage adapter that isolates the platform from archived MinIO dependencies.

#### 2. Tasks Included
- `TASK-001`: Python Runtime & Dependency Environment Alignment (`pyproject.toml`)
- `TASK-002`: Abstract Storage Adapter Specification (`backend/credence_gov/storage_adapter.py`)

#### 3. Deliverables
- `pyproject.toml` with strict pins matching `docs/DEPENDENCIES.md`.
- `backend/credence_gov/storage_adapter.py` defining `StorageAdapter` protocol, `LocalStorageAdapter`, and S3 abstraction.
- Unit tests verifying package installation and storage adapter behavior.

#### 4. Exit Criteria & Quality Gates
- `pip install -e .` completes with zero build errors.
- `python -m pytest` passes 100% of existing and new test cases.
- No direct hardcoded imports of `minio` in domain logic.

#### 5. Rollback Plan
- Revert modifications to `pyproject.toml` and remove `storage_adapter.py` via Git. Restore baseline `backend/credence_gov/storage.py`.

#### 6. Validation Protocol
```bash
python -m pip install -e .
python -m pytest backend/tests/
```

---

### Phase 1: Persistence Foundation & Data Integrity Core

#### 1. Goal
Transition the system from ephemeral in-memory Python dictionaries to persistent relational PostgreSQL storage with strict schema models, Alembic migrations, PostgreSQL Row-Level Security (RLS), and atomic audit hash-chain writes.

#### 2. Tasks Included
- `TASK-003`: Relational Database Schema & SQLAlchemy 2 Models (`backend/credence_gov/models.py`)
- `TASK-004`: Alembic Migration Pipeline Baseline (`backend/migrations/`)
- `TASK-005`: PostgreSQL Row-Level Security (RLS) Policies
- `TASK-006`: Persistent Hash-Chain Audit Ledger Integration (`backend/credence_gov/audit.py`)

#### 3. Deliverables
- Declarative SQLAlchemy 2 models for `Tenant`, `User`, `Case`, `Artifact`, `AuditEvent`, `PolicyDecision`, and `ReviewTask`.
- Alembic migration `0001_initial_schema.py` and rollback script.
- RLS migration establishing `app.current_tenant` security boundaries.
- Unit and integration tests verifying transactional persistence and hash-chain tampering detection.

#### 4. Exit Criteria & Quality Gates
- Schema creation succeeds on SQLite/PostgreSQL without foreign key cycles or syntax errors.
- Committing a case and artifact atomically appends an immutable `AuditEvent` with verified `event_hash`.
- Tampering with any historical audit row causes chain verification to fail.

#### 5. Rollback Plan
- Run `alembic downgrade -1` to roll back database DDL. Revert `models.py` and restore in-memory stubs if database engine initialization fails.

#### 6. Validation Protocol
```bash
python -m pytest backend/tests/test_phase6_storage.py backend/tests/test_phase7_audit.py
```

---

### Phase 2: Core Domain API & Zero Trust Middleware

#### 1. Goal
Expose authenticated, tenant-isolated REST API endpoints under FastAPI with strict Pydantic v2 validation, RFC 7807 problem details, and Keycloak OIDC JWT verification.

#### 2. Tasks Included
- `TASK-007`: FastAPI Application Scaffold & Error Handling (`backend/credence_gov/app.py`)
- `TASK-008`: Keycloak OIDC Authentication & RBAC Dependency Injection (`backend/credence_gov/auth.py`)
- `TASK-009`: Case Intake & Artifact Upload Endpoints (`backend/credence_gov/api.py`)

#### 3. Deliverables
- `backend/credence_gov/app.py` hosting the FastAPI application instance.
- `backend/credence_gov/auth.py` with `get_current_user` and `require_role(...)` dependencies.
- `POST /api/v1/cases` and `POST /api/v1/cases/{id}/artifacts` wired to persistent models and storage adapter.
- Test suite verifying JWT authentication, role denial, and valid intake flow.

#### 4. Exit Criteria & Quality Gates
- Unauthenticated requests to protected endpoints return `401 Unauthorized`.
- Requests from unauthorized roles return `403 Forbidden`.
- Successful case intake returns `201 Created` with mandatory advisory banner and immutable SHA-256 digest.

#### 5. Rollback Plan
- Disable new routes in `app.py`; fall back to in-memory `CaseAPI` class.

#### 6. Validation Protocol
```bash
python -m pytest backend/tests/test_phase5_api.py
```

---

### Phase 3: Feature Expansion & Governance Engine

#### 1. Goal
Implement high-value expanded features derived directly from existing case, artifact, and audit data: automated chain-of-custody verification, temporal conflict detection, BSA 2023 s.63 electronic certificates, and YAML-governed deterministic policy packs.

#### 2. Tasks Included
- `TASK-010`: Automated Chain-of-Custody Verifier & Tamper Scanner (`backend/credence_gov/integrity_scanner.py`)
- `TASK-011`: Temporal Conflict Detector - As-Of Guard (`backend/credence_gov/temporal_guard.py`)
- `TASK-012`: BSA 2023 Section 63 Electronic Certificate Generator (`backend/credence_gov/bsa_certificate.py`)
- `TASK-013`: Deterministic Policy Pack & Human Review Queue (`backend/credence_gov/policy.py`)

#### 3. Deliverables
- `integrity_scanner.py` for automated continuous audit verification.
- `temporal_guard.py` blocking citations published after case `as_of_date`.
- `bsa_certificate.py` formatting legal electronic certificates under Indian Evidence Act/BSA 2023.
- Upgraded `policy.py` enforcing multi-tier review routing and non-binary evidence states.

#### 4. Exit Criteria & Quality Gates
- Batch integrity scanner detects byte modifications in test fixtures.
- Temporal guard rejects citations post-dating case as-of date.
- Policy engine strictly refuses any "real/fake" verdict and routes elevated cases to human reviewers.

#### 5. Rollback Plan
- Remove feature expansion modules and restore baseline `backend/credence_gov/policy.py`.

#### 6. Validation Protocol
```bash
python -m pytest backend/tests/test_phase8_policy.py
```

---

### Phase 4: Sandboxed Intelligence Worker & Async Queue

#### 1. Goal
Decouple heavy, untrusted artifact processing into asynchronous Celery tasks running with zero network egress, integrating ClamAV antivirus stream scanning and quarantine storage.

#### 2. Tasks Included
- `TASK-014`: Celery Task Pipeline & Redis Queue Integration (`backend/credence_gov/tasks.py`)
- `TASK-015`: ClamAV Antivirus Stream Scanner & Quarantine Vault (`backend/credence_gov/antivirus.py`)

#### 3. Deliverables
- `backend/credence_gov/tasks.py` defining Celery tasks for asynchronous parsing and analysis.
- `backend/credence_gov/antivirus.py` implementing ClamAV TCP client.
- Quarantine isolation routines preventing untrusted files from touching production buckets.

#### 4. Exit Criteria & Quality Gates
- Uploaded infected files are rejected with `400 Malicious File Detected` and quarantined.
- Parsing tasks run asynchronously without blocking API request threads.
- Worker timeout triggers automatic fallback to `insufficient_evidence` with mandatory human review.

#### 5. Rollback Plan
- Revert async queue configuration; execute parsing synchronously within safe memory bounds during testing.

#### 6. Validation Protocol
```bash
python -m pytest backend/tests/
```

---

### Phase 5: Evidence Package Export & Cryptographic Signing

#### 1. Goal
Assemble complete, court-ready portable Evidence Packages (ZIP dossiers) containing case metadata, citations, audit trail excerpts, and an Ed25519 digitally signed manifest.

#### 2. Tasks Included
- `TASK-016`: Portable Evidence Package Dossier Builder (`backend/credence_gov/package_builder.py`)
- `TASK-017`: Ed25519 Cryptographic Manifest Signing (`backend/credence_gov/crypto_signer.py`)
- `TASK-018`: CI/CD Pipeline Automation & Quality Gates (`.github/workflows/ci.yml`)
- `TASK-019`: Master Verification & Final Report Generation

#### 3. Deliverables
- `package_builder.py` compiling verifiable ZIP packages with mandatory advisory banners.
- `crypto_signer.py` generating and verifying Ed25519 signatures over package manifests.
- Hardened `.github/workflows/ci.yml` running linting, type checks, and security tests.
- Final validation report documenting production readiness and test outputs.

#### 4. Exit Criteria & Quality Gates
- Generated packages verify against Ed25519 public keys; any modified byte causes verification failure.
- Mandatory banner `"Decision support. Not a finding of fact."` is present in all exported documents.
- 100% of automated tests pass in CI.

#### 5. Rollback Plan
- Retain previous package generation stubs in `foundation.py`.

#### 6. Validation Protocol
```bash
python -m pytest
```
