# stamped-l3-core

Stamped L3 intelligence engine — deterministic MD/PF engines, suppression, and transactional outbox.

Part of the Stamped platform ([IMPLEMENTATION_PLAN Phase B](../../IMPLEMENTATION_PLAN.md)). Reads telemetry via an L2 query client (fixture-backed until `stamped-l2` query API ships), emits contract-aligned `Finding` objects through an in-memory outbox.

## Layout

```
src/stamped_l3_core/
  models/finding.py      Finding dataclass + dedupe_key
  clients/l2.py          L2QueryClient protocol + FixtureL2Client
  engines/md.py          MD overlap detection (kVA vs baseline band)
  engines/pf.py          PF slab breach stub
  suppression.py         startup_window + maintenance_calendar checks
  outbox.py              TransactionalOutbox (in-memory)
  scheduler.py           run_hot_path() — MD engine hot path
  rulepack_loader.py     semver rulepack manifest loader
  detection_lane.py      ADR-015 delivery mapping (l4 vs lab_only)
  lab_export.py          RunArtifact 1.1.0 export + /lab/export HTTP for eval Lab UI
  challenger/attribution_shadow.py  ADR-016 ranking ablations + motif stub (Lab-only)
tests/
  unit/                  engine, suppression, outbox unit tests
  golden/                fixture → Finding golden replay
  fixtures/              L2 measurement JSON fixtures
```

## Lab export (for stamped-l3-eval)

```bash
pip install -e .
stamped-l3-lab
# GET http://127.0.0.1:8090/lab/export
# Optional: CORE_LAB_TOKEN=… Authorization: Bearer …
```


## Quick start

```bash
cd consumers/stamped-l3-core
pip install -e ".[dev]"
pytest -q
```

## L2 workaround (Phase B)

L3 never receives `L2_DATABASE_URL`. Until the L2 query API is live, `FixtureL2Client` loads JSON fixtures from `tests/fixtures/` (or a configured directory). Swap to an HTTP client when `stamped-l2` ships.

## Contracts

Findings conform to `contracts/schemas/finding.json` in the pinned platform submodule. Dedupe key = `sha256(category|sorted_assets|window)`.

## Platform pin

Pin `external/contracts` SHA in release notes when integrating with the platform repo submodule.
