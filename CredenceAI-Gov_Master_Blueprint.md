# CredenceAI-Gov: The Complete Master Blueprint

**Government Digital Evidence, Authenticity and Trust Assurance Platform**
*Unified edition: merges the "Complete Project Plan (v3)" with the "First-Principles Assessment and Detailed Implementation Blueprint"*

> **How to read this document**
>
> - Figures marked *(proposal)* or *(assumption)* are targets or planning inputs, not measured results.
> - Costs are planning estimates, not quotations.
> - Legal and compliance items need confirmation by counsel and your security officer.
> - Scores and percentages given for the plan itself are judgment, not measurement.
> - **Status labels** used throughout, to stop roadmap items being mistaken for current capability:
>   - **Existing (documented):** the repository documents the capability. This does not mean every deployment is live or independently tested.
>   - **Partial:** the repository describes the work as in progress, optional or configuration-dependent.
>   - **Proposed:** part of the target blueprint, with no implementation evidence in the repository.
>   - **Implemented and tested / Implemented, validation pending / Planned** are the three labels to use in presentations once code exists (see §26).

---

## Table of contents

**Part A: The Idea**
1. The idea in one page
2. First-principles restatement (purpose, core claim, what is not claimed)
3. Problem, inputs, users and roles
4. Current foundation (what the repository already has)
5. Scope: workflows, Release 1 capabilities, non-goals, lead-workflow decision

**Part B: Architecture and Features**
6. System architecture
7. Shared analysis contract (the typed result envelope)
8. Evidence integrity
9. Verify engine (claims and sources)
10. Inspect (provenance, images, documents, and the video/audio plugin specs)
11. Protect (link capture, and the cyber-analysis plugin spec)
12. Decision engine, policy, risk tiers and human oversight
13. User interface (evidence-first)
14. Responsible-AI governance and model lifecycle
15. Security, privacy and compliance

**Part C: Scalability**
16. Scalability

**Part D: Scientific Credibility**
17. Scientific credibility and evaluation

**Part E: Delivery**
18. Deployment and operations
19. Roadmap with gates
20. Team and cost
21. Acceptance metrics

**Part F: Judgment**
22. Risks (red team) and design flaws with mitigations
23. Strengths
24. Trade-offs and alternatives
25. Key insights
26. Open decisions, first 30 days and status language
27. The whole idea on one page

**Appendices**
A. Complete feature catalogue
B. Module status matrix
C. Requirements traceability template
D. Glossary

---

# PART A: THE IDEA

## 1. The idea in one page

**Definition.** CredenceAI-Gov is a low-cost, evidence-first platform that helps authorised government analysts verify claims, documents and images. It collects traceable evidence, checks provenance, applies deterministic policy, and routes consequential decisions to human reviewers. It produces an **evidence package**, never a verdict.

**The problem.** Government departments meet questionable claims, forged documents, doctored images and suspicious links through scattered tools and informal chat threads. The result is slow, inconsistent, hard to defend and impossible to audit.

**What it produces.** One controlled case per question, with hashed originals, sourced evidence, an evidence matrix, a policy-driven review path and a signed, portable package that another department, auditor or court-facing process can verify.

**What it never does.**

- It never outputs a universal trust score or a binary real/fake label.
- It never treats "no manipulation detected" as "authentic".
- It never acts autonomously: no publishing, takedown, notification or enforcement.
- It never lets an LLM control authorisation, retention, deletion, risk tier or audit.

**Principles.**

> Evidence before AI. Provenance before prediction. Rules before automation. Human authority before consequential action. Audit before scale. **Claim only what is validated. Scale only what is measured.**

---

## 2. First-principles restatement

### 2.1 The idea in plain language

CredenceAI helps people assess whether digital information is credible, whether media may have been manipulated, whether linked resources pose risk, and whether the AI system's own conclusions were produced transparently and under controls.

It is **not** four unrelated tools behind one interface. Its central workflow is:

1. Accept a claim, file, URL, document or (later) security indicator.
2. Identify the kind of analysis required.
3. Collect and preserve the input and its context.
4. Run the appropriate analysis components.
5. Compare results with independent evidence.
6. Assess uncertainty, risk and policy constraints.
7. Present a reasoned result with supporting evidence.
8. Route uncertain or consequential cases to a human reviewer.
9. Preserve a traceable record of inputs, model versions, decisions and review actions.

### 2.2 Core claim (a hypothesis, not a result)

A unified evidence-and-governance architecture gives more useful digital-trust assessments than isolated classifiers, because it combines source credibility, media analysis, evidence consistency, provenance, risk signals, uncertainty and human oversight. This becomes a demonstrated claim only after implementation, evaluation on representative data and end-to-end testing. Gate S2 (§17.13) tests exactly this.

### 2.3 Purposes

| Purpose | Meaning |
|---|---|
| **Verification** | Examine claims and artifacts using multiple sources and methods |
| **Authenticity assessment** | Surface indicators consistent with synthetic or manipulated media |
| **Defensive security** | Safely capture and triage suspicious links; export evidence to existing SOC and CERT-In processes |
| **Responsible operation** | Constrain automation, expose uncertainty, enable human review, document model behaviour |
| **Auditability** | Preserve evidence lineage so any assessment can be reconstructed |

### 2.4 What the project does not claim

It cannot always determine truth, prove that a person is who a recording depicts, guarantee detection of every deepfake, or establish that a source is trustworthy from a score alone. Specifically:

- A cryptographic hash proves a recorded byte sequence is unchanged. It does **not** prove the original was genuine.
- A model confidence value is not automatically a calibrated probability.
- A "project-alignment percentage" is a planning estimate, not model accuracy.
- Authority is not truth: a primary source can be outdated, and a company is authoritative only about its own announcement.

### 2.5 Six properties that must never be conflated

| Property | Question it answers | Typical evidence |
|---|---|---|
| **Authenticity** | Does the artifact appear manipulated or synthetic? | Detector output within its validity envelope, forensic checks |
| **Accuracy** | Is the claim supported by evidence? | Sourced spans, tiering, evidence matrix |
| **Integrity** | Does the artifact match what was recorded at intake? | SHA-256, WORM store, hash chain |
| **Provenance** | What is known about origin and handling history? | C2PA, signatures, custody events |
| **Security** | Does the artifact or link present a risk? | Isolated snapshot, reputation feeds (later) |
| **Trust decision** | What is the policy-governed interpretation for this use case? | Rule-derived evidence state plus human disposition |

Each is represented separately and only combined by deterministic policy, never by a hidden average.

---

## 3. Problem, inputs, users and roles

### 3.1 Inputs and what the platform does with them

| Input | Real question | What the platform does |
|---|---|---|
| Viral claim | Is credible evidence supporting it? | Decompose, retrieve, classify stance, build evidence matrix |
| Document or circular | Is it genuine and unaltered? | Hash, signature checks, revision checks, comparison to records |
| Image | Is there provenance? Any manipulation indicators? | Metadata, C2PA, repeat-media lookup, validated detector (if enabled) |
| Link | Is it safe to examine, and what does it say? | Isolated snapshot capture, hashed as evidence |
| News report | Is it corroborated by primary sources? | Source tiering and independence estimate |
| Handled evidence | Can its history be proven? | Custody record, hash-chained audit, signed package |

### 3.2 Roles

| Role | Capability |
|---|---|
| Analyst | Submits and investigates cases |
| Reviewer | Reviews elevated (R2) cases |
| Supervisor | Approves critical (R3) dispositions |
| Administrator | Users, policies, configuration |
| Auditor | Read-only audit access |
| System service | Machine-to-machine actions |

Secondary audiences named in the repository (researchers, compliance teams, due-diligence users) can be served by the same workflow only if access control and domain-specific decision criteria stay explicit.

---

## 4. Current foundation (what the repository already has)

The repository documents CredenceAI as a multi-source search-intelligence platform. These items are **Existing (documented)** unless marked otherwise, and each needs verification in the target deployment.

| Area | Documented foundation | Reuse in CredenceAI-Gov |
|---|---|---|
| Backend and jobs | FastAPI, Celery, Redis asynchronous jobs | Modular-monolith API and named worker queues |
| Frontend and SDK | React, Vite, Tailwind, TypeScript; TypeScript SDK | Analyst UI, extended to GIGW 3.0 / WCAG 2.1 AA |
| Retrieval adapters | SearXNG, Wikidata, Wikipedia, GDELT, OpenAlex, Common Crawl (availability is configuration-dependent) | Optional live-search mode; curated corpus is the primary evidence base |
| Search intelligence | Intent classification, source selection, normalisation, quality scoring, hybrid ranking | Retrieval layer. Quality score is **not** claim truth |
| Research workflows | Goal decomposition, multi-job research | Claim decomposition and multi-claim cases |
| Evidence structures | Evidence graph, entity linking, claims, intelligence cards, evidence panel | Evidence matrix, extended to media, provenance and reviewer evidence |
| Agent layer | Orchestration, per-job working memory, budget enforcement, decision trails (**Partial**: tracker marks some behaviour in progress) | Bounded, policy-gated; no autonomous action |
| Access control | Authentication, user-scoped resources, API keys, quotas, multi-tenant controls | Re-run isolation tests for every new endpoint and artifact |
| AgentGate | Separately deployed governance/policy microservice | Candidate host for policy gates: media processing, review, model use |
| Operations | Docker, deployment configs, migrations, CI workflows, ops docs | Basis for the cell template and CI evaluation harness |

**Not verified in the repository** (therefore **Proposed**): a production multimodal deepfake detector, a unified trust-scoring model (deliberately not built, see §12), a cryptographic chain-of-custody service, and a dedicated cyber threat-intelligence module.

**First action:** audit the repo against the four hard dependencies (§6.3) and list what to keep, wrap or replace.

---

## 5. Scope

### 5.1 Workflows

- **W1 Claim and information verification.** Claim → decompose → retrieve authoritative evidence → stance → evidence matrix.
- **W2 Artifact authenticity.** Image or document → secure intake → hash → provenance → forensics → matrix → review.
- **W3 Link triage.** Release 1 is snapshot capture only. Reputation checks arrive later.

### 5.2 Release 1 capabilities (12)

