---
type: Decision Defense Brief
title: "L3 — Decision Defense Brief (Rules vs ML vs LLM and everything else)"
description: >-
  Study guide for defending every accepted L3 decision: when to use rules,
  classical ML, foundation models, optimisation, or LLMs; engine-by-engine
  attack/response cards; repo topology; eval gates; competitive counters.
tags: [stamped-energy, l3, decisions, debate, pedagogy]
timestamp: "2026-07-14T00:00:00Z"
status: Accepted decisions as of 2026-07-14 — synthesize of ADRs + L3/L4 specs + consumer DECISIONS
---

# L3 Decision Defense Brief

> **Read this to argue, not only to recall.** Every section has a *thesis*, *why*, *what we rejected*, and *how an opponent attacks / how you answer*.
>
> **Authority sources (cite these, not vibes):**
> - Spec: [`L3-intelligence-core.md`](L3-intelligence-core.md)
> - Boundary with language: [`L4-knowledge-and-reasoning.md`](L4-knowledge-and-reasoning.md)
> - Quality spine: [`../cross-cutting/04-evaluation-and-quality.md`](../cross-cutting/04-evaluation-and-quality.md)
> - ADRs: [012](../../decisions/ADR-012-l3-artifact-repo-topology.md) · [013](../../decisions/ADR-013-counterfactual-savings-ledger.md) · [014](../../decisions/ADR-014-ts-foundation-model-role.md) · [014 promotion](../../decisions/ADR-014-promotion-record.md)
> - Plan matrix: [`../../IMPLEMENTATION_PLAN.md`](../../IMPLEMENTATION_PLAN.md) §11
> - Consumer decisions: [`consumers/stamped-l3-rulepacks/DECISIONS.md`](../../consumers/stamped-l3-rulepacks/DECISIONS.md) · [`consumers/stamped-l3-eval/DECISIONS.md`](../../consumers/stamped-l3-eval/DECISIONS.md)

---

## 0. How to use this document

| Goal | Where to go |
| --- | --- |
| 60-second elevator defense | §1 |
| Answer “why not just ML / LLM / digital twin?” | §2–§3 |
| Defend one engine (baseline, MD, rules…) | §4 |
| Defend three-repo split / rulepack axes / Lab UI | §5–§6 |
| Defend eval gates and “precision > recall” | §7 |
| Win vs Zerowatt-style attacks | §8 |
| Steelman Q&A drills | §9 |
| Know what you must *not* overclaim | §10 |

**Honesty markers (from the L3 spec):** `[~]` approximate / benchmark-derived · `[!]` evolving — do not treat as customer-facing settled fact.

---

## 1. The one-sentence thesis (memorise this)

**L3 owns numbers that must survive a plant engineer and an M&V auditor; therefore everything that can be deterministic or linear-in-parameters *is*, classical ML is a supporting challenger, foundation models stay in shadow, and LLMs live in L4 for language — never for ₹ math.**

Expand in four claims:

1. **Product truth is the DISCOM bill**, not a model score. The 15–20% target is the *sum of closed prescriptions* across six waste categories, not one heroic model output ([L3 §1](L3-intelligence-core.md)).
2. **Precision beats recall.** Plant attention is scarce; a false prescription destroys the closure rate that the savings model depends on.
3. **Explainability is a hard gate**, not UX polish. One sentence to a plant electrical engineer, or the engine is disqualified as primary of record.
4. **L3 never emits prose.** Findings carry category, evidence window, confidence, ₹ decomposition onto a tariff line. L4 turns that into prescriptions; L5 verifies on the bill.

If you remember only one diagram, remember this:

```text
  Trust boundary for money numbers
  ─────────────────────────────────
  Deterministic / TOW-P of record  →  may cite on M&V path
  Classical ML (LightGBM, SPC)     →  may detect / forecast; ₹ still from tariff math
  Foundation models (TimesFM)      →  shadow only (ADR-014)
  LLMs                             →  L4 composition/language only; vetoed by L3 rules
```

---

## 2. The decision taxonomy — five tools, not “AI vs not AI”

Opponents often collapse everything into “use AI.” Your first move is to **name five distinct tools** and force the argument onto the right tool for the job.

### 2.1 The five tools

