---
type: Product Architecture
title: "Stamped Research & ML Citations — Core Stack + Frontier Watchlist"
description: "Citable bibliography of classical SPC, M&V baselines, LightGBM/TimesFM, and frontier time-series foundation models — separated into product-of-record vs evaluate/track for client-facing technical conversations."
tags: [stamped-energy, technical, ml, research, citations, timesfm, lightgbm, spc, foundation-models]
timestamp: "2026-07-24T19:30:00Z"
---

# Research Papers & ML Approaches Behind Industrial Energy Intelligence

*Companion to [L3 — Intelligence Core](layers/L3-intelligence-core.md), [L3 — Decision defense brief](layers/L3-decision-defense-brief.md), and [Technical architecture](02-technical-architecture.md). This is the **narrative + bibliography** layer for client-facing technical conversations; L3 remains the engineering SSOT for what is wired.*

> **Purpose of this document.** Give founders and sellers a *technically advanced, citation-honest* language for client conversations — Physics · Models · Agents · Closure — without inventing papers or pretending every frontier model is already the system of record.
>
> **How to read the two lanes**
>
> | Lane | Meaning in a client meeting |
> |---|---|
> | **CORE — product of record** | What actually drives findings, ₹, and M&V. Name these confidently. |
> | **FRONTIER — evaluate / shadow / watchlist** | Real, trending research we track (and in some cases already run in shadow). Name these to show technical depth. Do **not** claim they write the invoice number unless a promotion ADR says so. |
>
> **Citation confidence tags**
>
> - **[VERIFIED]** — bibliographic details confirmed against primary sources in this authoring pass.
> - **[FROM L3 SSOT]** — already curated in `L3-intelligence-core.md`; treated as project-canonical.
> - **[GENERAL]** — foundational classic; attribution is standard in the field.

---

## 0. One-slide map — stack → research family

| Client-facing pillar | What the plant hears | CORE research family | FRONTIER name-drops (honest) |
|---|---|---|---|
| **01 · Physics** | Versioned rule packs; PF/tariff arithmetic; every finding cites a rule version | Affinity laws, specific power, Stefan–Boltzmann-style heat loss, tariff/PF slab math; industrial SPC on residuals | Physics-informed neural networks (PINNs) as the *research language* for “hard physics constraints in the loss” — we use the *idea*, not necessarily a full PDE-PINN in production |
| **02 · Models** | Industrial load models, not a chatbot on meter dumps | TOW-P / CalTRACK-style baselines · EWMA/CUSUM/MEWMA · Isolation Forest · Matrix Profile · LightGBM quantile | TimesFM · Chronos · Moirai · MOMENT · PatchTST · N-BEATS / N-HiTS · TFT · Anomaly Transformer |
| **03 · Agents** | Floor action: what / why / who / effort / ₹ / due | Deterministic ranking (`₹ × confidence / effort`) + structured finding contract | LLM agents for prose only — never invent the ₹; conformal / quantile bands for uncertainty language |
| **04 · Closure** | Priced onto DISCOM lines; M&V locked at issue | IPMVP · ASHRAE Guideline 14 · bill-line decomposition | Advanced uncertainty quantification (conformal prediction) as the research frame for “distribution-free coverage” |

**The credibility line (say this out loud):**  
*"We run peer-reviewed statistics and M&V-grade regression as the system of record, LightGBM where probabilistic ranking wins, and we shadow the same time-series foundation models Google/Amazon/Salesforce publish — without letting a black box write the number on your bill."*

---

## 1. CORE — Statistical Process Control (lead with this)

This is the highest-credibility section for plant EEs and pharma/QA audiences. Same mathematical family as GMP process control — named methods, known false-alarm theory, not “AI vibes.”

### 1.1 Shewhart control charts
**Shewhart, W.A. (1931). *Economic Control of Quality of Manufactured Product.* D. Van Nostrand.** *[GENERAL]*