1. SSO-ready authentication, MFA, RBAC, tenant isolation
2. Case creation from claim text, PDF or image
3. Evidence integrity: hashing, immutable originals, custody, audit chain
4. Curated authoritative corpus with hybrid retrieval
5. Claim decomposition and stance classification with quoted spans
6. Provenance basics: metadata, C2PA, PDF signatures, repeat-media lookup
7. Evidence matrix
8. Policy rules and review queue
9. Signed evidence package and report
10. Observability, backup and tested restore
11. Evaluation harness in CI
12. Capacity and cost telemetry

### 5.3 Non-goals

- A universal trust score
- Autonomous takedown or response
- Face or speaker identification, emotion detection
- Blockchain, an own foundation model, SIEM/SOAR
- Video and audio before validated plugins exist

### 5.4 Modality sequencing (reconciling the two source documents)

The assessment document lists image, video, audio and cyber as analysis domains. The project plan defers video, audio and reputation analysis. The unified position:

| Modality / domain | Release | Why |
|---|---|---|
| Claims and sources | R1 | Reuses existing retrieval; highest evidence value |
| Documents (signatures, revisions, register comparison) | R1 | Ground truth is department-owned; no GPU, no LLM needed |
| Image (provenance, repeat-media, optional detector) | R1 provenance; R2 detector only if gate S4 passes | A detector is credible only after validation on degraded data |
| Link capture | R1 | Safe, hashed snapshot only |
| Link reputation / cyber enrichment | R3 | Needs licensed feeds and isolation maturity |
| Video and audio | R3 plugins; until then, export to an accredited lab | Highest evaluation burden; sampling can miss brief edits |

Unit-level specifications for the R3 modalities are kept in §10.5 and §11.3 so the design is not lost.

### 5.5 Lead-workflow decision at Gate G0

A cheap pre-build test decides which workflow leads Release 1 (§26.1). It checks whether authoritative answers exist often enough for open claims (W1). If they do not, the lead becomes **official-record authenticity**: "did this department actually issue this document?" That is a W2 variant with department-owned ground truth, no LLM and no GPU. About 90% of the core is shared, so the decision changes sequencing, not architecture.

---

# PART B: ARCHITECTURE AND FEATURES

## 6. System architecture

### 6.1 Four planes

```text
Users ─► SSO / MFA / RBAC ─► API (FastAPI, stateless)
│
├─ CONTROL PLANE       identity · tenancy · policy packs · audit
├─ EVIDENCE PLANE      case service · WORM object store · hashing · custody · package
├─ INTELLIGENCE PLANE  corpus · retrieval · claim analyzer · provenance · sandboxed plugins
└─ REVIEW PLANE        evidence matrix · risk tier · review queue · report
```

The assessment's six logical layers map onto these planes:

| Assessment layer | Plane |
|---|---|
| 1. Intake and identity | Control |
| 2. Specialised analysis | Intelligence |
| 3. Evidence and provenance | Evidence |
| 4. Decision and governance | Control (policy) + Review |
| 5. Presentation and action | Review (advisory only; no action integrations) |
| 6. Lifecycle assurance (evaluation, drift, audit, recovery) | Cross-cutting (§14, §17, §18) |

### 6.2 Technology

| Layer | Choice | Rationale |
|---|---|---|
| Frontend | React + TypeScript to GIGW 3.0 / WCAG 2.1 AA | Accessibility is a procurement requirement |
| API | FastAPI modular monolith | Reuses existing code |
| Identity | Keycloak (OIDC/SAML) | SSO, MFA and federation without a custom IAM |
| Database | PostgreSQL with full-text search and pgvector | One datastore |
| Queue | Redis + Celery with named queues | Already in the repo |
| Object storage | S3-compatible with object lock | Immutable originals without blockchain |
| Upload safety | ClamAV, sandboxed parsers, size and type limits | The platform ingests hostile files |
| Provenance tools | ExifTool, open-source C2PA libraries, perceptual hashing | Free |
| Models | Small multilingual embedder on CPU, an approved LLM (hosted or local), one detector plugin | GPU optional |
| Policy | Versioned rule packs evaluated in code (AgentGate is a candidate host) | Deterministic and testable |
| Observability | OpenTelemetry, Prometheus, Grafana, Loki | Open source |
| Deployment | Docker Compose, with a Helm chart at the HA tier | No orchestration before need |

Run one licence review of every component early, since several popular infrastructure projects have changed licences.

### 6.3 Four hard dependencies

1. **Identity before cases.** Nothing is stored without an owner, tenant and classification.
2. **Integrity before analysis.** No analyzer touches an artifact lacking a hash and custody record.
3. **Citations before summaries.** The LLM reasons only over retrieved text, and every displayed statement traces to a stored span.
4. **Policy before automation.** No automated step exists unless a rule authorises it.

### 6.4 Analyzer plugin contract and Model Registry

Each analyzer declares its ID, version, supported inputs, resources, output schema, confidence semantics, known limitations, model hash, timeout and **validity envelope** (§17.2). Analyzers run in sandboxed workers with no network by default, return structured findings only and cannot write to cases directly.

A signed **Model Registry** entry holds:

- Version and hash, licence, owner
- Intended and prohibited use
- Evaluation results and benchmark version
- Validity envelope, validation date and review-by date

Past its review-by date, a model is blocked from automated use by policy. Weights load only from safe formats (safetensors) and are hash-pinned.

### 6.5 Modular monolith first, services only when measured

Split a service out only when a measured bottleneck demands it. The first candidates are media workers and the crawler.

| Option | Benefit | Cost |
|---|---|---|
| Worker modules in the existing backend | Simple deployment, shared data model | Dependency and scaling coupling |
| Separate inference service | Independent scaling and runtime dependencies | Network, deployment, monitoring and contract complexity |

**Decision rule:** start with worker-isolated modules unless GPU/runtime needs, a security boundary or independent scaling justify a separate service.

---

## 7. Shared analysis contract (the typed result envelope)

Every module exposes the same job lifecycle and a versioned, typed result. Unknown fields are handled safely, and untrusted input is never treated as executable instructions.

| Field | Meaning |
|---|---|
| `analysis_id` | Unique identifier |
| `tenant_id` / `owner_id` | Access-control scope |
| `input_type` | text, image, document, URL (later: video, audio, telemetry) |
| `input_reference` | Secure reference to the stored input; never a raw path |
| `created_at`, `completed_at` | Timestamps |
| `status` | queued, running, completed, failed, cancelled, review-required |
| `module` | Analyzer responsible |
| `model_name`, `model_version` | Where applicable, linked to the Model Registry |
| `classification` | Domain-specific outcome, **not** a universal real/fake label |
| `confidence`, `uncertainty` | With documented semantics (not assumed to be calibrated probabilities) |
| `evidence[]` | Typed findings with source references, timestamps or segments |
| `limitations[]` | Known caveats relevant to this run |
| `policy_decision` | allowed, restricted, blocked, review-required, plus rule-pack version |
| `review_state` | Reviewer decision and rationale, when applicable |
| `provenance_reference` | Link to the integrity and lineage record |

Lifecycle features: timeouts, cancellation, retries with backoff, idempotency keys and a dead-letter queue (§16.5).

---

## 8. Evidence integrity

### 8.1 Intake flow

```text
Validate → malware scan → case + evidence ID → SHA-256 → timestamp
        → encrypt with per-case key → store original (WORM) → custody event
```

Validation covers file signature, MIME type, extension, size and dimension limits, and safe decoding. Metadata is extracted where present.

### 8.2 Rules

- Originals are never modified. Every transformation is a **derived artifact** recording its parent hash, tool and version.
- Every view, download, analysis, review and export is an audit event.
- **Retention versus erasure.** Originals are encrypted under per-case data keys, so deletion at end of retention destroys the key (crypto-shredding). The audit chain retains only hashes and metadata, so integrity history survives lawful erasure. Legal hold suspends deletion.
- Reviewer decisions are linked to the exact analysis they relate to.
- Key rotation and retention classes are defined before real data is loaded.

### 8.3 Audit

- Events form a **per-case hash chain**.
- Each cell computes a **daily Merkle root over all events and signs it**, so any event can be verified with an inclusion proof in O(log n) without scanning the log.
- An optional RFC 3161 trusted timestamp can anchor the daily root.
- An authorised **integrity-verification endpoint** re-checks hashes and chains on demand.

### 8.4 Evidence package

```text
manifest.json · original_hashes.json · claims.json · sources.json · evidence.json
analyzer_results.json · model_manifest.json · policy_decisions.json
reviewer_actions.json · audit_extract.json · report.pdf · manifest.sha256 · signature
```

The report and manifest carry a fixed banner: **"Decision support. Not a finding of fact."** The package is signed with the organisation's key (the signing arrangement is confirmed with the department). Cross-cell and cross-department handoff happens only through this package.

### 8.5 What each cryptographic operation proves

| Operation | Proves | Does not prove |
|---|---|---|
| SHA-256 at intake | Bytes unchanged since intake | The content was genuine before intake |
| Signature on package | Package came from the holder of the key and is unaltered | The findings are correct |
| Hash chain / Merkle root | Log not silently altered | The logged actions were wise |
| RFC 3161 timestamp | Existence at or before a time | Anything about authorship |

Blockchain anchoring is rejected for now: it adds cost and privacy complexity without solving the initial-truth problem. It is justified only if independent parties must verify records without trusting the operator.

### 8.6 Legal fit and limits

The package should help the department produce the hash-based certificate for electronic records under the Bharatiya Sakshya Adhiniyam 2023 (s.63). Confirm the exact format with legal. The platform is **decision support, not an accredited forensic laboratory**. Cases needing court-grade media forensics are exported with the package to an accredited lab.

---

## 9. Verify engine (claims and sources)

### 9.1 Authoritative corpus

- Ingest designated sources: gazettes, ministry and department portals, press releases, regulators, standards bodies and public legislative and court records.
- Every fetch is a **hashed, timestamped snapshot** with effective-date and supersession metadata.
- The source list is human-curated. A pinned, verified domain list with change alerts guards against lookalike and compromised domains.
- The crawler is a separate, rate-limited job respecting robots.txt and site terms.
- Live search (the existing SearXNG, GDELT and similar adapters) is optional, connected mode only, and results enter the case as snapshotted evidence.
- A named **corpus owner** is responsible for ingestion health, because crawlers rot.

### 9.2 Source tiers

| Tier | Evidence |
|---|---|
| T1 | Primary official or statutory record |
| T2 | Regulator, recognised institution, standards body, peer-reviewed research |
| T3 | Established news organisation |
| T4 | Organisation or company statement, independent OSINT, social media |
| T5 | Anonymous or unknown |

