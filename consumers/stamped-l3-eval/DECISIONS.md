# Decisions — stamped-l3-eval

## D001 — Lab UI lives in eval

- **Selected:** Internal Lab UI under `stamped-l3-eval/ui`
- **Not:** L6 customer dashboard or core runtime UI
- **Rationale:** ADR-012 eval role = corpus, gates, and engineer forensics

## D002 — RunArtifact is SSOT for UI

- **Selected:** UI renders only `run-artifact.v1` (or live payload of same shape)
- **Rationale:** Consistency; no client-side detectors

## D003 — Offline + optional live

- **Selected:** Offline artifacts default; `CORE_LAB_URL` attach for live
- **Rationale:** Reproducible debug + present-tense inspection

## D004 — P0 auth = shared secret

- **Selected:** `LAB_SHARED_SECRET` middleware
- **Defer:** OIDC to P2

## D005 — Dual-lane Lab retention (ADR-015)

- **Selected:** Required `delivery` ∈ {`l4`,`lab_only`} status includes `hypothesis`
- **UI:** Primary lane filter; status secondary
- **Rationale:** Retention without polluting L4 outbox

## D006 — Attribution scores in inspector

- **Selected:** Render attribution `scores` + shadow agree/disagree chips
- **Rationale:** Explainability path is co-start ranking (ADR-016 shadows Lab-only)