Plot each measurement with limits at roughly ±3σ. Catches large point excursions; weak on slow drift — which is exactly why EWMA/CUSUM exist.

### 1.2 EWMA — Exponentially Weighted Moving Average
**Roberts, S.W. (1959). “Control Chart Tests Based on Geometric Moving Averages.” *Technometrics*, 1(3), 239–250.** *[VERIFIED]*

Running average that weights recent readings more than old ones. Sensitive to small, sustained drifts (compressor creep, off-shift baseload, furnace holding load).

**Stamped use:** primary detector for “consumption has run X% above baseline for N consecutive days.”

### 1.3 CUSUM — Cumulative Sum
**Page, E.S. (1954). “Continuous Inspection Schemes.” *Biometrika*, 41(1–2), 100–115.** *[VERIFIED]*

Running total of off-target error. Provably strong (in expected-delay sense) for a persistent mean shift of known size.

**Stamped use:** alongside EWMA to decide “new worse regime” vs “one hot/busy day.”

### 1.4 Hotelling’s T² (multivariate distance)
**Hotelling, H. (1931). “The Generalization of Student's Ratio.” *Annals of Mathematical Statistics*, 2(3), 360–378.** *[VERIFIED]*

Joint judgment across correlated variables: \(T^2 = (x-\mu)^\top \Sigma^{-1}(x-\mu)\).

### 1.5 MEWMA — Multivariate EWMA
**Lowry, C.A., Woodall, W.H., Champ, C.W., & Rigdon, S.E. (1992). “A Multivariate Exponentially Weighted Moving Average Control Chart.” *Technometrics*, 34(1), 46–53.** *[VERIFIED]*

Smooth a *vector* of signals (kW + pressure + temperature), then apply a Hotelling-style distance. Memory charts should run *with* T², not instead of it (inertia after large opposite excursions).

> **Client line:** *"We watch correlated plant vitals the way a doctor reads temperature, pulse, and BP together — with the same SPC family used in process validation for decades."*

---

## 2. CORE — Baseline, M&V, and tariff arithmetic

### 2.1 TOWT → TOW-P (time-of-week & production)
**Price, P. (2010). *Methods for Analyzing Electric Load Shape and its Variability.* LBNL-3713E.** *[FROM L3 SSOT / VERIFIED path]*  
**Mathieu et al. (2011). *Quantifying Changes in Building Electricity Use…* LBNL-4944E.** *[FROM L3 SSOT]*

168 hourly time-of-week indicators + piecewise temperature (buildings). Stamped adaptation: **TOW-P** — production rate as the dominant covariate; temperature kept for chillers/HVAC.

### 2.2 CalTRACK / OpenDSM
Open, published M&V regression methodology and LF Energy OpenDSM (formerly OpenEEmeter) implementation — elastic-net hourly models, occupied/unoccupied segmentation. *[FROM L3 SSOT]*

### 2.3 IPMVP & ASHRAE Guideline 14
Industry bar for whether a claimed saving is defensible: Options A/B/C/D; acceptance via **CV(RMSE)** and **NMBE**. *[FROM L3 SSOT]*  
Typical published thresholds (confirm against current text before quoting to auditors): monthly NMBE ±5% / CV(RMSE) ≤15%; hourly bands looser under G14.

### 2.4 Deterministic commercial math (not ML)
MD histogram vs CMD, spike post-mortem ₹, PF slab / TOD windows, billing-demand floors — arithmetic on tariff contracts. This is the part competitors often bury under “AI”; we put it first because it is what the DISCOM invoice actually charges.

---

## 3. CORE — Classical ML that earns its place

### 3.1 LightGBM (gradient boosting)
**Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. (2017). “LightGBM: A Highly Efficient Gradient Boosting Decision Tree.” *NeurIPS 2017.*** *[VERIFIED]*

GOSS + Exclusive Feature Bundling → strong tabular learners. Industrial telemetry is a spreadsheet (sensors × timestamps); GBMs dominate this shape in competitions (incl. M5 lineage) and recent load-forecast comparisons.

