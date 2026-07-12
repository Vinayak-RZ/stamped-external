---
type: Product Architecture
title: "L5 — Closure & Verification (Workflow, WhatsApp, M&V)"
description: "Deep research and design spec for Stamped Energy's Layer 5 — prescription workflow engine, WhatsApp-first notification router, IPMVP-style M&V engine, DISCOM bill reconciliation, savings ledger, and audit trail."
tags: [stamped-energy, technical, layer-spec]
timestamp: "2026-07-09T00:00:00Z"
---

# L5 — Closure & Verification (Workflow, WhatsApp, M&V)

*Research document, July 2026. Companion to the [technical architecture](../02-technical-architecture.md) §9 and §3.3. Siblings: [L2 — Universal Repository](L2-universal-repository.md) · [L4 — Knowledge & Reasoning](L4-knowledge-and-reasoning.md) · [L6 — Experience & Integration](L6-experience-and-integration.md).*

> **Honesty convention:** `[~]` approximate / benchmark-derived · `[!]` evolving — verify before customer-facing claims.
> Prices, rates, and vendor terms below were verified against public sources in July 2026 and **will drift** — re-verify before contracts.

---

## 1. Role in the 15–20% target — closure rate is the multiplier on detection

Every other layer in the Stamped stack produces *potential*. L5 is the only layer that produces the thing the customer actually buys: **a verified reduction in the DISCOM bill, in rupees per month**.

The savings equation for the platform is multiplicative, not additive:

```
verified_savings = detection_coverage × prescription_quality × closure_rate × persistence × verification_yield
```

| Factor | Owned by | Typical failure mode in the industry |
| --- | --- | --- |
| Detection coverage | L1–L3 | Blind spots (no sub-metering) |
| Prescription quality | L4 | Generic "energy is high" alerts nobody can act on |
| **Closure rate** | **L5 workflow + notification** | Insight dies in a dashboard or a PDF audit report |
| **Persistence** | **L5 re-detection + M&V window** | Fixed behaviour regresses in 6 weeks, nobody notices |
| **Verification yield** | **L5 M&V + bill reconciliation** | "Done" claimed but bill never moved; customer disputes the number |

The architecture doc sets the target: **≥60% of high-priority prescriptions acted within one billing cycle** `[!]` (§3.3 of the [technical architecture](../02-technical-architecture.md)). The arithmetic makes the stakes concrete. Suppose L3/L4 detect ₹6L/month of addressable waste at a plant with a ₹40L monthly bill (a 15% detection rate, consistent with the six-category stack). Then:

| Closure rate | Verified ₹/month | % of bill | Customer perception |
| --- | --- | --- | --- |
| 20% (dashboard-only delivery `[~]`) | ₹1.2L | 3% | "Another monitoring tool" |
| 40% | ₹2.4L | 6% | Marginal — churn risk |
| **60% (L5 target)** | **₹3.6L** | **9%** | Renews; expands to Path A |
| 80% (mature account) | ₹4.8L | 12% | Reference customer |

Two structural observations follow:

1. **Closure rate is the cheapest lever in the whole stack.** Doubling detection coverage requires more meters, more connectors, more models. Doubling closure rate requires workflow design, WhatsApp delivery to a named owner, and disciplined escalation — mostly product engineering, not data acquisition.
2. **Verification is what makes closure compound.** A verified ₹62k/month MD win is a sales asset, a renewal argument, and a calibration signal to L3. An unverified "we think we saved you money" is a liability. The trust anchor of the entire company — *savings verified on the DISCOM bill* — is implemented in this layer and nowhere else.

L5 also carries the **anti-churn loop**: reason codes from deferred/rejected prescriptions flow back to the L3 calibration layer (wrong owner, capex blocked, production constraint, already fixed), so the system stops re-issuing prescriptions the plant cannot or will not act on, and reframes ones it should.

---

## 2. Requirements from the architecture

### 2.1 Input contract — from [L4](L4-knowledge-and-reasoning.md)

L5 consumes the `Prescription` record exactly as specified in the architecture (§8.3). Fields L5 depends on and must not receive null:

| Field | L5 use |
| --- | --- |
| `id`, `priority`, `waste_category` | Workflow identity, queue ordering, ledger rollups |
| `what / why / who / effort / when` | WhatsApp card content; `who` must resolve to a **named person or role** in the L2 owner map |
| `impact {inr_monthly, kwh_monthly, tco2e_monthly, confidence_interval}` | Potential side of the ledger; escalation weighting |
| `evidence_refs[]` | Audit trail lineage; dispute-resolution evidence bundle |
| `mv_plan {method, baseline_id, verification_window}` | **The M&V contract.** L4 must propose a method and reference a locked baseline in the L2 baseline store *at issue time*, not at verification time |

**Hard requirement on L4:** a prescription without a resolvable owner and an M&V plan is rejected back to L4 (`status = blocked_incomplete`). Unowned work orders never close [32]; unverifiable prescriptions poison the ledger.

### 2.2 Output contract — to [L6](L6-experience-and-integration.md) and [L2](L2-universal-repository.md)

L5 writes three durable artifacts:

1. **Workflow event stream** — every state transition, notification send/delivery/read receipt, reminder, escalation, and reason code, append-only, consumed by the L6 prescription queue and the audit trail.
2. **`LedgerEntry` records** into the L2 M&V & intensity ledger (schema in architecture §6.5): `potential_kwh/inr`, `realised_kwh/inr`, `avoided_tco2e`, `mv_method`, `bill_line_refs[]`, `verification_status ∈ {pending | verified | disputed}`.
3. **Calibration signals** to L3: reason-code taxonomy counts per plant/category, closure latency distributions, verification-vs-estimate error (realised ÷ potential per category — feeds the L4 impact calculator's confidence intervals).

### 2.3 Non-functional requirements

| Requirement | Rationale |
| --- | --- |
| Notification delivery within 5 min of Rx issue for `urgency=high` | MD spikes are perishable — Monday 07:12 spike must reach the supervisor before the next co-start |
| Idempotent transitions; exactly-once ledger writes | Duplicate "Done" taps from WhatsApp webhooks must not double-count savings |
| Baselines immutable once a verification window opens | The single most attackable point in a customer dispute |
| Full lineage: bill line → LedgerEntry → Rx → finding → source tags | The "evidence bundle" a CFO or OEM auditor pulls |
| Works when the plant has one WhatsApp-capable phone and no dashboard logins | Band A plants have thin office staffing on night shifts |
| Multi-tenant, per-plant reminder/escalation policy | Escalation to an MD-owner in a promoter-run plant is different from a listed-company plant head |

---

## 3. Researched landscape

### 3.1 WhatsApp Business Platform — state of play, July 2026

**Pricing model.** Meta moved from conversation-based to **per-message pricing on 1 July 2025** [1][2]. Every delivered *template* message is billed individually by category. India switched to **INR billing in January 2026**, and marketing rates rose ~10% at the same time [2][3]. Current India base rates (verify at contract time — rate-card updates need only 1 month notice [1]):

| Message category | India rate (per delivered msg) | Notes |
| --- | --- | --- |
| Marketing template | ₹0.8631 | Flat — **no volume discounts** [2][3] |
| **Utility template** | **₹0.1150** | Volume tiers unlock up to ~30% lower at scale [1][3] |
| Authentication template | ₹0.1150 | Not relevant to Stamped |
| Service (free-form, within window) | **Free** | Since Nov 2024, service conversations free [1] |
| Utility template *inside* an open service window | **Free** | Critical design lever [1][3] |

**The 24-hour customer-service window.** When the user messages the business (including tapping a button), a 24-hour window opens. Inside it: free-form messages of any type are free, utility templates are free, and **interactive messages (buttons, lists) become available** [1][4]. Click-to-WhatsApp ads open a 72-hour fully-free window [1] — irrelevant for Stamped's B2B use but confirms the mechanics.

**Interactive messages** [4][5][7]:

| Type | Constraints | Template needed? | Usable outside 24-h window? |
| --- | --- | --- | --- |
| Reply buttons | ≤3 buttons, 20-char labels, 256-char IDs; webhook returns `button_reply` with the ID | No | **No** |
| List message | 1 button opening ≤10 rows | No | **No** |
| **Quick-reply buttons on an approved template** | ≤3 buttons | Yes (Meta approval) | **Yes — can be sent as a business-initiated notification** [5] |
| WhatsApp Flows | Multi-screen structured forms; sent via template `FLOW` button or in-window CTA | Yes for notification use | Yes via template [7] |

This is the pivotal fact for Stamped's UX: **a business-initiated prescription card can carry `[Acknowledge] [Done] [Defer]` quick-reply buttons via an approved utility template.** The user's tap opens a service window, inside which the richer list messages (e.g., a 10-row defer-reason picker) and free-form follow-ups cost nothing [1][4][5].

**Templates, quality, and rate limits** [6]:

- Templates are reviewed automatically at creation; must be `APPROVED` before sending. Utility templates must be genuinely transactional in wording or Meta reclassifies them as marketing (7.5× the price).
- Each template carries a **quality rating** from user feedback (blocks, reports, read rates); low quality can pause a template or the whole number's sending capacity.
- **Messaging limits are portfolio-based**, starting at 250 business-initiated messages/24 h (Tier 0) for unverified businesses and scaling automatically (checked every 6 h) to 1k → 10k → 100k → unlimited with business verification and healthy usage [6]. A Stamped plant generates perhaps 5–30 business-initiated messages/day, so even Tier 0 covers ~10 plants; verification removes the ceiling.
- **Opt-in is mandatory**: businesses must obtain consent before sending business-initiated messages. For Stamped this is contractual (onboarding form: name, role, WhatsApp number, consent checkbox) — clean because users are the customer's own staff.

**BSP landscape for India** [8][9][10][11]:

| Route | Cost structure | Fit for Stamped |
| --- | --- | --- |
| **Meta Cloud API direct** | ₹0 platform fee; Meta rates only; you build sending, webhooks, template mgmt, opt-out | Best unit economics; requires ~2–4 weeks eng effort; Meta support is ticket-only |
| **Gupshup** | Enterprise BSP; per-message markup ~₹0.10–0.15 + negotiated platform fees [9][11] | Overweight for Stamped's volumes; built for banks/fintech scale |
| **Twilio** | ~$0.005/msg + Meta fees; **USD invoicing** → GST/FX drag makes effective cost 30–50% higher than INR-billed providers [10] | Poor fit; only attractive if bundling US SMS (not needed) |
| **MSG91** | Positions "Meta's price is your price," monetises adjacent services [9] | Reasonable managed fallback; also strong for DLT SMS |
| **AiSensy** | ₹999/mo + ~₹0.20/msg markup on lower tiers [10] | SMB campaign tooling — Stamped doesn't need the marketing UI |
| **Interakt (Jio Haptik)** | ₹999–2,499/mo + per-msg markup on lower tiers [10][11] | D2C/Shopify-oriented; wrong shape |
| **Wati** | ~₹2,499–13,999/mo + per-agent inbox fees [11] | Shared-inbox SaaS; wrong shape |

**Cost model at Stamped's scale** `[~]`: a plant receiving 20 prescriptions/month, each generating ~3 business-initiated utility templates (issue, reminder, verification result) plus in-window traffic = ~60 paid utility messages ≈ **₹7/plant/month** at Meta base rates. Even at 500 plants, WhatsApp spend is ~₹3.5k/month — three orders of magnitude below one prescription's value. **Message cost is irrelevant; deliverability, template quality, and engineering control are the decision criteria.** This inverts the usual BSP-selection logic (which optimises marketing blast costs) and argues for the direct Cloud API.

**Fallback channels:**

- **SMS (India):** requires TRAI **DLT registration** — Principal Entity on an operator portal (Jio/Airtel/Vi/BSNL, valid across all), 6-char alphabetic header, per-template registration with `{#var#}` placeholders, PE–telemarketer binding; unregistered traffic is **silently dropped** by operator scrubbing. First-time setup 2–4 weeks; 2025 rules added mandatory category suffixes [12][13]. Worth doing once, early, so the fallback exists before it's needed.
- **Email:** near-zero deliverability urgency value on a plant floor; retain for the monthly sustainability pack and plant-head digests only (per architecture §9.2).
- **Voice call (manual):** the customer-success escalation of last resort — the P0 "fallback" is a human, and that's fine at 5–20 accounts.

### 3.2 Workflow engine — build vs buy

Three realistic families, evaluated against Stamped's actual workload — **entity lifecycle orchestration** (a prescription moving through six states over days-to-weeks, with timers, reminders, escalation, and human actions), *not* high-volume distributed transaction coordination:

| Option | Strengths | Costs / risks | Verdict for Stamped |
| --- | --- | --- | --- |
| **Temporal (self-host or Cloud)** | Durable execution, deterministic replay, mature SDKs, timers at scale [16] | Separate cluster (or vendor bill); code re-architected around workers/activities; replay semantics are overkill when state is a status column [14][15] | Defer — right tool for the wrong problem class at this stage |
| **BPMN engines (Camunda 8 / Zeebe)** | Visual process models, human-task support, enterprise governance [16] | BPMN modelling overhead; Zeebe cluster ops; Java-centric gravity; process is simple enough that BPMN adds ceremony, not clarity | No |
| **Custom state machine on Postgres** (+ transactional outbox + durable DB-backed timers; optionally DBOS-style library) | State lives in the prescription row — "restart and continue from committed status" is exactly the need [14][15]; zero extra infrastructure; transactional exactly-once with the ledger writes for free | Team owns retries, timer scheduler, observability — bounded scope for a 6-state machine | **Yes for P0–P2** |

The deciding questions from the build-vs-buy literature map cleanly [14][15]: Does the workflow need deterministic replay? No — entity-is-state suffices. Is workflow volume independent of app volume? No — tens of transitions per plant per day. Is the workflow core product logic encoding revenue and compliance? **Yes** — which is precisely the case where owning the engine is justified [4-appcreators]. The one discipline to import from Temporal-world: **timers must be durable rows in Postgres** (a `scheduled_actions` table polled by a worker), never in-process `sleep()`s, so reminders survive deploys and crashes [14].

**Idempotency & audit design patterns (established practice):**

- Every state transition is an INSERT into an append-only `prescription_events` table (event sourcing lite); the `prescriptions.status` column is a projection. Transition + ledger write + outbox message in **one Postgres transaction**.
- WhatsApp webhook handling keys on `(prescription_id, button_id, wamid)` — Meta redelivers webhooks, so dedupe on the WhatsApp message ID.
- Illegal transitions (e.g., `Done` on an already-`Verified` Rx) are recorded as rejected events, not silently swallowed — they show up in the audit trail as user intent.

### 3.3 M&V engine — the moat (deep dive)

#### 3.3.1 The IPMVP frame

IPMVP's four options, mapped to Stamped's reality [17][18][23][24]:

| IPMVP option | What it is | Stamped application |
| --- | --- | --- |
| **Option A** — retrofit isolation, key parameter measured | Measure the key parameter; stipulate the rest | Category rules where one parameter dominates: PF correction (measure PF, stipulate hours), CMD right-sizing (pure tariff arithmetic) |
| **Option B** — retrofit isolation, all parameters | Continuous measurement at the measure boundary (feeder/sub-meter) | Path A per-Rx verification: compressor SP drift, furnace holding load, chiller COP — where a feeder meter bounds the affected equipment |
| **Option C** — whole facility | Regression of facility-level (bill or incomer) consumption on independent variables; captures all interactive effects [23][24] | **The bill-truth backbone.** Path B accounts from day one; also the portfolio-level cap for every account |
| **Option D** — calibrated simulation | Building-energy model calibrated to bills | Not applicable — industrial process loads, no simulation budget; skip |

> **Note on naming:** the architecture doc §9.3 table swaps the conventional A/B/C labels `[!]` — this document uses **standard IPMVP naming** (C = whole facility, B = retrofit isolation with full measurement) and the architecture doc should be corrected to match.

**Measurement boundary** is the organising concept [18][23]: draw it around the equipment affected by the prescription; all energy crossing the boundary must be measured or estimated. Per-category default boundaries:

| Waste category (§3.1 of architecture) | Default boundary | Default M&V option |
| --- | --- | --- |
| Power quality & MD | Incomer (whole facility) | Option C on the **MD/kVA line** — billing-demand arithmetic is deterministic, noise is low |
| Furnace & process heat | Furnace feeder; else incomer during non-production windows | B if feeder metered; else C with window filtering |
| Idle & auxiliary loads | Incomer, non-production hours only | C variant: "non-production kWh" sub-series |
| Compressed air | Compressor house feeder | B (specific power kW per unit air proxy) |
| Cooling/HVAC/chillers | Chiller feeder or BMS kW | B with ambient-temperature routine adjustment |
| Source mix & TOD shifting | Multi-source meters + TOD registers on bill | C on the **TOD line items** — bill registers are the truth |
| PF / CMD contract items | Bill only | A — pure tariff computation, no regression needed |

#### 3.3.2 Statistical acceptance criteria — ASHRAE Guideline 14

ASHRAE G14 supplies the numeric gates Stamped's baseline models must pass before a verification claim is publishable [17][19][20]:

| Criterion | Threshold (monthly models) | Threshold (daily/hourly) |
| --- | --- | --- |
| NMBE (net mean bias error) | ±0.5% `[~]` | ±0.5% |
| CV(RMSE) of baseline model | ≤15% `[~]` (monthly); ≤25% commonly cited for calibrated models [19] | ≤25% |
| Savings uncertainty | <50% of reported savings at 68% confidence [19] | same |

The classical rule of thumb — Option C needs savings **>10% of baseline consumption** to be distinguishable from noise with monthly bills [19] — matters enormously for Stamped: *a single prescription* (say 1.5% of bill) is **not detectable** on the monthly bill alone, but the *portfolio of closed prescriptions* (8–15% cumulative) **is**. EVO's own analysis shows sub-10% savings become detectable when using **daily or hourly interval data** instead of twelve monthly points [19] — which Stamped has from the incomer meter. This resolves the core tension: **per-Rx verification runs on interval data (Option B/C-hourly); the customer-facing bill claim runs on Option C monthly with the portfolio**.

#### 3.3.3 CalTRACK / OpenEEmeter — the automation template

CalTRACK methods (reference implementation: OpenEEmeter) standardise exactly what Stamped must automate: **avoided energy use** = counterfactual baseline prediction − metered consumption, computed from meter + weather data with fixed model forms (billing/daily methods, hourly TOWT-style methods) [21][22]. Directly importable practices:

- **Fractional Savings Uncertainty (FSU)** reporting, using the modified ASHRAE G14 formulation with autocorrelation correction; CalTRACK procurement programs set FSU gates of 15–25% at 90% confidence [21]. Stamped should print FSU (or an equivalent CI) next to every verified number — this is the "confidence interval" the L4 schema already promises.
- **Portfolio aggregation**: individual-site (here: individual-Rx) uncertainty is high; aggregated portfolio uncertainty shrinks ~√N. CalTRACK explicitly blesses portfolio-level claims where site-level noise is unacceptable [21] — the formal justification for Stamped's two-tier attribution (below).
- **Data-quality preconditions**: ≥12 months baseline (Stamped: accept 9–12 with a flag `[~]`), coverage thresholds, exclusion of estimated reads — encode as automated gates before a baseline can be locked.
- Industrial caveat `[!]`: CalTRACK models are weather-driven (buildings). Stamped's independent variable is **production**, not degree-days — the model forms need swapping (kWh ~ f(tonnage, SKU mix, shifts, ambient)), but the *procedural* skeleton (fixed model forms, fit gates, FSU, portfolio rollup) transfers intact. This is the moat: nobody has published a CalTRACK-equivalent for Indian industrial production-normalised M&V.

#### 3.3.4 Baseline adjustments, locking, and non-routine events

IPMVP savings algebra [18]:

```
savings = (baseline period use ± routine adjustments ± non-routine adjustments) − reporting period use
```

- **Routine adjustments** — variables expected to vary: production volume, product mix, ambient temperature, shift count. Handled inside the regression.
- **Non-routine events (NREs)** — static factors that were assumed constant but changed: new production line, added compressor, changed shift pattern, plant expansion [17][20]. Handled by explicit, documented, one-off **non-routine adjustments (NRAs)** — the single largest source of Option C disputes [17]. Detection: monitor static factors (L2 context store: shift calendar, asset registry, CMD changes) + automated change-point detection on the incomer series; every NRA must be a signed, versioned artifact in the audit trail.
- **Baseline locking** `[design decision]`: when L4 issues an Rx, the `mv_plan.baseline_id` pins a **specific, immutable, versioned baseline model** (coefficients + training window + fit stats hash). Later model improvements create *new* baseline versions for *new* prescriptions; a locked verification is never retro-recomputed except through a formal NRA with dual reporting (original + adjusted). Without this, every model retrain silently rewrites customers' historical savings — a credibility time-bomb.

#### 3.3.5 Attribution when prescriptions overlap in time

The industry answer, from ESCO/EPC practice: **don't fight interactive effects at the measure level — verify the net at the facility level** [23][24][17]. When multiple ECMs interact (lighting affects HVAC; in Stamped's world, furnace scheduling affects MD and TOD simultaneously), IPMVP directs you to Option C for the aggregate and treats per-measure numbers as engineering allocations, not measurements [24][17].

