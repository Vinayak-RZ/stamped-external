# stamped-l3-eval — Internal Lab UI (Nawab)

> Branch `cursor/l3-eval-lab-ui-272a` · Authority ADR-012 · User locks: Next.js Lab + offline artifacts + live attach

## §0 Metadata

| Field | Value |
| --- | --- |
| Mode | feature |
| Stack | Python CLI + Next.js App Router + RunArtifact JSON |
| Estimated commits | 22–30 |

## §1 Objective

Internal Lab UI to inspect every engine/rule/ML detection (emitted, suppressed, shadow) for corpus windows; offline-first with optional live core attach.

## §7 Phases

| Phase | Exit |
| --- | --- |
| 0 | PRODUCT/DESIGN + README + this plan |
| A | run-artifact.v1 + golden fixtures |
| B | CLI lab-run / artifact show |
| C | Next.js Lab offline views |
| D | Core lab export |
| E | Live attach |
| N | Auth + validate.sh + PR |

## §18 Protocol

Ponytail on edits · Impeccable product register · UI never invents detections.