**Stamped use:** **quantile** LightGBM for short-horizon **MD exceedance ranking** (“will today set a new MD?”). Challenger/residual analyser for baselines — **not** the M&V baseline of record (coefficients must remain printable).

### 3.2 Isolation Forest
**Liu, F.T., Ting, K.M., & Zhou, Z.-H. (2008). “Isolation Forest.” *IEEE ICDM 2008*, 413–422.** *[VERIFIED]*

Anomalies isolate in fewer random partitions. Secondary multivariate detector on shift feature vectors (mean kW, PF, load factor, SEC).

### 3.3 Matrix Profile (shape discords & motifs)
**Yeh, C.-C. M., Zhu, Y., Ulanova, L., Begum, N., Ding, Y., Dau, H. A., Silva, D. F., Mueen, A., & Keogh, E. (2016). “Matrix Profile I: All Pairs Similarity Joins for Time Series…” *IEEE ICDM 2016*, 1317–1322.** *[VERIFIED]*  
**Implementation:** Law, J. (2019). STUMPY — *JOSS* (DOI 10.21105/joss.01504). *[FROM L3 SSOT]*

Nearest-neighbor distance for every window → **discords** (never-seen startup shapes) and **motifs** (recurring plant signatures). Training-free; one main hyperparameter (window length).

### 3.4 Why “simple” often beats exotic detectors
**Wu, R. & Keogh, E. (2021/2022). “Current Time Series Anomaly Detection Benchmarks are Flawed…” *IEEE TKDE* / ICDE 2022.** *[FROM L3 SSOT]*  
Headline finding often cited: large fractions of popular benchmarks are solvable with trivial rules; authors report no forceful reproducible evidence that deep AD beats simpler methods across the board.

**Stamped stance:** industrial energy anomalies are mostly *known-physics deviations from a good baseline*. Intelligence lives in baseline + suppressions (startup, mix change, maintenance), not in an exotic detector score.

---

## 4. FRONTIER — Deep forecasting architectures (name these)

These are the models sharp ML-aware buyers have heard of. Position as **challenger / research pedigree**, not invoice SoT.

### 4.1 PatchTST
**Nie, Y., Nguyen, N. H., Sinthong, P., & Kalagnanam, J. (2023). “A Time Series is Worth 64 Words: Long-term Forecasting with Transformers.” *ICLR 2023.*** *[VERIFIED]*  
arXiv:2211.14730

Patches subsequences as tokens + channel-independence. Major step that made Transformers competitive again on long-horizon forecasting benchmarks.

**Client line:** *"Same patching idea that unlocked modern time-series transformers — we use that research wave for challenger forecasts, not as the M&V baseline."*

### 4.2 N-BEATS
**Oreshkin, B. N., Carpov, D., Chapados, N., & Bengio, Y. (2020). “N-BEATS: Neural basis expansion analysis for interpretable time series forecasting.” *ICLR 2020.*** *[VERIFIED]*  
arXiv:1905.10437

Deep residual stacks with optional interpretable trend/seasonality basis. Famous for beating statistical hybrids on M4-class benchmarks *without* hand-crafted TS components.

### 4.3 N-HiTS
**Challu, C., Olivares, K. G., Oreshkin, B. N., Garza Ramirez, F., Mergenthaler Canseco, M., & Dubrawski, A. (2023). “NHITS: Neural Hierarchical Interpolation for Time Series Forecasting.” *AAAI 2023*, 37(6), 6989–6997.** *[VERIFIED]*  
DOI: 10.1609/aaai.v37i6.25854

Hierarchical interpolation + multi-rate sampling — often cited ~20% accuracy gains vs late Transformer baselines with large compute cuts on long horizons.

### 4.4 Temporal Fusion Transformer (TFT)
**Lim, B., Arık, S. Ö., Loeff, N., & Pfister, T. (2021). “Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting.” *International Journal of Forecasting*, 37(4), 1748–1764.** *[VERIFIED]*  
arXiv:1912.09363 · DOI: 10.1016/j.ijforecast.2021.03.012