| Tool | What it optimises for | What it is bad at | Stamped home |
| --- | --- | --- | --- |
| **A. Deterministic rules & physics** | Exactness, audit, known failure modes, versioned behaviour | Unknown-unknown patterns; needs good thresholds | Rulepacks, tariff/PF/MD arithmetic, waste taxonomy, suppressions |
| **B. Classical statistical / linear-in-params models** | M&V-grade baselines, known false-alarm theory, printable coefficients | Pure accuracy contests vs GBMs on rich covariates | TOW-P baselines, EWMA/CUSUM residuals, hierarchical priors |
| **C. Classical ML (tabular / boosting)** | Forecast ranking, residual challenge, multivariate oddity | Unauditable ₹ claims; ops cost if every plant retrains a zoo | LightGBM MD exceedance; GBM baseline *challenger*; Isolation Forest secondary |
| **D. Foundation / deep sequence models** | Zero-shot cold-start bands, fleet transfer hypotheses | Audit path, ops, data hunger at single-plant scale | TimesFM **shadow only** (ADR-014); deep AD / LSTM rejected as primary |
| **E. LLMs / agents** | Language, ranking narrative, playbook composition | Inventing numbers, physics, tariff slabs, control advice | **L4 only**, template-fast-path first; L3 rules veto is final |

**Optional sixth:** small **optimisation** (greedy / MILP) for source-mix dispatch — still not ML; evaluated as simulated-vs-actual ₹.

### 2.2 The “which tool?” rubric (use this live in debate)

Ask these questions **in order**. Stop at the first “yes.”

| # | Question | If YES → | Stamped example |
| --- | --- | --- | --- |
| 1 | Must the output be **exactly reproducible** from tariff order / physics formulas for legal or bill reconciliation? | **Rules / deterministic calculator** | PF slabs, billing demand floor, TOD ₹, stagger what-if on measured profiles |
| 2 | Must an **auditor reprint coefficients** and CV(RMSE)/NMBE in an M&V report? | **Linear-in-parameters baseline (TOW-P)** | SEC / energy baseline of record |
| 3 | Is the job **known-physics deviation from a good baseline** (holding load, SP drift, PF slip)? | **Rules + residual SPC**, not a deep detector | Anomaly of record = EWMA/CUSUM on residuals |
| 4 | Is the job **short-horizon probabilistic ranking** where pinball/calibration matters more than a printed β? | **Classical ML (LightGBM quantile)** | “Will today set a new MD?” |
| 5 | Do we lack plant history and only need a **wide, non-cited band** for UX cold-start? | **Fleet priors** first; foundation model only as *shadow/dashboard band* | Weeks 0–2 onboarding |
| 6 | Is the job **turning a structured finding into supervisor language / playbook action**? | **LLM in L4**, never inventing the number | Prescription draft + template smooth |
| 7 | Is someone proposing the model **own the ₹ number or actuate the plant**? | **Reject** — violates read-only + M&V boundary | “RL dispatch that writes setpoints” |

**One-liner of the rubric:** *If a plant engineer or auditor will ask “show your working,” you do not get a neural net of record.*

### 2.3 Why “hybrid” is the correct word — and how not to abuse it

Stamped **is** hybrid. The hybrid is **asymmetric**:

| Layer of hybrid | Allowed role |
| --- | --- |
| Rules / tariff / TOW-P | **Engine of record** for findings and ₹ paths that can become M&V |
| LightGBM / Isolation Forest / Matrix Profile | **Challenger / enrichment** — improve detection or forecast ranking |
| TimesFM | **Shadow** — must pass ADR-014 gates; still never M&V citation without a *new* ADR |
| LLM | **Downstream consumer of Findings** — language & composition; vetoed by deterministic tools |

What “hybrid” must **not** mean in an argument: “whatever model scores highest on a Kaggle-style MAPE becomes the savings claim.” That collapses the product into unverifiable AI.

### 2.4 Rule vs ML vs LLM — the forced comparison table

Use this when someone asks for a single slide.

| Criterion | Rules / deterministic | Classical ML | LLM (L4) |
| --- | --- | --- | --- |
| Bill-line ₹ exactness | **Wins** | Cannot own tariff truth | Must not invent ₹ |
| Explain to plant EE in one sentence | **Wins** (formula) | Partial (feature importances ≠ audit) | Good language, weak proof |
| Version for M&V replay | Semver rulepack + params_hash | Registry model version | Prompt/model version — not enough alone |
| False-positive control | Thresholds + suppressions + golden CI | Threshold + calibration | Template + verifier + rules veto |
| Data hunger | Low | Medium | N/A for numeric engines |
| Failure mode we fear | Stale threshold / missing suppression | Silent drift / opaque ₹ | Hallucinated number or unsafe advice |
| Where Stamped puts it | L3 primary for waste detectors & tariff | L3 supporting forecasts/challengers | L4 only |

