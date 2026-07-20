# ADR-019: L5 runtime charter and cross-service consistency

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-20 |
| **Deciders** | Engineering (L5 architecture overhaul) |
| **Related** | [ADR-008](ADR-008-layer-repo-topology-and-interfaces.md) · [ADR-013](ADR-013-counterfactual-savings-ledger.md) · [L5 SSOT](../technical/layers/L5-closure-and-verification.md) · [L2 query API](../handoff/stamped-l2-query-api-sketch.md) |

---

## Context

L5 (Closure & Verification) must ship as a real service without re-deciding topology, workflow engine, or ledger write semantics. Prior docs conflicted: production-engineering sketched a “core monolith” including workflow/M&V; the L5 research draft implied local ledger tables and a single Postgres transaction spanning ledger writes; Temporal was proposed at P1–P2.

Accepted boundaries (user confirmed 2026-07-20): **separate `stamped-l5` repo**, **L2 stores append-only ledger**, **no L5 direct DB access to L2**.

---

## Decision summary

| # | Topic | Decision |
| --- | --- | --- |
| 1 | Repo | **One repo `stamped-l5`** — FastAPI modular monolith |
| 2 | L5 database | **Dedicated Postgres DB `stamped_l5`** (may share RDS *instance*) for workflow, timers, inbox/outbox, verification cases |
| 3 | Workflow engine | **Custom state machine + durable `scheduled_actions`** through P0–P2 |
| 4 | Jobs / events | **Postgres outbox + SKIP LOCKED workers** — no Redis/Kafka/Temporal by default |
| 5 | Ledger writes | **L5 `ledger_append_intent` → idempotent `POST /v1/ledger/entries` on L2** |
| 6 | Consistency model | **At-least-once + idempotent append + explicit ACK states** — never claim distributed single-transaction or exactly-once delivery |
| 7 | Prescription vs workflow | **L4 Prescription = intake contract; L5 WorkflowState/WorkflowEvent = runtime truth** |
| 8 | Deploy (P0) | ECS Fargate API + worker in `ap-south-1`; cost-first sizing |

---

## 1. Runtime shape

```
stamped-l5
├── packages/api          # webhooks, analyst actions, L6 query
├── packages/worker       # timers, outbox, M&V, opportunity_cost
├── packages/domain/*     # workflow, notification, verification, reconciliation, evidence, integration
└── packages/migrate      # L5 schema only
```

**Rejected:** embedding L5 in an L2–L6 mega-monolith (violates ADR-008); Temporal Cloud at P0 (ops + ₹ cost before proven need); Redis job queue before measured Postgres pain.

---

## 2. Ledger append protocol

1. Approve claim in L5 transaction → write `verification_case` + `ledger_append_intent` + local outbox row.
2. Worker POSTs to L2 with stable `dedupe_key` / Idempotency-Key.
3. L2 inserts into `ledger.mv_ledger` (append-only) or returns duplicate success.
4. L5 marks intent `acked` and emits L6 events.

**Ambiguous timeout:** retry same key; do not create a second intent payload identity.

---

## 3. Upgrade triggers (Temporal / split)

Revisit Temporal Cloud **only if** both are true:

- M&V window / escalation bugs repeatedly survive deploys despite durable timers, **and**
- Engineering time spent on timer correctness exceeds Temporal Cloud cost for the fleet size.

Split API/worker further or add Redis **only** on measured lag/CPU triggers.

---

## Consequences

- Handoff docs must not instruct L5 to open `L2_DATABASE_URL`.
- L5 SSOT and production-engineering must reference this ADR for workflow engine choice.
- Contract pack gains `workflow-event.json` for L5→L6 stream.
- Opportunity-cost job (ADR-013) uses the same append protocol.

---

## Alternatives considered

| Option | Rejected because |
| --- | --- |
| L5 stores ledger SoR locally | Breaks L2 financial truth / ADR-013 |
| Temporal from day one | Cost + ops surface before failure evidence |
| Shared L2–L5 database writes | Violates ADR-008 non-negotiable rules |
| Saga framework | Only external side effects are Meta/L2 — retries + idempotency suffice |
