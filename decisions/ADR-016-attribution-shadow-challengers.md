# ADR-016: Attribution shadow challengers

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-15 |
| **Deciders** | Engineering (L3 attribution / Lab shadows) |
| **Related** | [ADR-015](ADR-015-l3-dual-lane-lab-detections.md) · [ADR-014](ADR-014-ts-foundation-model-role.md) · [L3 §3.4](../technical/layers/L3-intelligence-core.md) · [L3-attribution-explainability.md](../technical/layers/L3-attribution-explainability.md) |

---

## Context

Of-record MD attribution is deterministic graph co-start ranking (`score = ramp_kw × proximity`). Team interest in SHAP / full industrial NILM as explainers must not displace auditability. Literature (2024–2025) still finds single-meter industrial NILM unrealistic; SHAP answers feature importance, not asset spike cause.

---

## Decision

| Role | Method | Lane |
| --- | --- | --- |
| **Of-record** | Ramp/changepoint + graph co-start + `ramp_kw × 1/(1+hops)` (+ corr tie-break) | `delivery=l4` when gated emit |
| **Shadow A** | Ranking ablations (corr-primary, flat proximity, ±5 min window) | `lab_only` / `shadow_only` |
| **Shadow B** | STUMPY motif concordance vs startup catalogue | `lab_only` / `shadow_only` |
| **Deferred** | Event NILM-lite signature match | P2: requires 1-min incomer + labelled spikes; Lab-only until new ADR |
| **Rejected** | SHAP as attribution shadow | Wrong question (features ≠ assets) |
| **Rejected** | Full deep NILM as P0/P1 shadow or of-record | Label/ops/incomer limitations |

Shadow rows carry `scores.shadow_method` and `scores.agree_with_primary`. They **never** stage to the L4 outbox.

### Promotion (unlikely to of-record)

Shadows may become challenger-primary for *ranking only* if:

1. Agree-rate / top-1 lift vs adjudicated spikes on ≥3 plants
2. No increase in Finding FP rate on golden corpus
3. New ADR to change of-record formula

---

## Consequences

- Lab Compare shows primary vs shadow agree chips
- Eval goldens include at least one attribution shadow row
- Docs: [L3-attribution-explainability.md](../technical/layers/L3-attribution-explainability.md)

---

## Alternatives considered

| Option | Rejected because |
| --- | --- |
| SHAP on GBM residual model | Explains covariates, not feeder cause; unstable on series |
| Full NILM transformer shadow in P0 | Noise + no labels; floods Lab |
| No shadows | Loses disagreement evidence that dual-lane was meant to retain |