---

## 3. Design constraints that decided everything upstream of model choice

If you skip these, every model argument becomes taste. These constraints are **why** boring models win.

| Constraint | Implication for L3 |
| --- | --- |
| 3–24 months history, ~15-min tags, patchy production | Deep sequence models are data-hungry and brittle; prefer TOW + piecewise + shrinkage |
| Plant EEs will challenge findings | Opaque primary engines are commercial suicide |
| IPMVP / ASHRAE-style M&V narrative | Baseline of record must be printable regression / deterministic |
| Small Python ML team | Fleet-shared code + per-plant params, not 100 custom models |
| Read-only OT | No RL that actuates; recommendations only |
| Closure rate ≥60% on high-priority Rx `[!]` | Precision > recall; alert budget; suppressions first-class |
| India DISCOM tariff complexity | Tariff engine is a **calculator**, not a learned model |
| Competitive: Zerowatt “1000s of rules + AI agents” | We match rule breadth with **semver audit trail** and beat on **bill-verified** proof |

---

## 4. Engine-by-engine defense cards

Format of each card: **Decision → Why → Rejected → Attack / Answer → Eval gate you cite**.

### 4.1 Baseline & SEC — TOW-P of record

| | |
| --- | --- |
| **Decision** | **TOW-P** (time-of-week + piecewise production ± temperature for HVAC): WLS / elastic-net style, CalTRACK/OpenDSM pedigree. Quantile bands from residual cells. |
| **Why** | M&V industry consensus is linear-in-parameters regression on independent variables. TOWT proven on buildings; we adapt temperature → production (“TOW-P”) for Indian manufacturing. Coefficients (β₀ fixed load, β₁ marginal kWh/unit) are meaningful to plant staff. |
| **Secondary allowed** | LightGBM / pyGAM as *challenger* and residual analysis; Prophet/STL for week-1 visual bands only. |
| **Rejected** | Deep sequence baselines (unauditable, data-hungry); Random Forest (dominated by GBM, opaque); GBM as *of record* (SHAP ≠ printable regression for auditor). |
| **Eval you cite** | ASHRAE G14 floors + Stamped tighter internals (monthly NMBE ±3% / CVRMSE ≤10% `[~]`); blocked time-series CV; M&V-eligible only after ≥90 days + coverage gates. |
| **Cold-start** | Fleet hierarchical priors → shrinkage → plant-dominated → day-90 M&V-eligible — **not** “run TimesFM and cite it.” |

**Attack:** *“LightGBM wins MAPE in papers; you’re leaving accuracy on the table.”*  
**Answer:** Accuracy is not the product metric. **Auditability and bill verification are.** GBM can sit in shadow/challenger; if it beats TOW-P on error *and* we invent an auditable citation path, that is a *new ADR* — it is not silent promotion. Papers that win forecasting contests are not M&V acceptance criteria.

**Attack:** *“Why not a physics digital twin / PINN?”*  
**Answer:** Surrogate twin = TOW-P + physics rulepacks + stagger simulator. Full Modelica/PINN is ops-heavy, label/calibration heavy, and not required to close the six waste categories on Path B bill lines. Competitive counter to Zerowatt twins is **explainable what-if + delay cost (ADR-013)**, not FMUs.

---

### 4.2 Anomaly & deviation — EWMA + CUSUM on residuals

| | |
| --- | --- |
| **Decision** | Primary = **SPC on baseline residuals** (EWMA + CUSUM). Secondary = Isolation Forest (shift features), Matrix Profile/STUMPY (shape discords / motifs). |
| **Why** | Most industrial “anomalies” we care about are **known-physics deviations from a good baseline**. Intelligence lives in baseline + suppressions, not exotic detectors. Wu & Keogh: deep AD benchmarks are flawed; no forceful evidence deep > simple. |
| **Rejected** | Autoencoders / deep AD as primary — unexplainable reconstruction scores, data hunger, false progress literature. |
| **Critical companion** | **Suppression service** (startup, production-mix, maintenance, data-quality) — first-class, shared, recorded on `suppressions_checked`. |

**Attack:** *“Why not unsupervised deep anomaly like everyone ships in demos?”*  
**Answer:** Demo metrics ≠ plant trust. We need “consumption 12% above production-adjusted baseline for 6 days,” not “reconstruction error 3.2.” SPC has ARL theory; deep AD does not give the engineer a causal sentence.

---

### 4.3 Demand & MD — deterministic core + LightGBM exceedance