**Flags:** self-interested, superseded, dead link, snapshot only.

### 9.3 Claim pipeline

Smallest functional units, in order:

1. **Intake and normalisation:** clean text, detect language, stamp the claim's **as-of date**.
2. **Intent classification** (existing) to choose the analysis route.
3. **Decomposition** into atomic checkable claims (LLM, constrained JSON schema).
4. **Source selection and hybrid retrieval** (keyword plus vector), **restricted to evidence that existed at the as-of date**. This prevents temporal leakage in both production and evaluation.
5. **Normalisation and deduplication** of results, with source metadata capture.
6. **Stance classification** per passage (supports, contradicts, neutral) with an exact quoted span.
7. **Citation check:** any statement without a matching span in a retrieved document is dropped automatically.
8. **Claim-to-evidence association** and corroboration/contradiction representation.
9. **Evidence matrix assembly** (§9.5) with score rationale.
10. **Citation and evidence display** in the UI.

Retrieved text is untrusted data (§15). The span check stops fabricated citations. It does not stop misread ones, which is why faithfulness is measured by humans (§17.5).

### 9.4 Independence

A heuristic lower-bound estimate using canonical URLs, near-duplicate detection (SimHash/MinHash), explicit wire attribution, shared quoted passages and publication order. It reports "N articles, at least M independent origins (estimate)", and "unknown" is a valid answer.

### 9.5 Output: evidence state from rules, not a score

Every signal has an operational definition and a threshold validated on Claim-Bench (§17.3). Nothing is graded by free-text LLM judgment.

| State | Rule (initial, validated in R1) |
|---|---|
| Supported | At least one T1/T2 supporting span, no T1/T2 contradicting span, evidence not superseded |
| Contradicted | At least one T1/T2 contradicting span and no T1/T2 support |
| Mixed | T1/T2 support and contradiction both present, or T3 conflicts with no T1/T2 evidence |
| Insufficient evidence | None of the above |
| Out of scope | Opinion, prediction or otherwise not checkable |

Caveat flags (stale source, single origin, snapshot only, media provenance absent) travel with the state. The signal matrix stays visible:

| Signal | Example |
|---|---|
| Independent origins (estimate) | ≥3 |
| Primary source | Present (T1) |
| Contradiction | Minor, older source |
| Freshness | Current |
| Media provenance | Absent |
| **Evidence state** | **Supported, with caveats** |

### 9.6 Claim clustering and verdict reuse

Many sightings of one viral claim become one case with sightings attached. Reuse of a prior result requires a similarity above a validated threshold, an unexpired TTL, unchanged evidence snapshots and, at R2+, analyst confirmation. See §16.4.

### 9.7 Multilingual

This is Release 2. It uses multilingual embeddings and open Indic translation models. Every added language needs its own gold set before it counts as supported.

---

## 10. Inspect (provenance, media, documents)

### 10.1 Provenance status

**Verified** (valid C2PA or signature), **Absent** or **Broken**. Absent is not suspicious, since most genuine content has no provenance.

### 10.2 Repeat-media lookup

Perceptual-hash comparison against the department's own case library and an archive of debunked or misused media. It catches repeats already seen. Wider reverse search is analyst-initiated and links out.

### 10.3 Metadata

Shown as a lead, never proof. It is easily forged and often stripped by platforms. Neither metadata nor a single model output is treated as conclusive.

### 10.4 Documents and images: detailed units

**Document checks (R1):** signature validation, revision and incremental-update detection, metadata inconsistencies, text-layer versus render comparison and, where a department register exists, comparison against issued-document records.

**Image pipeline units:**

1. Upload endpoint and authorisation
2. File signature, MIME, extension, size and dimension validation
3. Safe decoding and normalisation
4. Original-file hashing
5. Metadata extraction
6. Detector selection and version recording (from the Model Registry)
7. Inference (inside the validity envelope only)
8. Optional region-level localisation when the model supports it
9. Calibration and uncertainty handling
10. Evidence serialisation and persistence
11. UI rendering of result, limitations and evidence
12. Human-review path for inconclusive or high-impact results

**One detector plugin, off by default.** It is enabled only after passing the media gate (S4, §17.13), and only inside its validity envelope. Outside it, the result is automatically Inconclusive with the reason shown. Output states: *Manipulation indicators detected / No indicators detected (not evidence of authenticity) / Inconclusive*. The detector never sets a status alone and is only one signal in the matrix.

**Known limitations:** compression, resizing, filters and ordinary editing can introduce artifacts; detectors age as generators change; benign edits can be flagged.

### 10.5 Video and audio plugin specifications (Release 3, validation-gated)

Not built in Releases 1–2. Analysts escalate through the evidence package to an accredited lab. When built, each is a sandboxed plugin that must pass its own scientific gate.

**Video plugin units:**

1. Upload and container validation
2. Duration, codec, frame-rate and resolution inspection
3. Safe decoding
4. Configurable frame sampling
5. Scene-change detection
6. Optional face detection and tracking, only where lawful and necessary
7. Frame-level inference
8. Temporal-consistency analysis
9. Audio-track extraction
10. Audio-video synchronisation analysis
11. Segment-level evidence aggregation
12. Video-level conclusion with uncertainty
13. Timestamped evidence display
14. Timeout, cancellation and retry handling

*Limits:* a suspicious frame does not make a whole video fake; sampling can miss brief edits; re-encoding, low resolution and overlays degrade performance; aggregation rules need validation.

**Audio plugin units:**

1. Upload and format validation
2. Safe decoding and resampling
3. Duration and channel inspection
4. Voice-activity or segment detection
5. Spectrogram or feature extraction
6. Synthetic-speech inference
7. Segment-level suspiciousness output
8. Confidence calibration
9. Audio-video sync check when paired video exists
10. Result serialisation and review workflow

*Limit:* synthetic-speech detection is **not** speaker identification. The platform never infers a real person's identity from voice (or face) similarity.

---

## 11. Protect (links and cyber analysis)

### 11.1 Release 1: link capture only

An analyst-initiated fetch runs in an isolated, network-restricted fetcher that cannot reach internal networks and produces a hashed snapshot (HTML and screenshot). The app host never fetches URLs. Links are defanged and never auto-clicked.

**Fetcher safeguards:** block private and internal address ranges (SSRF), restrict protocols and redirects, enforce egress controls, set resource and time limits, never execute active content, log analyst access, and test with safe fixtures.

### 11.2 Release 3: reputation checks

Reputation checks from free or open feeds where the licence permits government use. Cyber incidents go to existing SOC and CERT-In processes; the platform exports evidence only. It is **not** a SIEM or SOAR.

### 11.3 Cyber-analysis plugin units (Release 3 specification)

1. URL, domain, email or indicator intake
2. Canonicalisation and validation
3. Safe parsing without executing active content
4. Reputation and threat-feed lookups where configured and licensed
5. Domain and URL lexical feature extraction
6. Redirect-chain inspection in an isolated environment, if enabled
7. Indicator-of-compromise (IOC) normalisation
8. Correlation across indicators and cases
9. Severity rationale with source attribution
10. Alert creation and triage state
11. Analyst notes and disposition
12. Service-health and recovery telemetry

**Safety boundary:** potentially malicious content is handled only in isolated, restricted infrastructure. Prototypes use controlled datasets and simulated traffic. AI recommendations never execute countermeasures; authorisation and policy gates remain mandatory, and a critical security flag is **non-compensatory** (no average can cancel it).

---

## 12. Decision engine, policy, risk tiers and human oversight

### 12.1 Decision order (fail-closed)

1. Check hard security and policy restrictions.
2. Check whether required evidence is missing or invalid.
3. Evaluate each domain-specific result separately.
4. Identify contradictions between modules.
5. Assess whether outputs are calibrated and applicable to this input (validity envelope).
6. Derive the evidence state by rule and write the rationale.
7. Route uncertain or consequential cases to human review.
8. Record exact inputs, versions, rule-pack and decision.

### 12.2 Why there is no trust score

The assessment allowed a weighted score "as a navigation aid". The unified plan goes further: **no aggregate score exists.** Combining incomparable measurements implies false precision, hides missing evidence and risks cancelling a critical finding. The signal matrix plus a rule-derived evidence state do the navigation job instead, and any future aggregate would need a published rubric, labelled validation data, calibration and non-compensatory gates.

### 12.3 Policy rules

Rules are versioned data evaluated by deterministic, unit-tested code, and each decision records its rule-pack version.

```text
IF evidence_sources < 2 AND no_primary_source      THEN state = insufficient_evidence
IF media_result = inconclusive AND impact = high   THEN human_review = mandatory
IF model_past_review_date OR input_outside_envelope THEN automated_use = forbidden
IF any_analyzer_error_or_timeout                   THEN state = insufficient_evidence + review
```

Policy is tested at API **and** worker boundaries with allowed, denied and escalated cases, so governance is observable in runtime behaviour and not only in documents.

**The LLM does:** decomposition, entity extraction, summaries and drafts. **It never does:** authorisation, retention or deletion, risk tier, audit or any action.

### 12.4 Risk tiers

| Tier | Meaning (set by impact, not model confidence) | Handling |
|---|---|---|
| R0 | Informational | Automatic, audited |
| R1 | Routine | Analyst confirms |
| R2 | Elevated (public impact, named individuals, legal consequence) | Reviewer approval |
| R3 | Critical | Supervisor plus second reviewer, mandatory evidence review |

### 12.5 Automation-bias controls

- Evidence is shown before the AI summary.
- R2 and above require a recorded rationale.
- Second review is sampled on R0/R1.
- Override rate and time-to-approve are tracked, with an alert when approval is near 100% and fast.

### 12.6 Advisory by design

- No publish, takedown or notification integrations exist.
- Every package carries the decision-support banner.
- **Dispositions** (Confirmed accurate, Miscontextualised, Cannot determine, Refer to external lab) are recorded separately from evidence states.
- Cases that affect named individuals record a notice and grievance route in the departmental process.

---

## 13. User interface (evidence-first)

The UI answers five questions: What was analysed? What was found? Why? How uncertain is it? What happens next?

