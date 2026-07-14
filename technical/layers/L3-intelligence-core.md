---
type: Product Architecture
title: "L3 — Intelligence Core (Models & Rules)"
description: "Deep research spec for Stamped's Layer 3 numeric engines — baseline/SEC, anomaly, attribution, rules & physics, demand/MD, tariff/PF, source-mix dispatch, waste classifier, per-plant calibration — with model-family recommendations and a full evaluation protocol."
tags: [stamped-energy, technical, layer-spec]
timestamp: "2026-07-09T00:00:00Z"
---

# L3 — Intelligence Core (Models & Rules)

*Research document · July 2026 · Author role: senior ML engineer, industrial time-series*

> **Honesty convention:** `[~]` approximate / benchmark-derived · `[!]` evolving — verify before customer-facing claims.
>
> **Siblings:** [L2 — Universal Repository](L2-universal-repository.md) · [L4 — Knowledge & Reasoning](L4-knowledge-and-reasoning.md) · [Evaluation & Quality](../cross-cutting/04-evaluation-and-quality.md) · [Technical architecture v2](../02-technical-architecture.md) (canonical) · Finding contract: [`contracts/schemas/finding.json`](../../contracts/schemas/finding.json)
>
> **Defend these decisions:** [L3 — Decision defense brief](L3-decision-defense-brief.md) (rules vs ML vs LLM, engine cards, ADR-012/014, debate drills)

L3 is the **numeric intelligence layer** of the Stamped stack: it converts normalised telemetry, bills, and production context from [L2](L2-universal-repository.md) into **structured, category-tagged finding objects** that [L4](L4-knowledge-and-reasoning.md) turns into prescriptions. L3 never emits prose. It emits numbers, evidence windows, confidence, and waste-category tags.

Design constraints that shaped every recommendation below:

- **Data reality:** 3–24 months of history per plant, 15-min granularity typical (1-min at incomer sometimes), production data patchy or delayed.
- **Interpretability is mandatory.** Findings go to plant electrical engineers (who will challenge them) and into IPMVP-style M&V narratives (which auditors will challenge). Any model whose output cannot be explained in one sentence to a plant engineer is disqualified as a primary engine.
- **Python stack**, cloud-primary, small ML team. Prefer boring, proven, low-ops model families.
- **Read-only.** L3 recommends; it never actuates.

---

## 1. Role in the 15–20% target

The 15–20% bill-reduction claim is **not one model's output** — it is the sum of closed prescriptions across six waste categories, each served by a specific combination of L3 engines (per [technical architecture §3.1](../02-technical-architecture.md)).

### 1.1 Engines → waste categories → savings bands

| # | Waste category | Primary L3 engines | Detection mechanism | Typical bill impact `[~]` |
|---|---|---|---|---|
| 1 | **Power quality & MD** | Demand & MD engine · Tariff & PF engine · Attribution | MD histogram vs CMD, spike post-mortem, co-start attribution, PF slab math | **3–8%** of bill (15–25% of MD line) |
| 2 | **Furnaces & process heat** | Baseline & SEC · Rules (holding/setback) · Waste classifier | SEC residual vs production-normalised band; holding kW in non-production windows | **2–5%** |
| 3 | **Idle & auxiliary loads** | Waste classifier · Anomaly · Baseline (shift bands) | Calendar-mismatch load (kW high, production = 0); off-shift baseload drift | **2–4%** |
| 4 | **Compressed air** | Rules (specific-power drift) · Anomaly · Attribution | kW per unit air proxy trending up at stable pressure band; unload cycling | **1–3%** |
| 5 | **HVAC / chillers** | Baseline (weather covariates) · COP-proxy rules · Tariff (TOD) | COP proxy degradation; off-shift AHU/chiller runtime; ambient-normalised excess | **1–3%** |
| 6 | **Source mix & scheduling** | Source-mix dispatch · Rules · Tariff | TOD exposure vs available solar/WHR/DG; dispatch simulation | **1–4%** |

Three structural implications for L3:

1. **No engine needs to be heroic.** Each category needs a detector good enough to find the top 2–3 recurring instances per plant per month with high precision. A 3% category closed reliably beats a 6% category detected at 40% precision that destroys trust.
2. **Precision > recall, everywhere.** The scarce resource is plant-side attention (supervisor actions per week). A false prescription costs more than a missed one — it burns the credibility that closure depends on (closure-rate target ≥60% on high-priority Rx `[!]`).
3. **The bill is the ground truth.** Every engine's ₹ estimate must decompose onto a DISCOM bill line (energy, demand, PF penalty, TOD) so [L5 M&V](L5-closure-and-verification.md) can reconcile it. This is why the tariff engine is deterministic and why baselines must be M&V-grade, not merely predictive.

### 1.2 What L3 must NOT do

- No generic "energy is high" alerts — findings without a category tag and an asset scope are blocked at the L3/L4 boundary.
- No black-box savings numbers — every `estimated_monthly_inr` carries the formula path (baseline delta × hours × tariff line rate).
- No autonomous control recommendations that violate the read-only stance.

---

## 2. Requirements from the architecture

### 2.1 Inputs from L2

L3 consumes only from the [Universal Repository](L2-universal-repository.md) — never raw plant protocols. Contracts it depends on:

| L2 store | What L3 reads | Granularity / freshness needed |
|---|---|---|
| Time-series store | kW, kVA, kWh, PF, kVArh per measurement point; quality flags | 15-min standard; 1-min incomer where available; ≤15 min lag for MD engine `[!]` |
| Energy graph | Plant → system → equipment → meter point; edges `feeds`, `shares_electrical_bus`, `starts_with` | On-change; attribution traverses ≤2 hops |
| Commercial context | TariffContract (CMD, MD rate, TOD windows, PF slabs), ShiftCalendar, SourceMix | On-change; tariff versioned by effective date |
| Production context | Batch/tonnage/parts per time window, SKU mix | Daily acceptable; SEC engine must tolerate 1–7 day lag and gaps |
| Feature store | Rolling kW stats, SEC, load factor, startup-event catalogue, non-production-energy ratio | Refreshed on schedule + on event |
| Baseline store | L3 writes baselines here; M&V (L5) reads the **locked** versions | Versioned, immutable once cited by a prescription |

**Data-quality preconditions** (enforced at L2, asserted at L3): stale-tag detection, gap-fill policy with `estimated` quality flags, and outlier flags. Every engine must degrade gracefully — e.g. baseline falls back from production-normalised to calendar-only when production tags go stale — and must record which mode it ran in, because M&V defensibility depends on it.

### 2.2 Output contract: the finding object

