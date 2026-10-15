# CredenceAI-Gov: Step-by-Step Execution Plan v2

*15 October 2026 · Basis: source-code forensic audit (27 tasks) merged with a red-team/blue-team review (3 new tasks plus additions to existing ones) · Status: Production NO-GO*

## 1. Verdict and how to use this plan

The current build is a synthetic prototype that displays assurance it has not earned: hardcoded integrity metrics, an integrity API that does not check, and compliance badges with nothing behind them. Fixing that comes before any new feature. The product's value is not more AI or more dashboards; it is making every evidence, security and compliance claim independently testable.

**Effort key:** S ≤ 2 days · M 3–7 days · L 1–3 weeks, for 1–2 developers. These are planning guesses, not measurements.

**Done rule:** a task is done only when its Accept test passes, someone other than the author can rerun it, and the result is committed.

## 2. Principles (non-negotiable)

1. **Claim rule.** Never display Verified, Compliant, Immutable or Authentic unless the system computes and can show proof of that exact claim. Use 'supports admissibility under BSA s.63, subject to the court', never 'ensures'.
2. **Trust starts at ingestion.** A hash proves a file did not change after upload, not that it was genuine before. Say this in the UI, the certificate and the threat model. Where a capture-side signature exists (C2PA, signed PDF), verify and record it.
3. **AI advises, people decide.** AI output is a cited, abstaining flag. It is never a verdict and never the basis of a certificate.
4. **Verify without us.** A stranger must be able to check a package offline with an open-source verifier, without trusting our server.
5. **Fail closed.** Scanner down, key missing, hash mismatch, missing artifact: reject and log. Never substitute simulated data.
6. **Lowest viable cost.** One node, open-source components, managed KMS before owning an HSM, scale only after a pilot proves demand.

## 3. Target architecture

- **Frontend:** UI only. No evidence bytes and no secrets on Vercel serverless.
- **API:** stateless service behind a reverse proxy (TLS, rate limits, security headers), OIDC login (Keycloak or a managed IdP), deny-by-default roles.
- **Database:** PostgreSQL with row-level security, an append-only custody table and migrations.
- **Object store:** MinIO or S3-compatible, versioning plus object lock, India-region or on-prem.
- **Workers:** isolated containers (no network, non-root, resource limits) for ClamAV, type sniffing, parsing, OCR, C2PA and PDF-signature checks.
- **Signing:** Ed25519 keys in KMS/HSM (SoftHSM for dev only); RFC 3161 timestamps from a recognised authority (free TSAs for dev only).
- **Transparency:** daily Merkle root of the custody ledger, published publicly; witnesses cosign during the pilot.
- **Verifier:** standalone open-source CLI, no network required.

## 4. Evidence package and verifier spec

**Package layout:** `evidence/` (original bytes, untouched), `derived/` (labelled previews and OCR), `manifest.json`, `manifest.sig`, `custody.jsonl`, `timestamp.tsr`, `merkle-proof.json`, `VERIFY.md`.

**manifest.json** (canonical JSON, RFC 8785): schema\_version, case\_id, artifacts with size, mime, SHA-256 and SHA-512, source and capture info (including any C2PA or PDF-signature result), custody head hash, Merkle root and proof, signer key\_id, tool versions, created\_at.

**Custody event:** seq, prev\_hash, actor, role, action, timestamp, payload\_hash. Event hash = SHA-256 of the canonical event plus prev\_hash. The table blocks UPDATE and DELETE.

**Verifier checks, in order:** file hashes → manifest signature and key status at timestamp → custody chain continuity → timestamp token → Merkle proof against the published root → separation-of-duties rules recorded in the chain. Output is pass/fail per check with a stable error code.

## 5. Step-by-step plan

### Phase P0 · Remove false assurance (week 1)

