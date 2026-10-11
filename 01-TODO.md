# 01-TODO.md
**Project:** CredenceAI-Gov (`Blackbebertex/Credence-AI`)  
**Scope:** Actionable, Prioritized, and Dependency-Mapped Task List  
**Traceability:** Linked directly to `00-MASTER-ASSESSMENT-AND-ARCHITECTURE.md` and `docs/requirements/implementation-spec.md`  
**Status:** Baseline Established  

---

## Task Management Protocol
Each task must be executed strictly in order. After each task:
1. Implement the required code or configuration.
2. Add or update unit/integration tests verifying the behavior.
3. Run the full test suite (`python -m pytest`).
4. Update this `01-TODO.md` file (check off completed task, log evidence).
5. Produce a diff summary and report progress.

---

## Phase 0: Discovery, Environment Alignment & Packaging Hygiene

- [x] **TASK-001: Python Runtime & Dependency Environment Alignment**
  - **Description:** Align developer environment with target runtime. Create `pyproject.toml` with strict pins matching `docs/DEPENDENCIES.md` (Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, pytest, structlog).
  - **Estimate:** 2 hours (1 SP)
  - **Dependencies:** None
  - **Traceability:** ADR-0002, `docs/DEPENDENCIES.md`
  - **Verification:** `pip install -e .` succeeds; `pytest` runs cleanly without version deprecation warnings. Status: Verified (17 passed).

- [x] **TASK-002: Abstract Storage Adapter Specification (MinIO Replacement Strategy)**
  - **Description:** Create `backend/credence_gov/storage_adapter.py` defining an abstract `StorageAdapter` protocol supporting S3-compatible APIs, Object Lock checks, and local file fallback for testing.
  - **Estimate:** 3 hours (2 SP)
  - **Dependencies:** TASK-001
  - **Traceability:** ADR-0003, RISK-001, FEAT-002
  - **Verification:** Unit test mocking S3 calls and local storage adapter passing with 100% test coverage. Status: Verified (4 unit tests passed).

---

## Phase 1: Persistence Foundation & Data Integrity Core

- [x] **TASK-003: Relational Database Schema & SQLAlchemy 2 Models**
  - **Description:** Implement declarative async SQLAlchemy 2 models for `Tenant`, `User`, `Case`, `Artifact`, `AuditEvent`, `PolicyDecision`, and `ReviewTask` in `backend/credence_gov/models.py`.
  - **Estimate:** 4 hours (3 SP)
  - **Dependencies:** TASK-001
  - **Traceability:** DATA-001, ADR-0002, FR-001
  - **Verification:** Schema generation script verifies all foreign keys, unique constraints, and indices in an SQLite/PostgreSQL test database. Status: Verified (test_models.py passed).

- [x] **TASK-004: Alembic Migration Pipeline Baseline**
  - **Description:** Initialize `alembic` migration scripts in `backend/migrations/` generating migration `0001_initial_schema.py`.
  - **Estimate:** 3 hours (2 SP)
  - **Dependencies:** TASK-003
  - **Traceability:** OPS-001, DATA-001
  - **Verification:** `alembic upgrade head` applies cleanly against test database; down-migration `alembic downgrade -1` cleanly rolls back. Status: Verified (Alembic upgrade head and downgrade base passed).

- [x] **TASK-005: PostgreSQL Row-Level Security (RLS) Policies**
  - **Description:** Author SQL migrations adding `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` and policies enforcing `tenant_id = current_setting('app.current_tenant')`.
  - **Estimate:** 4 hours (3 SP)
  - **Dependencies:** TASK-003, TASK-004
  - **Traceability:** ADR-0004, SEC-001, RISK-002
  - **Verification:** Multi-tenant test passes: User with tenant A receives 0 rows when querying tenant B cases. Status: Verified (0002_row_level_security.py and test_rls_simulation.py passed).

- [x] **TASK-006: Persistent Hash-Chain Audit Ledger Integration**
  - **Description:** Upgrade `backend/credence_gov/audit.py` to write `AuditEvent` records directly into the database within the calling database transaction.
  - **Estimate:** 3 hours (2 SP)
  - **Dependencies:** TASK-003
  - **Traceability:** ADR-0005, NFR-001, FR-004, FR-005
  - **Verification:** Integration test proves that committing a case also atomically commits the audit event; tampering with a database row causes `verify_chain()` to fail. Status: Verified (test_audit_db.py passed with 2 tests).