All nine engines emit the same schema. **Canonical:** [`contracts/schemas/finding.json`](../../contracts/schemas/finding.json) · summary in [technical architecture §5.2](../02-technical-architecture.md#52-l3--l4-finding). This is the entire interface to [L4](L4-knowledge-and-reasoning.md):

```json
{
  "schema_version": "1.0.0",
  "finding_id": "f-2026-07-08-0042",
  "org_id": "org_acme",
  "plant_id": "plant_ghaziabad_1",
  "category": "compressor_sp_drift",
  "waste_category": 4,
  "assets": ["compressor-2"],
  "evidence": {
    "metric": "specific_power_kw_per_nm3min",
    "baseline_value": 5.8,
    "actual_value": 6.7,
    "window": "2026-06-15T00:00:00Z/2026-07-05T00:00:00Z",
    "baseline_id": "bl-c2-2026w22",
    "baseline_band": [5.5, 6.1],
    "supporting_tags": ["compressor-2/active_power", "compressor-2/line_pressure"],
    "rule_version": "1.4.2"
  },
  "confidence": 0.91,
  "estimated_monthly_kwh": 12000,
  "estimated_monthly_inr": 84000,
  "inr_decomposition": {"bill_line": "energy_kvah", "rate_ref": "tariff-upcl-hv2-2026"},
  "urgency": "high",
  "engine": "rules.compressor_sp_drift",
  "engine_version": "1.4.2",
  "rule_or_model_ref": "rulepack://compressor/1.4.2#sp_drift",
  "suppressions_checked": ["startup_window", "production_mix_change"],
  "dedupe_key": "sha256:a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
}
```

**Field names (locked):** use `baseline_value` / `actual_value` — not `baseline` / `actual`. `plant_id` and `org_id` are required. Top-level `engine` + `engine_version` + `rule_or_model_ref` identify the producer; optional `evidence.model_version` / `evidence.rule_version` version the cited baseline/rule artefacts.

Contract rules that matter for L3 design:

1. **`engine` + `engine_version` + `rule_or_model_ref` are mandatory** — M&V cites them; the model registry (§5.6) must be able to reproduce any historical finding.
2. **`confidence` is calibrated, not cosmetic** — it feeds the L4 ranker (`score = inr × confidence / effort`), so per-engine calibration curves are part of the evaluation protocol (§5). Cold-start defaults: §5.2.
3. **`evidence.baseline_id` points to an immutable baseline version** in the L2 baseline store when the finding cites a baseline (required for M&V-eligible ₹).
4. **`dedupe_key`** = sha256 of (category, sorted assets, window) — L3 emits at most one open finding per key; persistence escalates severity instead of re-emitting.
5. Findings are **idempotent and replayable**: same inputs + same engine version ⇒ same finding. This makes backtesting (§5.4) and audit possible.

---

## 3. Researched landscape per engine

### 3.1 Baseline & SEC models

The baseline engine is the keystone: anomaly detection, idle-load detection, SEC drift, and M&V all consume its expected-band output. The research question is which regression family gives **M&V-grade accuracy with interpretability** on 3–24 months of 15-min industrial data.

**a) The M&V regression tradition (linear models with engineered covariates).**
The energy-efficiency industry has converged on transparent regression for baselines because savings claims must survive audit. [IPMVP](https://evo-world.org/en/products-services-mainmenu-en/protocols/ipmvp) [22] and [ASHRAE Guideline 14](https://www.eeperformance.org/uploads/8/6/5/0/8650231/ashrae_guideline_14-2002_measurement_of_energy_and_demand_saving.pdf) [7] both frame the baseline as a regression of energy on independent variables (weather, production, occupancy), evaluated on CV(RMSE) and NMBE (§5.1). For industrial plants the canonical independent variable is **production output**, giving the classic `kWh = β₀ + β₁·units + β₂·HDD/CDD + calendar terms` form — β₀ is the load-independent (fixed) energy, β₁ the marginal energy per unit, both directly meaningful to a plant engineer.

**b) TOWT — time-of-week & temperature (LBNL / CalTRACK / OpenDSM). Researched deeply, as required.**
TOWT was introduced by Price ([LBNL-3713E, 2010](https://eta-publications.lbl.gov/sites/default/files/LBNL-3713E.pdf)) [1] and operationalised by Mathieu et al. ([LBNL-4944E, 2011](https://eta-publications.lbl.gov/sites/default/files/LBNL-4944E.pdf)) [2]. Mechanics, per the [CalTRACK methods §3.7–3.8](http://docs.caltrack.org/en/latest/methods.html) [3] and the [nmecr implementation](https://kw-labs.github.io/nmecr/) [6]:

- The week is divided into **168 hourly time-of-week indicator variables** (nmecr also supports a 672 × 15-min variant [6]) — one coefficient per hour-of-week captures the recurring operating schedule *without needing an occupancy/shift feed*.
- Temperature enters as a **piecewise-linear continuous function** over ~6 temperature bins, so non-linear thermal response is captured while remaining a linear regression.
- Data is segmented into **occupied / unoccupied (high-load / low-load) modes** using the residuals of a preliminary HDD/CDD regression — times-of-week that are under-predicted ≥65% of the time are labelled occupied [3][6]. This is an automated shift-discovery mechanism.
- Weighted least squares fits; in LBNL's M&V testing it equalled or outperformed other industry-standard models for annual prediction [1][25], and it was validated on the EVO Advanced M&V testing portal's 367-building dataset [23].
- Open implementations: [RMV2.0](https://github.com/LBNL-ETA/RMV2.0) (R, LBNL) [26], [nmecr](https://kw-labs.github.io/nmecr/) (R, kW Engineering) [6], and [OpenDSM, formerly OpenEEmeter](https://github.com/opendsm/opendsm) (Python, LF Energy) [4]. OpenDSM's current hourly model has evolved past pure TOWT into an **elastic-net regression** where each hour is informed by all 24 hours of the day (capturing thermal lag), with day-type clustering to avoid overfitting month × weekday combinations [5]. Its billing/daily models descend from PRISM piecewise temperature regression [4]. The US DOE approved OpenEEmeter for the IRA HOMES programme — a strong signal of regulatory acceptance of this model class [24].

**Why TOWT matters for Stamped, and where it must be adapted `[~]`:** TOWT is building-centric — temperature is the dominant driver. In Indian manufacturing the dominant driver is **production schedule**, and temperature matters mainly for HVAC/chiller feeders. But the *structure* transfers directly: time-of-week dummies are exactly a data-driven shift calendar, and the occupied/unoccupied segmentation is exactly production/non-production discovery when the shift calendar is missing or wrong (common). The adaptation is to swap/augment the temperature term with production covariates: **"time-of-week & production" (TOW-P)** — TOW dummies + piecewise-linear terms in production rate + optional temperature term for weather-sensitive feeders. This keeps the WLS/elastic-net machinery, the CalTRACK sufficiency rules, and the M&V pedigree.

**c) GAMs (pyGAM).** Generalized additive models fit smooth non-linear terms per covariate while remaining decomposable — each feature's partial effect can be plotted and explained ([pyGAM](https://pygam.readthedocs.io/en/latest/) [16]). A GAM `kWh ~ s(production) + s(ambient) + f(hour_of_week)` is effectively a smoothed TOWT and is a good mid-step when piecewise-linear underfits. Cost: more hyperparameters than OLS, less standard in M&V audits (auditors know linear regression; they don't know spline penalties).

**d) Gradient boosting (LightGBM/XGBoost) and random forest.** GBMs are the strongest tabular predictors — [LightGBM](https://lightgbm.readthedocs.io/) [17] dominated the M5 forecasting competition and beats deep models on hourly load data ([Greek DSO study, Energies 2025: LightGBM best MAPE 1.20% vs CNN/LSTM/GRU variants](https://www.mdpi.com/1996-1073/18/19/5060)) [11]. Random forest is strictly dominated by GBMs on accuracy at this data shape and offers no interpretability advantage. The problem: a GBM baseline is not directly auditable — SHAP explanations approximate but do not constitute a regression coefficient an M&V reviewer can verify. Verdict: GBMs are **challenger models and residual analysers**, not the M&V baseline of record.

**e) Prophet / STL decomposition.** [Prophet](https://facebook.github.io/prophet/) [18] and STL decompose trend + weekly/daily seasonality and are fast to stand up, but they model time only — no production covariates natively (Prophet regressors are linear add-ons), and Prophet's changepoint machinery is designed for growth trends, not plant regimes. Useful for week-1 cold-start visual bands and for detecting shift-seasonality structure; not the baseline of record. STL residuals are, however, a fine input to anomaly detection.

**f) Quantile regression for bands.** Expected *bands* (P10–P90), not point estimates, are what the anomaly engine and dashboards consume. Options: quantile loss on linear models (statsmodels), GBM quantile objective (LightGBM `objective=quantile`), or empirical residual quantiles per time-of-week cell. Pinball loss is the standard evaluation metric (§5.3).

