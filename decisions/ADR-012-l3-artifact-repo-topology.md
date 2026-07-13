# ADR-012: L3 artifact repo topology

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-13 |
| **Deciders** | Engineering (L3/L4 intelligence plan) |
| **Related** | [ADR-008](ADR-008-layer-repo-topology-and-interfaces.md) · [ADR-001](ADR-001-l1-repo-split-and-boundaries.md) · [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) |

---

## Context

ADR-008 maps one deployable repo per layer (`stamped-l3` → Finding). The L3/L4 intelligence plan requires **semver rulepacks**, **golden eval corpora**, and an **engine runtime** with independent release cadences — similar to how L1 splits into edge/cloud/bill ([ADR-001](ADR-001-l1-repo-split-and-boundaries.md)).

Skills applied: `backend-architecture`, `system-design-tradeoffs`.

---

## Decision

Split L3 implementation into **three repositories** at the intelligence boundary:

| Repo | Role | Deployable? |
| --- | --- | --- |
| `stamped-l3-core` | Engine runtime, schedulers, transactional outbox, MLflow registry | **Yes** |
| `stamped-l3-rulepacks` | Semver YAML/JSON physics + tariff rulepacks + golden windows | Artifact only |
| `stamped-l3-eval` | Golden corpus + rolling backtest CLI + champion/challenger gates | Artifact only |

**ADR-008 unchanged at layer interface:** one `Finding` outbox from `stamped-l3-core`; L3→L4 boundary identical.

Rulepacks and eval repos are **consumers of platform contracts** via `external/contracts` submodule — analogous to contracts distribution ([ADR-011](ADR-011-stamped-platform-submodule-distribution.md)).

---

## Rationale

- **Independent semver** for rulepacks without redeploying engines (Zerowatt-style rule breadth with Stamped audit trail).
- **CI golden replay** per rulepack tag without coupling to core release train.
- **L1 precedent** — three repos at L1 layer is accepted; artifact repos are not a fourth intelligence engine.

---

## Consequences

- Consumer repos pin two submodule SHAs: `external/` (platform) + rulepack tag at deploy time.
- `stamped-l3-core` loads rulepacks by semver manifest, never embeds rules in engine code.
- REPOS.md lists three L3 repos; ADR-008 repo map footnote references ADR-012.

---

## Alternatives considered

| Option | Rejected because |
| --- | --- |
| Monorepo `packages/core` + `packages/rulepacks` | Couples release cadences; harder vertical ownership |
| Five+ repos (one per engine) | Ops overhead; ADR-008 one-Finding-outbox rule violated |
