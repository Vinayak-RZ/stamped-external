# stamped-l4 — P0 build order

> **Aligned with:** [L4 spec](../technical/layers/L4-knowledge-and-reasoning.md) · [ADR-013](../decisions/ADR-013-counterfactual-savings-ledger.md)  
> **Depends on:** Finding + Prescription contracts frozen (platform Phase A)

---

## Exit criterion (P0 complete)

- Template-fast-path produces valid `Prescription` from fixture `Finding` (md_overlap, pf_slab_breach)
- Numeric verifier + schema gate block invalid payloads
- Eval harness manifest lists ≥20 golden tasks
- No direct L2 DB access — tools via HTTP only

---

## Phase D — Template path (P0)

| Step | Deliverable | Exit test |
| --- | --- | --- |
| D1 | Template taxonomy doc | md_overlap, pf_slab templates defined |
| D2 | Template renderer | Finding → Prescription JSON |
| D3 | Numeric verifier | Rejects LLM-arithmetic drift >1% |
| D4 | Schema gate | Invalid Prescription → blocked |
| D5 | Eval manifest | 20+ task IDs listed |

**Lane A only in P0** — LangGraph full agent deferred P1.

---

## Template-fast-path categories (P0)

| Finding category | Template ID | LLM? |
| --- | --- | --- |
| `md_overlap` | `md_overlap.stagger_costart.v1` | No |
| `pf_slab_breach` | `pf_slab.apfc_health.v1` | No |
| `tod_exposure` | `tod_exposure.shift_load.v1` | No |

---

## Tools (P1 LangGraph)

Seven read-only/deterministic tools per L4 spec §2.4 — no OT writes.

---

## Submodule + contracts

Same `external/` submodule as l3-core. Prescription schema includes lifecycle timestamps per ADR-013.
