# ADR-023: L6 EMS console and dual-mode analyst context

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-21 |
| **Deciders** | Engineering (L6 architecture + UI handoff) |
| **Related** | [ADR-018](ADR-018-l4-pilot-execution-knowledge-reasoning.md) · [ADR-020](ADR-020-l5-mv-claim-governance.md) · [ADR-021](ADR-021-l5-notification-and-evidence.md) · [ADR-022](ADR-022-l6-bff-runtime-boundary.md) · [L5 SSOT](../technical/layers/L5-closure-and-verification.md) · [L4 SSOT](../technical/layers/L4-knowledge-and-reasoning.md) · [workflow-event.json](../contracts/schemas/workflow-event.json) |

---

## Context

Product decisions (2026-07-21):

1. L6 is an **ops-first control room**, not a chart gallery.
2. EMS-style alarms are detected/hinted by L3, routed by L5, and **rendered/acted in L6**.
3. The analyst must not live only as a left-rail drawer: it needs a **full workspace** and a **route-aware side assistant**.
4. Cognitive load must stay low: advanced EMS/energy modules appear via **progressive reveal**, never by dumping every skill on Today.

L4 owns RAG/agent runtime ([ADR-018](ADR-018-l4-pilot-execution-knowledge-reasoning.md)); L6 owns chat UX only.

---

## Decision summary

| # | Topic | Decision |
| --- | --- | --- |
| 1 | EMS ownership | **L6 renders** alarm console; **L5 owns** raise/ack/escalate/silence/clear truth |
| 2 | Alarm states | `raised` · `acked` · `escalated` · `silenced` · `cleared` (from L5 / `WorkflowEvent`) |
| 3 | Home density | Today shows **≤7** decision signals; advanced modules behind role-aware **More / Reveal** |
| 4 | Analyst modes | **Dual-mode**: (A) contextual side assistant, (B) full `/analyst` workspace |
| 5 | Analyst phasing | Contextual shell contracts + UI in **P0**; full workspace + L4 live chat in **P1** |
| 6 | Context policy | Side assistant receives an **explicit, user-visible, removable** screen-context envelope — never silent page scrape |
| 7 | RAG | Always via L4 HTTP; L6 does not embed vectors or run tools |
| 8 | Language | **English through P2** ([ADR-018](ADR-018-l4-pilot-execution-knowledge-reasoning.md) §10) — Hindi deferred |
| 9 | Irreversible actions | Ack / defer / reject / silence require explicit user action; agent may **propose**, never auto-commit |

---

## 1. EMS console (P0)

| Concern | Rule |
| --- | --- |
| Data | L5 alarm list query + SSE `alarm_*` / `ops_*` events |
| Actions | Ack / escalate / silence / open evidence / link Rx — POSTs through L6 BFF → L5 with Idempotency-Key |
| UX | Severity-first, ageing badges, keyboard triage, stale-connection banner, mobile-capable ack |
| Colour | ISA-101: grayscale normal; colour only for abnormal / overdue |
| Non-goal | L6 is **not** a SCADA HMI or OT alarm system of record |

---

## 2. Progressive disclosure

Primary nav (always): **Today · Alarms · Prescriptions · Evidence · Analyst · Reports**.

Role-gated **More** reveals: Energy analytics, Equipment health, TOD/MD, Intensity/CO₂, Integrations, Admin.

Rules:

- Reveal preference remembered per user.
- Critical open alarms and assigned Rx **cannot** be hidden by collapsing More.
- Today never becomes a dashboard of every module.

---

## 3. Dual-mode analyst

### Mode A — Contextual side assistant (P0 shell)

Mounted beside a working screen (Alarms, Prescriptions, Evidence, Energy, …).

```text
AnalystContextEnvelope {
  org_id, plant_id, user_id, role
  route_id, screen_title
  focus_entity?: { type: alarm|prescription|asset|ledger_entry, id }
  visible_summary: string[]     # user-visible chips only
  time_range?: { from, to }
  exclude_keys?: string[]       # user removed chips
}
```

- UI shows attached chips; user can remove any chip before send.
- BFF validates tenant match and strips secrets / hidden DOM / raw tokens.
- L4 still runs RAG over corpus + tools; screen context is **additional**, not a replacement.

### Mode B — Full analyst workspace (P1)

Route `/analyst`: conversation column, sources/citations, evidence canvas, saved investigations, **handoff-to-action** (create/open Rx, deep-link alarm) with human confirm.

---

## 4. Security constraints

1. No prompt injection via untrusted page HTML — only structured envelope fields.
2. Cross-tenant `focus_entity` IDs rejected at BFF.
3. Audit: every analyst turn logs model id, tokens, latency, tool calls (from L4), and envelope hash.
4. WhatsApp / magic-link surfaces must not feed raw chat into agent context ([ADR-018](ADR-018-l4-pilot-execution-knowledge-reasoning.md)).

---

## Consequences

- L6 SSOT phasing moves conversational analyst from vague P3 → **P0 contextual / P1 full**.
- UI charter must specify EMS console and both analyst modes with acceptance criteria.
- Reference seed implements Mode A chrome + Mode B layout against fixtures; live L4 wiring is consumer P1.

---

## Alternatives considered

| Option | Rejected because |
| --- | --- |
| Drawer-only AI (demo `AiDrawer`) | Undervalues investigation; context of active screen is weak |
| Full analyst in P0 | Blocks EMS/queue closure on L4 maturity |
| Silent full-page context scrape | Prompt injection + PII/secret leak risk |
| Separate EMS micro-frontend | Over-splits one product; progressive reveal covers density |
