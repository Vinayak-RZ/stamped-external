# ADR-013: Counterfactual savings ledger

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-13 |
| **Deciders** | Engineering (L3/L4 intelligence plan) |
| **Related** | [ADR-008](ADR-008-layer-repo-topology-and-interfaces.md) · [L5 spec](../technical/layers/L5-closure-and-verification.md) · [ledger-entry.json](../contracts/schemas/ledger-entry.json) |

---

## Context

Zerowatt's Digital Brain tracks recommendations and equipment health; Stamped differentiates on **bill-verified closure** and **accountability for delay**. When a prescription is acted on late, the customer loses savings during the delay window — a counterfactual cost that should be modeled and surfaced without claiming M&V verification.

---

## Decision

1. **New ledger entry type:** `LedgerEntry.entry_type = opportunity_cost`
2. **Lifecycle timestamps on Prescription:** `first_recommended_at`, `implemented_at`, `verified_at`
3. **Store split:** L5 `opportunity_cost` job computes and writes; L2 stores append-only ledger rows
4. **Verification label:** `verification_status = modeled` (never `verified` for counterfactual rows)
5. **Formula (P0):** `realised_inr = delay_days × (potential_inr / 30)` where `delay_days = implemented_at − first_recommended_at`

---

## Rationale

- Separates **verified bill savings** from **modeled delay cost** — auditors cannot confuse the two.
- Enables L6 narrative: "You could have saved ₹X more if acted on date Y."
- Feeds L3 calibration: chronic delay categories get reframed prescriptions.

---

## Consequences

- Contract schema `ledger-entry.json` v1.0.0 includes `opportunity_cost` enum + `modeled_reason` + `delay_days`.
- L6 handoff documents display disclaimer for modeled entries.
- Disputes handled via L5 reason codes, not silent ledger edits (append-only preserved).

---

## Alternatives considered

| Option | Rejected because |
| --- | --- |
| Store counterfactual on Prescription only | No ledger rollup; breaks M&V reporting |
| Mark opportunity_cost as `verified` | Misleading; not bill-reconciled |
| L4 computes delay cost | L4 never owns financial truth |