**g) Cold-start with fleet priors.** With <4 weeks of data, a per-plant regression is unstable. Practice: initialise from **vertical fleet priors** (published SEC ranges + anonymised fleet aggregates per the architecture's ML-06), run a deliberately wide band, and tighten as weeks accumulate — formalised as Bayesian/hierarchical updating in §3.9.

**h) How M&V-grade requirements constrain model choice.** ASHRAE G14 acceptance: **monthly — NMBE ±5%, CV(RMSE) ≤15%; hourly — NMBE ±10%, CV(RMSE) ≤30%** [7][8][3]. IPMVP's stricter hourly guidance is NMBE ±5% / CV(RMSE) ≤20% [8]. G14's whole-building path also requires ≥12 continuous months of baseline data for its standard path and caps CV(RMSE) at 20% (energy) / 30% (demand) for the no-uncertainty-calculation route [7]. Note the prompt's working numbers ("CVRMSE ≤25% hourly") were tighter than the G14 hourly threshold (30%) — verified figures are used here, and Stamped adopts *internal* targets tighter than G14 (§5.1). The constraint this imposes: **the baseline of record must be a model whose functional form, coefficients, and residual statistics can be printed in an M&V report** — i.e. linear-in-parameters regression. Anything fancier serves detection, not verification.

### 3.2 Anomaly & deviation detection

**a) Residual-based statistical process control (the default).** Compute residual = actual − baseline expectation, then monitor residuals with classical SPC: **EWMA** charts detect small sustained shifts; **CUSUM** accumulates deviation and is optimal for detecting a persistent mean shift of known size; Shewhart/z-score catches large point excursions. These methods are interpretable ("consumption has run 12% above the production-adjusted baseline for 6 days"), have known false-alarm rates (ARL theory), and are cheap. This is the pattern the architecture already sketches (EWMA on residuals) and matches what M&V practitioners do with baseline residuals.

**b) Isolation Forest.** Liu et al.'s isolation forest [20] is an unsupervised outlier detector on feature vectors (not raw series) — appropriate for multivariate "this shift's feature vector (kW stats, PF, SEC, load factor) is unusual" detection. Fast, few parameters, but explanations are weak ("isolated early in random trees") — usable as a *secondary* detector whose findings must be re-expressed via the features that drove them.

**c) Autoencoders / deep anomaly detection.** High capacity, but require more data than 3–24 months of one plant provides, drift with regime changes, and produce reconstruction-error scores that cannot be explained to a plant engineer. See (e).

**d) Matrix Profile (STUMPY).** The matrix profile computes, for every subsequence, the z-normalised distance to its nearest neighbour ([STUMPY](https://github.com/stumpy-dev/stumpy) [10]); maxima are **discords** (anomalous shapes — e.g. a startup ramp that looks like no other startup), minima are motifs (recurring patterns — useful for discovering startup signatures for the attribution engine). Exact, training-free, single-parameter (window size), and intuitive [10]. Good fit for shape-level anomalies that residual charts miss, and for building the startup-event catalogue.

**e) Why simple methods usually win here — verified against literature.** Wu & Keogh ([IEEE TKDE 2021 / ICDE 2022](https://wu.renjie.im/research/anomaly-benchmarks-are-flawed/ICDE2022_TSAD.pdf)) [9] showed the standard anomaly benchmarks (Yahoo, Numenta, NASA, OMNI) suffer triviality, unrealistic anomaly density, mislabelled ground truth, and run-to-failure bias — **86.1% of the Yahoo benchmark is solvable with a one-line rule** — and state they are "not aware of a single paper that presents forceful reproducible evidence that deep learning outperforms much simpler methods" for anomaly detection [9]. For Stamped the practical conclusion is stronger still: our anomalies are mostly *known-physics deviations from a good baseline* (holding load present, SP drifted, PF slipped), so the intelligence belongs in the **baseline and the suppression logic**, not in an exotic detector.

**f) Contextual suppression is where the real engineering is.** False-positive sources at a plant: startup/shutdown transients, production-mix changes, planned maintenance, monsoon/ambient swings, DISCOM supply events. Each engine must check a shared suppression service: startup windows (per asset class, default 90 s–15 min), production-mix-change windows (SKU share moves > threshold), maintenance calendar, and data-quality windows (gap-filled data never triggers anomalies). Suppressions applied are recorded on the finding (`suppressions_checked`) for auditability.

### 3.3 MD forecasting & demand engines

**a) The deterministic core (not ML).** Most of the MD engine's value needs no forecasting: MD histogram vs CMD (30/60/90-day), per-spike post-mortem cost = f(MD rate, excess kVA, billing-demand floor — e.g. UP's `max(recorded MD, 75%·CD)` rule), and the **stagger simulator** — a deterministic what-if that time-shifts a candidate asset's measured startup profile and recomputes the 15-/30-min windowed peak. This is arithmetic on real profiles, fully explainable, and is the fastest verified win on Path B.

**b) Short-horizon peak forecasting ("will today set a new MD?").** Literature and competition evidence favour **gradient boosting with lag/calendar features** at this data scale: LightGBM beat CNN/LSTM/GRU/CNN-LSTM on hourly system load across all metrics in a 2025 comparative study (MAPE 1.20%, R² 0.994) [11]; the M5 competition was dominated by LightGBM approaches [11][17]; and mixed steel-plant results for LSTM variants (BiLSTM best in one plant study, but with 59% MAPE on volatile hourly data [29]) confirm deep sequence models are not reliably better on single-site industrial data with limited history. SARIMA/exponential smoothing are reasonable statistical fallbacks for very thin data but handle covariates (day-type, shift, production plan) poorly. Deep models (LSTM/N-BEATS/TFT) need more history than 3–24 months of one plant and add ops burden without demonstrated accuracy gain at this scale — realistic verdict: **LightGBM quantile models per plant, SARIMA fallback, no deep learning in P0–P2** `[~]`.

**c) Formulation.** Predict the **P90 of remaining-day peak kVA** given the morning sequence (intraday hierarchical features: last 2–4 h load shape, day type, shift plan, month, current month-to-date MD). The decision variable is "probability today's peak exceeds current month MD / CMD" — a probabilistic exceedance alert, which tolerates moderate MAPE as long as ranking/calibration is right (evaluated by pinball loss + exceedance precision/recall, §5.3).

