# Decisions log — L3/L4 Intelligence

> Significant decisions during execution of [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md).  
> Formal ADRs live in [decisions/](decisions/) and are indexed in [decisions/README.md](decisions/README.md).

## Pending ADRs (Phase A)

| ADR | Title | Status |
|-----|-------|--------|
| ADR-012 | L3 artifact repo topology (core + rulepacks + eval) | draft — see IMPLEMENTATION_PLAN §4 |
| ADR-013 | Counterfactual savings ledger (`opportunity_cost`) | draft — see IMPLEMENTATION_PLAN ADR-013 sketch |
| ADR-014 | Time-series foundation model role (TimesFM shadow-only) | draft — see IMPLEMENTATION_PLAN TimesFM section |

## Recorded during plan authoring (v3)

| Topic | Choice | Rationale |
|-------|--------|-----------|
| L3 repo split | 3 repos (core, rulepacks, eval) | L1 edge/cloud/bill precedent; semver rulepacks independent of engine |
| M&V baseline | TOW-P of record | IPMVP/ASHRAE G14 auditability |
| L4 P0 | Template-fast-path (no LLM) | High-confidence md_overlap/pf_slab; LangGraph P1 |
| TimesFM | Shadow-only P2 | Never M&V engine of record until eval gates pass |
| P0 rulepack vertical | Incomer MD/PF/TOD (recommended default) | Bill-truth wins fastest; forging P1 |

## Open questions

See IMPLEMENTATION_PLAN.md § Open questions — resolve before Phase A execution scope is final.
