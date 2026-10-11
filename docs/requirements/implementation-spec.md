# CredenceAI-Gov implementation specification

**Status:** Draft, derived from `CredenceAI-Gov_Master_Blueprint.md`  
**Implementation status:** No application code is present in this checkout. Blueprint references to existing CredenceAI capabilities are unverified here.  
**Decision gate:** R0 must be satisfied before processing pilot data or implementing workflow-specific analyzers.

## Executive interpretation

CredenceAI-Gov is an advisory evidence-management and analysis platform for authorized government analysts. It creates traceable cases from claims, documents, images, and (later) links; preserves artifact integrity and handling history; assembles sourced findings; applies deterministic policy; and routes elevated decisions to people. Its product is an evidence package, not a truth verdict. It must not autonomously publish, notify, remove content, or enforce a decision.

## Problem and users

The stated problem is fragmented, inconsistent, slow, and poorly auditable review of questionable claims and digital artifacts. Intended users explicitly named by the source are:

| User | Supported responsibility |
|---|---|
| Analyst | Create and investigate cases |
| Reviewer | Review elevated cases |
| Supervisor | Approve critical dispositions |
| Administrator | Manage users, policies, and configuration |
| Auditor | Read-only audit access |
| System service | Authorized machine-to-machine operations |

Researchers, compliance teams, and due-diligence users are secondary audiences, not approved pilot roles.

## Core workflows

1. **Claim verification (W1):** claim and as-of date → normalize/decompose → retrieve eligible sources → associate quoted spans and stance → evidence matrix with caveats → policy and human review as required → exportable package.
2. **Artifact review (W2):** claim/case → validate and malware scan → hash and preserve original → provenance/signature/revision checks → findings linked to source artifact → evidence matrix → policy/review → package.
3. **Link capture (W3):** submit URL → isolated snapshot capture → hash and attach snapshot. Reputation checks and response actions are out of scope for R1.

## Requirement classification and inventory

Priority definitions: **MUST HAVE** is a Release 1 control or core workflow requirement; **SHOULD HAVE** is needed for a credible pilot but can be sequenced after the first vertical slice; **COULD HAVE** is optional; **FUTURE** is explicitly later release; **UNCLEAR** requires an owner decision; **CONFLICTING** has incompatible source directions; **NOT IMPLEMENTABLE AS WRITTEN** lacks measurable definition, required input, or approved authority. Every requirement below is source-derived and remains proposed until implemented and verified.