Attention + gating + variable selection for mixed static/known-future/observed inputs — the “interpretable deep forecaster” story Google Cloud popularised.

**Honest Stamped constraint:** TFT/N-BEATS/N-HiTS need more clean history and ops cost than a single plant’s 3–24 months usually justifies as *primary*. LightGBM quantile + TOW-P remains the practical winner at plant scale.

---

## 5. FRONTIER — Time-series foundation models (the exciting part)

This is the “LLM moment for meters.” Pretrain once on enormous corpora; zero-shot or few-shot on a new plant series. **Stamped policy ([ADR-014](../decisions/ADR-014-ts-foundation-model-role.md)): TimesFM is shadow-only until promotion gates pass. Never M&V / SEC / ₹ of record.**

### 5.1 TimesFM (Google Research) — *already on our shadow roadmap*
**Das, A., Kong, W., Sen, R., & Zhou, Y. (2024). “A decoder-only foundation model for time-series forecasting.” *ICML 2024.*** *[VERIFIED]*  
arXiv:2310.10688 · pretrained on ~100B time-points; patched decoder; ~200M params class.

**Stamped use:** optional TimesFM 2.x + exogenous regressors as **shadow challenger** for cold-start bands / transfer hypotheses. Promotion requires beating seasonal-naive **and** LightGBM on pinball across ≥3 plants, no FP regression, batch SLO — then a *new* ADR before any citation-path use.

### 5.2 Chronos (Amazon / AWS AI Labs)
**Ansari, A. F., Stella, L., Turkmen, C., et al. (2024). “Chronos: Learning the Language of Time Series.”** *[VERIFIED]*  
arXiv:2403.07815

Tokenize scaled values into a discrete vocabulary; train T5-style LMs with cross-entropy; sample probabilistic trajectories. Strong zero-shot results across 40+ datasets. Later **Chronos-Bolt** variants emphasise speed.

**Client line:** *"Amazon’s research stack treats load curves as a language model problem — we track that family for probabilistic cold-start, same honesty rules as TimesFM."*

### 5.3 Moirai (Salesforce AI Research)
**Woo, G., Liu, C., Kumar, A., Xiong, C., Savarese, S., & Sahoo, D. (2024). “Unified Training of Universal Time Series Forecasting Transformers.” *ICML 2024* (Oral).** *[VERIFIED]*  
arXiv:2402.02592 · LOTSA corpus >27B observations · any-variate attention · mixture output distributions. Code: Uni2TS.

### 5.4 MOMENT (Auton Lab / CMU lineage)
**Goswami, M., Szafer, K., Choudhry, A., Cai, Y., Li, S., & Dubrawski, A. (2024). “MOMENT: A Family of Open Time-series Foundation Models.” *ICML 2024.*** *[VERIFIED]*  
arXiv:2402.03885 · Time Series Pile · open weights for forecasting **and** classification / anomaly / imputation under limited supervision.

> **Why this section impresses without lying:** these are ICML/ICLR-grade systems from Google, Amazon, Salesforce, and top academic labs. A company that can *name them correctly, place them in a shadow lane, and refuse to put them on the bill* looks more advanced than a company that claims “our proprietary AI” with no citations.

---

## 6. FRONTIER — Advanced anomaly & uncertainty

### 6.1 Anomaly Transformer
**Xu, J., Wu, H., Wang, J., & Long, M. (2022). “Anomaly Transformer: Time Series Anomaly Detection with Association Discrepancy.” *ICLR 2022* (Spotlight).** *[VERIFIED]*  
arXiv:2110.02642

Association discrepancy via Anomaly-Attention — anomalies struggle to form non-trivial associations with the full series. Impressive on public industrial/ops benchmarks.

**Stamped placement:** lab/challenger lane only. Primary anomaly of record stays **EWMA/CUSUM on baseline residuals** (explainable ARL theory). Wu & Keogh still applies as the scientific caution against benchmark theatre.