| Screen | Contents |
|---|---|
| **Submission** | Claim text, PDF, image or link; classification and purpose set at intake |
| **Job status** | Queued/running/completed/failed, retry or cancel |
| **Case workspace** | Evidence first, AI summary after; claims, spans, source tiers, caveat flags |
| **Evidence matrix** | Signal matrix and rule-derived state, with missingness shown |
| **Authenticity panel** | Provenance status, repeat-media hits, detector state (or Inconclusive with reason), limitations |
| **Review queue** | Tiered queue, rationale capture, SLA ageing |
| **Responsible-AI monitor** | Model versions, evaluation dates, drift signals, policy events, review backlog |
| **Audit explorer** | Chronological record of submission, processing, model runs, policy decisions and reviewer actions, with inclusion-proof verification |
| **Cyber centre (R3)** | Indicators, severity, enrichment sources, investigation state |
| **Admin** | Users, policy packs, retention classes, corpus health |

Rules: personal data and faces masked where not needed; accessible to GIGW 3.0 / WCAG 2.1 AA; simulated or illustrative data is always labelled as such; every new workflow gets API contracts, state management, error handling and tests before UI polish.

---

## 14. Responsible-AI governance and model lifecycle

Governance is not complete because policies exist on paper. It must be enforced at runtime and tested.

| Control | Implementation |
|---|---|
| Model registry | Signed entry per model (§6.4) |
| Model card | Intended and prohibited use, training and evaluation provenance, known limitations |
| Dataset record | Version, licence and usage restrictions |
| Evaluation report | Per media type and, where lawful, per relevant subgroup |
| Calibration report | Reliability diagrams and Brier score (§17.7) |
| Drift monitoring | Signals and review thresholds (§17.11) |
| Adversarial testing | Standing prompt-injection and evasion suites |
| High-risk policy | Rule-gated actions; fail-closed behaviour |
| Human review | Queue, reviewer identity, rationale |
| Explanation template | Tied to observed evidence, never free-form |
| Reproducible decision record | Replayable from stored artifacts |
| Incident and rollback | Procedure for degraded models; model disabled by policy when past review-by date |

Every output reports its model and policy lineage (100% recorded, §21).

---

## 15. Security, privacy and compliance

### 15.1 Threat model

| Threat | Control |
|---|---|
| Hostile uploads (malware, parser exploits, decompression bombs) | Scan, sandboxed parsing, limits, never execute |
| Indirect prompt injection from retrieved pages and documents | Untrusted-data handling, fixed output schemas, LLM with no tools or network, span check, hidden-text stripping, standing red-team suite. This is mitigation, not elimination |
| Lookalike or compromised official domains | Pinned verified domain list, certificate checks, change alerts |
| Cross-tenant leakage (including vector search and caches) | Row-level security, per-tenant filters, automated isolation tests |
| Insider over-access | Least privilege, case-level ACL, access reason on restricted cases, audit review |
| Corpus poisoning | Human-curated sources, snapshot hashing, change alerts |
| Detector evasion | Detector is one signal, periodic revalidation |
| Model supply chain | Hash-pinned weights, safe formats, no auto-download in production |
| Leakage to an external LLM | Policy blocks external LLM by data classification |
| Evidence tampering | WORM, hash chain, signed Merkle roots |
| SSRF and hostile links | Isolated fetcher, blocked internal ranges, restricted redirects |

### 15.2 Privacy

Every artifact carries purpose, retention class, access level and delete-after, with legal hold. Face and personal data are masked in views that do not need them. Everything uses TLS in transit and encryption at rest, with per-case keys (§8.2). Media, voice, faces, URLs and telemetry can be sensitive, so data minimisation, explicit retention, deletion workflows and legal review apply before any real-user deployment.

### 15.3 Legal and policy context (verify each item with counsel)

- The IT Rules amendment on synthetic content was notified on 10 February 2026 and took effect on 20 February 2026. It requires synthetic content to be labelled and embedded with metadata or identifiers, bars platforms from stripping them, and sets a three-hour window to disable access after lawful orders. A human-review case workflow cannot sit on the critical path of such a deadline. Provenance data is only present on compliant content, so absence proves nothing.
- The DPDP Rules were notified on 14 November 2025, and most substantive rules (3, 5 to 16, 22 and 23) commence eighteen months after publication, roughly May 2027, during your pilot. The Central Government can exempt specific State instrumentalities or types of processing from some obligations, so which exemptions apply to your department is a ruling you need in writing.
- Government fact-finding that feeds takedown is legally contested. The Bombay High Court struck down the 2023 IT Rules provision for Fact Check Units, and the Supreme Court declined to stay that ruling while issuing notice on the Union's challenge. The platform is not that unit, but the advisory-only design (§12.6) and a counsel-reviewed charter are mandatory.

*Note: these legal statements were carried over from the source plan and not independently re-verified here.*

### 15.4 Compliance register (confirm with counsel and the security officer)

| Item | Design implication |
|---|---|
| DPDP Act 2023 and Rules 2025 | Security safeguards, logging, retention and erasure controls |
| CERT-In Directions (April 2022) | Six-hour incident reporting and rolling 180-day log retention for covered entities, with central logging and incident export built in |
| GIGW 3.0 / WCAG 2.1 AA | Accessibility in the definition of done |
| IT Act 2000; Bharatiya Sakshya Adhiniyam 2023 | Digital signatures, electronic-evidence certificate support |
| Current IT Rules on synthetic content | Platform assists review and does not decide takedown |
| MeitY-empanelled cloud or NIC hosting; security audit by a CERT-In empanelled auditor | Needed before production, so start the lead-time conversation in R0 |
| Departmental data classification and AI governance guidance | Every output reports model and policy lineage |

---

# PART C: SCALABILITY

## 16. Scalability

### 16.1 What actually has to scale

Three things scale, and compute is the smallest:

1. **Humans.** Reviewer and analyst throughput is the binding constraint.
2. **Trust infrastructure.** Audit, integrity verification, signing and the registries.
3. **Compute and data.** Workers, storage, retrieval and LLM cost.

Illustrative arithmetic (assumptions, replaced by pilot measurements):

- 3,000 cases a day with 15% reaching R2/R3 gives 450 reviewed cases a day.
- At 20 minutes each, that is 150 hours a day. At 6 productive review hours per person, that is **25 reviewers at full load, about 31 at a healthy 80% utilisation**.
- With 20% of cases carrying an image and about 2 s of GPU time each, that is roughly 20 GPU-minutes a day.

So reviewer throughput must scale first, and compute follows cheaply.

### 16.2 Load model and tiers

**Load drivers:** raw submissions per day, dedup ratio, artifacts per case, artifact size, claims per case, retrieval queries per claim, LLM tokens per claim, GPU-seconds per image, reviewer minutes per tier, retention years.

**Derived:**

- New cases per day = submissions × (1 − dedup ratio).
- Storage per year ≈ cases/day × artifacts × size × 365 × derived-artifact factor. For example, 3,000 × 5 × 3 MB × 365 × 1.3 ≈ **21 TB a year**.
- Keep reviewer utilisation below about 80%, or wait times grow sharply.

| Tier | Design target (not measured) | Deployment |
|---|---|---|
| T0 Pilot | ≤25 analysts, ≤300 cases/day | 1 cell, 2 hosts |
| T1 Department | ≤150 analysts, ≤3,000 cases/day | 1 cell, HA, GPU pool |
| T2 State or ministry cluster | ≤1,000 analysts, ≤30,000 cases/day | N cells plus control plane |
| T3 National federation | Many cells | Federated policy and model registry, shared evaluation |

### 16.3 Cell architecture (the scale-out unit)

- A **cell** is a complete, independent data plane: API, PostgreSQL, object store, workers, corpus, keys and audit.
- No case data leaves a cell. Cross-cell handoff happens only through signed evidence packages.
- A thin **central control plane** distributes signed policy packs and signed model manifests, runs release and benchmark management, and collects opt-in anonymised metrics.
- This contains blast radius, keeps per-department data sovereignty and gives a simple air-gapped variant (a cell fed by signed update bundles) at no extra product cost.
- Cells are stamped from one infrastructure-as-code template (a Compose profile first, then a Helm chart). The design target is that **a new cell stands up in a day**.

### 16.4 Human-throughput scaling

- **Claim clustering and canonicalisation:** many sightings of one viral claim become one case with sightings attached.
- **Verdict reuse with expiry:** requires similarity above a validated threshold, an unexpired TTL, unchanged evidence snapshots and, at R2+, analyst confirmation. A change in a source invalidates dependent results.
- **Tiered triage** keeps humans on R2/R3, with sampled audit on R0/R1.
- **Backlog controls:** queue-age alerts, an SLA per tier and surge rules that defer bulk work.
- The **false-merge rate** of clustering is a measured scientific metric (§17.5), because a wrong merge is a correctness error.

### 16.5 Compute scaling

- Queues are separated by workload and **priority class**: P0 deadline-bound, P1 elevated, P2 routine, P3 bulk and reprocessing. Each class has its own worker pool, because broker-level priorities are only approximate.
- **Admission control:** per-tenant quotas, rate limits and artifact limits. Overload returns 429 with a retry hint, and bulk imports are throttled.
- Jobs are **idempotent**: idempotency keys, transactional outbox, retries with backoff and a dead-letter queue.
- **Autoscale on oldest-message age against the SLO**, not CPU. GPU workers scale on depth × service time and can scale to zero.
- An **LLM gateway** enforces per-case and per-tenant token budgets, response caching keyed by canonical claim hash, timeouts, a circuit breaker and a fallback model.
- GPU inference uses micro-batching.

### 16.6 Data scaling

- Audit and evidence tables are partitioned by tenant and time, with PgBouncer, read replicas for reporting, and cold cases archived to object storage with manifests.
- **Vector search:** pgvector first. Move to a dedicated engine only when measured p95 latency, recall or memory breaches budget at the tier's corpus size.
- The corpus is sharded by tenant or domain. Re-embedding uses versioned indexes and a dual-index cutover.
- Object storage uses erasure coding and lifecycle tiering with WORM retained. Integrity scrubbing re-hashes a sample continuously and does a full scan quarterly.
- The Merkle audit (§8.3) keeps verification cheap at any log size.

### 16.7 Cost scaling

A **cost-per-case ledger** records CPU-seconds, GPU-seconds, LLM tokens, storage GB-months and reviewer minutes per case from day one. It enforces hard LLM token caps per case (alerts at 80%) and produces a monthly cost-per-case and cost-per-resolved-case report. The levers are dedup and verdict reuse, caching, quantised or distilled models, and sampled rather than exhaustive audit.