| | |
| --- | --- |
| **Decision** | **Deterministic first:** MD histogram vs CMD, spike post-mortem ₹, stagger simulator on **measured** startup profiles. **Forecast:** LightGBM quantile for remaining-day peak exceedance; SARIMA thin-data fallback. |
| **Why** | Most MD value is arithmetic on real profiles (Path B fastest win). Forecast is a *ranking/calibration* problem (“P(new monthly MD today)”), where GBMs dominate at this data scale vs LSTM/TFT. |
| **Rejected** | LSTM/N-BEATS/TFT as P0–P2 primary — no reliable accuracy case at single-plant 3–24 month history; real ops cost. TimesFM only shadow (ADR-014). |
| **Eval** | Pinball @ P50/P90; exceedance precision/recall; must beat seasonal-naive + persistence or ship the simple rule. |

**Attack:** *“Foundation models zero-shot better forecasts now.”*  
**Answer:** Possibly as challenger — **prove it under ADR-014 gates** (beat naive + LightGBM on ≥3 plants, no FP regression, batch SLO). Promotion to M&V citation still requires a **new ADR**. As of promotion record: **do not promote** — skeleton not evidenced.

---

### 4.4 Attribution — graph co-start ranking, not NILM

| | |
| --- | --- |
| **Decision** | Ramp/changepoint catalogue + energy-graph traversal + `score = ramp_kw × proximity(asset)` with correlation tie-break. |
| **Proximity locked** | `proximity = 1/(1+hops)`; hops via `feeds` / `shares_electrical_bus`; max depth 4. Shared-bus boolean alone rejected as too coarse. |
| **Rejected** | Full industrial NILM as core — immature, label-starved, residential toolkits; P3 signature hints only `[!]`. |

**Attack:** *“Competitors claim AI disaggregation from the incomer alone.”*  
**Answer:** Industrial NILM reviews (2024) still list overlapping continuous loads and scarce labels as open problems. We **monotonically improve** with feeder metering (Path A depth) and stay explainable. Feeder meters beat magic disaggregation for trust.

---

### 4.5 Rules & physics — versioned Python/YAML packs (+ ZEN tables for tariff)

| | |
| --- | --- |
| **Decision** | Physics rules as **pure functions + YAML params** per semver pack; tariff/threshold decision tables via **ZEN/JDM** where business-editable tables help. Findings cite `rulepack://…#rule_id`. |
| **Why** | Industry pattern: rules-first for explainability, ML underneath. Rules-as-code in git, golden-tested, CI-gated, independent semver (Zerowatt breadth *with* audit trail). |
| **Rejected** | Drools/JVM BRMS (wrong ecosystem); durable_rules (stale); **LLM-generated rules as of-record** (belongs in L4 suggestions only); embedding rules inside engine code (kills independent release). |
| **Consumer D001–D003** | Domain × vertical × tariff axes; optimization methods as **first-class rule IDs**; dual path incomer → `domain/incomer` during cutover. |

**Attack:** *“Rules don’t scale; you’ll drown in if-statements.”*  
**Answer:** Scale lever is **catalog axes** (domain packs + vertical overlays + DISCOM tables + plant params), not a megaclass. Thresholds are calibrated parameters with fleet bounds (§3.9), not code forks per plant. Golden CI makes each pack a micro-product.

**Attack:** *“Have the LLM write the rules.”*  
**Answer:** LLM-assisted authoring may exist later as a **suggestion** path, but **runtime of record** must remain deterministic, golden-tested, semver-pinned. Otherwise M&V replay and dispute resolution die.

---

### 4.6 Tariff & PF — fully deterministic

| | |
| --- | --- |
| **Decision** | Tariff **calculator** encoding DISCOM orders as versioned data. No ML. |
| **Why** | Wrong PF penalty ₹ is not “soft error” — it is a false commercial claim. Bill reconstruction **±2% per line** is a hard gate before any plant’s ₹ estimates go live. |
| **Rejected** | Any learned tariff model. |

**Attack:** *“Tariffs are messy; ML could approximate.”*  
**Answer:** Approximation of a published tariff order is a **bug**, not a model. If tables are complex, invest in parsers and ZEN tables, not regression on historical bills as a substitute for the order.

---

### 4.7 Source-mix dispatch — greedy rules → MILP if needed

| | |
| --- | --- |
| **Decision** | Greedy deterministic solver first; MILP (OR-Tools/PuLP) when storage / inter-window coupling appears `[~]`. |
| **Rejected** | RL / learned dispatch — unjustifiable risk and opacity for read-only advisory + tariff coupling. |