---

## Phase 2: Core Domain API & Zero Trust Middleware

- [x] **TASK-007: FastAPI Application Scaffold & Error Handling**
  - **Description:** Create `backend/credence_gov/app.py` configuring FastAPI, CORS, custom exception handlers adhering to RFC 7807 (Problem Details), and `/health` endpoints.
  - **Estimate:** 3 hours (2 SP)
  - **Dependencies:** TASK-001, TASK-003
  - **Traceability:** API-001, FR-001, NFR-003
  - **Verification:** `GET /health` returns `{"status": "healthy"}`; validation errors return `application/problem+json`. Status: Verified (test_app.py passed).

- [x] **TASK-008: Keycloak OIDC Authentication & RBAC Dependency Injection**
  - **Description:** Implement `backend/credence_gov/auth.py` providing FastAPI dependencies `get_current_user` and `require_role(...)` verifying JWT signature, expiration, and audience against Keycloak JWKS.
  - **Estimate:** 4 hours (3 SP)
  - **Dependencies:** TASK-007
  - **Traceability:** SEC-001, FR-002, Diagram 2
  - **Verification:** Unit tests verifying valid mock JWT succeeds, expired JWT returns 401, wrong role returns 403. Status: Verified (test_auth.py passed with 4 tests).

- [x] **TASK-009: Case Intake & Artifact Upload Endpoints**
  - **Description:** Implement `POST /api/v1/cases` and `POST /api/v1/cases/{id}/artifacts` in `backend/credence_gov/api.py` connected to database and storage adapter.
  - **Estimate:** 4 hours (3 SP)
  - **Dependencies:** TASK-002, TASK-003, TASK-006, TASK-007, TASK-008
  - **Traceability:** API-001, API-002, FEAT-001, FEAT-002, FR-001, FR-003
  - **Verification:** End-to-end API test creating a case and uploading bytes; verifies SHA-256 in DB matches artifact digest. Status: Verified (test_api_endpoints.py passed with 4 tests).

---

## Phase 3: Feature Expansion & Governance Engine

- [x] **TASK-010: Feature Expansion 1 - Automated Chain-of-Custody Verifier**
  - **Description:** Implement `backend/credence_gov/integrity_scanner.py` with a batch verification routine that traverses the audit hash-chain and verifies stored artifact digests.
  - **Estimate:** 4 hours (3 SP)
  - **Dependencies:** TASK-006
  - **Traceability:** FEAT-EXP-01, Diagram 6
  - **Verification:** Test proves that corrupting an artifact file or an audit row triggers an integrity alert. Status: Verified (test_integrity_scanner.py passed with 3 tests).

- [x] **TASK-011: Feature Expansion 3 - Temporal Conflict Detector (As-Of Guard)**
  - **Description:** Implement `backend/credence_gov/temporal_guard.py` validating that source citation timestamps precede or equal `CaseRecord.as_of_date`.
  - **Estimate:** 3 hours (2 SP)
  - **Dependencies:** TASK-003
  - **Traceability:** FEAT-EXP-03, BR-006, PR-11
  - **Verification:** Citations dated after case as-of date are flagged and excluded with `TemporalConflictException`. Status: Verified (test_temporal_guard.py passed with 2 tests).

- [x] **TASK-012: Feature Expansion 4 - BSA 2023 Section 63 Certificate Generator**
  - **Description:** Implement `backend/credence_gov/bsa_certificate.py` generating electronic certificates detailing hash continuity, system identifiers, and operator credentials.
  - **Estimate:** 5 hours (3 SP)
  - **Dependencies:** TASK-006, TASK-009
  - **Traceability:** FEAT-EXP-04, RISK-003, `docs/COMPLIANCE_REGISTER.md:L10`
  - **Verification:** Output schema validation test confirming all statutory certificate fields are present and signed. Status: Verified (test_bsa_certificate.py passed with 2 tests).

