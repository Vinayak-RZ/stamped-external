# stamped-l4

L4 **template-fast-path** scaffold (Lane A, P0). Maps high-confidence `Finding` categories to deterministic `Prescription` JSON — no LLM.

Aligned with [handoff/stamped-l4-build-order.md](../../handoff/stamped-l4-build-order.md) and platform contracts under `external/contracts/` (submodule).

## Supported categories

| Finding category | Template ID |
| --- | --- |
| `md_overlap` | `md_overlap.stagger_costart.v1` |
| `pf_slab_breach` | `pf_slab.apfc_health.v1` |
| `tod_exposure` | `tod_exposure.shift_load.v1` |

## Layout

```
src/stamped_l4/
  template_renderer.py   # Finding → Prescription
  verifier.py              # schema gate + 1% numeric drift check
tests/
  unit/
  eval/golden_tasks.json   # ≥20 golden task IDs
  fixtures/                # sample Finding JSON
```

## Setup

```bash
cd consumers/stamped-l4
python -m pip install -e ".[dev]"
pytest
```

## Usage

```python
from stamped_l4.template_renderer import render_prescription
from stamped_l4.verifier import verify

prescription = render_prescription(finding_dict)
ok, errors = verify(prescription, finding_dict)
```

## Exit criteria (P0)

- [x] Template renderer for md_overlap, pf_slab_breach, tod_exposure
- [x] Numeric verifier (impact within 1% of finding estimate)
- [x] Required-field schema gate
- [x] Eval manifest with ≥20 task entries
- [ ] LangGraph lane (P1)
- [ ] HTTP tools to L2 (P1)

## Contracts

Pin platform submodule at `external/` and validate against `contracts/schemas/prescription.json` when wiring CI.