### 6.2 Conformal prediction (distribution-free uncertainty)
**Angelopoulos, A. N. & Bates, S. (2021). “A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification.”** *[VERIFIED]*  
arXiv:2107.07511

Finite-sample coverage guarantees without trusting model likelihoods — wrap *any* forecaster (including LightGBM or TimesFM) to say “90% prediction set” with teeth.

**Client line:** *"When we quote a band, the research frame is conformal / quantile coverage — not a neural net smiling with fake confidence."*

### 6.3 Physics-informed ML (PINNs) — the missing citation, now filled
**Raissi, M., Perdikaris, P., & Karniadakis, G. E. (2019). “Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations.” *Journal of Computational Physics*, 378, 686–707.** *[VERIFIED]*  
DOI: 10.1016/j.jcp.2018.10.045

Encode governing physics into the learning objective. Stamped’s compressor/furnace packs are **physics-constrained hybrids** (thermodynamic floors, affinity laws) — conceptually aligned with PIML/PINN research even when the production artefact is a versioned rule + calibrated residual, not a full PDE network.

---

## 7. What we deliberately do *not* claim

### 7.1 Industrial NILM as magic disaggregation
**Systematic review:** industrial NILM remains data-starved; SOTA often validated on single-machine / lab-like settings (*Renewable & Sustainable Energy Reviews*, 2024). *[FROM L3 SSOT]*

**Stamped substitute:** feeder-level metering + energy-graph attribution. Slower to set up; actually works.

### 7.2 “Deep learning everywhere”
Auditability, data volume (one plant ≠ internet-scale), and plant-EE explainability disqualify black-box primary engines for ₹ on an invoice. Frontier models live in **shadow / challenger** until gated ([ADR-014](../decisions/ADR-014-ts-foundation-model-role.md)).

---

## 8. Talk tracks that sound advanced *and* survive a sharp EE

| If they say… | You answer… | Cite / name |
|---|---|---|
| “Isn’t this just another AI dashboard?” | “The number on your bill path is regression + tariff arithmetic you can print. ML ranks and challenges; it doesn’t invent ₹.” | TOW-P, IPMVP/G14, LightGBM as challenger |
| “How do you avoid alert spam?” | “SPC on production-normalised residuals — EWMA + CUSUM — with known false-alarm behaviour, plus startup/mix suppressions.” | Roberts 1959, Page 1954 |
| “Do you use foundation models?” | “Yes in shadow — TimesFM class, same research wave as Chronos/Moirai. Promotion needs pinball gates vs LightGBM across plants. We won’t put a foundation model on your M&V citation until it earns it.” | Das et al. ICML 2024; ADR-014 |
| “Why not LSTM/Transformer as primary?” | “PatchTST/N-HiTS/TFT are real SOTA *in papers*. At one plant with months of history, LightGBM quantile + physics baselines win on ops cost and auditability — and the literature on AD benchmarks warns against exotic detectors.” | Nie ICLR 2023; Wu & Keogh; Ke et al. 2017 |
| “Can you see every machine from one incomer?” | “That’s industrial NILM. Published reviews say it’s not reliable yet at plant scale. We meter feeders and attribute on the graph.” | 2024 RSER review |
| “Prove the saving.” | “IPMVP-style options, ASHRAE acceptance stats, potential vs realised ledger tied to DISCOM line items.” | IPMVP, G14 |

---

## 9. Phrase bank — high-signal technical language

Use sparingly; one or two per meeting beats a buzzword dump.