---

### 4.8 Waste classifier — taxonomy table, not a model

| | |
| --- | --- |
| **Decision** | Deterministic mapping of finding category → one of six waste categories. |
| **Why** | It is a product taxonomy. Learning it only matters if free-form findings appear (P3, unlikely). |
| **Rejected** | Learned classifier in P0–P2. |

---

### 4.9 Per-plant calibration — parameters + hierarchical shrinkage, not per-plant model zoos

| | |
| --- | --- |
| **Decision** | Fleet-shared engine code; plant params bounded; hierarchical Bayesian / empirical-Bayes shrinkage on baseline params; threshold tuning from L5 reason codes. |
| **Rejected** | Per-plant full model retraining as the scaling strategy — ops explosion and M&V instability. |
| **Guardrail** | Calibration must never silently disable a category (mass rejection = CS signal). |

---

### 4.10 Time-series foundation models — ADR-014 shadow

| | |
| --- | --- |
| **Decision** | TimesFM 2.5 + XReg designated **shadow challenger** (optional `timesfm` extra). **Never** M&V baseline / SEC of record. |
| **Promotion gates** | Beat seasonal-naive **and** LightGBM on pinball (≥3 plants); no golden FP regression; batch latency SLO; human ADR for any citation-path change. |
| **Promotion record** | **Do not promote** (2026-07-13) — gates not evidenced; continue LightGBM primary for MD exceedance. |
| **Hosting default** | Pilot: self-hosted CPU batch. Vertex/BQ only if promotion + egress approved. |

**Attack:** *“You’re anti-innovation.”*  
**Answer:** We **scheduled** innovation: shadow → gates → optional challenger-primary for *exceedance only*. Refusing to put a 200M-param model on the M&V citation path is **pro-verification**, not nostalgia.

---

## 5. Structural decisions (repos, interfaces, runtime)

### 5.1 Three L3 repos (ADR-012)

| Repo | Role |
| --- | --- |
| `stamped-l3-core` | Deployable runtime: engines, schedulers, outbox, MLflow registry, lab export |
| `stamped-l3-rulepacks` | Semver physics/tariff artifacts + goldens |
| `stamped-l3-eval` | Corpus, backtest CLI, champion/challenger gates, **internal Lab UI** |

**Why not monorepo packages?** Independent release cadence for rule breadth (Zerowatt-like) without redeploying engines; golden CI per pack tag.  
**Why not five+ repos (per engine)?** Ops overhead; ADR-008 still wants **one Finding outbox** from one L3 deployable.  
**ADR-008 reconciliation:** Artifact repos ≠ a fourth intelligence *layer*; same pattern as L1 edge/cloud/bill split.

**Attack:** *“Submodule pin hell.”*  
**Answer:** Real cost — accepted. Mitigate with pinned platform tag + rulepack semver manifest loaded by core (never embed rules in engine code). Worse failure mode is shipping tariff rules that cannot be versioned independently of a hot-path deploy.

### 5.2 L2/L3/L4 boundaries you must defend as non-negotiable

| Boundary | Rule | Why |
| --- | --- | --- |
| L3 → L2 | Read-only query API; **no `L2_DATABASE_URL` in L3** | Layer topology (ADR-008); prevents god-service |
| L3 → L4 | Finding outbox only | Stable contract; L4 cannot reach into engines |
| L3 output | Numbers/evidence/confidence — **no prose** | Language models must not own the numeric interface |
| Read-only OT | Recommend never actuate | Safety + India compliance posture |
| Finding identity | `engine` + `engine_version` + `rule_or_model_ref` + optional `baseline_id` | Historical reproducibility for disputes |

### 5.3 Dual-mode execution (hot / warm / cold)

| Path | Engines | Point of the split |
| --- | --- | --- |
| Hot | MD/PF/suppressions after 15-min rollup | Trust-critical, fast, deterministic |
| Warm | EWMA/CUSUM, rulepack batch | Shift-scale detectors |
| Cold | TOW-P refit, backtests, TimesFM shadow | Never blocks hot path |

**Defense:** Expensive/uncertain work cannot jeopardise the bill-critical MD/PF path. Historian backfill replays cold with `late: true` tags.

### 5.4 Rulepack catalog axes (consumer D001–D002)

```text
domain/{pack}/{semver}/rules/{rule_id}.yaml   ← universal methods
verticals/{industry}/params.yaml              ← priors / thresholds only
tariffs/{discom}/{semver}/                    ← DISCOM tables
plants/{id}/params.yaml                       ← outside rulepacks repo
```

