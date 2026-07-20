# Architecture decisions (cross-repo)

Decision records for the Stamped platform. **Distributed via [stamped-external](https://github.com/vinayak-rz/stamped-external) submodule** at `external/` in each product repo ([ADR-011](ADR-011-stamped-platform-submodule-distribution.md)).

| ADR | Title | Status |
| --- | --- | --- |
| [ADR-001](ADR-001-l1-repo-split-and-boundaries.md) | L1 repo split, edge packaging, schemas, transport, tag mapping | **Accepted** (2026-07-09) |
| [ADR-002](ADR-002-build-all-aws-networking.md) | Build-all software, plant networking, AWS cost-first deployment | **Accepted** (2026-07-09) |
| [ADR-003](ADR-003-connectors-edge-monorepo.md) | connectors-edge monorepo, Go/Python packages, asset IDs, templates | **Accepted** (2026-07-09) |
| [ADR-004](ADR-004-compliance-driven-architecture.md) | Compliance-driven architecture (CERT-In, DPDP, OT, metering) | **Accepted** (2026-07-09) |
| [ADR-005](ADR-005-edge-agent-go-architecture.md) | Go edge-agent architecture (buffer, OTA, plugins, testing) | **Accepted** (2026-07-09) |
| [ADR-006](ADR-006-fleet-ota-substrate.md) | Fleet OTA substrate — enhanced manual until ~20 devices | **Accepted** (2026-07-09) |
| [ADR-007](ADR-007-connectors-cloud-repo-charter.md) | connectors-cloud repo charter — L1 cloud ingest only | **Accepted** (2026-07-10) |
| [ADR-008](ADR-008-layer-repo-topology-and-interfaces.md) | Layer-per-repo topology; L1→L6 interface contracts | **Accepted** (2026-07-10) |
| [ADR-009](ADR-009-stamped-l2-repo-charter.md) | stamped-l2 repo charter — one DB, HTTP P0, cost-first AWS | **Accepted** (2026-07-12) |
| [ADR-010](ADR-010-deployment-profiles-and-portability.md) | Three deployment modes — local, local-dashboard, cloud | **Accepted** (2026-07-12) |
| [ADR-011](ADR-011-stamped-platform-submodule-distribution.md) | stamped-platform submodule — single source of truth | **Accepted** (2026-07-12) |
| [ADR-012](ADR-012-l3-artifact-repo-topology.md) | L3 artifact repos — core, rulepacks, eval | **Accepted** (2026-07-13) |
| [ADR-013](ADR-013-counterfactual-savings-ledger.md) | Counterfactual savings ledger (`opportunity_cost`) | **Accepted** (2026-07-13) |
| [ADR-014](ADR-014-ts-foundation-model-role.md) | Time-series foundation model shadow-only role | **Accepted** (2026-07-13) |
| [ADR-015](ADR-015-l3-dual-lane-lab-detections.md) | L3 dual-lane lab detections (`delivery` l4 vs lab_only) | **Accepted** (2026-07-15) |
| [ADR-016](ADR-016-attribution-shadow-challengers.md) | Attribution shadow challengers (ablations + STUMPY; not SHAP/NILM) | **Accepted** (2026-07-15) |
| [ADR-017](ADR-017-l4-adaptive-retrieval-and-web-trust.md) | L4 adaptive hybrid RAG + web-search trust tiers (T1–T4) | **Accepted** (2026-07-17) |
| [ADR-018](ADR-018-l4-pilot-execution-knowledge-reasoning.md) | L4 pilot execution — LangGraph early pull, L6 UI, Path H hop-2, Path W/Phoenix in P2, English through P2 | **Accepted** (2026-07-19) |
| [ADR-019](ADR-019-l5-runtime-and-consistency.md) | L5 runtime charter — modular monolith, Postgres workflow, L2 ledger append protocol | **Accepted** (2026-07-20) |
| [ADR-020](ADR-020-l5-mv-claim-governance.md) | L5 M&V claim governance — two-tier IPMVP, analyst gate, verification_status | **Accepted** (2026-07-20) |
| [ADR-021](ADR-021-l5-notification-and-evidence.md) | L5 notification + evidence — Meta direct, shared number, DLT P0/SMS P1 | **Accepted** (2026-07-20) |

Compliance register: [../compliance/india-compliance-register.md](../compliance/india-compliance-register.md)

**L5 handoff:** [../handoff/stamped-l5-architecture-handoff.md](../handoff/stamped-l5-architecture-handoff.md) · [../handoff/stamped-l5-build-plan.md](../handoff/stamped-l5-build-plan.md)

When a downstream repo (L2, L3, …) needs L1 context, start with [../technical/README.md](../technical/README.md) then read ADRs here.