### 3.4 Attribution

**a) Event/ramp detection.** Detect load steps/ramps per feeder tag: derivative thresholding on smoothed kW, CUSUM-style step detection, or changepoint methods (e.g. PELT via `ruptures`). Output: startup-event catalogue (asset, t₀, ramp magnitude, duration) in the L2 feature store.

**b) Co-start / graph analysis.** For an incomer MD spike at time T: traverse the energy graph for assets on the shared bus, select events within ±3 min of T, rank by **score = ramp_kw × proximity(asset)**. Cross-correlation of feeder vs incomer deltas over the window ranks partial contributors when scores are close. A recurring co-start pair (e.g. furnace preheat ∩ line ramp every Monday 06:55) is detected by frequency analysis of the event catalogue — this recurrence is what turns a post-mortem into a **schedule prescription**.

**Electrical proximity (locked definition for §5.2 attribution gates):**

| Symbol | Definition |
| --- | --- |
| `hops(asset)` | Shortest undirected path length in the L2 energy graph from `asset` to the spike meter (incomer), following `feeds` / `shares_electrical_bus` edges; max traverse depth 4 |
| `proximity(asset)` | `1 / (1 + hops(asset))` — same-bus (`shares_electrical_bus`, hops = 0 or 1 via bus node) scores higher than feeder two hops away |
| `ramp_kw` | Measured startup ramp magnitude (kW) from the startup-event catalogue |
| `score` | `ramp_kw × proximity(asset)` — rank descending; ties broken by higher `|corr(feeder_Δ, incomer_Δ)|` in the ±3 min window |

Shared-bus boolean alone is **not** used as the proximity term (too coarse for multi-feeder plants). Asset-class weights are deferred P2 — P0/P1 use graph hops only so the formula stays auditable.

**c) NILM / disaggregation — researched, and ruled out as a core engine.** Industrial NILM is an active research field — a 2024 systematic review in *Renewable & Sustainable Energy Reviews* (the first since 2015) catalogues the state of the art and its open problems: industrial loads are continuous and highly variable, events overlap, noise is high, multi-phase and reactive signals are needed, and **labelled industrial datasets are scarce** [12]. Current SOTA is transformer/CNN-LSTM disaggregation validated on single machines in lab-like settings [12]; the standard toolkit [NILMTK](https://github.com/nilmtk/nilmtk) [21] is residential-centric (kettles and fridges, not 500 kW furnaces). Verdict: full NILM at an industrial incomer is a research project, not a product feature. Stamped's substitute is **feeder-level attribution** — the plant already has (or progressively adds) feeder meters, so attribution is a ranking problem over metered candidates plus SCADA state tags, which is tractable, explainable, and improves monotonically with Path A depth. NILM-lite techniques (signature matching of large distinctive loads at a 1-min incomer) may appear in P3 as a hint generator only `[!]`.

### 3.5 Rules & physics engine

**a) Landscape.** Options researched:

| Option | What it is | Fit for Stamped |
|---|---|---|
| [GoRules ZEN](https://github.com/gorules/zen/) [13] | Rust BRE, Python bindings (`zen-engine`), rules as JSON Decision Model files, visual editor, sub-ms in-process eval, git-versionable [13][14] | Good for **tariff/threshold decision tables** (PF slabs, TOD windows, urgency mapping) where non-engineers may eventually edit |
| [durable_rules](https://github.com/jruizgit/rules) [30] | Python forward-chaining / CEP engine | Low maintenance activity; stateful CEP better handled by our stream jobs; avoid |
| Drools-class (JVM BRMS) | Enterprise rule platforms | Wrong ecosystem (JVM), heavy ops; avoid |
| Plain versioned Python + YAML parameter packs | Rules as pure functions over feature-store inputs; thresholds/constants in YAML per vertical/plant | Best for **physics rules** that need real math (regressions over windows, integration, simulation) |

The key research finding is that the industry pattern (see PredCo, Zerowatt learnings in the [master document](../00-stamped-master-document.md) competitive landscape) is **rules-first for explainability with ML underneath** — and that modern practice treats rules as code: JSON/YAML artefacts in git, unit-tested, CI-gated, released with semver [13].

**b) Physics formula inventory per waste category** (the deterministic heart of L3; all constants are per-plant calibratable, §3.9):

| Category | Core formulas | Rule examples |
|---|---|---|
| MD / demand | `billing_demand = max(MD_recorded, floor%·CD)`; window peak = max of 15-/30-min mean kVA; spike ₹ = ΔkVA × MD_rate (+ excess penalty if MD > CD) | co-start > CMD risk; stagger ≥ N min; shed non-critical in TOD peak |
| PF | `kVA = kW/PF`; `kVAr_needed = kW·(tanφ₁ − tanφ₂)`; kVAh uplift ≈ `kWh/PF`; penalty/rebate per slab table | PF < slab threshold sustained → APFC health / load-balance Rx; leading PF at light load → over-compensation Rx |
| Compressed air | specific power = kW / (Nm³/min proxy); screw compressors ≈ 5.5–6.5 kW per Nm³/min at 7 bar `[~]`; unload power ≈ 15–35% of loaded kW `[~]`; leak proxy = off-shift CFM demand | SP drift > x% at stable pressure band → filter/fouling/leak Rx; unload duty > y% → sequencing Rx |
| Furnace / heat | holding energy = holding kW × non-production h; radiation loss ∝ εσA(T⁴−T₀⁴) → setback saving from temperature delta; kWh/ton vs charge weight regression | holding kW in non-production window → setback schedule; preheat earlier than needed vs MES plan |
| Idle loads | idle kW threshold per asset class (e.g. CNC idle 40–70% of run power `[~]`); phantom = kW > floor when production = 0 | machine state = idle ∧ kW > threshold for > N min → sleep/shutdown Rx |
| HVAC / chillers | COP proxy = cooling proxy (ΔT × flow or capacity signal) / kW; ambient-normalised expected kW from baseline | COP proxy degradation > x% → fouling/refrigerant/setpoint Rx `[!]`; AHU runtime outside occupancy |
| Tariff / source mix | TOD exposure = kWh in peak windows × rate delta; CMD right-size = MD histogram P95 + margin vs CD; dispatch value = Σ(source-shiftable kWh × rate delta) | CMD oversized → contract review Rx; solar/WHR under-drawn in peak TOD → dispatch Rx |

**c) Versioning & testing.** Rule packs are semver-versioned per category (`rulepack://compressor/1.4.2`); every finding cites its pack version; packs ship with **golden test datasets** (recorded plant windows + expected findings) run in CI; threshold changes are plant-calibration parameters (§3.9), never code edits.

### 3.6 Demand & MD engine — covered in §3.3

(Deterministic histogram/post-mortem/stagger core + LightGBM quantile exceedance forecast.)

### 3.7 Tariff & PF engine