Merge order: domain → vertical → plant → tariff ₹.  
Optimization methods (furnace setback, stagger, shed, CMD rightsize…) are **separate rule IDs**, not one vague enum — so Findings and goldens can name the method.

---

## 6. Eval Lab & quality decisions

### 6.1 Why `stamped-l3-eval` exists (and is not L6)

| Decision | Defense |
| --- | --- |
| Eval owns corpus + backtest CLI + Lab UI | ADR-012: quality/forensics is a first-class artifact surface |
| Lab UI in eval, not core | Core stays headless runtime; UI is engineer tool |
| RunArtifact v1 is SSOT for UI | UI must never invent detections (PRODUCT/DESIGN) |
| Offline default + optional `CORE_LAB_URL` | Reproducible debug first; live attach second |
| P0 auth = shared secret | Speed for internal lab; OIDC deferred |

**Attack:** *“Why build a Lab UI at all?”*  
**Answer:** Precision product needs **forensic visibility of suppressions and shadow ML** equal to emits. Without it, engineers only see what escaped to L4 — FP root-cause becomes folklore.

### 6.2 Evaluation philosophy (cross-cutting)

Memorise the quality stack direction: **push checks downward.**

```text
Bill M&V (ultimate) → supervisor labels → shadow/canary → offline ML/LLM evals → deterministic gates
```

For L3 specifically:

| Gate | Defends against |
| --- | --- |
| Golden telemetry replay | Silent rule/engine regressions |
| Bill reconstruction ±2% | Fake ₹ |
| G14/IPMVP floors | Unverified baselines cited as M&V |
| Precision ≥0.75 (P1) / ≥0.85 (P2) `[~]` | Trust collapse |
| Alert budget (~5 findings/plant/day `[!]` hypothesis) | Attention exhaustion |
| Champion/challenger shadow ≥2 weeks | Hot-swap wishful thinking |
| Confidence priors then reliability curves | Fake “0.99 confidence” from raw detector scores |
| TimesFM promotion gates | Hype displacing TOW-P |

**Confidence cold-start priors (cite these):** tariff/MD arithmetic 0.85 · rules 0.75 · residual anomaly 0.55 · attribution 0.60 · LightGBM MD 0.50 · TimesFM **n/a — never ranks Rx**.

---

## 7. Phasing logic — why we built “boring ₹” first

| Phase | L3 shape | Defense of ordering |
| --- | --- | --- |
| **P0** | Deterministic MD/PF/tariff + incomer rulepack + calendar TOW + residual EWMA | Fastest bill-verifiable trust; de-risks Path B |
| **P1** | Full TOW-P, SEC, attribution, waste packs, LightGBM challenger, registry | Needs ~90 days clean data anyway |
| **P2** | MD exceedance primary ML, greedy dispatch, TimesFM shadow, auto-threshold | Forecast after baselines exist |
| **P3** | COP depth, MILP, NILM-lite hints | Only after taxonomy + meters justify |

**Sentence to use:** *We sequence by how quickly the DISCOM bill can falsify us — not by how impressive the model card looks.*

---

## 8. Competitive defense (Zerowatt and “AI-native” narrators)

| Their claim | Your counter | Evidence path |
| --- | --- | --- |
| Physics digital twin + thousands of rules | Semver rulepacks + deterministic engines + cited `rule_or_model_ref` | Finding contract + rulepack CI |
| Society of AI agents / NL brain | Template-fast-path P0 + bounded LangGraph P1; **rules veto final** | L4 architecture; six of seven tools deterministic |
| 20–30% savings narrative | 15–20% **bill-verified**, precision-first | L5 ledger + DISCOM reconciliation |
| Equipment health / PdM breadth | Electrical proxies + matrix profile (later); meter-tagged findings | No black-box health scores as ₹ owners |
| Foundation-model forecasts | Shadow until gates; LightGBM/TOW-P of record | ADR-014 + promotion record |
| Delay ignored | Counterfactual `opportunity_cost` ledger (modeled, never “verified”) | ADR-013 |

**Moral high ground line:** They optimise *story*; we optimise *invoice concordance and closure accountability*.

---

## 9. Steelman debate drills (practice aloud)

### Q1. “Isn’t this just a rules engine with ML lipstick?”

**Steelman opponent:** Rules will miss novel waste; ML finds structure in data; you’re underusing modern AI.

