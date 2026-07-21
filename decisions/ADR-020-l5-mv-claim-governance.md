# ADR-020: L5 verification & savings claim governance

| Field | Value |
| --- | --- |
| **Status** | Accepted (superseded in part 2026-07-21 — ops-first) |
| **Date** | 2026-07-20 · **Revised** 2026-07-21 |
| **Deciders** | Engineering (L5 architecture overhaul + ops-first revision) |
| **Related** | [L5 SSOT](../technical/layers/L5-closure-and-verification.md) · [ADR-013](ADR-013-counterfactual-savings-ledger.md) · [ADR-019](ADR-019-l5-runtime-and-consistency.md) · [finding.json](../contracts/schemas/finding.json) · [ledger-entry.json](../contracts/schemas/ledger-entry.json) |

---

## Context

Earlier ADR-020 treated “verified” as bill/IPMVP reconciliation. Product clarified (2026-07-21): **verification means the operational fault cleared** (load stabilized, leak fixed, coincidence broken, SEC drift reversed) proven on telemetry. Bill confirmation is deferred. Savings are tracked as **Stamped-calculated** amounts now.

---

## Decision summary (binding)

| # | Topic | Decision |
| --- | --- | --- |
| 1 | What “verified” means | **Ops-cleared** via Finding `ops_clearance` held for `stabilize_window` |
| 2 | Bill path | **Deferred** — not a P0/P1 gate |
| 3 | Detection vs alarms | **L3 detects**; **L5** routes EMS alarms + evaluates clearance |
| 4 | P0 savings tracking | `potential_savings` at issue; `realised_savings` with **`ops_confirmed`** after clearance |
| 5 | Reserved status | `verification_status=verified` reserved for **future bill path** |
| 6 | Counterfactual | `opportunity_cost` always `modeled` (ADR-013) |
| 7 | Corrections | Append-only + `supersedes_entry_id` |
| 8 | Regress | `reopen_if_regresses` → reopen workflow, re-raise alarm, compensating ledger |
| 9 | IPMVP / Option C | Deferred appendix — re-enable behind product flag later |
| 10 | Analyst gate | **Not** required for every ops-clear; optional for disputes/overrides |

---

## Claim statuses

| `verification_status` | Meaning |
| --- | --- |
| `pending` | Potential posted or clearance in flight |
| `ops_confirmed` | Telemetry clearance held — **P0 customer-facing “verified”** |
| `modeled` | Counterfactual / non-ops estimate (e.g. opportunity_cost) |
| `disputed` | Challenge open |
| `verified` | **Reserved** — bill-reconciled (deferred) |

---

## Gating checklist before `ops_confirmed`

1. Finding(s) expose `ops_clearance` with `related_tag_ids` + predicate + `stabilize_window`.
2. Rx reached DONE (or predicate already true with policy allow).
3. L2 tag coverage sufficient for stabilize window.
4. Predicate holds continuously for stabilize window.
5. Ledger append intent written with calculated realised ₹/kWh.

---

## Consequences

- L6 must label ops-confirmed distinctly from any future bill-verified badge.
- L3 must emit Finding 1.1.0 `ops_clearance` (+ optional `alarm_hint`) — see [stamped-l3-ops-clearance-consumer-prompt.md](../handoff/stamped-l3-ops-clearance-consumer-prompt.md).
- Prior “analyst reviews every verification” / “Option C account truth as gate” language is **superseded** for P0–P1.

---

## Alternatives considered

| Option | Rejected because |
| --- | --- |
| Bill-only verified | Misaligns with plant reality; slow feedback |
| Ops-only with no ₹ tracking | Loses calculated savings accountability |
| L5 re-implements detectors | Duplicates L3; use catalog map instead |