Fully deterministic — a **tariff calculator, not a model**. It encodes each DISCOM's tariff order (rates, TOD windows, PF slab penalties/rebates, billing-demand floors, kVAh vs kWh billing) as versioned data (ZEN decision tables fit naturally here [13]), maps bill lines to components, and computes the marginal ₹ of any kWh/kVA/PF change on the correct line. Research basis is the repo's own DISCOM knowledge base ([demand charges](/knowledge/energy-efficiency/demand-charges/understanding.md), [power factor](/knowledge/energy-efficiency/power-factor-capacitor-banks/understanding.md)): billing demand floors of 75–85% of CD, PF thresholds of 0.90/0.95 with slab surcharges, kVAh billing making PF an implicit ~18% uplift at PF 0.85 `[~]`. The engine's correctness is testable against parsed historical bills: **reconstruct the bill from telemetry + tariff model to within ±2% before trusting any ₹ estimate** (§5.2).

### 3.8 Source-mix dispatch engine `[P1→P2]`

Given solar/WHR/DG availability, grid TOD windows, and process constraints, recommend a dispatch schedule. Research verdict: at Stamped's scale this is a **small deterministic optimisation** — greedy rules cover most single-site cases (draw cheapest available source per window subject to constraints); a MILP (PuLP/OR-Tools, minutes-scale solve) is warranted only when storage or inter-window coupling appears `[~]`. Competitor precedent: Greenovative's 15-min dispatch governance case study. Not ML; evaluated by simulated-vs-actual ₹ delta.

### 3.9 Waste classifier & per-plant calibration

**Waste classifier:** in P0–P1 this is a **deterministic mapping** — every finding category maps to one of the six waste categories via a maintained table (it is a taxonomy, not a model). A learned classifier only becomes relevant if/when free-form findings appear (P3, unlikely).

**Per-plant calibration & cold-start** — the research-relevant part:

- **Parameter layer, not retraining** ([architecture L3 engines table](../02-technical-architecture.md) — per-plant calibration row): plant config = anomaly sensitivities, SEC norms, idle thresholds, startup suppression windows, shift boundaries. Model *code* is fleet-shared; parameters are per-plant.
- **Hierarchical / partial pooling:** treat plant-level baseline coefficients (e.g. compressor SP, furnace holding kW, idle floors) as draws from a vertical-level prior distribution. With 2 weeks of data the posterior sits near the fleet prior (wide bands); with 6 months it is dominated by plant data. Implementable as closed-form Bayesian linear regression updates or empirical-Bayes shrinkage — no MCMC needed for linear-in-parameters baselines `[~]`. This is the formal version of "fleet priors → tightened bands weeks 4–10".
- **False-positive-driven threshold tuning:** L5 workflow reason codes (rejected / already-fixed / wrong-owner / deferred) flow back as labels. Per plant per category, adjust detection thresholds to hold the precision target (§5.2) — e.g. raise the CUSUM decision interval where rejections cluster. This is the single most valuable learning loop in the system because it directly optimises the closure metric.
- **Guardrail:** calibration may tighten/loosen thresholds within fleet-defined bounds only; it must never silently disable a category (a plant that rejects everything is a customer-success signal, not a tuning signal).

---

## 4. Recommended approach

### 4.1 Model family per engine — decision table

| Engine | Primary (of record) | Challenger / secondary | Explicitly rejected (and why) |
|---|---|---|---|
| **Baseline & SEC** | **TOW-P regression** — time-of-week dummies + piecewise-linear production (+ temperature for HVAC feeders), WLS/elastic-net, per CalTRACK/OpenDSM pattern [3][4][5]; quantile bands from per-cell residuals | LightGBM (accuracy challenger + residual analysis) [17]; pyGAM where piecewise underfits [16]; Prophet/STL for week-1 visual bands [18] | Deep sequence models (data-hungry, unauditable); random forest (dominated by GBM, equally opaque) |
| **Anomaly & deviation** | **EWMA + CUSUM on baseline residuals** (SPC, known false-alarm rates) | Isolation Forest on shift-level feature vectors [20]; Matrix Profile/STUMPY for shape discords & motif mining [10] | Autoencoders/deep AD — no reproducible evidence of superiority [9], unexplainable, data-hungry |
| **Attribution** | **Ramp/changepoint detection + energy-graph co-start + cross-correlation ranking** (deterministic pipeline) | Motif mining (STUMPY) to learn startup signatures [10] | Full industrial NILM — immature, label-starved, residential-toolkit-centric [12][21]; revisit signature-matching hints in P3 `[!]` |
| **Rules & physics** | **Versioned Python rule packs + YAML parameter packs** (physics math) · **ZEN/JDM decision tables** for tariff/threshold logic [13][14] | — | JVM BRMS (ops weight); durable_rules (staleness); LLM-generated rules (belongs in L4, and only as suggestions) |
| **Demand & MD** | **Deterministic**: MD histogram, spike post-mortem, stagger simulator on measured profiles | **LightGBM quantile** intraday peak-exceedance forecast [11][17]; SARIMA fallback for thin data | LSTM/N-BEATS/TFT at single-plant scale — no accuracy case, real ops cost [11][29] |
| **Tariff & PF** | **Deterministic tariff calculator**, tariff orders as versioned data (ZEN tables) | — | Any ML (this must be exact) |
| **Source-mix dispatch** | **Greedy rule solver**; MILP (OR-Tools/PuLP) when storage/coupling appears `[~]` | — | RL / learned dispatch (unjustifiable risk & opacity) |
| **Waste classifier** | **Deterministic category mapping table** | — | Learned classifier (nothing to learn yet) |
| **Per-plant calibration** | **Hierarchical Bayesian shrinkage on baseline params + bounded threshold tuning from Rx feedback** | — | Per-plant model retraining (ops explosion, M&V instability) |

### 4.2 Why this shape is right for Stamped

1. **Everything of record is linear-in-parameters or deterministic** → every finding and every M&V claim can be reproduced by hand from the report. This is the moat for the "bill-verified" positioning, not a limitation.
2. **ML where it pays, in supporting roles:** GBMs sharpen forecasts and challenge baselines; matrix profile mines signatures; isolation forest sweeps for the unknown-unknowns. None of them are load-bearing for a ₹ claim.
3. **One codebase, many plants:** fleet-shared engine code + per-plant parameter packs + hierarchical priors is the only shape that scales to 100+ plants with a small ML team (the Greenovative-style "base model + per-plant parameterisation" pattern noted in [master document](../00-stamped-master-document.md)).
4. **Suppression logic is a first-class shared service** — most anomaly-quality problems will be solved there, not in detector choice.

### 4.3 Baseline engine — concrete design `[~]`

- **Granularities:** 15-min (band for anomaly/idle), shift (SEC + dashboards), daily/monthly (M&V of record).
- **Model per (meter point × granularity):** TOW-P with: 168 TOW dummies (15-min models use 672 or hour-of-week + intra-hour term); production covariates piecewise-linear with 1–2 knots; temperature piecewise term only for weather-sensitive feeders; elastic-net regularisation for stability on short history [5].
- **Occupancy/shift discovery:** CalTRACK-style residual segmentation [3] cross-checked against the declared ShiftCalendar; disagreement itself is a finding (declared vs actual shift pattern — often an idle-load discovery).
- **Data sufficiency gates** (CalTRACK-inspired [3]): minimum 90 days before a baseline is "M&V-eligible"; coverage ≥90% of expected intervals; production covariate used only when ≥70% of windows have production data — else calendar-only mode, flagged.
- **Versioning:** baselines are immutable snapshots (`bl-{asset}-{yyyyWww}`); a prescription locks the version it cited; recalibration produces a new version.
- **Cold-start ladder:** week 0–2 fleet-prior band (wide) → week 2–6 shrinkage posterior → week 6–13 plant-dominated → day 90+ M&V-eligible.