### 16.8 Scale proof protocol (the gate)

1. Replay an anonymised, realistic workload mix at **1×, 3× and 10×** the tier target.
2. Record p95 per stage, queue age, error rate, DB load, simulated reviewer wait and cost per case.
3. Run a **72-hour soak test**.
4. Run chaos drills: kill workers, fail the DB primary (T1+), cut the LLM link, restore from backup and stamp a fresh cell.
5. **Pass:** SLOs hold at 3×, and at 10× the system sheds P3 and protects P0.

**Purchase rule:** do not buy the next tier's infrastructure until measured utilisation stays above 60–70% for two weeks, or a funded rollout demands it.

### 16.9 Deliberately not scaled yet

No active-active multi-region before T2, no Kubernetes before the T1 HA need, and no cross-cell search (aggregate metrics only).

---

# PART D: SCIENTIFIC CREDIBILITY

## 17. Scientific credibility and evaluation

### 17.1 Claim classes set the burden of proof

| Class | Examples | Burden |
|---|---|---|
| **A: Traceable** | Hashes, signature checks, snapshots with quoted spans, rule evaluations | Verifiable by recomputation, covered by known-answer software tests |
| **B: Statistical** | Stance labels, decomposition, clustering, independence estimates, detector scores | Measured error rates with confidence intervals, a validity envelope and calibrated abstention |
| **C: Generated text** | Summaries and explanations | Display-only. Every sentence maps to Class A spans and never drives a decision |

Only Class A, and Class B inside its envelope, may influence the evidence state or risk tier.

### 17.2 Validity statement (enforced by the registry)

> Component X v1.4, measured on Benchmark v3 (n = …), domain D (for example messaging-recompressed JPEG, ≥480 px): TPR a% (95% CI) at FPR ≤ 1% (CI). **Not valid for:** video, faces under 64 px, generators released after date T. **Expires:** date.

The policy engine checks each input against the envelope. Outside it, the result is automatically Inconclusive with the reason shown.

### 17.3 Credence-Bench: datasets built in-house

| Set | Content | Construction |
|---|---|---|
| **Claim-Bench** | 300 gold claims growing to ≥1,000, each with gold evidence, an as-of date and a label from {Supported, Refuted, Not enough evidence, Conflicting} | De-identified past department cases plus public fact-check archives (licence-checked). Evidence must pre-date the claim |
| **Media-Bench** | Authentic, synthetic (several open generator families) and **edited-authentic** (benign crops, filters, captions as false-positive traps), each pristine and degraded | Authentic items from verified sources. Degrade by passing items through the **real messaging and social apps**, screenshots, re-encoding, resizing and cropping. Add an in-the-wild set from debunked cases with labels from fact-checker consensus, noting label noise |
| **Document-forgery set** | Genuine public government documents and forged variants (template edits, number or date changes, pasted signatures, layout reflow), scanned and compressed | Constructed in-house, with ground truth known by construction |
| **Adversarial suite** | Prompt-injection payloads, negation, paraphrase and number-swap perturbations, outdated-document traps, lookalike domains, near-duplicate-but-different claims | Maintained as a standing regression set |

Rules:

- **Label taxonomy** for media: synthetic, manipulated, edited, authentic-with-provenance, unknown. Never treat "not detected" as "authentic".
- **Time-split generators.** Generators released after the tuning cutoff form the unseen-generator test.
- **Privacy.** Use consented or non-person content, with no identifiable citizen faces without a lawful basis.
- **Sealed test.** 30% of each set is sealed with a custodian independent of the developers. It is opened only at a gate under a pre-registered analysis, and refreshed quarterly (an opened slice becomes dev data).
- Published evaluations on in-the-wild content report substantial drops against academic benchmarks, which is why representative, degraded data is non-negotiable.

### 17.4 Annotation protocol

- Use written guidelines, ≥3 independent annotators per gold item and senior adjudication.
- Annotators never see model outputs, which avoids anchoring.
- Report Krippendorff's alpha or Cohen's kappa per label type. Treat roughly ≥0.8 as reliable and 0.67–0.8 as tentative. Below that, **the task definition is the problem**.
- Human disagreement sets the ceiling for model performance, so measure it.
- Effort (assumption): about 500 annotator-hours per 1,000 claims, plus about 400 for in-the-wild media. Synthetic and verified-source media carry construction-time ground truth.

### 17.5 Metrics per component

| Component | Primary metric | Also report |
|---|---|---|
| Retrieval | recall@k of gold evidence (as-of date), MRR | Latency, per-language slices |
| Stance / label | Macro-F1, per-class recall, accuracy **conditional on correct evidence** | Confusion matrix |
| Citation faithfulness | Human-judged entailment of span → statement (sample) plus an NLI check | Error taxonomy: misread, overgeneralised, out of context |
| Abstention | Risk–coverage curve, false-support rate on "not enough evidence" items | Coverage at fixed risk |
| Calibration | Brier score, reliability diagram, ECE as a secondary check | Per-slice |
| Clustering and reuse | **False-merge rate**, false-split rate | Reuse hit rate |
| Independence estimate | Precision and recall of origin clusters on hand-labelled syndication sets | Rate of "unknown" |
| Detector | **TPR at FPR ≤ 1%**, FPR on degraded-authentic and edited-authentic, per-generator recall | AUROC for ranking only |
| Document forensics | Detection rate per forgery type at fixed FPR on genuine documents | Scan-quality slices |
| Cyber (R3) | Alert precision, false-alarm rate, time to triage, feed freshness | Per-feed slices |
| Human + system | Accuracy, time, confidence calibration, over-reliance rate | Per-analyst variance |
| Platform | Latency, throughput, queue delay, failure rate, availability, restore time | Per-tier SLO |

No single headline accuracy is ever reported, and "95% alignment" style figures are never presented as model results.

### 17.6 Statistical rigor

- **Sample size:** n ≈ z²·p(1−p)/d². Worst case ±5% needs about 385 items and ±3% about 1,070. Pinning FPR near 1% to ±0.5% needs **about 1,500 authentic negatives**.
- Use Wilson or Clopper-Pearson intervals. Use **cluster bootstrap** by source or event, because items from one event are not independent.
- **Rule of three:** zero failures in n trials bounds the true rate at about 3/n (95%). A "zero tolerated" claim needs n large enough to mean something.
- **Pre-register** metrics, thresholds, slices and analysis scripts before opening the sealed set.
- Limit the number of candidate models, and correct for multiple slice tests or label them exploratory.

### 17.7 Calibration, uncertainty and abstention

- Hold out a separate **calibration split**, using temperature scaling or isotonic regression, recalibrated per slice.
- Use **split conformal prediction** for set-valued outputs (for example {Supported} or {Supported, Mixed} or abstain). It gives marginal coverage at the chosen error level under exchangeability. Exchangeability breaks under distribution shift, so monitor empirical coverage on a rolling labelled sample and recalibrate when it drifts.
- **Envelope gate:** check resolution, estimated JPEG quality, format, language and domain, plus an embedding-distance out-of-distribution signal.
- Publish **selective-prediction performance**, such as "answers X% of cases at ≤ Y% error". The pilot owner agrees the operating point.

### 17.8 Baselines and ablations (the product must beat them)

| Claim verification | Detector |
|---|---|
| B0 analyst with a search engine, unaided | B0 no detector |
| B1 BM25 retrieval only plus analyst | B1 trivial heuristics (metadata, error-level analysis) |
| B2 LLM without retrieval | |
| B3 full pipeline | |

A component that does not beat its baseline on end-to-end analyst outcome is **removed**, so evaluation also controls scope creep.

### 17.9 Robustness evaluation

Test compression-quality sweeps, resizing, cropping, screenshots, noise and repeated re-encoding. Add basic adversarial attacks on the detector as part of red-teaming, plus the unseen-generator test. For text, test paraphrase, negation and number swaps. Add temporal traps, the prompt-injection corpus and per-language slices.

### 17.10 Human + system study (before the pilot)

- **Design:** within-subject crossover, ≥8–10 analysts and ≥200 items, unaided versus aided.
- **Measures:** accuracy against gold, time, confidence calibration, and an **over-reliance rate** from a controlled seeded-error condition (a deliberately wrong suggestion shown only in the study, never in production).
- **Analysis:** a mixed-effects model with analyst and item as random effects.
- **Requirement:** aided is no worse on accuracy and better on time, with over-reliance under the agreed cap.

### 17.11 Reproducibility, drift and revalidation

- **CI harness:** every change to a model, prompt, rule pack, corpus pipeline or chunking runs the dev benchmark and blocks merge on regression beyond tolerance.
- Everything is pinned: containers, seeds, dataset hashes and prompt versions. Evaluation results attach to the Model Registry entry.
- **Production monitoring:** input shift (resolution, JPEG quality, language mix), score-distribution drift (PSI or KS), override rate per component, and a **quarterly fresh in-the-wild labelled sample (n ≥ 300)**.
- **Revalidation triggers:** a drift alarm, a new major generator family or a structural change in a source.
- Reproducibility means **replayable from stored artifacts**, not re-runnable, since hosted models get deprecated.

### 17.12 Independent validation and transparency

An external academic or laboratory partner replicates the evaluation on a sealed or independent set. Publish methodology, model cards and dataset datasheets, and open the evaluation harness (not the sensitive data) so procurement and audit can inspect it.

### 17.13 Scientific gates

| Gate | Requirement |
|---|---|
| **S1** | Annotation agreement acceptable before any model result counts |
| **S2** | Pipeline beats B1 and B2 with confidence intervals excluding zero improvement. If not, **ship retrieval plus case management only** |
| **S3** | Risk–coverage published and the operating point approved by the pilot owner |
| **S4** | Detector reaches TPR at FPR ≤ 1% on degraded and edited-authentic data (CI) and passes the unseen-generator slice, otherwise it stays disabled |
| **S5** | Human+system study passed |
| **S6** | Independent replication within the agreed tolerance |
| **S7** | Drift monitors live and the revalidation runbook exercised |

---

# PART E: DELIVERY

## 18. Deployment and operations

### 18.1 Connectivity modes (cell variants)

| Mode | What works |
|---|---|
| Connected | Everything, including live search and a hosted LLM where classification policy allows |
| Restricted | Allowlisted egress, corpus plus allowlisted sources, approved or local LLM |
| Air-gapped | Corpus via signed sync bundles, local models, no live retrieval. The UI states "live search unavailable" and never silently bypasses network policy |

