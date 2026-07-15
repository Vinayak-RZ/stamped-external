# Decisions log — L3/L4 Intelligence

> [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) · ADRs in [decisions/](decisions/)

## Accepted ADRs (Phase A)

| ADR | Title | Status |
|-----|-------|--------|
| ADR-012 | L3 artifact repo topology | **Accepted** |
| ADR-013 | Counterfactual savings ledger | **Accepted** |
| ADR-014 | TS foundation model shadow role | **Accepted** |
| ADR-015 | L3 dual-lane lab detections | **Accepted** |
| ADR-016 | Attribution shadow challengers | **Accepted** |

## ADR-014 promotion (Phase P2)

**Decision:** Do not promote TimesFM — remain shadow-only. See [ADR-014-promotion-record.md](decisions/ADR-014-promotion-record.md).

## Plan defaults applied

| Topic | Choice |
|-------|--------|
| P0 rulepack vertical | Incomer MD/PF/TOD |
| L4 P0 | Template-fast-path only |
| Consumer location | `consumers/` scaffolds (split to GitHub repos per REPOS.md) |
| Rulepacks catalog axes | Domain × vertical × tariff (see `consumers/stamped-l3-rulepacks/DECISIONS.md`) |
| Optimization methods | First-class rule IDs in furnace / idle / load_management packs |
| Eval Lab UI | Internal Next.js lab in `stamped-l3-eval` over RunArtifact + optional CORE_LAB_URL |
| L3 decision defense brief | Synthesis doc for arguing rules/ML/LLM/FM placement — [`technical/layers/L3-decision-defense-brief.md`](technical/layers/L3-decision-defense-brief.md) |
| Dual-lane Lab retention | All structured candidates → RunArtifact; only `delivery=l4` / `emitted` → L4 outbox — [ADR-015](decisions/ADR-015-l3-dual-lane-lab-detections.md) |
| Attribution explainability | Graph co-start of-record; shadows = ablations + STUMPY — [`L3-attribution-explainability.md`](technical/layers/L3-attribution-explainability.md) · [ADR-016](decisions/ADR-016-attribution-shadow-challengers.md) |