| ID | Requirement | Type | Priority | Source | Dependency | Acceptance criteria |
|---|---|---|---|---|---|---|
| FR-001 | Create a case from claim text, PDF, or image and associate an authorized owner, tenant, and classification. | Functional | MUST HAVE | §§5.2, 6.3, 13 | G0 scope; identity; classification policy | Authorized user can create each approved input type; each persisted case has owner, tenant, classification; unauthenticated/untagged creation is rejected. |
| FR-002 | Support analyst investigation, elevated review, critical supervisor disposition, admin configuration, and auditor read-only access. | Functional | MUST HAVE | §§3.2, 12 | Role/permission matrix | Authorization tests prove each role's permitted actions and deny unlisted actions; auditor mutations are denied. |
| FR-003 | Provide W1 claim decomposition, as-of retrieval, stance, exact evidence spans, citation validation, and evidence matrix. | Functional | MUST HAVE if W1 selected | §§5.1, 9 | G0 lead workflow; corpus; language; evaluation data | Each displayed claim finding links to a stored source snapshot and exact matching span; citations without matching spans are omitted; retrieval excludes evidence published after as-of date. |
| FR-004 | Provide W2 document/image intake and provenance findings without claiming provenance proves truth. | Functional | MUST HAVE for selected artifact workflow | §§5.1, 10 | G0; approved formats; ground-truth source | Each finding references the original hash and tool/version; absent or invalid provenance is reported distinctly; no result asserts genuine solely from absent manipulation indicators. |
| FR-005 | Capture submitted links as isolated, hashed snapshots; no reputation analysis in R1. | Functional | MUST HAVE for W3 if retained in pilot | §§5.1, 11 | Isolation design; network policy | Snapshot artifacts and metadata are linked to case and hash; fetch cannot access internal/private network destinations; reputation lookup is unavailable in R1. |
| FR-006 | Produce a rule-derived evidence state and caveats, never a universal trust score or binary real/fake verdict. | Functional | MUST HAVE | §§1, 2, 9, 12 | Approved versioned rules | Outputs are one of Supported, Contradicted, Mixed, Insufficient evidence, Out of scope, with rule version and rationale; no aggregate trust score is emitted. |
| FR-007 | Route elevated cases to a review queue; require recorded rationale at R2+ and supervisor approval for R3. | Functional | MUST HAVE | §§3.2, 12, 13 | Risk policy; reviewer staffing | Policy test fixtures prove R2 cannot complete without rationale and R3 without authorized supervisor; queue records age and state. |
| FR-008 | Export a portable evidence package with integrity manifest, findings, policy/review history, and advisory banner. | Functional | MUST HAVE | §§8.4, 10, 12 | Signing-key decision; package schema | Package verifies against published schema and signature; manifest covers included files; report states “Decision support. Not a finding of fact.” |
| FR-009 | Record case lifecycle and derived-artifact lineage. | Functional | MUST HAVE | §§7, 8 | Data model; event definitions | Every derived artifact identifies parent hash, tool, version, and creation time; lifecycle transitions reject invalid transitions. |
| FR-010 | Support isolated advisory-only operations; no autonomous publication, takedown, notification, or enforcement. | Functional | MUST HAVE | §§1, 5.3, 12 | Charter; authorization policy | API and worker permission tests show no such action capability is exposed or invoked. |
| NFR-001 | Keep a reproducible audit history and detect artifact or event-chain modification. | Auditability | MUST HAVE | §§8, 10, 15 | Storage and signing/key plan | Mutation of a stored test artifact or event causes integrity verification to fail; authorized verification returns a verifiable result. |
| NFR-002 | Provide backup and restore with proposed RPO ≤15 minutes and RTO ≤4 hours. | Reliability | SHOULD HAVE; thresholds require owner approval | §§17, 18; SC15 | Hosting, backup design, data volume | A documented restore exercise meets approved RPO/RTO and records measured results. |
| NFR-003 | Provide observability for service health, queue age, latency, and resource/cost per case. | Observability | SHOULD HAVE | §§16, 18; SC5–SC6, SC17 | Deployment target; load model | Dashboards/metrics expose agreed service, queue, and cost measures; alerts are exercised in staging. |
| NFR-004 | Meet GIGW 3.0 / WCAG 2.1 AA and responsive evidence-first interface goals. | Accessibility | MUST HAVE for pilot UI | §§6, 13 | Screen workflows; accessibility review | Agreed automated and manual accessibility checks pass for critical workflows; keyboard and screen-reader paths are documented. |
| NFR-005 | Set pilot latency, concurrency, availability, and throughput targets from measured workload rather than assumptions. | Performance | UNCLEAR | §§16, 21, 26 | Pilot owner and load model | Owner-approved load profile and thresholds exist; a repeatable pilot-load report records measurements. |
| NFR-006 | Minimize recurring cost and preserve practical vendor portability. | Maintainability/cost | SHOULD HAVE | §§6, 16, 20, 24 | Hosting and procurement constraints | Deployment, data export, and component/license inventory are documented; monthly/annual/TCO estimate states assumptions. |
| SEC-001 | Enforce SSO-ready identity, MFA, RBAC, tenant isolation, and case access controls. | Security | MUST HAVE | §§5, 6, 15; C1–C4 | Identity provider and role matrix | Authentication, role boundary, object ownership, and cross-tenant tests pass for every protected endpoint and artifact. |
| SEC-002 | Validate hostile uploads, scan for malware, sandbox parsers, and enforce size/type/dimension limits. | Security | MUST HAVE | §§8, 15; E1, I15 | Approved file formats; scanner runtime | Malformed, mismatched, oversized, and infected fixtures are rejected or quarantined without analysis; limits are configurable and logged. |
| SEC-003 | Hash originals at intake, preserve immutable originals, encrypt data, and record custody events. | Security/integrity | MUST HAVE | §§8, 15; E2–E7 | Object store, key management, retention policy | Intake creates SHA-256 and custody event before analysis; stored original remains byte-identical; encryption/key handling is verified. |
| SEC-004 | Treat retrieved text and uploaded content as untrusted; analyzers have bounded permissions and network access disabled by default. | Security | MUST HAVE | §§6.4, 9, 15 | Worker isolation; threat model | Prompt-injection and parser test cases cannot alter policy, permissions, or case data; worker egress is denied unless explicitly allow-listed. |
| SEC-005 | Apply retention classes, legal holds, and approved deletion/crypto-shredding behavior. | Security/privacy | UNCLEAR / Decision required | §§8, 15, 26 | Counsel and records owner decisions | No production intake until schedule, hold authority, deletion scope, and audit metadata retention are approved and tested. |
| SEC-006 | Protect secrets, apply rate limits, and avoid sensitive information in logs. | Security | MUST HAVE | §§6, 15, 16 | Deployment and data classification | Secret scan is clean; rate-limit tests return defined responses; log review confirms configured sensitive fields are redacted. |
| SEC-007 | Use signed evidence packages and establish signing-key custody/rotation. | Security | MUST HAVE for export; key details UNCLEAR | §§8.4, 15, 26 | Department key arrangement | Valid signatures verify; altered package fails; key owner, rotation, backup, revocation, and recovery procedures are approved. |
| DATA-001 | Model tenants, users/roles, cases, artifacts, source snapshots, claims/findings, policy decisions, reviews, and audit/custody events with relational constraints. | Data | MUST HAVE | §§6–9, 12; Appendix A | Workflow and retention decisions | Migrations enforce required ownership, foreign-key, uniqueness, and lifecycle constraints; no critical relationship exists only in application code. |
| DATA-002 | Version source snapshots, analyzer results, model/policy versions, and reviewer decisions so findings can be reconstructed. | Data | MUST HAVE | §§7–9, 14 | Versioning contract | Export and audit view identify exact input hashes and analyzer/model/policy versions for every finding and decision. |
| DATA-003 | Define retention, legal hold, classification, and ownership fields before real data intake. | Data/privacy | MUST HAVE | §§6.3, 8, 15 | Counsel/records owner | Schema and intake reject data lacking approved classification and retention assignment. |
| INT-001 | Integrate with Keycloak via OIDC/SAML for SSO/MFA, subject to government identity availability. | Integration | SHOULD HAVE; identity provider confirmation required | §6.2; C1 | Hosting/network/identity owner | Staging federation succeeds and logout/expiry/MFA behavior is verified; local dev identity cannot be used for production. |
| INT-002 | Use S3-compatible object storage with object lock, plus malware and provenance tools where approved. | Integration | SHOULD HAVE | §§6, 8; E3, I1–I3 | Procurement/license review | Adapter contract tests verify object lock and integrity behavior; tool versions/licenses are recorded. |
| INT-003 | Optional connected-mode search results enter cases only as timestamped, hashed snapshots. | Integration | COULD HAVE for R1 | §§4, 9; V4 | Network approval; corpus owner | Live adapter is disabled by default; enabled results are stored as snapshots with source URL, time, and content hash. |
| INT-004 | Integrate with machine-readable issued-document register if one exists. | Integration | UNCLEAR | §26.1; I6 | Department register and owner | If available, a documented read-only adapter returns verifiable match/no-match/unknown with register version; otherwise feature is deferred. |
| GOV-001 | Version and audit deterministic policy packs; policy, not model confidence, controls permissions and review. | Governance | MUST HAVE | §§6, 12, 14; C6 | Policy owner | Every decision records policy version and matched rules; policy tests prove confidence cannot override hard gates. |
| GOV-002 | Maintain model/analyzer inventory, limitations, intended use, evaluation, validity envelope, and review date. | Governance | MUST HAVE for any model in pilot | §§6.4, 14; SC14 | Model owner and evaluation plan | Unregistered, expired, or out-of-envelope analyzer is blocked or marked review-required according to approved policy. |
| GOV-003 | Preserve human authority and automation-bias controls for consequential cases. | Governance | MUST HAVE | §§1, 12, 14 | Review staffing and policy | Reviewer rationale and overrides are auditable; no machine output is presented as final authority. |
| EVAL-001 | Establish reproducible datasets, baselines, annotation guidance, sealed evaluation, and CI regression harness. | Quality | SHOULD HAVE before pilot; dataset scope decision needed | §§17, 19; SC8–SC13 | Lead workflow, language, custodian, corpus | Versioned evaluation run reproduces reported metrics; sealed data is access-controlled; regression thresholds are approved and enforced. |
| OPS-001 | Provide separate development, staging, and production configuration, health checks, migration, rollback, and incident procedures. | Operations | SHOULD HAVE | §§18–19 | Hosting model and operators | Clean environment setup and staging deployment are repeatable; migration and rollback are documented and exercised. |
| OPS-002 | Publish monthly, annual, per-user/per-case and 5-year TCO estimates with assumptions. | Operations/cost | UNCLEAR until workload/procurement known | §§20, 26 | Load model, staffing, procurement quotes | Cost model identifies quantities, unit prices, exclusions, and uncertainty; no estimate is represented as a quote. |
| PILOT-001 | Define pilot owner, users, geography, support, training, baseline, and measurable success thresholds. | Pilot | UNCLEAR / Decision required | §§19, 21, 26 | Named department and counsel-cleared charter | Signed pilot charter names accountable owners and thresholds before pilot data is processed. |