- **P0-01 Kill public privileged sessions (M).** Do: delete the demo-session route and default tokens; deploy OIDC with MFA for reviewer, approver and admin; add deny-by-default role middleware; rotate any secret that was ever exposed. **Accept:** every route returns 401 when unauthenticated; the role × route matrix passes; secret scan of code and git history is clean.
- **P0-02 Remove false claims (S).** Do: delete hardcoded 100% metrics, 'BSA Compliant' badges and fabricated provenance; replace with computed labels such as 'Hash recorded' and 'Not independently verified'; add a CI check that fails the build if a banned claim word appears in UI strings without a linked verification record. **Accept:** the CI gate works; every displayed status maps to a computed field.
- **P0-03 Real integrity API (M).** Do: recompute SHA-256 of stored bytes, recompute the custody chain, compare to the manifest; return per-check results (hash\_match, chain\_valid, signature\_valid, timestamp\_valid) with reasons; never default to true. **Accept:** each tamper case returns false with a specific code; unit tests cover every check.
- **P0-04 Gate the statutory certificate (S).** Do: certificate endpoint requires a verified hash, a complete custody chain, named authorized signers with active keys and a completed legal checklist; otherwise return 409 listing missing preconditions. **Accept:** four negative tests, one per missing precondition.
- **P0-05 Fix export (S).** Do: one canonical path resolver; export fails if any referenced artifact is missing; remove the simulated-bytes fallback. **Accept:** deleting an artifact makes export fail; every path in an exported manifest exists.
- **P0-06 Frontend truth (S).** Do: health check calls the authenticated backend; remove the localhost fallback from production builds via environment config; show distinct messages for network failure, 401, 403 and 5xx. **Accept:** with the backend down the UI says 'Backend unreachable', never 'Connected'; E2E test.
- **P0-07 Threat model (S), new.** Do: one page covering assets, actors, trust boundaries, the top threats in section 7, and an explicit trust-starts-at-ingestion statement. **Accept:** reviewed by a second person and linked from the README.

**P0 exit:** no demo privilege, no false claim, no unchecked integrity result. Until then, no real evidence is accepted.

### Phase P1 · Secure evidence foundation (weeks 2–6)

- **P1-01 PostgreSQL and tenancy (L).** Do: schema for tenants, users, cases, artifacts, custody\_events, reviews, signatures and grants; migrations; row-level security keyed to tenant and case grants; the app connects as a non-superuser; state changes run in transactions. **Accept:** restart loses nothing; cross-tenant suite (read, write, list, guessed IDs) is all denied.
- **P1-02 Immutable storage (L).** Do: versioned bucket with object lock; store original bytes unchanged; hash server-side while streaming; keep derived files separate and labelled; host in India-region or on-prem, evidence never on Vercel serverless. **Accept:** overwrite and delete fail while locked; re-hash after restore equals the manifest.
- **P1-03 Custody ledger and timestamps (L).** Do: append-only table with a trigger blocking UPDATE and DELETE; hash-chained events; RFC 3161 token on each manifest; daily Merkle root published publicly. **Accept:** modifying, deleting or reordering any event is detected by the verifier; the timestamp token verifies offline.
- **P1-04 Safe ingestion (M).** Do: streaming upload with size caps; magic-byte type sniffing; quarantine bucket; fail-closed ClamAV; parsing only in sandboxed workers. **Accept:** EICAR test file is quarantined; with the scanner stopped, uploads are refused; zip-bomb and polyglot samples are rejected.
- **P1-05 Keys, manifests, offline verifier (L).** Do: Ed25519 keys in KMS/HSM with rotation and a revocation list (past signatures stay verifiable at their timestamp); SHA-256 plus SHA-512 canonical manifests; build the standalone verifier from section 4. **Accept:** the verifier runs on an air-gapped machine, passes a clean package and fails every case in section 6 with the expected code.
- **P1-06 Retention and recovery (M).** Do: retention schedule per case type; legal-hold flag that blocks deletion; deletion only with two-person approval and a ledger entry; nightly backup of database and object versions to a separate location; quarterly restore drill. **Accept:** a restore into a clean environment passes the verifier on all sample cases; measured RPO and RTO are recorded.
- **P1-07 Web hardening (S), new.** Do: HSTS, CSP without inline scripts, X-Content-Type-Options, frame-ancestors, Referrer-Policy, secure cookies, rate limiting, noscript fallback, og tags, canonical link, favicon. **Accept:** an external header scan grades A; Lighthouse best-practices is 95 or higher.

**P1 exit:** evidence survives restarts, tampering is detected, a stranger can verify a package offline.

### Phase P2 · Complete the product (weeks 5–9)