**Your answer:**
1. Agree that novel structure exists — that is why challengers (GBM, Isolation Forest, Matrix Profile, TimesFM shadow) exist.
2. Disagree that novel structure should own the **₹ citation path** before auditability.
3. Most paid waste in our six categories is **known physics + tariff math** (MD coincidence, PF slabs, holding, idle, SP drift, TOD). Rules+baseline win the *closed ₹*, not the Kaggle leaderboard.
4. Closure rate kills products that cry wolf. Precision architecture is a **GTM** choice as much as an ML choice.

### Q2. “Why not put an LLM in L3 to classify and estimate savings?”

**Answer:** Category without contract and ₹ without formula path are blocked at the L3/L4 boundary on purpose. LLMs hallucinate numbers under narrative pressure. L4 may *phrase* a finding; the finding’s `estimated_monthly_inr` must already decompose onto a tariff line from L3 tools. If LLM estimates ₹, L5 M&V becomes theatre.

### Q3. “Why TOW-P over GBM baseline if GBM is more accurate?”

**Answer:** Define accuracy. For M&V, accuracy includes **reproducible adjusted baseline** with published CVRMSE/NMBE. GBM wins point prediction; TOW-P wins **defensible savings attribution**. Challenger may later displace *detection* bands — not silently the ledger baseline.

### Q4. “Three repos is over-engineering for a startup.”

**Answer:** Cost is real. Benefit is shipping tariff/physics changes at **rulepack semver speed** with golden CI, while core release train stays stable — the exact capability competitors advertise as “1000s of rules.” Monorepo couples those cadences. L1 already accepted multi-repo at one layer.

### Q5. “When *would* you promote TimesFM or deep models?”

**Answer (specific):**
- **MD exceedance challenger-primary:** ADR-014 gates on ≥3 plants + no FP regression + latency — then maybe. Still not M&V baseline.
- **M&V baseline:** only with a new ADR inventing an audit story equivalent to printable regression (today: none accepted).
- **Anomaly primary:** if residual+suppression approach fails precision targets *and* a deep model beats it on adjudicated labels with explainability retrofit — currently literature does not justify leap.

### Q6. “Precision > recall means you’ll miss savings.”

**Answer:** Missed savings are recoverable in the next cycle; burned trust is not. Product math multiplies detection × **closure**. 60% closure on fewer high-precision Rx beats 20% closure on a firehose. Alert budget and ranking exist to surface the top ₹ opportunities first.

### Q7. “Why is waste classifier not ML?”

**Answer:** Categories are a designed ontology tied to playbooks and L4 templates. A classifier that invents a seventh free-form category creates orphan prescriptions. Taxonomy ownership stays with product/engineering.

### Q8. “Where does ML actually earn its keep then?”

**Honest answer (use this — it builds credibility):**
1. LightGBM MD exceedance ranking (P2 primary forecast).
2. Challenging baselines / residual analysis.
3. Isolation Forest / Matrix Profile for unknown or shape-level issues.
4. Hierarchical shrinkage (statistical learning) for cold-start.
5. Threshold calibration from L5 labels (the **most valuable learning loop**).
6. TimesFM shadow for transfer hypotheses — gated.

ML is load-bearing for **forecast ranking and calibration loops**, not for tariff truth.

### Q9. “How do you stop rulepacks becoming unmaintainable?”

**Answer:** Schema-validated YAML, one rule ID per method, golden fixtures as regression tests, bounded plant overrides, vertical overlays that **cannot invent Finding categories**, CI replay on pack tag, `rule_or_model_ref` on every Finding for blast-radius analysis.

### Q10. “Show me the decision hierarchy in 20 seconds.”

```text
Bill / physics exact?     → Rules & calculators
Auditor needs β coeffs?   → TOW-P baseline
Known deviation pattern?  → Rules + SPC residuals
Probabilistic ranking?    → LightGBM (etc.)
Cold-start UX only?       → Fleet priors (± shadow FM)
Language / playbook?      → LLM in L4 + veto
Anything else claiming ₹? → Reject until new ADR
```

---

## 10. What is decided vs open — do not overclaim

### Settled (safe to defend as “accepted”)

- L3 role: numeric Findings only; read-only; Python; interpretability gate
- Engine-of-record table in L3 §4.1
- ADR-012 three-repo topology
- ADR-014 TimesFM shadow + **do-not-promote** record
- ADR-013 counterfactual ledger type (L5 computes; not L3/L4 money truth)
- Rulepack axes + optimization-as-rule-IDs
- Eval Lab in eval repo; RunArtifact SSOT
- P0 = deterministic incomer MD/PF/TOD path
- L4 P0 template-fast-path (no LLM ownership of high-confidence singles)