### 4.4 Rules engine — concrete design

```text
rulepacks/
  compressor/1.4.2/
    rules.py          # pure functions: (features, params, tariff) -> findings
    params.default.yaml   # fleet defaults per vertical
    tests/golden/     # recorded windows + expected findings
  tariff/upcl-hv2/2026.1/
    slabs.jdm.json    # ZEN decision tables: PF slabs, TOD windows, floors
plants/{plant_id}/params.yaml   # calibrated overrides (bounded)
```

- Rules are **pure and side-effect-free**: inputs from the feature store, outputs finding objects. The stream/batch runner owns scheduling.
- CI: golden tests must pass per pack release; a params change re-runs the plant's last 90 days in shadow (§5.5) before activation.
- Every finding carries `rulepack@version + params_hash` — full reproducibility for M&V audit.

---

## 5. How this layer is tested and evaluated

This is the mandatory protocol. It has five parts: per-engine metrics & targets, offline backtesting, online monitoring & drift, retraining/rollout governance, and registry/lineage. It feeds the cross-cutting [evaluation doc](../cross-cutting/04-evaluation-and-quality.md).

### 5.1 Baseline & SEC engine

**Metrics:** CV(RMSE), NMBE (per ASHRAE G14 definitions [7][8]), MAPE for dashboards, pinball loss at P10/P50/P90 for bands, plus **band coverage** (empirical % of actuals inside P10–P90; target 80% ± 5).

**Targets** — external floor = verified G14/IPMVP thresholds; internal target = what a credible ₹ claim needs `[~]`:

| Granularity | G14 floor (verified) | Stamped internal target `[~]` | Notes |
|---|---|---|---|
| Monthly | NMBE ±5%, CV(RMSE) ≤15% [7][8] | NMBE ±3%, CV(RMSE) ≤10% | M&V of record; also G14 whole-building path caps 20%/30% (energy/demand) with 12 mo data [7] |
| Daily | — (no G14 daily criterion) | CV(RMSE) ≤20% | working level for Rx sizing |
| Hourly/15-min | NMBE ±10%, CV(RMSE) ≤30% [7][8]; IPMVP stricter: ±5%/20% [8] | CV(RMSE) ≤25%, NMBE ±5% | detection band quality; prompt's "25%" adopted as *internal* hourly target, deliberately tighter than G14's 30% |

**Acceptance rule:** a baseline that fails its granularity's floor is not M&V-eligible — findings may still flow for detection, but ₹ estimates are labelled low-confidence and Rx from it cannot enter verified-savings claims.

### 5.2 Anomaly, rules & attribution engines

- **Precision/recall on labelled incidents.** Label sources: pilot-plant incident logs, engineer adjudication of a weekly sample, and L5 reason codes (accepted/fixed = TP; rejected/not-real = FP). Targets `[~]`: **precision ≥0.75 at P0, ≥0.85 by P2** on high/medium-urgency findings; recall tracked but not gated early (we cannot know all misses; estimate via periodic manual audits of high-cost windows).
- **Alert budget `[!]` unvalidated assumption:** ≤ **N findings/plant/day** (starting hypothesis **N=5**) and ≤2 high-urgency/day — hard cap with ranking overflow to a digest. **Not derived from pilot data**; revisit after the first plant has ≥30 days of delivered prescriptions. Until then treat N as a product knob, not a measured SLO.
- **Attribution accuracy:** for adjudicated MD spikes, top-1 cause correct ≥70%, top-3 ≥90% `[~]` — scoring uses `ramp_kw × proximity` per §3.4(b).
- **Tariff engine correctness:** reconstruct ≥3 historical bills per plant from telemetry + tariff model to **within ±2% per line item** before the plant's ₹ estimates go live; re-run on every tariff-order update.
- **Confidence calibration — cold-start + ongoing:**
  - **Days 0–90 (no labelled closure history):** use **engine prior confidence** (fixed table below) — not uncalibrated detector scores as if they were acceptance probabilities. L4 ranker still uses `score = inr × confidence / effort`, so priors must be conservative.
  - **After ≥20 adjudicated outcomes per engine×plant (or fleet-pooled if plant-thin):** fit reliability curve; switch that engine to **empirical calibration**.
  - **Ongoing:** reliability curves + Brier per engine at least **quarterly** once past cold-start; `confidence` must stay monotone with realised acceptance rate.

  | Engine class | Cold-start prior confidence | Cap until calibrated |
  | --- | --- | --- |
  | Deterministic tariff / PF / MD arithmetic | 0.85 | 0.90 |
  | Rules pack (physics thresholds) | 0.75 | 0.85 |
  | Residual anomaly (EWMA/CUSUM) | 0.55 | 0.75 |
  | Attribution co-start ranking | 0.60 | 0.80 |
  | LightGBM MD exceedance | 0.50 | 0.75 |
  | TimesFM / foundation shadow | **n/a — never ranks Rx** | — |

### 5.3 Forecast engines (MD exceedance)

- **Pinball loss** at P50/P90 (primary, since output is quantiles); MAPE on P50 for legibility (target ≤8% on remaining-day peak by mid-morning `[~]`).
- **Exceedance alert quality:** precision/recall on "new monthly MD set today" events; false-alarm cost is a needless intervention, miss cost is a month of higher billing demand — tune threshold to plant's MD rate.
- **Baseline comparator:** every forecast model must beat seasonal-naive (same weekday last week) and the deterministic persistence rule on rolling backtests, else ship the simple one.

### 5.4 Backtesting design (all engines)

- **Rolling-origin evaluation** for forecasts: expanding window, step = 1 week, horizon = intraday; report metric distributions, not single numbers.
- **Blocked time-series CV** for baselines (contiguous folds with gap/embargo between train and test to prevent leakage via autocorrelation — per Bergmeir & Benítez [19]); never random K-fold on time series.
- **Event replay** for rules/anomaly/attribution: the golden-dataset corpus (recorded plant windows with adjudicated findings) grows every month from pilots; every engine release replays the full corpus in CI; regressions block release.
- **Seasonal coverage caveat:** with 3–24 months history, a backtest may not span a full seasonal cycle — findings sensitive to season (HVAC, monsoon) carry wider bands until 12 months observed `[!]`.

### 5.5 Drift detection, retraining triggers, rollout