- **P2-01 Case lifecycle (L).** Do: state machine Draft → Ingested → Verified → Analyzed → In review → Approved → Exported → Independently verified; each transition needs a role and preconditions and writes a custody event. **Accept:** one E2E run from upload to offline-verified export; illegal transitions are rejected.
- **P2-02 Real provenance graph (M).** Do: build nodes (artifact, source, actor, tool run, review, signature) and edges from the database. **Accept:** the graph regenerated from the database matches the display; a code search finds no hardcoded nodes.
- **P2-03 Separation of duties (M).** Do: uploader ≠ reviewer ≠ approver; conflict-of-interest declaration; two approvers for critical cases; admins cannot edit evidence or custody. **Accept:** policy tests; every blocked attempt is logged.
- **P2-04 Robust usability (M).** Do: server-side search, filters and pagination; input validation; retry states; readable errors; no optimistic UI for evidence actions. **Accept:** E2E tests; injected failures show the right message.
- **P2-05 Accessibility and mobile (M).** Do: WCAG 2.2 AA-oriented work, full keyboard flow, labels, contrast, 360 px layout. **Accept:** axe CI has no critical violations; a manual screen-reader pass on three critical flows.

**P2 exit:** one real case runs end to end with independent reviewers.

### Phase P3 · Grounded AI and governance (weeks 8–12)

- **P3-01 Sandboxed analysis (L).** Do: versioned tools whose name, version and hash are recorded in every result; OCR only where justified; PDF signature validation; C2PA check; metadata extraction; isolated workers with no network. **Accept:** results are reproducible for a given tool version; sandbox-escape tests fail.
- **P3-02 Grounded, abstaining AI (M).** Do: every claim cites an evidence span (artifact id and offsets); a validator rejects uncited claims; as-of-date filtering; contradiction detection; abstain when support is thin; output is advisory flags only, never authentic or fake. **Accept:** an injected unsupported claim is rejected; abstention rate is reported.
- **P3-03 Benchmarks (L).** Do: labelled synthetic plus public set; report precision, recall, macro-F1, false-support rate, calibration and robustness across the languages your users file in; compare against classical baselines such as hash, metadata and rule checks. **Accept:** report committed; release blocked below thresholds fixed in advance.
- **P3-04 AI and platform red-team (M).** Do: prompt injection in documents, fabricated citations, forged EXIF and metadata, adversarial PDFs and images, SSRF, cross-tenant prompts. **Accept:** findings log with fix status; zero open critical findings.
- **P3-05 Governance and witnesses (L).** Do: publish a charter; two-person rule changes; independent audits; appeals through a different witness; witnesses cosign daily Merkle roots; a witness that cosigns a root later shown inconsistent loses its bond or standing; verifier bug bounty; no token. **Accept:** a witness cosignature verifies in the verifier; a mock appeal is completed.

**P3 exit:** AI never overstates, and governance is documented and exercised.

### Phase P4 · Production quality and release (weeks 11–15)

- **P4-01 CI/CD (M).** Do: unit, integration, Playwright E2E, axe, SAST, dependency scan, SBOM (CycloneDX) and secret scan; the section 6 tamper suite and break-it cases (empty, oversized and wrong-type uploads, refresh mid-flow, custody edits) as required checks. **Accept:** protected main branch; all checks required. Start this in week 2, not week 11.
- **P4-02 Performance (M).** Do: load test 10, 50 and 100 users with 1, 5 and 10 MB uploads; record API p95, Core Web Vitals and cost per case; commit the Lighthouse report. **Accept:** repeatable scripts and a results table; suggested targets only until measured: mobile Lighthouse ≥ 90, LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1.
- **P4-03 Operations (M).** Do: metrics, alerts, runbooks, key-recovery drill, rollback, DR test against proposed RPO ≤ 15 min and RTO ≤ 4 h. **Accept:** drill reports.
- **P4-04 Legal and security review (L).** Do: counsel reviews the s.63 flow, certificate format and disclaimers; DPDP (consent, purpose, retention, breach notice); CERT-In duties (logging and incident reporting); STQC or empanelled audit; GeM listing; accessibility and records rules; one real sample certificate signed off by a practicing lawyer. **Accept:** written legal opinion and audit report. Confirm all regulatory specifics with counsel.
- **P4-05 Pilot and release gate (M).** Do: synthetic-data UAT with one buyer type (a cyber cell or a litigation firm); independent penetration test; release-gate meeting. **Accept:** signed approvals.
- **P4-06 Market proof (S), new.** Do: competitor matrix against Issured, DigiTrust and the C2PA ecosystem; write a one-line differentiator and test it with three prospective users. **Accept:** matrix plus interview notes. Do this in week 3 so you validate the buyer before building more.