Stamped's two-tier design:

1. **Tier 1 — Account truth (Option C):** monthly whole-facility avoided-use + bill-line reconciliation produces `verified_account_savings` — the number on the invoice-facing ledger. This is what "verified on the DISCOM bill" means, and it is portfolio-of-Rx by construction.
2. **Tier 2 — Per-Rx attribution:** each Rx gets its own boundary estimate (Option A/B where metered, engineering estimate where not). Then a **reconciliation constraint**: `Σ per-Rx attributed savings ≤ Tier-1 account savings` for the period. If the sum exceeds the facility-level truth, per-Rx numbers are scaled down pro-rata (by boundary-measurement confidence, metered Rx protected first) `[design decision]`. Per-Rx numbers are displayed with an "attributed" label; the account number carries the "verified" label. This mirrors how performance-contract ESCOs survive audits: the guaranteed number is facility-level; measure-level splits are supporting detail [24].

Time-overlap handling: when Rx-B closes while Rx-A's verification window is open inside the same boundary, Rx-A's counterfactual absorbs Rx-B's effect unless boundaries are disjoint. Rules: (a) disjoint feeder boundaries → verify independently; (b) shared boundary → verify jointly as a **prescription bundle** with one combined window and allocate by engineering estimate; (c) MD/TOD/PF line items → deterministic tariff arithmetic per event, no regression, so overlap is a non-issue.