- [x] **TASK-013: Deterministic Policy Pack & Human Review Queue**
  - **Description:** Upgrade `backend/credence_gov/policy.py` and `mvp.py` to support YAML-based rulepacks, risk tier routing (R1 routine, R2 elevated, R3 supervisor), and mandatory review rationales.
  - **Estimate:** 4 hours (3 SP)
  - **Dependencies:** TASK-003, TASK-007
  - **Traceability:** FR-006, FR-007, FR-008, GOV-001
  - **Verification:** Cases with inconclusive or mixed evidence are routed to `ReviewTask` with state `PENDING_REVIEW`; R2 cases cannot close without rationale. Status: Verified (test_policy_risk.py passed with 3 tests).

---

## Phase 4: Sandboxed Intelligence Worker & Async Queue

- [x] **TASK-014: Celery Task Pipeline & Redis Queue Integration**
  - **Description:** Configure Celery application with prioritized queues (`p0_deadline`, `p1_elevated`, `p2_routine`) and worker task wrappers in `backend/credence_gov/tasks.py`.
  - **Estimate:** 4 hours (3 SP)
  - **Dependencies:** TASK-001, TASK-009
  - **Traceability:** Diagram 4, `docs/architecture/architecture.md:L23`
  - **Verification:** Task enqueuing and processing verified via Celery test runner / in-memory broker test. Status: Verified (test_tasks.py passed with 2 tests).

- [x] **TASK-015: ClamAV Antivirus Stream Scanner & Quarantine Vault**
  - **Description:** Implement ClamAV daemon TCP client in `backend/credence_gov/antivirus.py` scanning incoming streams; quarantines infected files and alerts audit log.
  - **Estimate:** 4 hours (3 SP)
  - **Dependencies:** TASK-002, TASK-006
  - **Traceability:** FEAT-EXP-07, SEC-002, FR-010
  - **Verification:** Ingesting simulated EICAR standard test string triggers 400 rejection and writes security audit event. Status: Verified (test_antivirus.py passed with 2 tests).

---

## Phase 5: Evidence Package Export & Cryptographic Signing

- [x] **TASK-016: Portable Evidence Package Dossier Builder**
  - **Description:** Implement `backend/credence_gov/package_builder.py` compiling case metadata, source citations, audit ledger excerpts, and artifacts into a structured ZIP dossier.
  - **Estimate:** 4 hours (3 SP)
  - **Dependencies:** TASK-006, TASK-009, TASK-012, TASK-013
  - **Traceability:** FR-008, FR-009, FEAT-007
  - **Verification:** Generated ZIP contains `manifest.json`, `audit_trail.json`, `findings.json`, and banner `"Decision support. Not a finding of fact."`. Status: Verified (test_package_signing.py passed).

- [x] **TASK-017: Ed25519 Cryptographic Manifest Signing**
  - **Description:** Implement `backend/credence_gov/crypto_signer.py` using `cryptography` library to sign `manifest.json` with Ed25519 private key; provides signature verification function.
  - **Estimate:** 3 hours (2 SP)
  - **Dependencies:** TASK-016
  - **Traceability:** SEC-007, FEAT-007, `scripts/gen_keys.py`
  - **Verification:** Signature verification passes on unmodified package and fails if any file in the ZIP is tampered with. Status: Verified (test_package_signing.py passed).

---

## Phase 6: Final CI Hardening, Regression & Master Validation

- [ ] **TASK-018: CI/CD Pipeline Automation & Quality Gates**
  - **Description:** Update `.github/workflows/ci.yml` to run automated linting (`ruff`), type checking (`mypy`), security scanning (`pip-audit`), and full `pytest` suite.
  - **Estimate:** 3 hours (2 SP)
  - **Dependencies:** All previous tasks
  - **Traceability:** OPS-001, `docs/MASTER_PROMPT.md:§12`
  - **Verification:** CI workflow passes on all branches; fails if any unit test or security audit fails.

- [ ] **TASK-019: Master Verification & Final Report Generation**
  - **Description:** Run full end-to-end integration and smoke tests across all modules. Generate final validation report.
  - **Estimate:** 2 hours (1 SP)
  - **Dependencies:** TASK-001 through TASK-018
  - **Traceability:** Final Deliverable Sequence
  - **Verification:** 100% test pass rate documented in terminal output.
