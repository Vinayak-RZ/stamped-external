# stamped-l5 — Architecture handoff

> **Audience:** Engineers / agents working on the L5 consumer or integrating L6.  
> **Consumer repo (live):** [Vinayak-RZ/closure-verification](https://github.com/Vinayak-RZ/closure-verification) — package `stamped-l5`  
> **README snapshot:** [../consumers/readmes/closure-verification.md](../consumers/readmes/closure-verification.md)  
> **Authority:** [L5 SSOT](../technical/layers/L5-closure-and-verification.md) · [ADR-019](../decisions/ADR-019-l5-runtime-and-consistency.md) · [ADR-020](../decisions/ADR-020-l5-mv-claim-governance.md) · [ADR-021](../decisions/ADR-021-l5-notification-and-evidence.md) · [ADR-013](../decisions/ADR-013-counterfactual-savings-ledger.md)  
> **L3 dependency:** [stamped-l3-ops-clearance-consumer-prompt.md](./stamped-l3-ops-clearance-consumer-prompt.md) · Finding 1.1.0 `ops_clearance`  
> **Contracts:** [`prescription.json`](../contracts/schemas/prescription.json) · [`workflow-event.json`](../contracts/schemas/workflow-event.json) · [`ledger-entry.json`](../contracts/schemas/ledger-entry.json) · [`finding.json`](../contracts/schemas/finding.json)  
> **Build plan:** [stamped-l5-build-plan.md](./stamped-l5-build-plan.md) (P0–P2 historical; see consumer README for shipped surface)

---

## 1. Mission

**stamped-l5** closes the loop: assign → alarm/notify → act → **ops-verify on telemetry** → track **calculated** ₹/kWh.

| Is | Is not |
| --- | --- |
| Workflow + durable timers | L3 detection engines |
| **EMS alarm router** (raise/ack/escalate/clear) | Re-implementing MD/idle/SEC detectors |
| **Ops-clearance verification** | Bill/IPMVP gate (deferred) |
| Calculated potential + ops_confirmed realised ledger | Claiming “verified on DISCOM bill” |
| WhatsApp-first notification | Plant dashboard UI (L6) |
| Opportunity-cost job (`modeled`) | OT / SCADA writes |

---

## 2. Upstream / downstream

```mermaid
flowchart LR
  L3[intelligence_core Finding] -->|ops_clearance| L4[knowledge_reasoning]
  L4 -->|Prescription| L5[stamped_l5]
  L5 -->|tag poll + ledger append| L2[stamped_l2]
  Meta[Meta_Cloud_API] <--> L5
  L5 -->|WorkflowEvent + alarms| L6[stamped_l6]
  L5 -->|false_clear / regress| L3
```

| Rule | Detail |
| --- | --- |
| Hard gate | Every cited Finding must include `ops_clearance` |
| VERIFIED | Ops-cleared — not bill |
| Financial SoR | L2 ledger via idempotent append |
| No L2 DB URL | HTTP only |

---

## 3. Target repo layout

```text
stamped-l5/
  packages/
    api/
    worker/              # timers, clearance poller, outbox, opportunity_cost
    domain/
      workflow/
      alarms/            # EMS router
      notification/
      verification/      # ops_clearance eval
      evidence/
      integration/
    migrate/
  tests/
  external/
```

---

## 4. Domain modules

| Module | Owns |
| --- | --- |
| `workflow` | States; `verified` = ops-cleared |
| `alarms` | EMS lifecycle + L6 query |
| `notification` | Meta templates / webhooks |
| `verification` | Poll L2; eval predicates; regress |
| `integration` | Finding fetch, L2 append, measurements |

---

## 5. P0 capability band

| Capability | Band |
| --- | --- |
| Intake + owner + ops_clearance hard gate | **P0 must** |
| Alarm raise/ack/escalate/clear | **P0 must** |
| Clearance poller + ops_confirmed ledger | **P0 must** |
| Potential savings at accept | **P0 must** |
| WhatsApp templates | **P0 must** |
| Bill-verified path | **Deferred** |
| SMS send | **P1** |

---

## 6. Related docs

| Doc | Use |
| --- | --- |
| [stamped-l5-build-plan.md](./stamped-l5-build-plan.md) | Commit matrix |
| [stamped-l3-ops-clearance-consumer-prompt.md](./stamped-l3-ops-clearance-consumer-prompt.md) | Paste into L3 agents |
| [L5 SSOT](../technical/layers/L5-closure-and-verification.md) | Full architecture |