### 3.4 Indian HT bill reconciliation — what the bill actually says

The DISCOM bill is the trust anchor, so L5 must speak its exact grammar. HT industrial bill line items (state-specific rates; structure is broadly common) [26][27][28][29][35]:

| Line item | Mechanics | Reconciliation relevance |
| --- | --- | --- |
| **Demand charge** | Billed on **billing demand** = max(recorded MD, 75–85% of contract demand — e.g. JVVNL: max(MD, 75% CMD) [28]; some boards use max of MD, 50% CMD, 75% of highest billed MD in 11 months [26]) | MD prescriptions only pay off **down to the CMD floor** — reducing recorded MD below 75–85% of CMD saves nothing until CMD itself is renegotiated. The impact calculator (L4) and the verifier (L5) must both encode the floor |
| **Excess demand penalty** | Recorded MD > CMD → 1.5–2× rate on the excess [29][35]; repeated breaches can force CMD escalation [28] | Highest-certainty verification: a penalty line that disappears is unambiguous |
| **Energy charge** | ₹/kWh or ₹/kVAh on consumption; kVAh billing makes PF directly monetary | kVAh states: PF gains show in the energy line, not a separate PF line — verifier must know which regime applies |
| **TOD charges/rebates** | Peak +20–35%, off-peak −15–25% on slot energy [27] | Load-shift Rx verified from **TOD register deltas** on the bill — deterministic |
| **PF incentive/penalty** | Slabbed: e.g. rebate 0–7% of the bill for PF 0.95→1.00, penalty below 0.90 [26][27] | Small, sharply non-linear line; verify on the printed PF value and slab |
| **FPPCA / FPPAS / FCA** | Fuel & power-purchase cost pass-through; Rule 14 (Elec. Amendment Rules 2022) enables **monthly automatic pass-through** up to 5% [30]; ~₹0.28–0.55/kWh typical [27]; TN/UP/WB don't allow automatic adjustment [30]; UP litigation in 2026 over stuffing legacy dues into FPPAS shows how volatile this line is [31] | **Pure noise for savings purposes.** Verified savings must be computed at *constant reference rates*, with FPPCA swings reported separately |
| **Electricity duty** | State tax, 6–20% on assessed charges [27] | Derived line — moves proportionally; exclude from attribution |
| **Misc** | Wheeling, meter rent, cross-subsidy surcharge (open access), arrears | Flag, exclude |

**Month-to-month noise sources that will drown a naive bill-delta claim:**

1. **Tariff revisions** — SERC orders change rates annually, sometimes mid-year [27].
2. **FPPCA swings** — monthly, ±tens of paise/kWh, entirely exogenous [30][31].
3. **Production changes** — the dominant kWh driver; a 15% production dip mimics a 15% "saving".
4. **Billing-cycle length** — 28–33 day reads; normalise to daily.
5. **Calendar mix** — festivals, Sundays, shutdown weeks.
6. **Weather** — for HVAC-heavy verticals (pharma) `[~]`.
7. **One-off lines** — arrears, subsidy true-ups, penalty reversals.

**The normalisation that survives scrutiny** (recommended algorithm in §4.4): decompose the bill delta into *rate effects* (tariff/FPPCA — not ours), *volume effects* (production — normalised away by regression), and *efficiency effects* (ours). Report all three, claim only the third. Presenting the decomposition openly is itself the trust move: the customer's accountant can follow every line. "The bill is final authority" then means: **the verified claim is stated as specific bill lines moving in the predicted direction after removing rate and volume effects, with the arithmetic attached** — not "your bill went down, we take credit."