- **Production-normalised residual SPC** — EWMA/CUSUM/MEWMA on TOW-P residuals  
- **Quantile / pinball-optimised MD exceedance** — LightGBM  
- **Shape discord discovery** — Matrix Profile / STUMPY  
- **Zero-shot patched decoder foundation model** — TimesFM (shadow)  
- **Tokenized probabilistic TS foundation model** — Chronos (watchlist)  
- **Any-variate universal forecaster** — Moirai (watchlist)  
- **Association-discrepancy anomaly attention** — Anomaly Transformer (lab)  
- **Physics-informed hybrid packs** — Raissi et al. research lineage; versioned plant rulepacks in product  
- **Distribution-free conformal bands** — Angelopoulos & Bates  
- **Bill-linked M&V ledger** — IPMVP + DISCOM line decomposition  

---

## 10. Master citation list (copy into decks / one-pagers)

### Classical SPC & multivariate
1. Shewhart (1931) — control charts. *[GENERAL]*  
2. Hotelling (1931) — \(T^2\). *[VERIFIED]*  
3. Page (1954) — CUSUM. *[VERIFIED]*  
4. Roberts (1959) — EWMA. *[VERIFIED]*  
5. Lowry et al. (1992) — MEWMA. *[VERIFIED]*  

### Baselines & M&V
6. Price (2010) LBNL-3713E — load shape / TOWT ancestor.  
7. Mathieu et al. (2011) LBNL-4944E — TOWT.  
8. CalTRACK methods; OpenDSM / OpenEEmeter (LF Energy).  
9. ASHRAE Guideline 14; EVO IPMVP.  

### Classical ML & shape methods
10. Liu, Ting & Zhou (2008) — Isolation Forest, ICDM.  
11. Ke et al. (2017) — LightGBM, NeurIPS.  
12. Yeh et al. (2016) — Matrix Profile I, ICDM.  
13. Law (2019) — STUMPY, JOSS.  
14. Wu & Keogh (2021/22) — flawed AD benchmarks, TKDE/ICDE.  

### Deep & foundation (frontier)
15. Lim et al. (2021) — Temporal Fusion Transformer, *Int. J. Forecasting*.  
16. Oreshkin et al. (2020) — N-BEATS, ICLR.  
17. Challu et al. (2023) — N-HiTS, AAAI.  
18. Nie et al. (2023) — PatchTST, ICLR.  
19. Das et al. (2024) — TimesFM, ICML · arXiv:2310.10688.  
20. Ansari et al. (2024) — Chronos · arXiv:2403.07815.  
21. Woo et al. (2024) — Moirai, ICML · arXiv:2402.02592.  
22. Goswami et al. (2024) — MOMENT, ICML · arXiv:2402.03885.  
23. Xu et al. (2022) — Anomaly Transformer, ICLR.  

### Physics & uncertainty
24. Raissi, Perdikaris & Karniadakis (2019) — PINNs, *J. Comp. Phys.*  
25. Angelopoulos & Bates (2021) — conformal prediction · arXiv:2107.07511.  

### Explicit non-claims
26. Industrial NILM systematic review (2024), *Renewable & Sustainable Energy Reviews*.  

---

## 11. Internal vs external use

| Audience | How to use this file |
|---|---|
| **Client / technical discovery** | Sections 0, 1, 3, 5 (TimesFM + Chronos/Moirai names), 8 |
| **Founder prep** | Whole doc; rehearse the CORE vs FRONTIER distinction |
| **Engineering** | Prefer [L3 intelligence core](layers/L3-intelligence-core.md) + ADRs for what is actually wired; this doc is the *narrative + bibliography* layer |
| **Website / deck** | Pull 4–6 names max (EWMA/CUSUM, LightGBM, TimesFM, PatchTST or Moirai, IPMVP). Link “research underlying each prescription” to Physics→Models→Agents→Closure |

---

## Honesty footer

- No titles, authors, or venues in this document were invented for effect.  
- **CORE** methods are what product architecture treats as of-record or primary challengers.  
- **FRONTIER** methods are real, citable, and exciting — positioned as shadow/evaluate unless an ADR promotes them.  
- If a client asks “is X in production on our plant tomorrow?”, answer from the L3 engine cards and ADR-014 promotion record — not from this name-drop list alone.

*Last verified citation pass: 2026-07-24.*
