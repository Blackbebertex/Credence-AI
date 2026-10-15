# CredenceAI-Gov Threat Model (P0-07)

**Document Status:** P0 Active Architectural Baseline  
**Governing Standard:** STRIDE + Section 7 Threat Matrix (Execution Plan v2)  
**Admissibility Reference:** Bharatiya Sakshya Adhiniyam, 2023 (Section 63)

---

## 1. Core Security Principle: Trust Starts at Ingestion

> **Trust starts at ingestion.**  
> A cryptographic SHA-256 digest or Merkle root proves that an evidentiary file or record has not changed *after* ingestion into the system. It does **not** prove that the file was authentic, unaltered, or truthful *prior* to capture or upload.  
> The system supports admissibility under BSA s.63 subject to judicial determination; it does not issue automated determinations of guilt, factual truth, or pre-ingestion authenticity. Where capture-side provenance exists (C2PA metadata, digitally signed PDFs), it is cryptographically inspected and recorded as advisory context.

---

## 2. Assets, Actors, and Trust Boundaries

### Evidentiary & System Assets
- **Original Evidence Binaries:** Bit-for-bit untouched raw uploaded files stored under immutable object locks.
- **Custody Ledger:** Sequential, SHA-256 chained audit events recording actor, timestamp, action, and payload hash. UPDATE and DELETE are prohibited.
- **Manifests & Digital Signatures:** RFC 8785 canonical JSON manifests signed with Ed25519 signing keys.
- **Statutory Certificates:** BSA 2023 Section 63 electronic certificates with deponent affirmations and cryptographic digests.
- **Cryptographic Keys:** Ed25519 private keys stored in KMS/HSM (SoftHSM for local dev), never committed to source.

### Actors & Roles (Least Privilege & Separation of Duties)
- **Intake Officer:** Permitted to upload evidence and record intake metadata; prohibited from approving cases.
- **Evidence Reviewer:** Assesses evidence, performs R1/R2 reviews, and records mandatory disposition rationales (≥20 chars).
- **Approving Authority:** Authorized deponent with designated signing credentials to generate statutory certificates.
- **Independent Auditor / Witness:** Read-only verification access; offline CLI verification (`scripts/verifier.py`).
- **System Administrator:** Node infrastructure maintenance; cryptographically prevented from altering custody chains or evidence bytes.

### Trust Boundaries
1. **Client Browser ↔ API Gateway:** Enforces TLS, CORS (`*.vercel.app`, `localhost`), rate limits, and Bearer token authentication.
2. **API ↔ Storage Engine:** Abstracted storage adapter enforcing immutable versioning and strict byte verification.
3. **API ↔ Forensic Verifier:** Offline standalone verification executable on air-gapped systems without server trust.
4. **Application ↔ Worker Sandbox:** Analysis/OCR tasks run in isolated non-root containers without outbound network access.

---

## 3. Top 11 Threats and Mitigations (Section 7 Matrix)

| # | Threat Vector | Impact | Mitigations & Controls | Verification & Test |
|---|---|---|---|---|
| **1** | **Forged evidence before upload** | Pre-ingestion tampered evidence presented as genuine | Explicit "Trust Starts at Ingestion" disclaimer in UI & certificates; capture-side signature inspection (C2PA/PDF); AI output restricted to advisory flags. | Claim rule CI check (`scripts/check_claim_rules.py`); statutory banner checks. |
| **2** | **Insider edits custody or artifacts** | Malicious alteration of evidence or audit logs | Object lock / immutable storage; sequential SHA-256 hash-chained custody events; published daily Merkle roots. | `test_tamper_matrix.py` (byte flip, custody edit/delete/reorder tests). |
| **3** | **Key compromise or theft** | Rogue evidence manifests signed | Ed25519 keys managed via KMS/HSM; certificate generation gated behind 4 statutory preconditions; key revocation lists with effective timestamps. | Precondition enforcement tests; `test_key_untrusted`. |
| **4** | **Cross-tenant access** | Unauthorized tenant accessing sensitive case files | Strict tenant isolation via tenant ID validation and row-level security (RLS); deny-by-default route authorization. | Cross-tenant test suite; unauthorized 403 test assertions. |
| **5** | **Malicious upload (malware, zip bomb, polyglot)** | Host compromise or denial of service | Size caps (10 MB intake default); magic-byte MIME type validation; sandboxed worker parsing without network egress. | Upload format validation; payload size gate tests. |
| **6** | **Prompt injection via evidence content** | Adversarial instructions hijacking AI decisions | Evidence content treated strictly as passive data; AI provides advisory decision support only; zero automated verdicts or certificates. | `package_builder` advisory banner; human-in-the-loop review queue. |
| **7** | **Server-Side Request Forgery (SSRF)** | Internal network scanning or cloud credential exfiltration | Sandboxed workers have no outbound network interface; API routes accept base64 or multipart uploads only; no outbound fetcher in P0. | Network egress isolation policy. |
| **8** | **Privileged administrator abuse** | Admin bypassing custody rules or editing cases | Separation of duties (uploader ≠ reviewer ≠ approver); admin cannot edit evidence or custody tables; all administrative actions appended to ledger. | Custody append-only immutability; role matrix verification. |
| **9** | **Replay or rollback of old manifests** | Presenting obsolete evidence state | Sequential sequence numbers; RFC 3161 timestamps; Merkle root matching. | `test_root_mismatch` verifier test. |
| **10** | **Software supply chain compromise** | Malicious dependencies in build pipeline | Pinned dependencies in `requirements.txt` and `package.json`; CI automated claim rules checker; tamper matrix regression suite. | CI automated tests (`pytest`, `check_claim_rules.py`). |
| **11** | **Denial of service and cost abuse** | Resource exhaustion on free-tier hosting | Ingestion rate limiting; bounded payload limits; client-side SHA-256 precomputation; fail-closed execution. | Resource cap tests; fail-closed negative precondition gates. |

---

## 4. Verification and Audit Procedure

Anyone—including defense counsel, judicial authorities, and third-party auditors—can verify the integrity of an exported evidence dossier without connecting to or trusting the CredenceAI-Gov server:

```bash
python scripts/verifier.py evidence_dossier_<case_id>.zip
```

The verifier strictly fails with defined exit codes:
- `0`: VERIFIED_CLEAN
- `2`: HASH_MISMATCH (Artifact bytes altered)
- `3`: SIGNATURE_INVALID (Manifest payload or Ed25519 signature tampered)
- `4`: KEY_UNTRUSTED (Signature key untrusted or mismatched)
- `5`: CHAIN_BROKEN (Custody ledger sequence gap, edit, or reorder)
- `8`: ROOT_MISMATCH (Merkle root does not match manifest head)