### Open / evolving `[!]` — concede uncertainty; do not bluff

1. 15-min vs 1-min incomer aliasing for stagger quality  
2. Production-tag coverage floor for SEC  
3. How hard Indian auditors bind ASHRAE/IPMVP vs bill reconciliation alone  
4. Maintenance calendar reliability (WhatsApp-grade logs → FP source)  
5. ZEN depth: tariff-only vs business-editable thresholds  
6. Hierarchical prior grain: vertical vs asset-class  
7. Alert budget N=5 — product knob until pilot evidence  
8. LLM confidence semantics at L4 ranker after volume exists  

**Debate hygiene:** When challenged on an `[!]` item, say: *“That’s an open measurement question; the architecture is designed so the answer changes a parameter or gate, not the trust model.”*

---

## 11. Pocket citations (name-drop list)

Keep these ready:

| Claim | Cite |
| --- | --- |
| TOWT / CalTRACK / OpenDSM pedigree | LBNL TOWT papers; CalTRACK §3.7–3.8; OpenDSM; ASHRAE G14 / IPMVP |
| Deep AD progress often illusory | Wu & Keogh, TKDE/ICDE 2022 |
| GBM vs deep on short-term load | Energies 2025 Greek DSO comparative (LightGBM) |
| Industrial NILM immaturity | RSER 2024 systematic review |
| Rules-as-code runtime | GoRules ZEN for tables; Python+YAML for physics packs |
| Foundation model role | ADR-014 + promotion record |
| Repo topology | ADR-012 |
| Eval-as-spine | `04-evaluation-and-quality.md` Q1–Q18 |

Full URL list lives at the bottom of [`L3-intelligence-core.md`](L3-intelligence-core.md).

---

## 12. Minimal mental model of the runtime (for architecture arguments)

```text
L2 stores (TS, graph, tariff, production, features, baselines)
        │ read-only
        ▼
┌──────────────── stamped-l3-core ────────────────┐
│ hot:  MD / PF / suppressions                     │
│ warm: residual anomaly + rulepack batch          │
│ cold: TOW-P refit, registry, TimesFM shadow      │
│ loads rulepacks by semver (never embeds)         │
│ emits Finding → transactional outbox             │
│ lab_export → RunArtifact for eval UI             │
└──────────────────────────────────────────────────┘
        │
        ├─ rulepacks artifact (domain×vertical×tariff)
        └─ eval artifact (goldens, backtest, Lab UI)
        │
        ▼
L4: templates / bounded agent → rules veto → Prescription
        ▼
L5: workflow + WhatsApp + M&V ledger (incl. opportunity_cost)
```

---

## 13. One-page “closing argument” you can reuse

Stamped’s L3 is deliberately **anti-hype** in the places the bill can kill us, and **selectively modern** where ranking and cold-start benefit.

We chose **rules and printable baselines** as engines of record because our customer is not a Kaggle judge — it is a plant electrical engineer plus an invoice. We chose **classical ML** where probability ranking is the job (MD exceedance) and where challengers improve residuals. We chose **foundation models as shadow** so innovation has a lab without contaminating M&V. We placed **LLMs in L4** so language cannot invent money. We split **core / rulepacks / eval** so rule breadth can scale like a catalog while the Finding contract stays singular.

If you attack that design, you must either (a) propose a new audit path for neural ₹ claims stronger than TOW-P + tariff reconstruction, or (b) accept higher false prescriptions and argue why closure won’t collapse. Until then, the decisions stand.

---

## 14. Suggested study path (2 hours)

| Time | Action |
| --- | --- |
| 15 min | Re-read this §1–§2 aloud |
| 25 min | L3 §4.1 decision table + §5 eval targets |
| 20 min | ADR-012 + ADR-014 + promotion record |
| 20 min | L4 scope rule + tool table (six deterministic tools) |
| 20 min | Rulepacks DECISIONS + AUTHORING + one incomer rule YAML |
| 20 min | Drill §9 Q1, Q2, Q3, Q5, Q8 without notes |

**Feynman check:** Explain without jargon: *“Why doesn’t Stamped let the LLM pick the savings number?”* If you cannot, re-read §2.2 and §4.6.

---

*End of brief. When a new ADR changes engine-of-record status, update §4 and §10 in the same PR as the ADR — this document must not drift from accepted decisions.*