- **Input drift:** PSI on key features (load distribution, production mix, PF) monthly vs the baseline-fit window — standard thresholds: <0.1 stable, 0.1–0.25 investigate, >0.25 act [15].
- **Residual drift:** CUSUM on *baseline residual mean* (the baseline monitoring its own health); sustained NMBE breach of §5.1 floors ⇒ recalibration candidate.
- **Structural change (non-routine events, in M&V language):** changepoint detection on the residual series; a detected regime change (new line commissioned, shift added) forces a **new baseline version**, never a silent refit — M&V requires the old version stays frozen.
- **Retraining triggers (any of):** PSI >0.25 on a load-bearing feature · NMBE floor breach 2 consecutive weeks · confirmed non-routine event · scheduled quarterly recalibration.
- **Champion/challenger rollout:** challenger runs in **shadow** on live data ≥2 weeks; promotion gates: beats champion on rolling CV(RMSE)/pinball **and** does not increase finding-level FP rate on replayed corpus **and** band coverage within 80±5. Promotion is a registry stage transition with human approval; previous champion is the instant-rollback slot. Pattern per standard registry-gated practice [15].
- **Kill switch per engine per plant:** ops can freeze an engine's emissions (not its computation) while investigating a quality incident.

### 5.6 Registry & lineage

- **MLflow model registry** [19] (or equivalent) holds every baseline/forecast model version: training window, features, params hash, eval report, git commit. Rule packs live in git with semver; the finding object's `engine_version`/`rule_or_model_ref`/`baseline_id` triple makes every historical finding reproducible.
- **Monthly quality report per plant** (auto-generated): baseline CV(RMSE)/NMBE by meter, findings issued vs accepted vs rejected by category, alert-budget utilisation, drift flags — reviewed in customer-success cadence, feeds threshold calibration (§3.9).

### 5.7 Compute sizing (back-of-envelope)

Aligned to architecture [§16.1](../02-technical-architecture.md) scale: **10s of plants (headroom ~100) · 200–2000 tags/plant**.

| Quantity | Estimate `[~]` | Notes |
| --- | --- | --- |
| Meter points needing a TOW-P baseline | Not every tag — energy/SEC-critical only | Default: **incomer + feeders + process-heat assets** ≈ **5–40 models/plant**, not 2000 |
| Fleet at 30 plants × 20 models | **~600 TOW-P models** | Linear WLS/elastic-net on 15-min × 90–365 d |
| Nightly refit wall-clock (single 4–8 vCPU worker) | **≪ 1 h** for 600 models | One plant's TOW-P fit is seconds–low tens of seconds; batch is I/O bound on Timescale reads |
| At 100 plants × 40 models | **~4000 models** | Still fits **one nightly batch worker**; fan out only if refit + eval + registry write exceeds the ops window |
| Hot-path (MD/PF/rules) | In-process after 15-min rollup | No GPU; per-plant compute is trivial vs DB query |
| LightGBM MD exceedance | **1 model/plant** | Tiny vs baselines |
| TimesFM shadow (P2) | Batch-only, optional | Do **not** size hot path for 200M foundation models |

**Policy:** baselines are **per asset_id that L3 engines read**, not per raw tag. Tag explosion does not imply model explosion. If nightly refit + golden replay + MLflow register exceeds **4 h wall-clock** at measured scale, add a second worker shard by `plant_id` — do not migrate the whole L3 stack to a cluster prematurely.

---

## 6. Build phasing P0–P3

Aligned to the [technical architecture](../02-technical-architecture.md) build phases and the savings stack (§3.2 / architecture §3.1).

| Phase | L3 scope | Model/rules deliverables | Eval deliverables |
|---|---|---|---|
| **P0** (wk 1–8) | MD + tariff + PF + first rules on incomer + bill (Path B) | Deterministic MD engine (histogram, post-mortem, stagger sim); tariff calculator + bill reconstruction; PF slab rules; calendar-only TOW baseline + residual EWMA for off-shift drift; finding-object contract frozen | Bill reconstruction ±2% gate; golden corpus v0 from pilot windows; alert budget live; manual adjudication loop |
| **P1** (mo 3–6) | Full TOW-P baselines, SEC engine, waste classifier, feeder attribution, compressor/furnace/idle rule packs | Production-covariate baselines + quantile bands; startup-event catalogue + co-start attribution; rule packs v1 for categories 2–5; fleet priors + shrinkage calibration; LightGBM challenger for baselines | Blocked-CV harness; G14 floor gating for M&V eligibility; precision ≥0.75 gate; PSI monitoring; MLflow registry live |
| **P2** (mo 6–12) | MD exceedance forecast; source-mix dispatch (greedy); cross-plant benchmark features; threshold auto-tuning from Rx feedback | LightGBM quantile intraday peak model; dispatch rule solver; bounded auto-calibration; champion/challenger pipeline | Shadow-mode rollout machinery; pinball/exceedance dashboards; precision ≥0.85; quarterly confidence-calibration review |
| **P3** | COP/HVAC depth, MILP dispatch where justified, NILM-lite signature hints `[!]`, PdM-signal fusion | Chiller COP-proxy models; MILP formulation; incomer signature matching (hint-only) | Seasonal-cycle-complete backtests; fleet-level meta-analysis of engine performance by vertical |

Deliberate sequencing logic: **deterministic ₹ engines first** (they verify fastest on the bill and de-risk trust), regression baselines second (they need 90 days of clean data anyway), ML forecasting third (it needs baselines + history), optimisation last.

---

## 7. Open questions

1. **15-min vs 1-min incomer for MD work `[!]`** — stagger simulation quality degrades at 15-min windows when DISCOM integrates at 15 min too (aliasing); how many ICP plants can give 1-min? Affects P0 connector priorities.
2. **Production data floor for SEC `[!]`** — what fraction of pilots can sustain ≥70% production-tagged windows? If low, SEC engine leans on shift-level proxies (counts from MES vs manual entry) and the value story shifts toward categories 1/3/4.
3. **G14 vs Indian M&V expectations `[~]`** — do Indian auditors/OEM supplier audits actually reference ASHRAE/IPMVP thresholds, or is bill reconciliation alone the accepted proof? Determines how hard to gate on CV(RMSE) floors vs internal use only.
4. **Suppression coverage** — is the maintenance calendar reliably available (SAP PM export vs WhatsApp-grade logs)? The biggest FP source is un-flagged planned work.
5. **ZEN adoption depth** — tariff tables in JDM are clearly right; do we also move category thresholds there (business-editable) or keep them in YAML under engineering control until P2?
6. **Hierarchical prior granularity** — vertical-level priors (forging vs pharma) vs asset-class-level (screw compressor 75–160 kW)? Asset-class is more transferable but needs a bigger fleet; start vertical, migrate `[~]`.
7. **Confidence semantics at L4** — should the ranker consume raw engine confidence or a fleet-calibrated acceptance-probability? Needs A/B once Rx volume is sufficient.
8. **Anomaly labels at scale** — adjudication cost grows with plants; when do we introduce weak-supervision (rules-as-labelers) to stretch engineer review time?

---

## 8. Competitive positioning — Zerowatt Digital Brain

*Added 2026-07-13 · IMPLEMENTATION_PLAN Phase A*

| Zerowatt claim | Stamped counter | Evidence path |
| --- | --- | --- |
| Physics digital twin + 1000s rules | Semver rulepacks + deterministic engines | `rule_or_model_ref` on every Finding |
| Society of AI agents + Zoe NL | Template-fast-path P0 + bounded LangGraph P1 | Schema-verified Prescription; rules veto |
| 20–30% savings narrative | 15–20% **bill-verified** precision-first | L5 ledger + DISCOM reconciliation |
| Equipment health / PdM breadth | Electrical proxies + matrix profile P2 | Findings cite meter tags, not black-box scores |
| 3D plant replica | Out of scope P0 | L6 queue + WhatsApp closure |

