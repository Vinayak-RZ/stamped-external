# L6 handoff — counterfactual display fields

> **Scope:** Display contract for `opportunity_cost` rows — still required in L6 UI.  
> **Full L6 handoff:** [stamped-l6-architecture-handoff.md](./stamped-l6-architecture-handoff.md) · [UI charter](./stamped-l6-ui-ux-charter.md)  
> **Contract:** [ledger-entry.json](../contracts/schemas/ledger-entry.json) · [ADR-013](../decisions/ADR-013-counterfactual-savings-ledger.md) · [ADR-020](../decisions/ADR-020-l5-mv-claim-governance.md)

---

## Prescription queue additions

When `LedgerEntry.entry_type = opportunity_cost`:

| UI field | Source | Label |
| --- | --- | --- |
| `delay_days` | ledger row | "Days delayed" |
| `realised_inr` | ledger row | "Estimated cost of delay" |
| `verification_status` | `modeled` | Badge: **Modeled — not bill-verified** |
| `first_recommended_at` | Prescription | "First recommended" |
| `implemented_at` | Prescription | "Implemented" |

## Disclaimer copy (required)

> This delay cost is modeled from prescription timing and estimated monthly impact. It is not verified against your DISCOM bill.

## API shape (sketch)

```json
{
  "prescription_id": "rx-…",
  "opportunity_cost": {
    "delay_days": 23,
    "modeled_inr": 21840,
    "verification_status": "modeled"
  }
}
```

L6 **reads** ledger via L2 query API (`GET /v1/ledger/entries…`) — never the L5-only append endpoint. L6 does not compute counterfactual locally.
