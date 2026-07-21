# ADR-022: L6 BFF runtime boundary and repo charter

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-21 |
| **Deciders** | Engineering (L6 architecture + UI handoff) |
| **Related** | [ADR-008](ADR-008-layer-repo-topology-and-interfaces.md) · [ADR-018](ADR-018-l4-pilot-execution-knowledge-reasoning.md) · [ADR-019](ADR-019-l5-runtime-and-consistency.md) · [ADR-020](ADR-020-l5-mv-claim-governance.md) · [L6 SSOT](../technical/layers/L6-experience-and-integration.md) · [L2 query API](../handoff/stamped-l2-query-api-sketch.md) |

---

## Context

L6 (Experience & Integration) is the customer-facing layer: dashboard, EMS alarm console, prescription queue, exports, outbound API/webhooks, and analyst UX. Prior docs left three ambiguities:

1. Whether the browser talks directly to L2/L4/L5 or through an L6 composition layer.
2. Whether L6's public `/v1` API is the same surface as the dashboard BFF.
3. Whether L6 may compute savings, clearance, or RAG locally.

Accepted product defaults (2026-07-21 plan): **ops-first control room**, **Next.js App Router**, **tenant-scoped BFF**, **HTTP-only to upstream layers**.

---

## Decision summary

| # | Topic | Decision |
| --- | --- | --- |
| 1 | Repo | **One repo `stamped-l6`** (planned GitHub: `Vinayak-RZ/stamped-l6`) |
| 2 | Topology | **Modular monolith**: `packages/web` (Next.js) + `packages/api` (BFF) + `packages/worker` (PDF/exports/webhooks) |
| 3 | Upstream access | **HTTP only** to L2 query, L4 analyst/prescription APIs, L5 workflow/alarms/events — **no** `L2_DATABASE_URL` / OT writes |
| 4 | Composition | Browser → L6 BFF → L2/L4/L5; browser never holds service keys |
| 5 | Public API | L6 public `/v1` is a **dogfooded thin surface over the same BFF** (P2); P0 dashboard uses session-auth BFF routes |
| 6 | Writes | Workflow ack/defer/reject/alarm actions and config only; audit via L5 |
| 7 | Realtime | **SSE** with `Last-Event-ID` resume (Redis pub/sub fan-out when multi-instance) |
| 8 | Claims | Render `ops_confirmed` and future bill `verified` as **separate badges**; never imply DISCOM verification from ops alone ([ADR-020](ADR-020-l5-mv-claim-governance.md)) |
| 9 | Ledger reads | L2 `GET /v1/ledger/entries…` only — never L5 append |
| 10 | Platform seed | `consumers/stamped-l6/` is a **non-canonical** typed reference UI seed for handoff |

---

## 1. Runtime shape

```text
stamped-l6/
  packages/
    web/          # Next.js App Router — RSC shells + client islands
    api/          # Tenant-scoped BFF (session + scoped API keys for public /v1)
    worker/       # BullMQ: PDF packs, CSV jobs, Standard Webhooks sender
  tests/
  external/       # stamped-external submodule
```

**Rejected:** browser-direct multi-service fan-out (tenancy/auth/audit leak risk); embedding L6 inside L5; direct Timescale access for charts.

---

## 2. Trust boundaries

| Boundary | Policy |
| --- | --- |
| Browser → BFF | Session cookie / OIDC; org→plant RBAC on every route |
| BFF → L2/L4/L5 | Service credentials; inject `X-Org-Id` / `X-Plant-Id`; strip cross-tenant params |
| Public `/v1` | Scoped API keys (`read:ledger`, `read:prescriptions`, `write:acknowledgements`, …) |
| OT / plant systems | **Read-only forever** — L6 never writes SCADA/EMS OT |
| Analyst context | Explicit envelope only ([ADR-023](ADR-023-l6-ems-and-analyst-context.md)) |

---

## 3. P0 vs later API surfaces

| Surface | Phase | Auth |
| --- | --- | --- |
| Session BFF (`/app/*` or Route Handlers) | **P0** | User session + RBAC |
| SSE event stream | **P0** | Session; resume via `Last-Event-ID` |
| Public REST `/v1` + OpenAPI | **P2** | Scoped keys / OAuth2 client-credentials |
| Standard Webhooks sender | **P2** | Per-endpoint HMAC secrets |

---

## Consequences

- Handoff and consumer agents must not invent L6-local clearance or counterfactual computation.
- Platform pack may ship UI reference components under `consumers/stamped-l6/`; product truth remains L5/L2 contracts + this ADR.
- Forge Industrial tokens ([design/forge-industrial-design-system.md](../design/forge-industrial-design-system.md)) are mandatory for product UI.

---

## Alternatives considered

| Option | Rejected because |
| --- | --- |
| Browser → L5/L2 directly | Duplicates tenancy, CORS, and audit; leaks service topology |
| GraphQL federation gateway | Unnecessary complexity before measured multi-client need |
| Separate "L6 public API" micro-repo | Violates ADR-008 one-repo-per-layer; BFF dogfooding keeps contracts honest |
