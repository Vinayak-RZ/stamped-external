---
type: Decision Defense / Engine Guide
title: "L3 — Attribution Explainability"
description: >-
  How Stamped attributes MD / demand spikes: deterministic co-start + energy-graph
  ranking; quality grade; why not SHAP/NILM; dual-lane + shadow challengers.
tags: [stamped-energy, l3, attribution, explainability]
timestamp: "2026-07-15T00:00:00Z"
---

# L3 — Attribution Explainability

> **Of-record explainability for demand spikes is not SHAP, NILM, or an LLM.**  
> It is **feeder/event ranking on the energy graph** — printable, one sentence to a plant EE.  
> Siblings: [L3 intelligence core §3.4](L3-intelligence-core.md) · [Defense brief](L3-decision-defense-brief.md) · [ADR-015](../../decisions/ADR-015-l3-dual-lane-lab-detections.md) · [ADR-016](../../decisions/ADR-016-attribution-shadow-challengers.md) · Rulepack [`costart_window`](../../consumers/stamped-l3-rulepacks/domain/attribution/1.0.0/rules/costart_window.yaml)

---

## 1. Role

When the incomer sets (or nearly sets) a billing MD peak, plant staff ask: **which assets co-started?** Attribution answers that with a ranked list and a formula they can check.

It feeds:

- MD post-mortem Findings (`md_overlap`, stagger prescriptions)
- Lab forensics (top-1 + runners-up + shadows)
- L4 language (LLM may phrase; it does **not** invent the ranked cause)

---

## 2. Of-record pipeline

1. **Event/ramp detection** on feeder tags → startup catalogue `(asset, t₀, ramp_kw, duration)` in L2 features  
2. At spike time **T**, collect events in ±`costart_minutes` (default **3**)  
3. Traverse energy graph (`feeds` / `shares_electrical_bus`), `hops ≤ max_hops` (default **4**)  
4. Rank: `score = ramp_kw × proximity`, `proximity = 1/(1+hops)`; tie-break `|corr(feeder_Δ, incomer_Δ)|`  
5. **One-sentence form:** “Asset X ramped Y kW within Z minutes of the peak window at hop distance H.”

| Symbol | Definition |
| --- | --- |
| `hops(asset)` | Shortest undirected path length to spike meter |
| `proximity` | `1 / (1 + hops)` |
| `ramp_kw` | Startup ramp magnitude from catalogue |
| `score` | `ramp_kw × proximity` |

Rulepack binding: `rulepack://attribution/{semver}#costart_window` (defaults in YAML).

---

## 3. Quality grade (honest)

| Context | Grade | Why |
| --- | --- | --- |
| **Path A** — feeders + graph | **Strong / product-ready** | Ranking over metered candidates is the industrial substitute for full NILM; improves with Path A depth |
| **Path B** — incomer-only, 15-min | **Weak–moderate** | Overlapping ramps alias in DISCOM window; thin candidates |
| Vs full industrial NILM as primary | **Prefer current** | Literature: scarce labels, noise, continuous/VFD loads; single-meter industrial disaggregation called unrealistic (HIPE / Energy Informatics 2025) |
| Vs SHAP for “who caused the spike?” | **SHAP is not a competitor** | SHAP explains model *features*, not feeder assets |

Eval targets `[~]`: top-1 cause ≥70%, top-3 ≥90% on adjudicated spikes; cold-start confidence prior **0.60** (cap 0.80 until calibrated).

---

## 4. Why not SHAP / full NILM

### SHAP

- Built for **feature attribution** of a learned model (hour, temp, lag…), not electrical asset cause.  
- Expensive / often **unstable** on time series (background-set sensitivity).  
- Does not produce M&V-grade or plant-EE sentences.  
- Optional later: LightGBM **MD forecast** introspection — **not** attribution shadow ([ADR-016](../../decisions/ADR-016-attribution-shadow-challengers.md)).

### Full industrial NILM

- 2024 systematic review: industrial NILM still open on overlapping continuous loads, labels, multi-phase signals.  
- Residential toolkits (e.g. NILMTK) map poorly to 500 kW furnaces.  
- HIPE study: *disaggregation with only one metering point is unrealistic* — submetering needed at plant scale.  
- Stamped Path A **is** progressive submetering; attribution uses it directly.

NILM-lite (event/transient signature match) may appear as **P2 Lab-only shadow** if 1-min incomer + labelled spikes exist — never of-record without a new ADR.

---

## 5. Dual-lane policy (ADR-015)

| Outcome | `delivery` | `status` | Outbox? |
| --- | --- | --- | --- |
| Top-1 passes suppression + confidence floor | `l4` | `emitted` | Yes |
| Runner-up ranks (2..N) | `lab_only` | `hypothesis` (or suppressed if gate hit) | No |
| Weak score margin / incomplete graph | `lab_only` | `hypothesis` | No |
| Calendar / DQ / startup suppress | `lab_only` | `suppressed` | No |
| Shadow challengers (ADR-016) | `lab_only` | `shadow_only` | No |

**Never silently drop** runner-ups — they are the discovery signal dual-lane exists to keep.

### Lab `scores` shape (of-record)

```json
{
  "ramp_kw": 180,
  "hops": 1,
  "proximity": 0.5,
  "score": 90,
  "corr_abs": 0.82,
  "rank": 1,
  "spike_ts": "2026-06-15T06:00:00Z",
  "event_ts": "2026-06-15T05:58:30Z"
}
```

Shadow rows add `shadow_method`, `agree_with_primary`, `primary_rank_ref`.

---

## 6. Shadow challengers (ADR-016)

| Shadow | What it stress-tests |
| --- | --- |
| Ranking ablations (corr-primary, flat proximity, ±5 min) | Formula sensitivity |
| STUMPY motif concordance | Shape agreement with known startups |
| NILM-lite signatures (P2 gated) | Incomer-only hints when high-res + labels exist |

All shadows → Lab-only. Promotion to of-record requires new ADR + multi-plant evidence.

---

## 7. Worked example

Spike at incomer 06:00, CMD risk. Catalogue: Furnace-A ramp 220 kW @ 05:58 (hops=1), Compressor-2 ramp 40 kW @ 05:59 (hops=2), AHU-1 ramp 15 kW @ 05:45 (outside ±3 min → excluded).

- Furnace-A: `220 × 0.5 = 110`  
- Compressor-2: `40 × 1/3 ≈ 13.3`  

**Emit (L4):** Furnace-A top-1.  
**Lab-only:** Compressor-2 as `hypothesis` rank 2; shadows re-rank / motif-check.

Sentence: “Furnace-A ramped 220 kW one hop from the incomer two minutes before the peak window.”

---

## 8. Debate card

**Attack:** *Use NILM/SHAP so we don’t need feeders.*  
**Answer:** Single-meter industrial NILM is not product-ready; SHAP does not name feeders. We invest in Path A meters and printable ranking — shadows test disagreement without polluting L4.

**Attack:** *Top-1 only loses savings.*  
**Answer:** Runner-ups stay in Lab (`lab_only`). L4 stays precision-first; discovery retained ([ADR-015](../../decisions/ADR-015-l3-dual-lane-lab-detections.md)).

---

## 9. Source map

- L3 §3.4 attribution + §4.1 decision table  
- Rulepack `domain/attribution/.../costart_window.yaml`  
- ADR-015 dual-lane · ADR-016 shadows  
- RSER 2024 industrial NILM review · Energy Informatics 2025 HIPE active learning · event-based industrial NILM (2025) · energy XAI/SHAP reviews  
