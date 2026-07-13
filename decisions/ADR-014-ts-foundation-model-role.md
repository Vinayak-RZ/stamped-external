# ADR-014: Time-series foundation model role

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-13 |
| **Deciders** | Engineering (L3/L4 intelligence plan) |
| **Related** | [L3 spec §3.1](../technical/layers/L3-intelligence-core.md) · [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) |

---

## Context

Time-series foundation models (TimesFM 2.5, Chronos, Moirai) offer zero-shot forecasting. Team interest in using them to compete with Zerowatt's predictive capabilities must not compromise Stamped's **M&V auditability** (TOW-P baselines, deterministic tariff, IPMVP narratives).

---

## Decision

| Role | Engine of record | Foundation model |
| --- | --- | --- |
| M&V baseline / SEC | TOW-P regression | **Never** |
| MD exceedance forecast | LightGBM quantile | Shadow challenger P2 only |
| Anomaly bands | EWMA/CUSUM on TOW-P residuals | Optional band challenger |
| Cold-start onboarding | Fleet hierarchical priors | Zero-shot dashboard bands until 90d data |
| PdM trend enrichment | Matrix profile + electrical proxies | Trend forecast hint only |

**TimesFM 2.5 + XReg** is the designated shadow challenger (Apache-2.0, covariate support). Optional dependency: `timesfm>=2.0.2` in `stamped-l3-core[challenger]` — not P0 install.

---

## Promotion gates (P2)

TimesFM may become **challenger-primary** for MD exceedance only if:

1. Beats seasonal-naive AND LightGBM on pinball loss (≥3 pilot plants)
2. Does not increase finding false-positive rate on golden corpus
3. Runs within batch latency SLO (CPU single-series acceptable)

Never promoted to M&V citation path or prescription `impact` without new ADR.

---

## Hosting default

- **Pilot:** self-hosted CPU batch inference
- **Fleet meta-analysis:** Vertex/BQ ML only if ADR-014 promotion + egress policy approved

---

## Alternatives considered

| Option | Rejected because |
| --- | --- |
| TimesFM as M&V baseline | Black-box; fails ASHRAE G14 audit |
| No foundation model | Misses cold-start and challenger value |
| Chronos primary | Eval deferred; TimesFM XReg fits covariate need |
