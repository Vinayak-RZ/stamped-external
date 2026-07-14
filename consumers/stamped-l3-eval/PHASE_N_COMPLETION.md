# Phase N — Eval Lab UI

## Completed

- RunArtifact v1 + goldens
- CLI `artifact show` / `lab-run`
- Next.js Lab: Corpus, Window forensic, Detectors, Compare, Live
- `LAB_SHARED_SECRET` gate (middleware + /login)
- Core `lab_export` + `stamped-l3-lab` HTTP
- validate.sh builds UI
- ADR-012 Lab UI note

## What you learned

- Eval Lab renders artifacts only — engines stay in core
- Product-register density beats dashboard chrome for forensics
- Live attach shares the same RunArtifact shape as offline goldens
