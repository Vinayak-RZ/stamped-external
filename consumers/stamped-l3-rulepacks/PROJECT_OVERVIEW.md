# Project overview — stamped-l3-rulepacks

## Purpose

Semver YAML/JSON **physics and optimization rulepack catalog** for Stamped L3. Declares thresholds, formulas, DISCOM tariff tables, and vertical priors. Consumed by `stamped-l3-core` via `RULEPACK_PATH`.

## System overview

| Axis | Role |
| --- | --- |
| `domain/` | Universal pack per waste / asset class + optimization methods |
| `verticals/` | Industry prior overlays (no new Finding categories) |
| `tariffs/` | DISCOM decision tables |

Findings cite `rulepack://domain/{pack}/{semver}#{rule_id}`. Engines stay in core.

## High-level architecture

Artifact repo only (ADR-012). Merge order into core: domain → vertical → plant params (external) → tariff ₹.

## Constraints

- No engine / ML / SCADA code in this repo
- Every Finding `category` from platform `finding.json` must map to ≥1 rule
- Goldens under `fixtures/golden/`; schema CI via pytest
