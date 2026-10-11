# Assumptions and decisions

Record of safe defaults for the synthetic-data P0 skeleton. These are not pilot approvals.

| ID | Date | Assumption / decision | Reason and limit |
|---|---|---|---|
| A-001 | 2026-10-09 | P0 contains documentation and local-only foundations; it processes no real government evidence. | Pilot owner, charter, classification, and handling decisions are unresolved. |
| A-002 | 2026-10-09 | All seed, fixture, demo, and evaluation content is synthetic and visibly labeled `SIMULATED`. | Prevent accidental confusion with operational evidence. |
| A-003 | 2026-10-09 | External LLM, live search, link fetching, detector use, and notification/action integrations are disabled by default. | Conservative data-egress and safety posture; no approvals or production adapters exist. |
| A-004 | 2026-10-09 | English-only is the P0 implementation language; the language field remains extensible. | The master prompt explicitly excludes other languages for this skeleton; evaluation data still needs provenance. |
| A-005 | 2026-10-09 | All analyst-visible outcomes remain advisory, evidence-linked, and non-binary. | Product rule; no trust score or real/fake output. |
| A-006 | 2026-10-09 | The walking skeleton may represent claim, PDF, image, and URL workflows with simulated/inconclusive analyzers; this does not resolve which workflow leads a government pilot. | New master prompt requires these intake modes; earlier blueprint R0 still controls pilot sequencing. |
| A-007 | 2026-10-09 | No real evidence is accepted until retention classes, legal hold, classification, key custody, and counsel/security review are approved. | These choices define lawful handling and safe operations. |
| A-008 | 2026-10-09 | Requested component versions below are candidates only until lockfiles, image digests, license audit, and vulnerability review are verified. | Docker daemon is currently inaccessible; the workstation also lacks Python 3.12 and Git repository metadata. |
| A-009 | 2026-10-09 | MinIO is not approved for production use by this P0 decision. | Upstream open-source repository was archived in 2026; evaluate maintenance, license, and replacement/enterprise terms before production. |
| A-010 | 2026-10-09 | GitHub Actions is a proposed CI target, not proof that this workspace is connected to a GitHub repository. | No `.git` directory exists in this checkout. |