## Business rules

- BR-001: Integrity, provenance, authenticity, claim accuracy, security, and trust disposition are distinct properties and must remain distinct in data and UI.
- BR-002: Hashes establish byte continuity from intake, not original authenticity.
- BR-003: No universal trust score or binary real/fake result is allowed.
- BR-004: No automated publishing, takedown, notification, enforcement, or other consequential action.
- BR-005: Evidence state is deterministic and policy-versioned: Supported, Contradicted, Mixed, Insufficient evidence, or Out of scope; caveats remain visible.
- BR-006: A source published after the claim's as-of date cannot support an as-of assessment.
- BR-007: Displayed claim findings must trace to a stored source and matching quoted span; span matching does not establish correct interpretation.
- BR-008: Every transformation creates a derived artifact linked to the parent hash and tool/version; original is never overwritten.
- BR-009: Models cannot authorize access, retention, deletion, risk tier, or audit behavior.
- BR-010: Uncertain/out-of-envelope analysis abstains or routes to human review under versioned policy.
- BR-011: Legal hold suspends approved deletion; expiry behavior follows approved records schedule.
- BR-012: R2+ rationale and R3 supervisor approval are mandatory, subject to approved risk definitions.

## Data entities and lifecycle

Candidate entities: Tenant, User, Role, Permission, Case, CaseAccessGrant, Artifact, DerivedArtifact, CustodyEvent, AuditEvent, Source, SourceSnapshot, Claim, EvidenceSpan, AnalysisJob, AnalyzerManifest, Finding, EvidenceState, PolicyPack, PolicyDecision, ReviewTask, ReviewerDisposition, EvidencePackage, RetentionClass, LegalHold, SigningKeyReference. Relationships and fields are logical candidates, not a frozen schema. Case lifecycle: created → intake validated → evidence preserved → analysis queued/running → findings ready or failed → policy routed → review/disposition → package exported → retained/held/deleted under approved schedule. Audit metadata retention and crypto-shredding scope require records/legal approval.