Air-gapped is a Release 3 variant. Until then, the only requirement is that nothing is hard-coded to an external dependency.

### 18.2 Graceful degradation

| Failure | Behaviour |
|---|---|
| GPU down | Detector unavailable, results show Inconclusive |
| LLM down | Manual claim entry, and retrieval and the evidence matrix still work |
| Search or crawler down | Corpus-only retrieval, with the UI stating live search is unavailable |
| Redis down | API read-only |
| Database failure | Failover at the HA tier |

### 18.3 Reliability targets (proposal)

- 99.5% availability
- RPO ≤ 15 minutes (WAL archiving) and RTO ≤ 4 hours
- Quarterly restore test, and a cell-stamping drill at least twice a year

### 18.4 Release and operations

- Signed releases, canary per cell, and an **upgrade-lag SLO** across cells.
- Central logging with 180-day retention, an incident case type and a CERT-In evidence export path, with runbooks for each.
- Cyber resilience includes safe failure and recovery: isolation, incident workflow, backups, service health and tested restoration.

---

## 19. Roadmap with gates

| Release | Content | Gates |
|---|---|---|
| **R0 Foundations (~6–8 weeks)** | Pilot owner, charter, data classification, threat model, load-model assumptions, annotation guidelines and benchmark design, answer-availability test, baseline time-per-case | **G0:** owner signed off, baseline collected, lead workflow chosen |
| **R1 Core (~5–6 months)** | The 12 capabilities in §5.2, Benchmark v1 (claims 300→600, media dev set), CI harness, capacity telemetry, cost ledger | **G1:** integrity and isolation suites pass. **S1:** annotation agreement. **G3:** audit reconstruction succeeds |
| **R2 Pilot hardening (~4 months)** | Sealed-set evaluation, human+system study, scale proof T0→T1, security audit, HA, signed packages, model registry and drift monitoring, second language, shadow-mode pilot, independent replication | **S2–S7. G5:** restore tested. **Scale gate (§16.8). G7:** pilot results |
| **R3 Expansion** | Link reputation, cyber plugin, local LLM, new-department cells, DR, air-gapped variant, video/audio plugins | Only with demand, funding and passing scientific gates for each new capability |

Timelines are assumptions for a team of about 8. The long poles (MoU, approvals, hosting, audit scheduling) sit outside the team, so plan for **18–24 months wall-clock**. Benchmark construction starts in R0, not after the build. The pilot runs in **shadow mode**: analysts work as usual while the system runs in parallel.

**Build order:** Identity → Case and integrity → Corpus and retrieval → Evidence matrix → Policy and review → Signed package → Evaluation harness and benchmarks → Hardening, audit and scale proof → Shadow pilot → Plugins and expansion. Everything expensive sits at the end of the chain.

**Recommended vertical-slice order inside R1:** (1) evidence-first slice: claim or link intake → retrieval → evidence matrix → report → audit record; (2) image/document slice: secure upload → provenance → uncertainty-aware result → human review → stored lineage; then expand modality by modality.

---

## 20. Team and cost

**Team (about 7–9 people):**

| Role | FTE |
|---|---|
| Backend / architecture | 2 |
| Frontend (accessibility-capable) | 1 |
| ML / retrieval | 1–2 |
| Evaluation scientist | 1 |
| DevSecOps | 1 |
| SRE / performance | 0.5 |
| Statistician | part-time |
| Annotators | 3–5 part-time |
| Domain / governance lead from the department | 0.5–1 |

External security audit and an independent validation partner sit outside the team. Pair ownership of security and ML to avoid key-person dependency.

| Cost bucket | Note |
|---|---|
| People | The dominant cost: person-months × local rates |
| Annotation labour | The largest new line from the evaluation program |
| Infrastructure | Placeholders carried from the earlier plan, **unvalidated**: prototype ₹0–1L incremental, PoC ₹2–5L, pilot ₹5–10L, HA ₹10–25L+, excluding people and audit. Replace them with the cost-per-case ledger once measured |
| Security audit and certification | External quote, so budget early |
| Evaluation infrastructure | Benchmark and sealed-set storage, load-test environment, possibly a second GPU |
| Licences | Near zero by design, with one early licence review |
| LLM usage | Measured per case, with a hard cap |
| Hosting | May be an internal cost on NIC or existing government VMs |

**"Low-cost" describes the build, not ownership.** Five-year support, corpus upkeep, model revalidation and re-audit are real costs that must be named in any proposal.

---

## 21. Acceptance metrics (proposals, agreed in R0)

| Area | Target |
|---|---|
| Stored-original hash mismatches | 0 |
| Audit completeness and chain verification | 100%, and verification passes |
| Cross-tenant access in the isolation suite | 0 failures |
| Prompt-injection suite | No policy bypass, no exfiltration |
| Annotation agreement | Krippendorff's alpha ≥ 0.8 target, ≥ 0.67 minimum |
| Retrieval | Beats the BM25 baseline with CI, with the absolute recall@10 threshold set in R0 |
| Citation faithfulness | 100% of displayed statements trace to a stored span, and a human-judged sample meets the agreed threshold |
| Abstention | Published risk–coverage curve with an approved operating point |
| Clustering false-merge rate | Set in R0 (for example ≤0.5%) and enforced before verdict reuse is enabled |
| Detector | TPR at FPR ≤ 1% with CI on degraded and edited-authentic data, otherwise disabled |
| Human+system | Over-reliance under the agreed cap |
| Independent replication | Within the agreed tolerance |
| Analyst time per case vs R0 baseline | Reduction target set with the owner (for example ≥30%) |
| Scale | SLOs hold at 3× tier target, 72-hour soak and chaos and restore drills pass |
| Cost | Cost per case reported monthly, with a hard LLM token cap per case |
| Model and policy version recorded | 100% |
| Override rate and reviewer time | Tracked, with alerts |

**End-to-end demonstrator test.** The system counts as functional end to end only when it can: accept an input through an authenticated interface; validate and safely store it; track a job through clear lifecycle states; run a real analysis component (or visibly label a simulation); return structured evidence with model version and limitations; show uncertainty and failure states; enforce tenant access and policy; route configured cases to a reviewer; keep an audit trail an authorised user can reconstruct; and pass tests for malformed inputs, unsupported formats, service failures, access violations and policy denials.

---

# PART F: JUDGMENT

## 22. Risks (red team) and design flaws with mitigations

### 22.1 Risk register

| # | Failure | Early warning | Kill or pivot test |
|---|---|---|---|
| 1 | No committed pilot | No named analysts by end of R0 | **Do not start R1** |
| 2 | Answers rarely exist (high abstention) | Answer-availability test below threshold | Lead with official-record authenticity, or stop |
| 3 | Government assessment tool pulled into the contested fact-check debate | Legal read flags exposure, or requests for auto-action | Narrow scope, advisory-only charter, no publish or takedown integrations |
| 4 | LLM stance or citations unreliable | Faithfulness below threshold | Drop LLM stance and keep the LLM as a drafting aid |
| 5 | Prompt injection or poisoned sources | Red-team failures | Block release |
| 6 | Detector fails S4 or harms people through false positives | FPR above the agreed cap | Keep it disabled |
| 7 | Benchmark unrepresentative, giving false confidence | Fresh in-the-wild sample underperforms the benchmark | Refresh sets, narrow claims |
| 8 | Reviewer rubber-stamping | Near-100% approval in seconds | Redesign the UI, force rationale, add sampled audit |
| 9 | Hosting or audit blockers | No hosting path by mid-R1 | Escalate, or deploy on the department's existing infrastructure |
| 10 | Corpus rot | Rising broken-source rate | Named corpus owner, ingestion monitoring |
| 11 | Scale spend ahead of demand | Utilisation under 60% | Apply the purchase rule (§16.8) |
| 12 | Cell sprawl overloads operations | Cell-stamping time or upgrade lag grows | Single template, signed releases, upgrade-lag SLO |
| 13 | Evaluation cost overrun | Annotation hours exceed plan | Shrink the sealed set but keep honest intervals, and cut components rather than rigor |
| 14 | Key-person dependency | One person owns security or ML | Paired ownership, runbooks |

### 22.2 Design flaws and limitations (from the first-principles assessment)

| Flaw | Why it matters | Mitigation built in |
|---|---|---|
| **Scope expansion** | Search, three media types, cyber, provenance, governance and dashboards each carry large engineering and evaluation burdens; shallow versions give a demo without capability | Vertical slice first; video, audio and cyber deferred to R3 |
| **Deepfake detection is an arms race** | New generators and post-processing break detectors; benign edits get flagged | Detector off by default, validity envelope, unseen-generator test, Inconclusive state, revalidation triggers |
| **Ground truth is hard** | Labels for real-world media are noisy; edited media can be legitimate | Label taxonomy, annotation protocol, agreement metrics, never "not detected = authentic" |
| **Score aggregation creates false precision** | Heterogeneous measures, missing values and correlation | No aggregate score; signal matrix; non-compensatory gates |
| **Provenance misunderstood** | Hashes prove continuity, not truth | §8.5 states exactly what each operation proves |
| **Cyber analysis adds operational risk** | SSRF, malware, exhaustion, exfiltration | Isolated fetcher, blocked ranges, no execution, safe fixtures |
| **Governance can become ceremonial** | Policy docs and audit screens do not prove enforcement | Fail-closed policy tests at API and worker boundaries; audit-reconstruction gate G3 |
| **Privacy and retention under-specified** | Media, voice, faces and telemetry are sensitive | Per-case keys, crypto-shredding, retention classes, legal hold |
| **Existing platform complexity** | Many services and adapters slow integration | Reuse job model and deployment conventions, define contracts before UI, avoid unnecessary microservices |
| **Alignment percentages are subjective** | No rubric or independent evaluator | Replace with a requirements traceability matrix (Appendix C) |
| **Missing operational details** | Users, file sizes, throughput, languages, budget, licences, staffing not specified | R0 decisions list (§26) |

---

## 23. Strengths

