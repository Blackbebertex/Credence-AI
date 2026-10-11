# Threat model — P0

**Status:** initial STRIDE-oriented draft; synthetic development only. This is not a security assessment or authorization to process government data.

## Assets and trust boundaries

- Assets: identity tokens, tenant/case metadata, original and derived evidence, source snapshots, signing/encryption keys, audit/custody chain, model and policy manifests.
- Boundaries: browser↔proxy/API; API↔PostgreSQL/Redis/object store; API↔workers; sandbox parser; outbound fetcher; Keycloak; telemetry/logging; CI and dependency registries.
- P0 has no real case data, production credentials, external model access, or active link fetcher.

## Initial controls and proof obligations

| Threat | P0 control | Later proving test |
|---|---|---|
| Spoofed identity / privilege escalation | OIDC validation and explicit role matrix required before protected case APIs | JWT issuer/audience/time/MFA tests; full role×endpoint matrix |
| Cross-tenant exposure | Tenant identity must derive from verified identity; PostgreSQL RLS planned | Missing-tenant returns zero rows; cross-tenant DB/vector/cache/object tests |
| Hostile upload / parser exploit | No analysis before validation, hash, custody, scan; parser isolated with no egress | EICAR, malformed files, decompression bomb, sandbox escape controls |
| Indirect prompt injection | Retrieved/uploaded text treated as data; LLM has no tools or network; mock default | Prompt-injection/adversarial corpus leaves policy/state unchanged |
| SSRF / DNS rebinding | No direct API fetch; isolated fetcher design only | Private IP, metadata, redirect, IPv6-mapped, rebinding tests |
| Evidence tampering | Original hash, immutable object/version, append-only audit, signed package | Byte flip and audit-row edit fail verification |
| Insider over-access | Least privilege, access reason, auditor read-only, access audit | RLS/RBAC, restricted-case reason and auditor artifact tests |
| Secret or content leakage | No secrets in Git; no raw case content in logs; external LLM disabled | Gitleaks and log-content tests |
| Dependency/image supply chain | Exact lockfiles, digests, license allowlist, scanners before release | CI dependency/image/license gate |
| Denial of service / queue starvation | Size limits, per-tenant quotas, bounded workers and priority queues | Quota, retry/DLQ, worker-loss tests |

## P0 exclusions

No production deployment, no live link fetching, no third-party LLM, no operational source ingestion, no real document uploads, no autonomous action endpoint, and no active deepfake detector. Key rotation, legal hold, retention and package signing require approved operator procedures before pilot use.
