# Progress — L3/L4 Intelligence (Beat Zerowatt)

> Live status for [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) · Nawab v3 · Branch `cursor/l3-l4-intelligence-272a`

## Current phase

**Complete** — P0 platform + consumer scaffolds through Phase N

## Completed phases

| Phase | Status | Notes |
|-------|--------|-------|
| 0 | done | IMPLEMENTATION_PLAN, PROGRESS, DECISIONS |
| A | done | Specs, ADR-012/013/014, contracts 0.6.0 |
| B | done | stamped-l3-core scaffold (9 tests) |
| C | done | rulepacks v0.1 + eval CLI |
| D | done | stamped-l4 template-fast-path (22 eval tasks) |
| P2 | done | TimesFM shadow stub; no promotion |
| N | done | validate.sh green |

## Blockers cleared

| Item | Status |
|------|--------|
| Finding contract frozen | done — contracts 0.6.0 |
| Pilot golden windows | done — synthetic v0 + golden_md_spike |
| L2 query API | workaround — FixtureL2Client in l3-core |

## Validation

```bash
./scripts/validate.sh
```

## Dual-lane Lab retention (2026-07-15)

| Item | Status |
|------|--------|
| ADR-015 / ADR-016 | done |
| RunArtifact 1.1.0 + Lab UI lanes | done |
| Attribution explainability + shadows | done |
| Core hot-path LabLog (no silent drop) | done |

## L4 architecture SSOT (2026-07-17)

| Item | Status |
|------|--------|
| L4 layer spec rewrite | done — adaptive RAG, dual lane, eval stack |
| ADR-017 adaptive retrieval + web T4 | done |
| handoff/stamped-l4-architecture-handoff.md | done (supersedes build-order) |

## L5 architecture overhaul (2026-07-20)

| Item | Status |
|------|--------|
| L5 SSOT rewrite (authority, runtime, M&V, P0–P3 cost) | done |
| ADR-019 / ADR-020 / ADR-021 | done |
| Contracts 0.7.0 (`workflow-event`, ledger supersession fields) | done |
| handoff/stamped-l5-architecture-handoff.md + build-plan | done |
| Cross-doc contradiction sync (arch §5.4/§11, prod-eng Temporal, L2 DDL) | done |

## Ops-first L5 + L3 enablement (2026-07-21)

| Item | Status |
|------|--------|
| L5 SSOT / ADR-020 / handoffs reframed: ops-clearance, EMS alarms, bill deferred | done |
| Contracts **0.8.0**: Finding 1.1.0 `ops_clearance`, ledger `ops_confirmed`, workflow alarm/ops events | done |
| L3 SSOT + arch §5.2 + build-order + paste-ready L3 prompt | done |
| L3-core / L4 fixtures scaffold sync for 1.1.0 | done |

## L6 architecture + UI handoff (2026-07-21)

| Item | Status |
|------|--------|
| ADR-022 / ADR-023 | done |
| L6 SSOT ops-first + EMS + dual-mode analyst | done |
| UI charter + architecture/build/onboarding handoffs | done |
| `consumers/stamped-l6` typed reference seed | done (tests + build green) |
| Hardening (contract-check + ponytail chip shrink + security checklist) | done |
| Live `Vinayak-RZ/stamped-l6` consumer repo | **planned** — follow [handoff/stamped-l6-build-plan.md](handoff/stamped-l6-build-plan.md) |

## Next (P1 — out of P0 scope)

- Create `stamped-l6` consumer repo from handoff + seed transfer manifest
- Create `stamped-l5` consumer repo per [handoff/stamped-l5-build-plan.md](handoff/stamped-l5-build-plan.md)
- L3 consumer repos: paste [stamped-l3-ops-clearance-consumer-prompt.md](handoff/stamped-l3-ops-clearance-consumer-prompt.md)
- Live L2 query API + ledger append endpoint
- LangGraph full agent lane (per L4 handoff); L6 Mode B live chat
- Forging/auto rulepacks
- Deferred bill reconcile / IPMVP Option C gate (not P0)
- TimesFM promotion re-eval with pilot data
- Event NILM-lite attribution shadow (gated 1-min + labels)