## 6. Tamper test matrix (must all fail correctly)

1. Flip one byte in an artifact → HASH\_MISMATCH.
2. Edit one manifest field → SIGNATURE\_INVALID.
3. Edit a custody event → CHAIN\_BROKEN.
4. Delete a custody event → CHAIN\_BROKEN (sequence gap).
5. Reorder custody events → CHAIN\_BROKEN.
6. Swap in another key's signature → KEY\_UNTRUSTED.
7. Replace the timestamp token → TIMESTAMP\_INVALID.
8. Replay an older valid manifest for a changed case → ROOT\_MISMATCH against the published Merkle root.
9. Sign after the key's revocation time → KEY\_REVOKED.

## 7. Threat model: top threats and controls

1. **Forged evidence before upload:** disclose trust-at-ingestion; verify capture-side signatures where present; never claim authenticity.
2. **Insider edits custody or artifacts:** append-only table, object lock, external Merkle roots, witness cosigns.
3. **Key theft:** KMS/HSM, rotation, revocation with effective time, signing requires approver role and MFA.
4. **Cross-tenant access:** row-level security, guessed-ID tests, per-case grants.
5. **Malicious upload (malware, zip bomb, polyglot):** quarantine, fail-closed scan, sandboxed parsers, size limits.
6. **Prompt injection through evidence content:** treat content as data, no actions triggered by AI output, validated citations.
7. **SSRF:** no outbound network in workers; strict allowlist if fetching is ever needed.
8. **Admin abuse:** admins cannot touch evidence or custody; two-person rule changes; all admin actions in the ledger.
9. **Replay or rollback of old manifests:** sequence numbers, timestamps, published roots.
10. **Supply chain:** pinned dependencies, SBOM, dependency scans, signed releases.
11. **Denial of service and cost abuse:** rate limits, quotas, upload caps, AI call quotas.

## 8. Governance and DAO-aligned incentives (permissioned, no token)

- **Roles:** intake officer, reviewer, approver, auditor, admin, witness. No role can both create and approve the same case.
- **Witness federation:** universities, forensic labs and bar bodies cosign the daily Merkle root. Reputation or a posted bond is slashed for cosigning a root later shown inconsistent.
- **Incentives:** a public bug bounty for forging a manifest or breaking the verifier; audit rewards for independent reviewers.
- **Rule changes:** two institutions must approve any protocol change; changes are recorded in the ledger.
- **Appeals:** any party can request independent re-verification by a different witness.
- **Boundary:** no token and no on-chain governance of evidence or outcomes. Use a blockchain only if it adds something beyond RFC 3161 plus public Merkle roots.

## 9. Cost control

- Start on a single node with open-source components; scale after the pilot proves demand.
- Use managed KMS instead of owning an HSM until funded.
- Run AI only on request and cache results by artifact hash and tool version; run cheap classical checks first.
- Defer the witness federation until the pilot; publish roots publicly in the meantime.

## 10. Timeline and critical path

- Week 1: P0. Week 2: start CI and the tamper suite. Week 3: P4-06 market proof.
- Weeks 2–6: P1. Weeks 5–9: P2. Weeks 8–12: P3. Weeks 11–15: P4, then pilot.
- **Critical path:** P0 → P1-01 → P1-02 and P1-03 → P1-05 → P2-01 → P4-04 and P4-05.
- **If budget or time is tight:** ship P0, P1-01 to P1-05, P2-01 and the CI tamper suite first, and defer P3 entirely.

## 11. Release gates

- **Security:** no public privileged sessions; all role and tenant-isolation tests pass.
- **Integrity:** every modified artifact, manifest or custody event is detected.
- **Reliability:** evidence survives restarts; backup and recovery tests pass.
- **AI:** validated benchmarks, failure analysis and abstention controls.
- **UX:** critical workflows pass accessibility and mobile tests.
- **Performance:** approved workload thresholds demonstrated with repeatable load tests.
- **Governance and legal:** independent review, legal opinion and audit evidence documented.

## 12. Limits of this plan

I have not seen the source code or a rendered version of the site; the audit findings are taken as given. Effort estimates are guesses, and the stack, team size and real workload will change them. Regulatory details (the s.63 certificate form, DPDP, CERT-In duties, STQC and GeM requirements) must be confirmed by counsel before they are treated as fact.
