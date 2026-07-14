# stamped-l3-rulepacks — Nawab Implementation Plan

> Artifact repo for semver physics/threshold packs · **ADR-012** · Branch `cursor/l3-rulepacks-catalog-272a`

## §0 Metadata

| Field | Value |
| --- | --- |
| Mode | project (artifact catalog) |
| Stack | YAML packs + pytest |
| Authority | ADR-012 · L3 §3.5 · `contracts/schemas/finding.json` |
| Estimated commits | 18–28 |

## §1 Objective

Authoritative **domain × vertical × tariff** catalog so `stamped-l3-core` loads thresholds via `RULEPACK_PATH` and never embeds furnace/idle/load-management constants.

**In:** YAML manifests, rule files, tariff tables, vertical priors, golden fixtures.  
**Out:** Engine code, TOW-P fits, L4 templates, plant `params.yaml`, SCADA writes.

## §2 Blockers

| Item | Status |
| --- | --- |
| Platform `finding.json` categories frozen | done |
| Core rulepack_loader accepts path/semver | done (sibling) |

## §7 Phases

| Phase | Exit |
| --- | --- |
| 0 | README catalog + this plan + AUTHORING |
| A | Manifest/rule JSON schemas + CI |
| B | incomer + tariff stub + PF/TOD goldens |
| C | All §E optimization rule YAML stubs |
| D | Vertical overlays |
| N | catalog coverage tests green |

## §9 Commit contract

One logical change per commit. Tests in same commit when adding goldens/schemas.

## §18 Protocol

Load ponytail on edits · README via extensive-readme · `pytest` gate before PR.
