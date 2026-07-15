# Phase completion — dual-lane Lab detections

## Completed

- RunArtifact **1.1.0** with required `delivery` + `hypothesis` status
- Golden fixtures migrated (MD includes attribution scores + shadow)
- Lab UI: L4 vs Lab-only lane filters, attribution inspector, shadow agree chips
- CLI lane counts; `artifacts/runs/` persist path

## Validation

```bash
cd consumers/stamped-l3-eval && python3 -m pytest -q
# 14 passed
```

## Outstanding

- Live core attach must export schema 1.1.0 (seed_demo updated in stamped-l3-core)
- NILM-lite signature shadow deferred P2 (ADR-016)

## What you learned

- **Concept:** Delivery lane separates trust path (L4) from discovery path (Lab) without widening emit gates
- **Pattern:** Mirror emitted into Lab; never silently `continue` on suppress
- **Trade-off:** Observation-only promotion preserves semver/golden discipline vs ad-hoc promote UI