### 3.5 Savings ledger — design precedents

Established patterns from financial ledger engineering, applied to savings accounting:

- **Append-only, double-entry-inspired:** entries are never updated or deleted; corrections are reversal entries referencing the original. Every entry carries `(prescription_id, period, mv_method, baseline_id_version, bill_line_refs[], author, created_at)`.
- **Dual (triple) currency:** every entry carries ₹, kWh, and tCO₂e as separate columns computed at entry time with the versioned tariff and emission factor — never derived on read, so a later factor update cannot silently rewrite history (matches architecture §11.4).
- **Potential vs realised as distinct entry types:** `potential` posted at Rx issue (L4 estimate), `realised` posted at verification. The dashboard "gap" (potential − realised) is itself a KPI — chronic gaps in a category indicate L4 over-estimation and feed calibration.
- **Dispute states:** `verification_status ∈ {pending, verified, disputed, resolved_upheld, resolved_adjusted, resolved_withdrawn}`. A dispute freezes the entry, opens a case with the evidence bundle, and resolution posts a new entry — the original is never edited.
- **Evidence bundles:** a per-entry exportable artifact — Rx card, evidence_refs time-series snapshots, locked baseline definition + fit statistics, bill PDF pages with parsed lines highlighted, NRA log, FSU/CI computation. This is what an OEM sustainability auditor or a CFO's internal-audit team receives. Generating it must be one click (L6), which means L5 must store every input immutably at verification time.

### 3.6 Closure-rate mechanics — what actually drives action in plants

Evidence from CMMS/maintenance-operations research maps almost one-to-one onto prescription closure:

| Finding | Source | L5 design consequence |
| --- | --- | --- |
| Unassigned work orders have "no owner, no urgency, no natural completion date" — assignment must be mandatory at creation, with escalation if unclaimed (typical: 4 h for P1, 24 h standard) | [32] | Rx cannot enter `Open` without a resolved named owner; unacknowledged high-priority Rx escalates in hours, not days |
| Invisible age is the biggest backlog driver; sort queues by age × priority × criticality; overdue anything triggers management escalation | [32] | Queue ordering = `score × age`; weekly plant-head digest leads with the oldest high-value open Rx |
| Users receiving >20–30 alerts/day ignore most of them; batch non-urgent into digests; reserve immediate pings for genuine urgency | [33] | **Per-role open-Rx cap** (already in L4 ranker, §8.5) + notification budget: ≤3 business-initiated pushes/role/day `[~]`; everything else rides the daily digest |
| Created-vs-completed ratio is the earliest signal of overload — issuing faster than the plant closes guarantees backlog and disengagement | [34] | L5 throttles L4: if plant closure ratio <0.7 over 14 days, new non-urgent Rx queue rather than send `[design decision]` |
| Completed-but-not-closed work inflates backlog; mandatory lightweight closeout beats optional thorough closeout | [32] | "Done" is one WhatsApp tap + optional photo; do **not** demand forms — M&V verifies anyway, so closeout friction buys nothing |
| Alarm rationalization (ISA-18.2 / EEMUA 191): fewer, prioritised, owner-mapped alarms outperform comprehensive alerting | [33] | The L4 ranker's quick-wins-first and dedup rules are the "rationalization" stage; L5 enforces the delivery budget |
| Escalation response rate and notification engagement must be measured and tuned quarterly, not assumed | [33] | L5 instruments per-template read rates, tap rates, time-to-ack — reviewed per account monthly |

**Reason-code taxonomy** (deferred/rejected → L3/L4 calibration), synthesised from CMMS failure categories [32] + Stamped architecture §9.1:

| Code | Meaning | Calibration effect |
| --- | --- | --- |
| `wrong_owner` | Routed to someone who can't act | Fix L2 owner map; re-route, don't penalise category |
| `production_constraint` | Can't act without stopping production | L4 re-frames to maintenance-window scheduling; lower urgency |
| `capex_blocked` | Needs spend approval | Split Rx: behavioural interim + capex proposal to plant head track |
| `already_fixed` | Condition self-resolved / duplicate | L3 detection latency or dedup gap — engineering signal |
| `disagree_diagnosis` | Plant disputes the Why | High-value signal: drop category confidence, trigger review |
| `safety_quality_risk` | Action risks product/safety | Hard veto — add to plant-specific rule exclusions |
| `no_response` (system-assigned) | Timed out through escalation | Distinct from explicit deferral; drives owner-map and channel review |

---

## 4. Recommended approach

### 4.1 Workflow engine — custom state machine on Postgres

**Decision: build** — a 6-state entity lifecycle with durable timers on the existing Postgres, using the transactional-outbox pattern; no Temporal/Camunda at P0–P2 `[!]` (revisit if multi-step machine-to-machine orchestration emerges, e.g., automated CMD renegotiation workflows).

**States and transitions:**

```
                       ┌──────────────┐
   L4 issues Rx        │   BLOCKED    │  (missing owner / mv_plan — bounced to L4)
        │              └──────────────┘
        ▼
   ┌────────┐  ack (tap/dashboard)  ┌─────────────┐  done (tap+optional photo) ┌────────┐
   │  OPEN  │ ────────────────────► │ IN_PROGRESS │ ─────────────────────────► │  DONE  │
   └────────┘                       └─────────────┘                            └────────┘
     │   │                             │                                          │ M&V window
     │   │ defer(reason)               │ defer(reason)                            ▼ closes
     │   ▼                             ▼                                   ┌────────────┐
     │  ┌──────────┐   resurface timer (48h–14d by reason)                 │  VERIFIED  │
     │  │ DEFERRED │ ────────────────────────► back to OPEN                └────────────┘
     │  └──────────┘                                                              │ shortfall /
     │ reject(reason)                                                             ▼ NRE / customer query
     ▼                                                                     ┌────────────┐
   ┌──────────┐                                                            │  DISPUTED  │→ resolved_*
   │ REJECTED │  (terminal; reason code mandatory; feeds calibration)     └────────────┘
   └──────────┘
```

Key rules:

- **Every transition requires an actor** (user, system-timer, M&V engine) and writes one `prescription_events` row; ledger postings and outbox notifications commit in the same transaction.
- **SLA timers** (durable rows): ack timeout `urgency=high` 4 h → re-ping owner; 24 h → escalate to plant head `[~]` per-plant configurable; standard Rx 48 h / 7 d. Done-but-unverified past `verification_window + 1 billing cycle` → auto-flag for review, never auto-verify.
- **Deferral is a snooze, not a grave:** deferred Rx resurface on a timer set by reason code (production constraint → next planned maintenance window from the L2 shift calendar).
- **Idempotency:** webhook dedupe on WhatsApp `wamid`; transition API requires `expected_current_state` (optimistic concurrency) so double-taps are no-ops recorded as duplicate-intent events.