## MVP boundary

| Feature | MVP | Later | Reason |
|---|---|---|---|
| Login, tenant scoping, roles, case ownership | Yes, after identity decision | Federation refinements | Foundational security boundary |
| One lead workflow chosen at G0 | Yes | Other workflow | Avoid building two unvalidated products |
| Secure intake, hash, custody, immutable original | Yes for artifact intake | Merkle proof and RFC3161 anchor | Minimum defensible chain; advanced proof can follow gate |
| Curated corpus and claim evidence matrix | Yes only if W1 chosen | Live search, clustering, multilingual expansion | Controlled and evaluable sources first |
| Official-document register check | Yes only if W2 chosen and register exists | Rich integrations | Depends on department ground truth |
| Provenance basics (metadata, C2PA/PDF signatures, repeat lookup) | Basic approved subset | Detector only after S4 | Provenance is feasible without claiming truth |
| Image deepfake detector | No | R2 after S4 | Validity envelope and degraded-data evaluation required |
| Link isolated snapshot capture | Conditional R1 | Reputation/cyber enrichment R3 | Safe capture only; isolation must be proven |
| Rule policy and review queue | Yes | Advanced workflow configuration | Human oversight is core |
| Signed evidence package | Yes after key arrangement | RFC3161 and BSA format support R2 | Key custody and legal format unresolved |
| Backup/restore, observability, capacity/cost telemetry | Pilot minimum | Scale proof/HA | Operational readiness before pilot |
| Video/audio/cyber threat intelligence | No | R3 plugins | Explicitly deferred and evaluation-intensive |
| Independent study, scale-out cells, air-gapped distribution | No | R2/R3 | Requires pilot evidence and scale need |