1. **Reuse of an existing evidence platform.** Retrieval, normalisation, quality scoring, evidence graphs and citations already exist, which reduces duplicated work.
2. **Existing service boundaries.** Backend, frontend, SDK, workers and AgentGate are separated, giving natural integration points (contracts still need design).
3. **Governance in the execution path.** AgentGate and policy controls are a starting point for budgets, authorisation and restrictions, making responsible operation observable.
4. **Evidence-centric outputs.** Sources, intermediate findings and decision history beat an unexplained binary label.
5. **Asynchronous processing foundation.** Celery and Redis suit long-running analysis, subject to capacity planning and isolation.
6. **Several audiences, one workflow.** Analysts, researchers, compliance and due-diligence users share the same evidence core.
7. **Demonstrability.** One coherent scenario can show input, analysis, evidence, policy, review and audit, provided the UI reflects real backend behaviour and labels anything simulated.
8. **Responsible uncertainty.** Multi-state outcomes (Supported, Contradicted, Mixed, Insufficient, Out of scope; Indicators / No indicators / Inconclusive) avoid forcing "real or fake" where false accusations are costly.
9. **Cell architecture.** Data sovereignty, small blast radius and a free air-gapped variant.
10. **A science layer that can remove features.** Baselines and gates prune components that do not earn their place.

---

## 24. Trade-offs and alternatives

### 24.1 Build versus integrate (detectors and models)

| Choice | Benefits | Costs and risks | Suitable when |
|---|---|---|---|
| Train from scratch | Control over data and architecture | High data, compute, expertise and evaluation burden | A suitable dataset and research capacity exist |
| Pretrained models | Fast and cheap start | Licence, domain shift, explainability, dependency | Early prototype with careful validation (**chosen**) |
| External detection API | Little serving infrastructure | Data sharing, privacy, availability, cost, vendor lock-in | Only if classification policy permits external processing |
| Hybrid ensemble | Complementary signals | Complexity, correlated errors, hard calibration | Independent evaluation shows real benefit |

### 24.2 Single score versus multidimensional report

A single score is easy to scan but hides missing evidence. A component matrix is more transparent but needs interpretation. **Chosen:** categorical rule-derived state plus the visible signal matrix, with no aggregate.

### 24.3 Blockchain versus conventional tamper-evident logs

Signed, hash-chained, Merkle-rooted logs are simpler, cheaper and usually sufficient inside an organisation. External anchoring helps only when independent parties must verify without trusting the operator. **Chosen:** conventional logs, optional RFC 3161 timestamp.

### 24.4 Automation versus human approval

Tier actions by risk: reversible, low-impact automation only under explicit policy (R0); human authorisation for anything consequential (R2, R3). In this platform **no action integrations exist at all**, so the question is limited to evidence handling and routing.

### 24.5 Broad launch versus staged slices

A broad launch tells a better story and ships weaker components. **Chosen:** staged, measured slices with gates.

### 24.6 Monolith versus services, and Compose versus Kubernetes

Modular monolith and Compose first; services and Helm only when measured need appears (§6.5, §16.9).

---

## 25. Key insights

1. **The product is a trustworthy decision process, not a fake-content classifier.** Detection is one signal among several.
2. **Evidence is the connective tissue.** Findings, provenance, reviewer decisions and (later) threat indicators share traceable identifiers and typed contracts.
3. **Uncertainty is a feature.** Inconclusive beats unsupported certainty.
4. **Authenticity, accuracy, integrity, provenance, security and trust decision are different questions.** Each needs its own evidence.
5. **A score cannot replace policy.** Critical findings and authorisation rules stay independent of any average.
6. **Responsible AI must be enforced and tested at runtime.**
7. **Keep the implementation inventory honest.** The repository offers a real foundation; new modalities are roadmap work until verified.
8. **A vertical slice beats six disconnected demos.**
9. **Evaluation is multidimensional.** Detection quality, calibration, robustness, latency, security, governance and recovery all matter.
10. **Provenance is continuity, not truth.**
11. **Humans are the real scaling bottleneck.** Reviewer throughput scales first; compute is cheap.
12. **Cyber resilience includes safe failure and tested recovery.**
13. **The strongest defensible claim is bounded:** CredenceAI aims to help users make better-informed assessments by combining specialised analysis with traceable evidence and governed human oversight, and that aim must be established by implementation and evaluation.

---

## 26. Open decisions, first 30 days and status language

### 26.1 Decisions needed from the pilot owner

- Which lead workflow (§5.5)
- The pilot language
- Whether any case content may leave the network (hosted LLM yes or no)
- The signing key arrangement
- Retention classes
- Whether a machine-readable register of issued documents exists
- Target users, expected file sizes, throughput and latency objectives, reviewer staffing and budget (not specified in either source document)

### 26.2 First 30 days

1. Secure a named pilot department and 3 analysts, and agree a counsel-reviewed, advisory-only charter.
2. Measure baseline: how analysts verify today and the time per case.
3. Run the **answer-availability test** on 200 real cases.
4. Draft the load model with the owner and replace the illustrative numbers.
5. Write annotation guidelines and run a 50-item agreement pilot.
6. Build the first 300 gold claims with as-of dates and gold evidence.
7. Name the sealed-set custodian and draft the pre-registration template.
8. Audit the existing repo against the four hard dependencies and list what to keep.
9. Hold the threat-model and data-classification workshop, and confirm the hosting path and audit lead time.
10. Stand up the CI evaluation skeleton and the cell template, and time one clean cell stand-up.

### 26.3 Project-status language

- **Implemented and tested:** code exists and a repeatable test or demonstration verifies behaviour.
- **Implemented, validation pending:** code exists, but performance, security or operational validation is incomplete.
- **Planned:** design or interface proposed, with no implementation evidence yet.

---

## 27. The whole idea on one page

```text
                      CREDENCEAI-GOV (one CELL)

 Users ─ SSO / MFA / RBAC ─► API ─► CASE SERVICE
                                        │
                  EVIDENCE INTEGRITY: hash · WORM · per-case keys · custody · Merkle audit
                                        │
        ┌───────────────────────────────┼───────────────────────────┐
     VERIFY                          INSPECT                      PROTECT
 corpus · claims · tiers      provenance · media · documents     link capture
        └───────────────────────────────┼───────────────────────────┘
                                        │
                     EVIDENCE MATRIX (rule-derived state, no score)
                                        │
                  POLICY ENGINE ─► RISK TIER ─► REVIEW QUEUE (humans)
                                        │
                  SIGNED EVIDENCE PACKAGE ("Decision support, not a finding of fact")

 CENTRAL CONTROL PLANE: signed policy packs · signed model manifests · benchmarks · releases
 SCIENCE LAYER: Credence-Bench · sealed sets · validity envelopes · calibrated abstention · gates S1–S7
 SCALE LAYER: load model · priority queues · verdict reuse · cost ledger · proof protocol
```

**Status, stated honestly:**

| Dimension | Design | Evidence |
|---|---|---|
| Architecture and integrity | Complete | Proven only by gates G1, G3, G5 |
| Scalability | Design complete (about 9/10 on paper) | **None** until the scale proof (§16.8) |
| Scientific credibility | Design complete (about 7/10 on paper) | **None** until gates S1–S7 |
| Buyer, budget and legal position | Not resolved by this plan | Resolved only by the R0 gate |

The plan is ready to build only after the R0 gate answers whether a pilot owner exists, whether answers exist often enough, and whether counsel clears the charter.

---

# APPENDICES

## Appendix A. Complete feature catalogue

Release: R1, R2, R3. Status is **Existing** (documented in the repo), **Partial**, or **Proposed**.

### A.1 Control plane

| ID | Feature | What it does | Release | Status |
|---|---|---|---|---|
| C1 | SSO and MFA | OIDC/SAML login via Keycloak | R1 | Proposed (repo has auth and API keys) |
| C2 | RBAC | Analyst, Reviewer, Supervisor, Admin, Auditor, System roles | R1 | Existing basis, extended |
| C3 | Tenant isolation | Row-level security, per-tenant filters, isolation tests | R1 | Existing basis, extended |
| C4 | Case-level ACL and access reason | Restricts sensitive cases, records why accessed | R1 | Proposed |
| C5 | Quotas and rate limits | Per-tenant admission control, 429 with retry hint | R1 | Existing basis |
| C6 | Versioned policy packs | Deterministic rules with recorded version | R1 | Existing basis (AgentGate), extended |
| C7 | Signed model manifests and policy distribution | Central control plane to cells | R2 | Proposed |

### A.2 Evidence plane

| ID | Feature | What it does | Release | Status |
|---|---|---|---|---|
| E1 | Secure intake validation | Type, size, signature, dimension checks; ClamAV scan | R1 | Proposed |
| E2 | SHA-256 hashing and timestamp | Fingerprint at intake | R1 | Proposed |
| E3 | WORM original store | Immutable originals with object lock | R1 | Proposed |
| E4 | Per-case encryption and crypto-shredding | Key destruction at end of retention | R1 | Proposed |
| E5 | Derived-artifact lineage | Parent hash, tool and version for every transformation | R1 | Proposed |
| E6 | Custody events | Records every view, download, analysis, review, export | R1 | Proposed |
| E7 | Per-case hash chain | Tamper-evident audit | R1 | Proposed |
| E8 | Daily signed Merkle root and inclusion proofs | O(log n) verification of any event | R1/R2 | Proposed |
| E9 | RFC 3161 timestamp anchor | Optional external time anchor | R2 | Proposed |
| E10 | Integrity-verification endpoint | On-demand hash and chain re-check | R1 | Proposed |
| E11 | Signed evidence package | Portable, verifiable bundle with banner | R1/R2 | Proposed |
| E12 | BSA s.63 certificate support | Hash-based electronic-record certificate (format to confirm) | R2 | Proposed |
| E13 | Retention classes and legal hold | Purpose, delete-after, hold override | R1 | Proposed |
| E14 | Integrity scrubbing | Continuous sample re-hash, quarterly full scan | R2 | Proposed |

### A.3 Intelligence plane: Verify