### 4.2 Notification design — WhatsApp-first, direct Cloud API

**BSP decision: Meta Cloud API direct**, with MSG91 as the contracted **SMS-DLT fallback** provider `[!]`.

Rationale: (a) message spend is negligible (~₹7/plant/month `[~]`, §3.1) so BSP markups buy nothing; (b) Stamped's differentiation lives in the interaction design — button IDs wired to workflow transitions, list-message reason pickers, per-template quality telemetry — which demands API-level control a SaaS inbox obscures; (c) USD-billed Twilio carries a 30–50% effective cost penalty and no India-specific value [10]; (d) the campaign UIs of AiSensy/Interakt/Wati solve marketing problems Stamped doesn't have [10][11]. Cost of the decision: 2–4 weeks of engineering for send pipeline, webhook receiver, template lifecycle management, and opt-in/opt-out records — infrastructure Stamped needs to own anyway for the audit trail. Prerequisite: Meta Business verification early (unlocks tier upgrades and 6k templates) [6].

**Message architecture:**

| Moment | Vehicle | Category / cost |
| --- | --- | --- |
| Rx issued | **Utility template** with quick-reply buttons `[Acknowledge] [Done] [Defer]`, ≤3 per Meta limit [5]; body = What/Why/₹/Who/When card | ₹0.115 |
| User taps any button | Opens 24-h service window; **list message** with defer-reason taxonomy (≤10 rows [4]) or free-form confirmation | Free in-window [1] |
| Reminder (unack'd) | Utility template, escalating copy | ₹0.115 |
| Escalation to plant head | Utility template + dashboard flag | ₹0.115 |
| Verification result ("₹58k verified on your March bill — line: MD charges") | Utility template; the single most retention-valuable message the platform sends | ₹0.115 |
| Daily/weekly digest | Utility template (compressed) or email for plant head | ₹0.115 |
| Photo evidence of Done | Free-form inbound; store to evidence bundle | Free |

Template discipline: keep wording strictly transactional (order-update register) so Meta doesn't reclassify utility → marketing at 7.5× price [1][6]; monitor per-template quality rating weekly and A/B copy only through new template registrations [6].

**Notification budget (anti-fatigue):** hard cap 3 business-initiated pushes per role per day `[~]` [33]; queue overflow into the digest; per-account monthly review of read/tap/time-to-ack metrics.

**Fallback chain:** WhatsApp delivery-failure webhook (or undelivered 6 h) → DLT-registered SMS with dashboard short-link → next-day customer-success call task for high-priority Rx. Complete DLT setup (entity, `STMPDE`-style header, templates, PE-TM binding) in P0 — it takes 2–4 weeks of calendar time and can't be rushed when needed [12][13].

### 4.3 M&V methodology — per prescription category

**Stance: Option C (whole-facility, production-normalised, bill-reconciled) is the account-level truth; Option A/B boundary measurements attribute per-Rx; per-Rx claims are capped by the account-level number** (§3.3.5). FSU/CI printed on everything [21].

| Category | Method | Baseline & adjustment | Verification window |
| --- | --- | --- | --- |
| MD & power quality | Deterministic tariff arithmetic on billing demand (Option A-like) + incomer interval data | MD histogram 90 d; billing-demand floor (max(MD, 75–85% CMD)) encoded per DISCOM [26][28] | 1–2 billing cycles |
| TOD shifting | TOD-register deltas on the bill, production-normalised | Slot-share baseline (kWh% per slot) over 90 d | 1 billing cycle |
| PF / CMD contract | Pure bill computation on PF slab / CMD terms [26] | Printed PF, 6-month history | 1 billing cycle |
| Idle & auxiliary | Option C sub-series: non-production-hour kWh vs shift calendar | Non-production baseline band per shift template | 2–4 weeks interval + bill confirm |
| Compressed air | Option B on compressor feeder (specific power) | kW ~ f(production proxy, pressure band) | 2–4 weeks |
| Furnace / process heat | Option B on feeder; else windowed Option C | SEC regression kWh/ton with product mix | 4–6 weeks |
| Chiller / HVAC | Option B with ambient routine adjustment `[~]` | COP proxy ~ f(ambient wet-bulb, load) | 4–8 weeks (season-aware) |
| Account total | **Option C monthly + interval**, CalTRACK-style automated pipeline | ≥9–12 months bills + incomer; kWh ~ f(production, calendar, ambient); G14 gates (CV(RMSE), NMBE) before lock [17][19][21] | Rolling monthly, cumulative |

Baseline governance: locked & versioned at Rx issue (§3.3.4); NRE watchlist from L2 static factors + change-point detection; NRAs are signed artifacts; dual reporting on any adjusted history.

### 4.4 Bill reconciliation algorithm

Monthly, on bill ingest (L1 parsed `BillLine`s):

```
1. VALIDATE   parse vs tariff model; recompute each line from registers
              (kWh, kVAh, MD, TOD registers, PF); flag DISCOM arithmetic
              errors (a customer-delight byproduct — billing mistakes found)
2. NORMALISE  daily-ise for cycle length; snapshot tariff version;
              extract FPPCA/duty as exogenous rate components
3. DECOMPOSE  Δbill = rate effect (tariff/FPPCA at baseline volumes)
                    + volume effect (production regression at baseline rates)
                    + efficiency effect (residual)          ← ours to claim
4. ATTRIBUTE  map efficiency effect to bill lines: MD line → MD prescriptions
              (deterministic); TOD registers → shift Rx; energy line →
              Option C avoided-use estimate with FSU
5. RECONCILE  compare Σ per-Rx attributed vs account-level efficiency effect;
              scale attribution if Σ exceeds cap; post LedgerEntries with
              bill_line_refs[]; verified where |modelled − billed| within
              tolerance band, else → disputed queue for analyst review
6. REPORT     customer-facing statement: three-way decomposition shown
              openly; verified ₹ at constant reference rates; FPPCA/tariff
              movements reported but not claimed
```

Tolerance band: verification passes when the billed line movement is within the FSU band of the modelled saving `[~]`; outside band → human-in-the-loop review before anything is shown as "verified." At P0 volumes (5–20 accounts) an analyst reviews **every** verification — automation earns trust before it earns autonomy.

### 4.5 Savings ledger & audit trail

Implement per §3.5: append-only Postgres tables (`ledger_entries`, `prescription_events`, `baseline_versions`, `nra_log`, `notification_log`), reversal-only corrections, triple currency computed at post time with versioned tariff + emission factors, dispute lifecycle, one-click evidence bundle export (PDF/ZIP) per entry and per period. Row-level immutability enforced by revoking UPDATE/DELETE from the application role; periodic hash-chain over the event stream `[!]` (cheap tamper-evidence, defer cryptographic signing until an enterprise customer asks).

---

## 5. How this layer is tested and evaluated

| Test class | Method | Pass criteria |
| --- | --- | --- |
| **M&V backtest on historical bills** | For every onboarded plant: fit baseline on months 1–9, "predict" months 10–12 with no interventions; measure phantom savings | Phantom savings ≈ 0 within FSU band; NMBE ±0.5%, CV(RMSE) within G14 gates [17][19]; any plant failing gates gets `low-confidence M&V` flag and Option C claims are withheld |
| **Synthetic intervention injection** | Inject known reductions (e.g., −8% non-production kWh) into replayed historical data; run the full pipeline | Recovered savings within FSU of injected truth across categories |
| **Billing-demand floor unit tests** | Golden test suite per DISCOM template (UPCL, MSEDCL, DHBVN, PVVNL, JVVNL…) covering floors, penalties, PF slabs, TOD math [26][28] | Recomputed bill lines match real anonymised bills to the rupee |
| **Workflow simulation** | Property-based tests over the state machine (no illegal transitions, no lost timers across simulated crashes/deploys); chaos test: kill worker mid-transaction | Zero orphaned states; exactly-once ledger postings under webhook redelivery |
| **Notification deliverability** | Track per-template: delivered %, read %, tap %, time-to-ack; Meta quality rating; fallback-trigger rate | Delivered ≥98% `[~]`; template quality ≥ Medium; time-to-ack P50 < 4 h for high-priority; fatigue check — pushes/role/day ≤ budget |
| **Closure funnel metrics** | Issued → acked → done → verified conversion per plant/category/owner; created-vs-completed ratio [34] | ≥60% high-priority acted within one billing cycle (architecture §3.3) `[!]`; ratio ≥0.7 sustained |
| **Dispute-rate tracking** | Disputed ÷ verified entries, monthly, per category; time-to-resolution; % resolved upheld | Dispute rate <5% `[~]` and falling; upheld ≥80% (else the pipeline is over-claiming) |
| **Estimate calibration** | Realised ÷ potential per category (the L4 feedback loop) | Median within 0.7–1.2 `[~]`; drift triggers impact-calculator re-review |
| **Evidence bundle audit drill** | Quarterly: generate a bundle for a random verified entry; walk it as a hostile auditor | Every number reproducible from bundle contents alone |

The backtest suite doubles as the **sales asset**: "we ran our M&V engine against your last 24 bills before claiming anything" is a differentiated pre-sales motion `[!]`.

---

## 6. Build phasing P0–P3

| Phase | Scope | Deliberately excluded |
| --- | --- | --- |
| **P0** (wks 1–8, 5–10 plants) | Postgres state machine (6 states, durable timers, event log); Cloud API integration — 4 utility templates (issue/reminder/escalation/verified) with quick-reply buttons; opt-in capture at onboarding; Meta business verification; **DLT registration started week 1**; MD/TOD/PF deterministic verifiers; Option C monthly baseline (production-normalised) with G14 gates; manual analyst review of all verifications; append-only ledger + basic evidence export; reason codes (7-code taxonomy) | Auto-verification; per-Rx attribution beyond deterministic categories; WhatsApp Flows; SMS sending (registration only) |
| **P1** (mo 3–6) | Option B feeder verification (compressed air, furnace); interval-data (daily/hourly) Option C for sub-10% detectability [19]; FSU computation on every claim [21]; SMS fallback live; escalation policies per-plant configurable; closure-funnel dashboards; L3 calibration feed live; NRE watchlist + NRA workflow | Chiller/ambient models; portfolio benchmarking |
| **P2** (mo 6–12) | Auto-verify within tolerance band (analyst on exceptions only); prescription bundles for shared-boundary overlap; dispute lifecycle + customer-facing evidence bundles; hash-chained audit log; ambient-adjusted HVAC M&V; multi-plant ledger rollups for listed accounts | — |
| **P3** | Fleet-level FSU-weighted portfolio reporting; WhatsApp Flows for structured closeout (photo + parts + notes) `[!]`; predictive closure scoring (which Rx will stall — pre-emptive escalation); customer-side maker-checker approvals for NRAs | — |

Dependency note: P0 M&V needs ≥9 months of historical bills at onboarding (L1 bill ingest backfill) — make historical bill collection a **contractual onboarding requirement**, not a nice-to-have.

---

## 7. Open questions

1. **Verification tolerance band** — what |modelled − billed| gap auto-verifies vs routes to analyst? Needs empirical setting from the first 3–5 accounts' noise floor `[!]`.
2. **Baseline window for seasonal verticals** — 9 months may straddle one season; do pharma/HVAC-heavy accounts require a full 12-month gate before Option C claims, delaying the account-level number past the 90-day program window? `[!]` Interim answer may be interval-data Option B only.
3. **Who arbitrates disputes contractually?** The 90-day program contract should name the method (this doc) and the arbiter (joint review with named plant engineer) — legal template needed.
4. **CMD renegotiation as a prescription type** — savings are real (billing-demand floor) but require a DISCOM application by the customer; how does verification treat a 2-month regulatory lag? `[!]`
5. **WhatsApp number strategy** — one Stamped number for all plants vs per-account numbers (quality-rating blast radius vs operational overhead) `[!]`.
6. **Meta pricing drift** — per-message rates change on 1-month notice [1]; utility→marketing reclassification risk on template copy; monitor quarterly. Low ₹ exposure but template-pause risk is operational.
7. **kVAh-billing states** — PF effects fold into the energy line; does the decomposition need a fourth (reactive) term for MSEDCL-type regimes? `[~]`
8. **Emission-factor vintage in the ledger** — state factor vs CEA national grid factor for tCO₂e postings; customer overrides create cross-account comparability gaps (architecture §11.4) `[!]`.
9. **Evidence-bundle retention & data residency** — bills and production data in bundles are commercially sensitive; retention policy and India-region storage commitments need enterprise-contract language.
10. **Throttling L4** — the closure-ratio-based issue throttle (§3.6) trades short-term detected-₹ optics for long-term engagement; needs product sign-off since it deliberately hides findings from an overloaded plant.

---

# Citations

1. https://developers.facebook.com/docs/whatsapp/pricing/ — Meta, WhatsApp Business Platform pricing (per-message model effective 1 Jul 2025; free service window; utility-in-window free; volume tiers; notice periods).
2. https://blueticks.co/blog/whatsapp-business-api-pricing-2026 — WhatsApp API pricing 2026; India INR rates and Jan 2026 rate changes.
3. https://mindlytics.in/blog/whatsapp-business-api-pricing-india-2026 — WhatsApp Business API pricing India 2026 (₹0.8631 marketing / ₹0.1150 utility; delivery-triggered billing).
4. https://developers.facebook.com/docs/whatsapp/guides/interactive-messages/ — Meta, interactive messages (reply buttons, list messages, Flows; 24-h window restriction for non-template interactive).
5. https://developers.facebook.com/docs/whatsapp/api/messages/message-templates/interactive-message-templates/ — Meta, interactive message templates (quick-reply buttons usable in business-initiated notifications).
6. https://developers.facebook.com/docs/whatsapp/message-templates/guidelines — Meta, template fundamentals (approval, quality rating, portfolio-based messaging limits, template caps).
7. https://developers.facebook.com/docs/whatsapp/flows/guides/sendingaflow/ — Meta, sending WhatsApp Flows (FLOW template button).
8. https://bizeract.com/blog/whatsapp-cloud-api-vs-twilio-india — Cloud API vs Twilio vs Indian BSPs decision guide.
9. https://richautomate.in/blog/msg91-vs-gupshup-india-2026-pricing-decoded — MSG91 vs Gupshup pricing structures 2026.
10. https://codingclave.com/guides/whatsapp-api-pricing-india-2026-comparison — Five-BSP India price comparison 2026 (AiSensy, Interakt, WATI, Gupshup, Twilio, direct API; USD-billing penalty).
11. https://richautomate.in/blog/gupshup-vs-wati-vs-interakt-india-2026 — Gupshup vs Wati vs Interakt platform-fee/markup models.
12. https://www.openmalo.com/blog/india-dlt-sms-marketing-setup-guide — TRAI DLT registration walkthrough (PE, headers, templates, timelines).
13. https://metareachmarketing.com/trai-dlt-compliance-guide-india-2026.php — TRAI/DLT compliance 2026 (silent blocking, category suffixes).
14. https://martinfric.dev/blog/posts/workflow-engine-why-not-temporal — Entity-lifecycle case for a custom engine over Temporal; durable DB timers.
15. https://dev.to/contrite42/durable-workflows-on-postgres-what-you-dont-need-temporal-actually-buys-you-3o0f — Postgres-backed durable workflows (DBOS) vs dedicated orchestrators.
16. https://www.kai-waehner.de/blog/2025/06/05/the-rise-of-the-durable-execution-engine-temporal-restate-in-an-event-driven-architecture-apache-kafka/ — Durable execution engines vs BPMN (Camunda/Zeebe) landscape.
17. https://www.energy.gov/sites/default/files/2024-10/mv_guide_5_0.pdf — US DOE FEMP M&V Guidelines v5.0 (options, NRAs, Option C challenges).
18. https://evo-world.org/images/corporate_documents/IPMVP-Generally-Accepted-Principles_Final_26OCT2018.pdf — EVO, IPMVP Generally Accepted Principles (measurement boundary, savings algebra, static factors).
19. https://evo-world.org/en/m-v-community/mv-focus/883-october-2020-m-v-focus-issue-7/1192-detecting-savings-under-10-using-ipmvp-option-c — EVO M&V Focus: detecting sub-10% savings with Option C; G14 thresholds (NMBE, CV(RMSE), savings uncertainty).
20. https://www.bpa.gov/-/media/Aep/energy-efficiency/measurement-verification/3-bpa-mv-regression-reference-guide.pdf — BPA regression reference guide (NMBE terminology, NRE handling, interval-data regression).
21. https://docs.caltrack.org/en/latest/methods.html — CalTRACK methods (avoided energy use, FSU formulation, portfolio aggregation, thresholds).
22. https://eemeter.readthedocs.io/tutorial.html — OpenEEmeter tutorial (metered savings, error bands for FSU).
23. https://evo-world.org/en/products-services-mainmenu-en/protocols/ipmvp — EVO IPMVP overview (whole-facility for multiple interacting EEMs).
24. https://veregy.com/understanding-the-international-performance-measurement-and-verification-protocol/ — IPMVP options in ESCO/EPC practice; interactive-effects guidance.
25. https://powertakeoff.com/ipmvp_option_c_vs_nmec/ — Option C vs NMEC ("M&V 2.0," interval-data automated modelling).
26. https://krahejacorppower.com/know-your-bill — HT bill anatomy (billing-demand formula variants, PF incentive slabs, FAC, ED, excess-demand charges).
27. https://zerowatt.energy/knowledge-centre/discom-tariff-guide/ — DISCOM tariff guide (billing demand 75–85% floor, TOD spreads, FCA ranges, ED ranges, bill composition).
28. https://cescrajasthan.co.in/kedl/pages/event/uploads/JVVNL_Tariff-24.pdf — JVVNL tariff order 2024-25 (billing demand = max(MD, 75% CMD); MD definition; PF rebate/surcharge).
29. https://www.heavengreenenergy.com/glossary/maximum-demand-penalty — MD penalty mechanics (1.5–2× multiplier; demand-charge share of HT bills).
30. https://powerline.net.in/2025/02/05/reforming-tariff-structures-the-cea-proposes-adjustments-to-the-fppas-model/ — FPPAS/Rule 14 monthly automatic pass-through; state adoption status (TN/UP/WB exceptions).
31. https://timesofindia.indiatimes.com/city/lucknow/uperc-says-fppas-not-meant-for-recovery-of-past-liabilities-questions-10-hike-from-uppcl/articleshow/131445003.cms — UPERC vs UPPCL FPPAS dispute 2026 (FPPAS volatility as bill noise).
32. https://eworkorders.com/work-order-delays-consequences/ — Work-order backlog causes (unassigned = never done; escalation windows; invisible age; closeout lag).
33. https://www.infodeck.io/resources/blog/maintenance-workflow-automation-guide/ — Notification fatigue thresholds (20–30 alerts/day), digest batching, escalation-engagement measurement.
34. https://tractian.com/en/blog/6-cmms-reports-to-optimize-your-industrial-maintenance — Created-vs-completed work-order ratio as backlog early-warning.
35. https://sunlithenergy.com/what-is-a-demand-charge-and-why-is-it-so-expensive/ — Demand-charge mechanics in India (contracted MD, 75–85% billing floor, ToD interaction).
