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
| ADR-017 | L4 adaptive retrieval + web trust tiers | **Accepted** |
| ADR-019 | L5 runtime charter and consistency | **Accepted** |
| ADR-020 | L5 M&V claim governance (ops-first 2026-07-21) | **Accepted** |
| ADR-021 | L5 notification and evidence policy | **Accepted** |

## L5 architecture (2026-07-20)

| Topic | Choice |
|-------|--------|
| Repo | Separate `stamped-l5` modular monolith (ADR-008/019) |
| Workflow | Postgres state machine + durable timers through P0–P2 — Temporal deferred |
| Ledger | L5 policy + append intent; L2 `ledger.mv_ledger` SoR (ADR-013/019) |
| Claims | Analyst gate P0; Option C account truth; A/B attribution capped (ADR-020) |
| Notify | Meta Cloud API direct; shared WA number; DLT P0 / SMS P1 (ADR-021) |
| Contracts | 0.7.0 — `workflow-event.json` + ledger supersession fields |
| Handoff | [handoff/stamped-l5-architecture-handoff.md](handoff/stamped-l5-architecture-handoff.md) · [build plan](handoff/stamped-l5-build-plan.md) |

## Ops-first verification + EMS (2026-07-21) — supersedes bill-first claim language

| Topic | Choice |
|-------|--------|
| Verified | Ops-cleared via Finding `ops_clearance` held for `stabilize_window` (ADR-020) |
| Bill path | Deferred — ledger `verified` reserved; P0 uses `ops_confirmed` |
| Savings tracking | Calculated potential at issue + ops-realised after clearance |
| Alarms | L3 detects + `alarm_hint`; L5 routes ack/escalate; L6 EMS console |
| Finding | **1.1.0** required `ops_clearance` (+ optional `alarm_hint`) |
| Contracts | **0.8.0** |
| L3 paste prompt | [handoff/stamped-l3-ops-clearance-consumer-prompt.md](handoff/stamped-l3-ops-clearance-consumer-prompt.md) |

## L4 architecture (2026-07-17)

| Topic | Choice |
|-------|--------|
| Repo | Single `stamped-l4` (runtime + corpus + eval) |
| Agent | Dual-lane: template (0 LLM) + bounded LangGraph (≤5 soft / 6 hard) |
| Retrieval | Adaptive hybrid H/G/V + allowlisted web T4 — [ADR-017](decisions/ADR-017-l4-adaptive-retrieval-and-web-trust.md) |
| Eval | Langfuse + Arize Phoenix + DeepEval (LangSmith optional) |
| Handoff | [handoff/stamped-l4-architecture-handoff.md](handoff/stamped-l4-architecture-handoff.md) |

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