| ID | Feature | What it does | Release | Status |
|---|---|---|---|---|
| V1 | Curated authoritative corpus | Human-curated T1/T2 sources as hashed snapshots | R1 | Proposed (adapters exist) |
| V2 | Pinned domain list and change alerts | Defends against lookalike or compromised domains | R1 | Proposed |
| V3 | Hybrid retrieval | Keyword plus vector with as-of-date filter | R1 | Existing basis, extended |
| V4 | Optional live search | Connected mode only, snapshotted into the case | R1 | Existing (SearXNG, GDELT, etc.) |
| V5 | Intent classification and source selection | Routes the query | R1 | Existing |
| V6 | Claim decomposition | Atomic claims via constrained JSON | R1 | Existing basis (goal decomposition) |
| V7 | Stance classification with quoted span | Supports, contradicts, neutral | R1 | Proposed |
| V8 | Citation check | Drops statements lacking a matching span | R1 | Proposed |
| V9 | Source tiers and flags | T1–T5, self-interested, superseded, dead, snapshot | R1 | Existing basis (quality scoring), re-defined |
| V10 | Independence estimate | Lower-bound distinct origins, "unknown" allowed | R1/R2 | Proposed |
| V11 | Evidence matrix and rule-derived state | Five states, caveat flags, signal matrix | R1 | Existing basis (evidence graph), extended |
| V12 | Claim clustering and verdict reuse | Canonical claims, TTL, invalidation on source change | R2 | Proposed |
| V13 | Multilingual retrieval and Indic translation | Second language with its own gold set | R2 | Proposed |
| V14 | Entity linking and evidence graph | Existing structures reused | R1 | Existing |

### A.4 Intelligence plane: Inspect and Protect

| ID | Feature | What it does | Release | Status |
|---|---|---|---|---|
| I1 | Metadata extraction (ExifTool) | Leads only, never proof | R1 | Proposed |
| I2 | C2PA verification | Verified / Absent / Broken | R1 | Proposed |
| I3 | PDF signature validation | Cryptographic signature check | R1 | Proposed |
| I4 | Document revision detection | Incremental updates, metadata inconsistencies | R1 | Proposed |
| I5 | Text-layer versus render comparison | Finds pasted or overlaid edits | R1 | Proposed |
| I6 | Issued-document register comparison | Checks department-owned ground truth | R1 (lead candidate) | Proposed |
| I7 | Repeat-media lookup | Perceptual-hash match to case library and debunked archive | R1 | Proposed |
| I8 | Image detector plugin | Validity-envelope-bound, off until S4 | R2 | Proposed |
| I9 | Envelope gate | Resolution, JPEG quality, format, language, OOD checks | R2 | Proposed |
| I10 | Link snapshot capture | Isolated fetch, HTML and screenshot, hashed | R1 | Proposed |
| I11 | Link reputation | Open feeds where licensed | R3 | Proposed |
| I12 | Cyber-analysis plugin | IOC normalisation, correlation, triage (§11.3) | R3 | Proposed |
| I13 | Video plugin | Sampling, temporal analysis, segments (§10.5) | R3 | Proposed |
| I14 | Audio plugin | Synthetic-speech analysis, not identification (§10.5) | R3 | Proposed |
| I15 | Upload sandbox | Sandboxed parsers, decompression-bomb limits | R1 | Proposed |

### A.5 Review plane

| ID | Feature | What it does | Release | Status |
|---|---|---|---|---|
| RV1 | Risk tiers R0–R3 | Impact-based handling | R1 | Proposed |
| RV2 | Review queue with SLA | Tiered, aged, with surge rules | R1 | Proposed |
| RV3 | Recorded rationale | Mandatory at R2+ | R1 | Proposed |
| RV4 | Automation-bias controls | Evidence first, sampled second review, override alerts | R1 | Proposed |
| RV5 | Dispositions | Confirmed accurate, Miscontextualised, Cannot determine, Refer to lab | R1 | Proposed |
| RV6 | Notice and grievance route | For cases affecting named individuals | R2 | Proposed |
| RV7 | Evidence-first UI (GIGW 3.0 / WCAG 2.1 AA) | Screens in §13 | R1 | Existing basis (React), extended |
| RV8 | Audit explorer | Chronological, verifiable history | R1/R2 | Proposed |
| RV9 | Responsible-AI monitor | Versions, drift, policy events, backlog | R2 | Proposed |

### A.6 Scale, science and operations

| ID | Feature | What it does | Release | Status |
|---|---|---|---|---|
| SC1 | Cell template | Stamp a full data plane in a day | R1/R2 | Proposed |
| SC2 | Priority queues P0–P3 | Separate worker pools per class | R1 | Existing basis (Celery), extended |
| SC3 | Idempotent jobs, outbox, DLQ | Safe retries | R1 | Proposed |
| SC4 | LLM gateway | Token budgets, cache, circuit breaker, fallback | R1 | Proposed |
| SC5 | Cost-per-case ledger | CPU, GPU, tokens, storage, reviewer minutes | R1 | Proposed |
| SC6 | Capacity telemetry | Queue age, utilisation, p95 | R1 | Proposed |
| SC7 | Scale proof protocol | 1×/3×/10×, 72 h soak, chaos | R2 | Proposed |
| SC8 | Credence-Bench | Four in-house sets with sealed splits | R0–R2 | Proposed |
| SC9 | CI evaluation harness | Blocks merges on regression | R1 | Proposed (CI exists) |
| SC10 | Calibration and conformal abstention | Risk–coverage, set-valued outputs | R2 | Proposed |
| SC11 | Drift monitors and revalidation runbook | PSI/KS, quarterly sample | R2 | Proposed |
| SC12 | Human+system study | Crossover with seeded errors | R2 | Proposed |
| SC13 | Independent replication | External lab or academic partner | R2 | Proposed |
| SC14 | Model Registry | Signed entries with review-by date | R2 | Proposed |
| SC15 | Backup, restore, DR | RPO ≤ 15 min, RTO ≤ 4 h, quarterly restore test | R1/R2 | Proposed |
| SC16 | Air-gapped variant | Signed sync bundles, local models | R3 | Proposed |
| SC17 | Observability stack | OpenTelemetry, Prometheus, Grafana, Loki | R1 | Proposed |
| SC18 | Central logging and CERT-In export | 180-day retention, incident case type | R1/R2 | Proposed |

---

## Appendix B. Module status matrix

| Capability | Repository-supported status | Target work and evidence needed |
|---|---|---|
| Search and multi-source retrieval | Documented as existing | Verify configured adapters and source availability in the target deployment |
| Intent classification and source selection | Documented as existing | Add tests for routing accuracy and fallback |
| Quality scoring and normalisation | Documented as existing | Document score semantics; do not equate search quality with truth |
| Evidence graph and claims | Documented as existing | Extend schema to media, provenance and reviewer evidence |
| Agent orchestration and working memory | Partial per improvements tracker | Verify bounded runtime behaviour in deployment |
| AgentGate policy service | Present as a separate service | Add policies for media processing, review and model use |
| Authentication and tenant isolation | Documented; tests referenced | Re-run authorisation and cross-tenant tests for new endpoints and artifacts |
| Image deepfake analysis | Not verified | Secure pipeline, evaluation, result contract, UI (gate S4) |
| Video deepfake analysis | Not verified | R3 plugin with its own gate |
| Audio synthetic-speech analysis | Not verified | R3 plugin; no identity claims |
| Unified trust score | Proposed, **now rejected by design** | Replaced by rule-derived evidence state and signal matrix |
| Cryptographic evidence provenance | Proposed | Hash records, lineage, signing, verification tests |
| Cyber threat-intelligence module | Not verified | R3 plugin; isolated, advisory |
| Model cards and drift monitoring | Proposed | Registry, cadence, thresholds, incident process |
| Unified dashboard | Proposed extension of existing frontend | Real APIs, evidence and uncertainty, reviewer-workflow tests |
| End-to-end evaluation | Not established | Reproducible datasets, metrics, baselines, results, limitations |

---

## Appendix C. Requirements traceability template

Replace percentage "alignment" claims with this table, one row per requirement.

| Requirement ID | Requirement | Implementation status | Evidence link (code, test, report) | Test result | Remaining gap |
|---|---|---|---|---|---|
| REQ-001 | Stored-original hash mismatches = 0 | | | | |
| REQ-002 | Cross-tenant isolation suite passes | | | | |
| REQ-003 | Every displayed statement traces to a stored span | | | | |
| … | … | | | | |

If a percentage is ever required, publish the scoring rubric and method with it.

---

## Appendix D. Glossary

- **Advisory-only:** the platform informs human decisions and never triggers publication, takedown or enforcement.
- **As-of date:** the date a claim was made; retrieval is limited to evidence existing then.
- **Authenticity:** assessment of whether media is genuine, synthetic or manipulated, from available indicators.
- **C2PA:** open standard for signed content-provenance metadata.
- **Calibration:** agreement between stated confidence and observed correctness on a representative set.
- **Cell:** a complete, independent data plane and the unit of scale-out.
- **Chain of custody:** documented history of evidence possession, transfer, processing and access.
- **Conformal prediction:** method giving set-valued outputs with a coverage guarantee under exchangeability.
- **Crypto-shredding:** erasing data by destroying its encryption key.
- **Digital provenance:** information about an artifact's origin, history and transformations.
- **Evidence graph:** structured relationships among claims, entities, sources and supporting or conflicting evidence.
- **Evidence package:** signed, portable bundle of originals' hashes, findings, decisions and audit extract.
- **Evidence state:** rule-derived label (Supported, Contradicted, Mixed, Insufficient evidence, Out of scope), not a score.
- **False negative / false positive:** a missed positive / a benign item wrongly flagged.
- **IOC (Indicator of Compromise):** observable such as a domain, IP, hash or URL used in security investigation.
- **Merkle root:** a single hash summarising many events, enabling logarithmic inclusion proofs.
- **Model drift:** change in inputs or behaviour that degrades performance or invalidates earlier evaluation.
- **Non-compensatory gate:** a rule that a high score elsewhere cannot override.
- **Policy gate:** a rule-based control that allows, restricts, blocks or escalates an operation independently of model confidence.
- **Risk–coverage curve:** error rate as a function of the share of cases the system answers.
- **TPR at FPR ≤ 1%:** detection rate at a fixed false-alarm ceiling on authentic content.
- **Trust assessment / trust decision:** context-specific, policy-governed synthesis of evidence; never an absolute guarantee of truth.
- **Validity envelope:** the measured domain inside which a model's results may be used.
- **WORM:** write-once-read-many storage.

---

**Document status.** Unified blueprint combining the CredenceAI-Gov Complete Project Plan (v3) and the First-Principles Assessment. Repository-derived statements reflect the supplied CredenceAI archive documentation as summarised in the assessment; all proposed capabilities require implementation and verification before being represented as complete. Legal items are carried from the source plan and need counsel confirmation.
