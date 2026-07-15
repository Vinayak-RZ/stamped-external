# Authoring a rulepack

## Add a rule (do not touch core)

1. Pick pack under `domain/<pack>/x.y.z/` (or create new semver).
2. Add `rules/<rule_id>.yaml` with required fields (see `schemas/rule-file.schema.json`).
3. Register in `manifest.yaml` `rules[]` with `id`, `file`, `category`.
4. Add golden under `fixtures/golden/` with `expected_finding.category` + `expected_rule_id`.
5. Regenerate `schemas/catalog_index.json` (or edit finding_category_coverage).
6. `pytest` green; bump pack semver on behaviour change (not docs-only).

## URI form

Findings cite: `rulepack://{pack}/{semver}#{rule_id}`

Example: `rulepack://furnace/1.0.0#furnace_holding_detect`

## Attribution explainability

MD / co-start ranking formulas and dual-lane / shadow policy live in the platform pack:

[`technical/layers/L3-attribution-explainability.md`](../../../technical/layers/L3-attribution-explainability.md) · pack defaults: `domain/attribution/*/rules/costart_window.yaml`

## Merge order into core

1. Load domain pack for category  
2. Overlay `verticals/<id>/params.yaml` defaults (thresholds only)  
3. Apply plant `params.yaml` (outside this repo)  
4. Resolve tariff tables from `tariffs/<discom>/`

## Forbidden

- Python engine code in this repo  
- Writing to SCADA / plant actuators  
- Black-box savings without formula_ref  
- Changing Finding enum without platform contract bump  