**Surrogate twins (not PINNs):** TOW-P + physics rulepacks + stagger simulator provide explainable "what-if" without Modelica FMUs. Counterfactual **delay cost** (ADR-013) is Stamped-specific accountability Zerowatt does not emphasize.

---

## 9. Dual-mode execution — hot / warm / cold

| Path | Trigger | Engines | SLO |
| --- | --- | --- | --- |
| **Hot** | 15-min rollup | MD histogram, PF slab, suppression | p95 < 30s post-rollup |
| **Warm** | Hourly / shift | EWMA/CUSUM, rulepack batch | p95 < 5 min |
| **Cold** | Nightly + historian backfill | TOW-P refit, eval backtest, TimesFM shadow (P2) | Batch |

Historian backfill: replay windows through cold path with `late: true` envelopes; findings tagged `engine_version` for audit. Hot path never blocks on cold refit.

---

## 10. Suppression service — shared contract

All engines call suppression before emit:

| Check | Source | Default |
| --- | --- | --- |
| `startup_window` | L2 feature store / SCADA state | 90s–15min per asset class |
| `production_mix_change` | SKU share delta | >10% shift |
| `maintenance_calendar` | L1 maintenance events | Planned window |
| `data_quality` | L2 quality flags | Reject `estimated` for M&V-eligible |

Applied suppressions recorded on `suppressions_checked[]`.

---

## 11. Time-series foundation models — shadow placement

See [ADR-014](../decisions/ADR-014-ts-foundation-model-role.md). **TimesFM is shadow-only P2** — never M&V engine of record. Primary stack unchanged: TOW-P, deterministic MD/tariff/rules, LightGBM quantile for MD exceedance.

---

# Citations

1. Price, P. — *Methods for Analyzing Electric Load Shape and its Variability*, LBNL-3713E (2010): https://eta-publications.lbl.gov/sites/default/files/LBNL-3713E.pdf
2. Mathieu et al. — *Quantifying Changes in Building Electricity Use, with Application to Demand Response* (TOWT), LBNL-4944E (2011): https://eta-publications.lbl.gov/sites/default/files/LBNL-4944E.pdf
3. CalTRACK Methods (§3.7–3.8, hourly TOWT + occupancy segmentation): http://docs.caltrack.org/en/latest/methods.html
4. OpenDSM (formerly OpenEEmeter), LF Energy — GitHub: https://github.com/opendsm/opendsm
5. OpenDSM hourly model methodology (elastic net, 24-h informed structure, day-type clustering): https://opendsm.energy/documentation/eemeter/hourly_model/methodology/
6. nmecr (kW Engineering) — TOWT implementation notes (672 15-min TOW variant, occupancy detection): https://kw-labs.github.io/nmecr/
7. ASHRAE Guideline 14-2002 — *Measurement of Energy and Demand Savings* (CV(RMSE)/NMBE criteria; whole-building path requirements): https://www.eeperformance.org/uploads/8/6/5/0/8650231/ashrae_guideline_14-2002_measurement_of_energy_and_demand_saving.pdf
8. Ruiz & Bandera — *Validation of Calibrated Energy Models: Common Errors*, Energies 10(10):1587 (FEMP/G14/IPMVP threshold comparison table): https://www.mdpi.com/1996-1073/10/10/1587
9. Wu & Keogh — *Current Time Series Anomaly Detection Benchmarks are Flawed and are Creating the Illusion of Progress*, IEEE TKDE 35(3) / ICDE 2022: https://wu.renjie.im/research/anomaly-benchmarks-are-flawed/ICDE2022_TSAD.pdf (DOI: https://doi.org/10.1109/tkde.2021.3112126)
10. STUMPY — scalable matrix profile library (Law, JOSS 2019): https://github.com/stumpy-dev/stumpy (paper: https://doi.org/10.21105/joss.01504)
11. *Short-Term Load Forecasting in the Greek Power Distribution System: A Comparative Study of Gradient Boosting and Deep Learning Models*, Energies 18(19):5060 (2025) — LightGBM best on all metrics: https://www.mdpi.com/1996-1073/18/19/5060
12. *Non-Intrusive Load Monitoring in industrial settings: A systematic review*, Renewable and Sustainable Energy Reviews (2024): https://www.sciencedirect.com/science/article/pii/S1364032124004295
13. GoRules ZEN Engine — open-source BRE, JDM format: https://github.com/gorules/zen/
14. GoRules Python rules engine (`zen-engine`): https://gorules.io/open-source/python-rules-engine
15. *A Practical Introduction to Population Stability Index (PSI)* — Coralogix (thresholds 0.1/0.25, drift monitoring practice): https://coralogix.com/ai-blog/a-practical-introduction-to-population-stability-index-psi/
16. pyGAM — generalized additive models in Python: https://pygam.readthedocs.io/en/latest/
17. LightGBM documentation: https://lightgbm.readthedocs.io/
18. Prophet — forecasting library: https://facebook.github.io/prophet/
19. MLflow Model Registry: https://mlflow.org/docs/latest/model-registry.html · Bergmeir & Benítez — *On the use of cross-validation for time series predictor evaluation* (blocked CV): https://doi.org/10.1016/j.ins.2011.12.028
20. Liu, Ting & Zhou — *Isolation Forest*, ICDM 2008: https://doi.org/10.1109/ICDM.2008.17
21. NILMTK — energy disaggregation toolkit (residential-centric): https://github.com/nilmtk/nilmtk
22. EVO — International Performance Measurement and Verification Protocol (IPMVP): https://evo-world.org/en/products-services-mainmenu-en/protocols/ipmvp
23. Manfren et al. — *Interpretable data-driven building load profiles modelling for M&V 2.0* (TOWT validation on EVO portal, 367 buildings): https://art.torvergata.it/retrieve/ffd8e3a4-0275-40e2-b3f0-eb1c7e9af8d5/Manfren_Interpretable_2023.pdf
24. LF Energy — OpenDSM project page (DOE approval of OpenEEmeter for IRA HOMES): https://lfenergy.org/projects/opendsm/
25. Crowe et al. (LBNL) — *Assessment of Model-Based Peak Demand Savings Estimation* (TOWT variants for peak prediction): https://eta-publications.lbl.gov/sites/default/files/crowe_-_assessment_of_model-based_peak_.pdf
26. RMV2.0 — LBNL M&V tool (R, TOWT): https://github.com/LBNL-ETA/RMV2.0
27. Energy Twin — *Time-of-Week and Temperature model explained* (implementation walkthrough): https://energytwin.io/time-of-week-and-temperature-model-explained/
28. UPPCL Tariff Order FY 2025-26 (billing-demand floor, PF provisions — via repo knowledge base): https://uppcl.org/site/writereaddata/siteContent/202511241749025833UPPCL%20Tariff%20Order%20FY%202025%2026.pdf
29. *Comparative evaluation of several models for forecasting hourly electricity use in a steel plant*, Scientific Reports (2026): https://www.nature.com/articles/s41598-026-43868-z
30. durable_rules — Python forward-chaining rules engine: https://github.com/jruizgit/rules
