# ADR-020: L5 M&V claim governance

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-20 |
| **Deciders** | Engineering (L5 architecture overhaul) |
| **Related** | [L5 SSOT](../technical/layers/L5-closure-and-verification.md) · [ADR-013](ADR-013-counterfactual-savings-ledger.md) · [ADR-019](ADR-019-l5-runtime-and-consistency.md) · [ledger-entry.json](../contracts/schemas/ledger-entry.json) |

---

## Context

Customer trust rests on “verified on the DISCOM bill.” Over-claiming (noisy Option C, overlapping Rx double-count, FPPCA swings, unlocked baselines) is an existential product risk. L5 research already sketched IPMVP two-tier design; this ADR freezes **claim governance** so implementers cannot silently auto-verify or mutate history.

---

## Decision summary

| # | Topic | Decision |
| --- | --- | --- |
| 1 | Account truth | **IPMVP Option C** (production-normalised) + bill reconciliation |
| 2 | Per-Rx attribution | Option **A/B**; hard cap `Σ Rx ≤ Tier-1` |
| 3 | Option D | **Not used** |
| 4 | P0 claim gate | **Human analyst reviews every verification** |
| 5 | Auto-verify | **P2+** only after empirical band from ≥3 plants and dispute rate &lt;5% |
| 6 | Baseline history | **12 months preferred**; **9 months provisional** → `low_confidence_mv`, manual-only |
| 7 | Baseline lock | Confirm lock when verification window opens; no silent retrain of cited baseline |
| 8 | Bill claim scope | Claim **efficiency effect only**; report rate/volume/FPPCA separately |
| 9 | Corrections | Append-only via new LedgerEntry + `supersedes_entry_id` |
| 10 | Counterfactual | `opportunity_cost` always `verification_status=modeled` (ADR-013) |
| 11 | Overlap | Disjoint → independent; shared boundary → **bundle** (P2); tariff lines deterministic |
| 12 | Emission factors | Version snapshotted at post; CEA national default |

---

## Claim statuses

| `verification_status` | Meaning |
| --- | --- |
| `pending` | Intent/model computed; not customer-verified |
| `verified` | Passed gates + analyst (P0) or auto-band (P2) + bill reconcile |
| `disputed` | Customer/analyst challenge open |
| `modeled` | Counterfactual or non-bill claim — **never** sold as bill-verified |

Dispute resolution outcomes (`resolved_upheld` / `resolved_adjusted` / `resolved_withdrawn`) live on **DisputeCase**, not as LedgerEntry `verification_status` values. Adjustments post compensating ledger rows.

---

## Gating checklist before `verified`

1. Baseline locked and G14 fit gates passed (Option C) or deterministic tariff path validated (A).
2. Verification window elapsed (or tariff-line immediate path with one billing cycle confirm).
3. Data-gap policy: windows with insufficient coverage → `data_insufficient`, no verified claim.
4. Decomposition shows non-zero efficiency effect attributable after rate/volume removal.
5. Attribution cap applied.
6. Analyst approval recorded (P0/P1) or auto-band satisfied (P2).

---

## Consequences

- L6 must not display `modeled` or `pending` as “verified on bill”.
- Sales 90-day program language must cite this methodology and name a dispute review process (legal template still open).
- L2 DDL CHECK for `verification_status` must include `modeled` and must not require mutable `superseded` status.

---

## Alternatives considered

| Option | Rejected because |
| --- | --- |
| Auto-verify from day one | False-claim risk at pilot volumes |
| Site-level Option C only, no per-Rx | Weak ops accountability / ranking feedback |
| Edit ledger rows on dispute | Breaks auditability |
| Weather-only CalTRACK models | Industrial driver is production, not degree-days |