## Unknowns, conflicts, and decisions

| Item | Classification | Handling |
|---|---|---|
| Lead workflow: open claims vs official-record authenticity | CONFLICTING / decision required | G0 answer-availability test on 200 cases; do not implement analyzer-specific path until selected. Shared case/evidence foundation may be designed. |
| Named pilot department, owner, three analysts, geography, support | UNCLEAR / blocking | Secure pilot owner and charter before pilot data. |
| Pilot language(s) and corresponding gold data | UNCLEAR / blocking for model/retrieval workflow | Select language and evaluation plan; no unsupported language claims. |
| Whether case data may leave the network / hosted LLM | UNCLEAR / blocking for hosted model | Default to no external transfer until explicit security/data-owner approval; local deterministic foundations can proceed. |
| Signing-key custody, rotation, recovery | UNCLEAR / blocking for signed export | Key owner and operating procedure required before production signing. |
| Retention classes, legal hold, deletion, audit retention | UNCLEAR / blocking for real data | Counsel/records officer approval before intake. |
| Issued-document register and API | UNCLEAR / conditional | Inspect with department; defer integration if absent. |
| File types/size limits and expected throughput/load | UNCLEAR | Define at threat-model and workload workshop before pilot. |
| Availability, latency and service levels | NOT IMPLEMENTABLE AS WRITTEN | Replace illustrative targets with owner-approved load and service objectives. |
| Cost estimates | NOT IMPLEMENTABLE AS WRITTEN | Produce once hosting, scale, staffing, and procurement inputs exist. |
| “Significant” application baseline in blueprint | CONFLICTING with checkout | Blueprint documents an existing platform, but this checkout contains only the blueprint. Treat all listed reuse as unverified; audit source repository before reuse. |
| “R1 signed package” vs details marked R1/R2 | CONFLICTING | Treat package as required for pilot only after key and legal fit decisions; Merkle/RFC3161/BSA certificate features are later/conditional. |
| BSA s.63 certificate format/legal sufficiency | UNCLEAR / not legal advice | Defer certificate generation until counsel confirms format and process. |
| GIGW 3.0 and WCAG 2.1 AA procurement applicability | UNCLEAR | Retain as target pending buyer confirmation and accessibility review. |
| Government rules and standards applicability | UNCLEAR | Jurisdiction suggests India, but hosting, records, privacy, security, procurement, and evidence requirements require named counsel/security review. |

## Phase roadmap and gates

1. **Phase 0 – Understand:** source interpretation, conflicts, users, workflows, initial requirement inventory. Complete in this document.
2. **Phase 1 – Normalize:** IDs, priorities, criteria, traceability. Draft baseline in this document; owner review still required.
3. **Phase 2 – MVP:** conditional scope recorded above; G0 decision required to freeze it.
4. **Phase 3 – Architecture:** modular monolith, planes, candidate stack, security/data boundaries documented in `docs/architecture/architecture.md`; decisions remain conditional on environment and procurement.
5. **G0 before application implementation:** pilot owner, counsel-cleared advisory charter, answer-availability study, language, data egress, key and retention decisions, register availability, workload and operator constraints. Gate failure pauses pilot-specific analyzer work; safe repo/stack audit and non-sensitive scaffolding may proceed.
6. **Phase 4+ – Foundation and vertical slice:** only after G0, implement one runnable vertical slice with migration, identity boundary, case intake, audit, review, API/UI, tests, local setup and operational docs. Do not claim later releases complete without evidence.

## Traceability status

This is a requirements baseline, not proof of implementation. Acceptance criteria need pilot-owner confirmation where thresholds or authority are involved. For each requirement, implementation status, code/test/report evidence, result, and remaining gap must be maintained before release claims are made.
