---
type: Product Architecture
title: "L2 — Universal Repository (Data Stores)"
description: "Deep research and store-by-store design for Stamped's L2 layer: time-series store, energy graph, commercial & production context, feature store, baseline store, and the M&V & intensity ledger — with technology picks and build phasing."
tags: [stamped-energy, technical, layer-spec]
timestamp: "2026-07-09T00:00:00Z"
---
# L2 — Universal Repository (Data Stores)

*Layer research document · July 2026 · Status: pre-build, research-grade*

> **Honesty convention:** `[~]` approximate / benchmark-derived · `[!]` evolving — verify before committing engineering effort.
>
> **Siblings:** [L1 — Connect & Normalise](L1-connect-and-normalise.md) · [L3 — Intelligence Core](L3-intelligence-core.md) · [L4 — Knowledge & Reasoning](L4-knowledge-and-reasoning.md) · [L5 — Closure & Verification](L5-closure-and-verification.md) · [Technical architecture](../02-technical-architecture.md)
>
> **Repo context:** `core-product/Stamped_Technical_Architecture_v1.md` §6 · `core-product/Stamped_Product_Definition_and_Architecture.md` §4.2

**TL;DR / verdict on the architecture defaults.** All four defaults survive scrutiny, with one refinement:

| Default | Verdict | One-line reason |
|---|---|---|
| TimescaleDB on Postgres as the core (TS + relational in one engine) | **Confirmed** | At Stamped's scale (≤ ~1–5k rows/s sustained, ~100k series max) a single Postgres+TimescaleDB node is comfortably sufficient, and co-locating telemetry with tariffs, graph, baselines and ledger eliminates a whole class of cross-store consistency problems [1][2][8][9] |
| No dedicated graph DB in v1 | **Confirmed, strongly** | 50–500 nodes/plant, ≤ 4 levels deep is three orders of magnitude below where Neo4j earns its ops cost; recursive CTEs + an in-memory graph object cover every L3 traversal [13][14][15] |
| No dedicated feature-store product in v1 | **Confirmed** | No sub-100ms online serving requirement, < 10 models, batch/micro-batch scoring — continuous aggregates + dbt-style jobs with explicit point-in-time discipline are the right tool [16][17][18] |
| Kafka/Redpanda upstream | **Confirmed with a P0 simplification** | Keep the event-bus contract, but at pilot scale (1–3 plants) a plain Postgres ingest API behind the same topic schema is acceptable; introduce Redpanda when fan-out to stream processors is real `[!]` |

---

## 1. Role in the 15–20% target

L2 is not a passive lake. Every rupee of the 15–20% verified bill reduction flows through this layer twice: once as raw evidence in, once as verified outcome out. If L2 is wrong, everything above it is confidently wrong.

| Store | Waste categories served (§3.1 of [technical architecture](../02-technical-architecture.md)) | Contribution to the target |
|---|---|---|
| **Time-series store** | All six | MD spike forensics (15-min or finer incomer kVA), SEC computation, idle-load detection, TOD exposure — the raw material for every finding. 3–8% of bill (MD/PF alone) is detected purely from incomer telemetry + bill `[~]` |
| **Energy graph** | 1 (MD attribution), 2–5 (asset-level Rx) | Turns "incomer spiked" into "Furnace 3 preheat ∩ Line 2 ramp caused it" and routes the prescription to the right named role. Attribution quality gates closure rate, and closure rate gates realised savings |
| **Commercial & production context** | 1, 6 + ₹ conversion for all | Without a correct, versioned tariff model, kWh findings cannot become ₹ findings. CMD sizing, TOD windows, PF slabs and FPPCA determine *which bill line* each prescription moves [25][26] |
| **Feature store** | 2, 3, 4, 5 | Pre-computed SEC, specific power, load factor, non-production ratio — the features L3 engines and the ranker consume. Freshness here bounds detection latency |
| **Baseline store** | All six (as the reference) | "Expected band" per asset/shift/product is the counterfactual against which waste is measured *and* against which M&V savings are computed. A mutable baseline destroys M&V defensibility [29][30] |
| **M&V & intensity ledger** | Output side of all six | The append-only record of potential vs realised ₹ + kWh + tCO₂e. This is the artefact the CFO renews on and the sustainability lead audits with. It must survive a hostile audit [19][20][31] |

**Design rule inherited from the architecture:** every L2 structure must either improve detection, improve prescription quality/closure, improve M&V defensibility, or produce sustainability evidence. Storage that only feeds charts is rejected.

---

## 2. Requirements from the architecture

### 2.1 Contract from L1 (inbound)

L1 delivers four canonical record types over the event bus (Kafka/Redpanda topics, or the P0 ingest API implementing the same schemas `[!]`):

| Record | Key fields | L2 destination |
|---|---|---|
| `Measurement` | `plant_id, asset_id, metric_type, ts_utc, value, quality (good/estimated/bad), source_system, source_tag, granularity` | Time-series store (hypertable), lineage columns preserved |
| `Event` | asset state transitions, alarms, detected ramps | Time-series store (separate event hypertable) |
| `ProductionRecord` | `batch_id, sku, qty, uom, line_id, window_start/end, source (ERP/MES/manual)` | Commercial & production context store |
| `BillLine` | parsed DISCOM bill: energy, MD recorded, billing demand, PF, TOD splits, FPPCA, penalties, ₹ amounts, bill period | Commercial context store; referenced by the M&V ledger |

L2 must accept **out-of-order and late data** (edge-buffered plants upload in batches after WAN outages; historian CSV backfills can arrive days late) and must preserve the `quality` flag end-to-end — L3 baselines must be able to exclude `estimated` points.

### 2.2 Contracts to L3 / L4 / L5 (outbound)

| Consumer | Query contract | Latency budget `[~]` |
|---|---|---|
| [L3](L3-intelligence-core.md) baseline & SEC engine | Windowed aggregates (1min/15min/shift/day) joined to production records; 13–36 months of history | Batch: minutes |
| L3 MD/demand engine | Raw + 1-min incomer kVA for spike post-mortem; last 90 days hot | Near-real-time: ≤ 60 s from ingest to queryable |
| L3 attribution engine | Graph traversal (≤ 4 hops) + co-windowed telemetry for candidate assets | Interactive: < 1 s |
| [L4](L4-knowledge-and-reasoning.md) prescription agent tools | `query_timeseries`, `get_baseline`, `traverse_graph`, `calculate_impact` — point lookups and small windows | Interactive: < 500 ms |
| [L5](L5-closure-and-verification.md) M&V engine | Locked baseline read; reporting-period aggregates; bill-line lookups; ledger append | Batch: minutes; ledger append transactional |
| L6 dashboard | Continuous-aggregate reads (30-day trend, TOD profile, top consumers) | Interactive: < 1 s p95 |

### 2.3 Scale envelope (sizing honesty)

| Dimension | P0 (pilots) | P2 (~year 2) `[~]` | Note |
|---|---|---|---|
| Plants | 1–3 | 30–50 | ICP: ≥ ₹30L/month bills |
| Tags per plant | 50–300 (Path B heavy) | 200–2,000 (Path A) | Series cardinality = plants × tags ≤ **100k** — trivial for every candidate engine |
| Ingest rate | < 100 rows/s | ~1–5k rows/s sustained; bursts to ~20k on backfill | Even the pathological case (50 plants × 2,000 tags × 1 Hz = 100k rows/s) is single-node territory for TimescaleDB/ClickHouse [8][9] |
| Raw retention | 13 months | 13 months raw, 36 months aggregates | See retention table §4.8 |
| Storage/yr, compressed | < 20 GB | ~150–400 GB `[~]` | Timescale columnstore typically 90–95% compression on regular telemetry [1][3] |

**The load-bearing observation:** Stamped's data problem is *breadth of context* (tariffs, topology, production, baselines, audit), not *volume of points*. That inverts the usual TSDB selection logic — join capability and transactional integrity matter more than ingest ceiling.

### 2.4 Non-functional requirements

- **Auditability:** ledger and locked baselines immutable; every prescription's evidence pointers resolvable years later.
- **Tenancy:** hard `org_id → plant_id` isolation; no query path can cross tenants (§14 of the technical architecture).
- **Residency:** India-region hosting for enterprise accounts (DPDP Act 2023 + Rules 2025 posture) [32][33][34].
- **Recovery:** PITR with RPO ≤ 5 min, restore drill-verified `[!]`.
- **Cost ceiling:** L2 infra for P0 must fit a seed-stage budget — one managed Postgres instance, not a five-service data platform.

---

## 3. Researched landscape

### 3.1 Time-series store

#### Candidates compared (state of the market, July 2026)

| Engine | Current state | Rollups / downsampling | Out-of-order writes | Joins with relational context | Ops burden | License / cost |
|---|---|---|---|---|---|---|
| **TimescaleDB** (now Tiger Data) | 2.28 (Jun 2026): hypercore row+columnstore, vectorised aggregation, `first()`/`last()` from batch metadata, incremental cagg refresh, `compress_after_refresh` single-policy refresh+compress [1][2][3][4] | **Best in class:** continuous aggregates are incremental materialised views with real-time union; hierarchical caggs (1min→15min→hour→day); retention + compression policies built in [4] | Native — it's Postgres heap until compressed; late data invalidates and re-refreshes caggs automatically | **Native SQL joins, same engine** — the differentiator | Low if you already run Postgres; single binary extension | Apache 2 core + TSL for compression/caggs — free to self-host, can't resell as a DBaaS (irrelevant for Stamped) |
| **InfluxDB 3.x** | Core (OSS, single node) intentionally limited for historical queries; Enterprise is commercial, per-CPU-core licensed, **queries stop on license expiry**; downsampling via a plugin, not built-in policies [5][6][7] | Plugin-based downsampler (scheduled jobs writing to target tables) [7] | Good (Parquet/object-store engine) | None — separate system, FDW/ETL needed | Medium; ecosystem churn (Flux deprecated, v1→v2→v3 migrations) is a real signal | Core free but constrained; Enterprise per-contract. Licensing risk is disqualifying for an audit-critical store `[!]` |
| **ClickHouse** | Excellent columnar OLAP; fastest analytics in most benchmarks (SciTS: >1.2M rows/s ingest, ~6× Postgres [8]; SmartCampus: ~1.6M rows/s, best query speed [9]) | TTL-based rollups, materialised views | Async inserts fine; mutations expensive | Limited joins vs Postgres; no transactional coupling with the ledger | Medium-high (second engine, ZooKeeper/Keeper for replication) | Apache 2. Right answer at 100× Stamped's scale, wrong answer now |
| **QuestDB** | Fastest raw ingest (4M+ rows/s claims [10]) | SAMPLE BY; materialised views newer | Historically weak, improved | Limited JOIN support [10] | Low-medium | Apache 2. Ingest speed solves a problem Stamped doesn't have |
| **VictoriaMetrics** | Superb Prometheus-class metrics store; handles IoT-scale cardinality; unlimited backfill within retention [11] | Automatic downsampling in enterprise; recording rules otherwise | Good [11] | None; **float64-only values**, no strings/booleans — machine `state` tags and quality flags don't fit the model [11][12] | Low | Apache 2 / enterprise tiers. A metrics store, not an evidence store |
| **"Just Postgres"** (declarative partitions, no extension) | Fine to ~10⁸ rows with manual partition + rollup jobs | Hand-rolled cron/pg_cron rollups | Native | Native | Low, but you re-implement Timescale's job system badly | Free |
| **Parquet/Iceberg + DuckDB lakehouse** | Strong pattern for *cold* telemetry: export aged chunks to Parquet on S3, Iceberg metadata, DuckDB/engine-of-choice for historical analytics `[~]` | Via compaction/aggregation jobs | N/A (batch) | Via export only | Medium (compaction, catalog) | Very cheap storage (~$0.023/GB-mo S3 standard, Mumbai similar) |

#### Benchmark honesty `[~]`

ClickHouse wins nearly every published ingest/analytics benchmark [8][9][10]. That is true and **irrelevant at Stamped's scale**: the SmartCampus benchmark's *slowest* contender ingests more per second than Stamped's entire fleet will produce in P2. Benchmarks measure the ceiling; Stamped's constraint is the floor — minimum ops burden, maximum contextual joins, one backup story, one tenancy story.

**Firm recommendation: TimescaleDB (self-hosted or Tiger Cloud/managed Postgres equivalent in ap-south-1).** Reasons, in order:

1. **One engine for six stores.** Telemetry, graph, tariffs, features, baselines and the ledger live in one transactional database. A `LedgerEntry` can foreign-key a `BillLine` and a locked `baseline_id` in the same commit. No cross-store consistency glue, no dual backup/restore, one RLS tenancy model.
2. **Continuous aggregates are 80% of the "feature store" and 100% of the downsampling story** — incremental, late-data-aware, hierarchically stackable, compressible in the same policy since 2.27 [1][4].
3. **Recent-version columnstore closes the analytics gap enough**: vectorised `time_bucket()` aggregation, ColumnarIndexScan answering COUNT/MIN/MAX/FIRST/LAST from chunk metadata (up to 70–289× on summary queries), bloom-filtered multi-column pruning [1][3].
4. **Escape hatches exist in both directions.** If analytics outgrow it: tiered storage / Parquet export of aged chunks to S3 + DuckDB for fleet-wide historical crunching `[!]`. If a single customer demands isolation: the whole L2 is one database to clone.

Rejections: InfluxDB 3 for licensing/continuity risk on an audit-critical store [6]; ClickHouse and QuestDB as premature second engines; VictoriaMetrics on data-model mismatch (float-only) [11][12]; bare Postgres because TimescaleDB is strictly superior for the same ops cost.

#### Per-candidate detail worth recording

**TimescaleDB / Tiger Data — what changed recently and why it matters here.** The 2.25–2.28 release train (Mar 2025 → Jun 2026) materially changed the analytics story: ColumnarIndexScan resolves `COUNT/MIN/MAX/FIRST/LAST` from chunk-level sparse-index metadata instead of decompressing batches (up to 289× on tested summary queries) [3]; `time_bucket()` grouping stays in the vectorised path end-to-end (~3.5×) [3]; 2.28 derives `first(value, time)`/`last(value, time)` straight from batch metadata — exactly the "latest reading per meter" shape Stamped's dashboard hammers [2]; and continuous aggregates gained `ADD COLUMN` without rebuild, incremental batched manual refreshes, and lighter invalidation locking [2]. Licensing nuance worth stating once: the *core* is Apache 2 but compression, caggs and several policies sit under the Timescale License (source-available, free to self-host and run commercially; forbidden only to offer TimescaleDB itself as a hosted DBaaS). Stamped sells energy intelligence, not database hosting — no conflict `[~]`.

**InfluxDB 3.x — why it is disqualified despite good engineering.** The v3 engine (Rust, Arrow, Parquet-on-object-storage) is genuinely modern, but the product split works against Stamped: Core (OSS) is intentionally constrained for historical queries — and 13-month forensic lookback is a *core* Stamped requirement; Enterprise fixes that behind a per-CPU commercial license where, on expiry, **queries return errors and a stopped server will not restart** [6]. Putting a license-expiry kill-switch under the store that backs an M&V audit trail is an unacceptable continuity risk regardless of price. Add the ecosystem churn (v1 → v2/Flux → v3/SQL, Flux deprecated) and the migration tax lands on us twice `[!]` [5][6][7].

**ClickHouse — the "right answer later, wrong answer now" candidate.** It wins benchmarks by an order of magnitude [8][9], and if Stamped ever operates 500+ plants with fleet-wide sub-second benchmark analytics, a ClickHouse sidecar fed from the Postgres WAL or the event bus is the natural evolution. What it cannot do is *be the one engine*: no transactional coupling with the ledger/baselines, weaker referential integrity, a second backup/tenancy/RLS story, and mutations (needed for late-data corrections in context tables) are expensive by design. Adopting it in v1 means running two databases before we have one customer.

**QuestDB / VictoriaMetrics — good tools, wrong problems.** QuestDB optimises ingest throughput Stamped will never approach and has historically limited JOIN support — SEC computation is a join-heavy workload [10]. VictoriaMetrics is a superb *metrics* store (cheap, high-cardinality-tolerant, unlimited backfill within retention [11]) but stores only float64 values — no strings/booleans — so machine states, quality flags and lineage columns need a second store immediately, defeating the purpose [12].

**"Just Postgres" and the lakehouse.** Plain partitioned Postgres would work at P0 scale but re-implements Timescale's chunk management, rollup jobs, and compression by hand — same engine, more code, worse compression (Timescale's delta-delta/Gorilla-class columnstore typically achieves 90–95% on regular telemetry [1][3]). The Parquet/Iceberg/DuckDB lakehouse is not an alternative but a **cold-tier complement**: from P2, aged raw chunks are exported to Parquet on S3 Mumbai (Iceberg catalog optional at our file counts `[~]`) where storage costs ~US$0.023/GB-month and DuckDB reads them directly for fleet-history analytics. This keeps the hot Postgres small and the escape hatch real without operating a second query engine day-to-day `[!]`.

#### Indicative P2 cost sketch `[~]`

| Item | Sizing | Monthly cost `[~]` |
|---|---|---|
| Managed Postgres+Timescale, ap-south-1 (4 vCPU / 32 GB, gp3 1 TB) | 50 plants, ~1–5k rows/s, hot 13 months compressed | US$600–900 (RDS-class) |
| Read replica (dashboards + L4 tools) | same class | US$600–900 |
| S3 Mumbai: backups + Parquet cold tier | ~1–2 TB growing | US$25–50 |
| Redpanda (3-node small or serverless) | P1+ | US$200–400 |
| **Total L2 data platform** | | **≈ US$1.5–2.2k/month ≈ ₹1.3–1.9L/month** |

Context: that is under 1% of the *monthly electricity spend of a single ICP plant* (≥ ₹30L). Infrastructure cost is not the constraint; engineering attention is — which is the strongest argument for one engine.

### 3.2 Energy graph

The research question was whether ~50–500 nodes/plant with typed edges justifies Neo4j/Memgraph. It does not — and the margin is not close.

| Option | Fit for Stamped | Evidence |
|---|---|---|
| **Neo4j / Memgraph** | Overkill. Graph DBs earn their cost at 3–4+ hop traversals over millions of edges, variable-length path analytics, centrality/community algorithms as core features [13][15]. Stamped's graph: ≤ 4 levels (Plant→System→Equipment→MeasurementPoint), a few hundred edges/plant, tens of thousands fleet-wide. Introducing one adds dual-database sync, Cypher skills, separate backup/tenancy — for zero measured benefit at this depth [13][14] |
| **Postgres adjacency (recursive CTEs)** | **Correct system of record.** Adjacency table + `WITH RECURSIVE` scales to tens of millions of edges at sub-second latency for typical depths; `CYCLE` clause guards accidental loops; FK integrity keeps edges pointing at real assets [14] |
| **In-memory graph loaded from relational tables** | **Correct hot path.** L3 attribution needs "co-active equipment on shared bus within ±3 min" many times per hour. Load the per-plant graph (a few KB) into a NetworkX/rustworkx structure in the attribution service, refresh on topology change events. Traversal cost becomes nanoseconds; Postgres stays the single writable truth |

Design implications validated by research: typed edges (`feeds`, `drives`, `shares_electrical_bus`, `starts_with`, `thermal_coupling` `[!]`) are just an `edge_type` enum column; vertical templates (forging, die casting, cement, pharma HVAC) are seed rows cloned at onboarding, not a modelling framework. Revisit only if fleet-wide cross-plant graph analytics (P3+) demand it — and even then, Apache AGE inside the same Postgres is the first step, not Neo4j [15] `[!]`.

### 3.3 Feature store

Feast/Tecton solve three problems: online serving at sub-100ms QPS, training/serving skew across many models/teams, and point-in-time (PIT) correctness [16][17]. Stamped's situation against each:

| Feature-store problem | Does Stamped have it in v1? |
|---|---|
| Sub-100ms online feature serving | **No.** Detection runs on 1–15 min micro-batches; prescriptions are minutes-scale. The "online store" is a Postgres query |
| Many models, shared features, team-scale reuse | **No.** ~5–10 model classes (ML-01…ML-07), one team. Inflection point for Feast is typically 10+ models with overlapping features and daily retraining [17] |
| Point-in-time correctness for training | **Yes — but it's a discipline, not a product.** AS-OF join pattern (`ROW_NUMBER()` over `feature_ts <= label_ts`) implemented in dbt models, plus tests asserting no feature timestamp exceeds the observation cutoff, fully covers it [16][18] |

Consensus across practitioner sources: for batch-scored ML without real-time serving, "the offline store *is* the feature store" — materialised views/aggregate tables with snapshot timestamps; adding Feast is ceremony that nobody will own [16][17]. **Verdict: no feature-store product in v1. Continuous aggregates (push-down features) + dbt-style transformation jobs (complex features: SEC, startup catalogue, non-production ratio) + PIT-join discipline.** Revisit trigger: a genuine real-time scoring requirement (e.g. predictive MD forecasting served to an operator screen at seconds latency) `[!]`.

### 3.4 Baseline store & model-registry adjacency

Two findings from M&V practice shape this store:

1. **IPMVP savings are computed against a baseline model plus adjustments**: `Savings = (Baseline − Reporting-period use) ± routine adjustments ± non-routine adjustments (NRAs)` [29][30]. Routine adjustments (production, weather) are parameters *of* the baseline model; NRAs handle static-factor changes (facility size, operating hours) and are the most abused element of Option C M&V — EVO explicitly warns that undisciplined adjustments degrade credibility [29][31].
2. **Therefore the baseline that a prescription cites must be immutable.** The industry-standard failure mode is silently re-fitting the baseline after the fact so savings look better. Stamped's answer: baselines are **versioned rows, locked on first citation**, and any correction is a *new version* with lineage to its predecessor — never an UPDATE. NRAs are stored as separate, dated adjustment records referencing the locked baseline, mirroring the IPMVP guide's requirement to document NRE criteria and methods in the M&V plan [30][31].

Model-registry adjacency: baseline rows should carry `model_type`, `model_params` (JSONB), `training_window`, `feature_set_version`, `rule_pack_version` — enough to reproduce the fit. A full MLflow-class registry is unnecessary in v1; the baseline table *is* the registry for the models that matter for money `[~]`. Artefacts (pickled models) can live in S3 keyed by `baseline_id` `[!]`.

### 3.5 Commercial & production context — Indian tariff reality

Research into current tariff orders (Rajasthan JVVNL/JdVVNL FY25-26, AP DISCOMs FY25-26) confirms the components the store must model, and adds precision [25][26]:

| Tariff concept | What the orders actually say | Modelling consequence |
|---|---|---|
| **Contract Demand (CMD)** | Demand in kVA the DISCOM commits to supply; if sanctioned in kW, converted at PF 0.90 [25] | Store CMD in kVA + sanction metadata; CMD-optimisation Rx needs the conversion rule |
| **Billing Demand floor** | "Maximum Demand actually recorded during the month **or 75% of Contract Demand, whichever is higher**" (Rajasthan; percentage varies by state) [25] | MD-reduction savings are **floored** — cutting recorded MD below 75% of CMD saves nothing until CMD itself is renegotiated. The ₹ impact calculator must know this per-DISCOM floor |
| **Maximum Demand definition** | Average kVA over the meter's 15/30-min integration period [25] | MD forensics need ≤ 1-min incomer data to see inside the integration window |
| **TOD windows** | State-specific; e.g. Rajasthan FY25-26: off-peak 12:00–16:00 → 10% rebate on energy charges; peak → surcharge; AP extends TOD to industrial ≥ 15 kW with seasonal peak windows (06–10, 18–22) [25][26] | TOD windows are **date-ranged, season-ranged, category-scoped** rate rules — a versioned structure, not columns |
| **PF slabs** | Maintain avg PF ≥ 0.90; surcharge ~1% of energy charges per 0.01 below; incentives ~0.5% per 0.01 above 0.95/0.97 thresholds; disconnection procedure below 0.70 [25] | Piecewise-linear slab table per tariff version |
| **FPPCA / FPPAS** | Fuel & Power Purchase (Cost) Adjustment Surcharge — monthly/quarterly variable ₹/kWh rider (AP caps monthly pass-through at 40 paise/unit) [26] | Time-varying surcharge series attached to the tariff, updated from bills |
| **Tariff revisions** | Annual orders + mid-year amendments | **Every rate structure is versioned with validity dates; bills validate against the version in force** |

**Worked example — why the versioned rate structure earns its complexity `[~]`.** A forging plant on a JVVNL-style HT industrial tariff: CMD 1,100 kVA, demand charge ₹270/kVA/month, energy charge ₹7.30/kWh, billing-demand floor 75% of CMD (= 825 kVA), PF surcharge 1% of energy charges per 0.01 below 0.90 [25].

- *MD prescription:* recorded MD is 1,180 kVA (over CMD — attracting excess-demand surcharge in most states). A stagger prescription cuts peak to 1,060 kVA → saves ₹270 × 120 = **₹32,400/month** on the MD line plus the excess-demand penalty. A second-order Rx then asks: the MD histogram now peaks at 1,060 against CMD 1,100 — CMD is roughly right. But had the plant's real peak been 700 kVA, *no MD reduction below 825 kVA saves anything* until CMD itself is renegotiated — the billing-demand floor makes "reduce CMD" its own prescription category. An impact calculator without the floor overstates savings and destroys trust on the first bill reconciliation.
- *PF prescription:* average PF 0.86 on ₹40L/month energy charges → surcharge = 4 steps × 1% = **₹1.6L/month**, recoverable by capacitor-bank correction — often the single fastest payback in the six categories.
- *TOD prescription:* shifting 40,000 kWh/month of compressor-driven load into a 12:00–16:00 off-peak window with a 10% energy-charge rebate saves 40,000 × ₹7.30 × 10% ≈ **₹29,200/month** — computable only if the TOD windows for *this tariff version, this season* are in the store.

All three computations touch different bill lines with different rate rules, which is exactly why `TariffContract` is a versioned structure (`tariff_version` + child `tod_window`, `pf_slab`, `surcharge_series` rows) rather than a flat rate column.

Emission factors: CEA CO₂ Baseline Database is the authoritative Indian grid factor, updated annually — v20 (Dec 2024, FY23-24: 0.727 tCO₂/MWh weighted average) and v21 (late 2025, FY24-25: ~0.710–0.7117 tCO₂/MWh provisional, all-India weighted average incl. RES & captive) [27][28]. Consequences: factors are **versioned rows** (`source=CEA, version=21.0, fy=2024-25, value, published_date`); recalculation never rewrites history — new factors apply forward; every tCO₂e figure discloses factor + version + vintage (§11.4 of the technical architecture). Customer overrides stored alongside with documented source.

### 3.6 M&V ledger — immutability techniques

Practitioner consensus on append-only Postgres design [19][20][21]:

1. **Privileges:** `REVOKE UPDATE, DELETE, TRUNCATE ... FROM PUBLIC`; app role gets `INSERT, SELECT` only — removes accidental and injection-borne mutation paths.
2. **Trigger backstop:** `BEFORE UPDATE OR DELETE` trigger raising an exception unconditionally; the trigger definition itself is exportable as a compliance artefact [20].
3. **Corrections are compensating entries**, never edits: a disputed ledger entry gets a `superseded_by` successor with a reason code [21].
4. **Tamper evidence (optional, cheap):** hash-chain columns (`seq`, `prev_entry_hash`, `entry_hash = H(prev_hash ‖ canonical_row)`), appends serialised per-org via `pg_advisory_xact_lock` to prevent chain forks; periodic verifier job walks the chain [19]. Recommended from P1 when the ledger becomes customer-billing-relevant `[!]`.
5. **Partition by period** for bounded indexes and archival; partition detachment is a privileged, runbooked operation [20].

Full event-sourcing (ledger as projection of an event log) was considered and rejected for v1: the ledger *is* the event log for its domain; a separate event store adds machinery without adding defensibility `[~]`.

### 3.7 Cross-cutting: tenancy, retention, backup, residency

**Tenancy.** 2026 consensus for B2B SaaS at Stamped's tenant count: **shared schema + `org_id` column + Postgres Row-Level Security as the enforced backstop**, with composite indexes leading on the tenant key [22][23]. Schema-per-tenant buys little here and complicates Timescale background jobs; database-per-tenant is the *escape hatch* for an enterprise contract demanding physical isolation or per-tenant PITR — which, notably, some large Indian manufacturers may demand in procurement [23][24]. RLS is defence-in-depth: the app still filters by `org_id` explicitly (index usage), the database guarantees correctness when the app fails [22][24].

**Backup/PITR.** Managed Postgres (RDS/Cloud SQL/Azure Flexible Server, or Tiger Cloud) in ap-south-1 gives WAL-based PITR out of the box; the untested restore is the real risk — hence restore drills in §5. Note one tension: hash-chained ledger + PITR restore to a point mid-chain is safe (chain is self-consistent at any prefix), but *selective* table restores must be forbidden by runbook.

**Residency.** AWS Mumbai (ap-south-1) and Hyderabad (ap-south-2) provide in-country storage; content does not leave the region unless the customer moves it [32]. DPDP Act 2023 + Rules 2025 use a blacklist transfer model (telemetry is mostly non-personal data anyway), but enterprise procurement and RBI-adjacent group policies increasingly demand India-region hosting regardless — enforce with SCP/region-deny controls so nothing is accidentally created elsewhere [33][34]. Azure Central India / GCP Mumbai are equivalent options; choose by managed-Postgres quality and credits `[!]`.

---

## 4. Recommended approach

### 4.0 Shape of the layer

One Postgres 17 + TimescaleDB 2.28 database (managed, ap-south-1), logical schemas per store, shared-schema multi-tenancy with RLS. Kafka/Redpanda feeds writer services; a thin read API (plus SQL for internal engines) serves L3–L6.

```
                     ┌───────────────────────────────────────────────┐
 L1 topics ─────────▶│  POSTGRES 17 + TIMESCALEDB (ap-south-1)       │
  measurements       │                                               │
  events             │  schema telemetry   measurement, event        │──▶ L3 engines
  production         │                     (hypertables + caggs)     │
  bill_lines         │  schema graph       asset, asset_edge         │──▶ L3 attribution
                     │  schema commercial  tariff_version, tod_window│    (in-mem mirror)
                     │                     pf_slab, shift_calendar,  │──▶ L4 impact calc
                     │                     production_record,        │
                     │                     bill, bill_line,          │──▶ L5 M&V
                     │                     emission_factor           │
                     │  schema features    (caggs + dbt tables)      │──▶ L3/L4
                     │  schema baselines   baseline (versioned,      │──▶ L3/L5
                     │                     locked-on-cite)           │
                     │  schema ledger      mv_ledger (append-only,   │──▶ L5/L6 exports
                     │                     hash-chained)             │
                     └───────────────────────────────────────────────┘
                              │ aged chunks (P2+) `[!]`
                              ▼
                     S3 (Mumbai) Parquet/Iceberg cold tier + backups
```

### 4.1 Time-series store

```sql
CREATE TABLE telemetry.measurement (
  org_id        uuid        NOT NULL,
  plant_id      uuid        NOT NULL,
  asset_id      uuid        NOT NULL,          -- FK → graph.asset
  metric        text        NOT NULL,          -- active_power_kw | apparent_power_kva | energy_kwh | pf | ...
  ts            timestamptz NOT NULL,
  value         double precision NOT NULL,
  quality       smallint    NOT NULL DEFAULT 0, -- 0 good | 1 estimated | 2 bad
  source_system text,
  source_tag    text
);
SELECT create_hypertable('telemetry.measurement', by_range('ts', INTERVAL '7 days'));
-- columnstore: segment by series, order by time
ALTER TABLE telemetry.measurement SET (timescaledb.enable_columnstore,
  timescaledb.segmentby = 'org_id, asset_id, metric', timescaledb.orderby = 'ts');
CALL add_columnstore_policy('telemetry.measurement', after => INTERVAL '7 days');
```

Continuous aggregates (hierarchical): `agg_1min` → `agg_15min` → `agg_hour` → `agg_day`, each `avg/min/max/sum(value) FILTER (WHERE quality=0)`, count of estimated/bad points carried along so downstream engines can judge window trustworthiness. Refresh policies use `compress_after_refresh` to land refreshed regions directly in the columnstore [1][4]. Shift-level aggregates are **not** caggs (shift boundaries are per-plant data, not fixed buckets) — they are dbt-style jobs joining `agg_15min` to `commercial.shift_calendar`.

Late/out-of-order data: hypertable inserts are unrestricted; cagg invalidation handles re-aggregation automatically. Backfills older than the columnstore boundary trigger chunk decompress-recompress — acceptable at Stamped's backfill rates; batch backfills should be rate-limited by the writer `[~]`.

Event stream (`telemetry.event`: state transitions, alarms, detected ramps) is a second, smaller hypertable with `jsonb` payload — kept out of `measurement` to preserve columnstore efficiency.

### 4.2 Energy graph

```sql
CREATE TABLE graph.asset (
  org_id uuid NOT NULL, plant_id uuid NOT NULL,
  asset_id uuid PRIMARY KEY,
  parent_id uuid REFERENCES graph.asset(asset_id),   -- containment hierarchy
  level text NOT NULL CHECK (level IN ('plant','system','equipment','measurement_point')),
  asset_class text,          -- compressor | furnace | chiller | incomer | ...
  name text NOT NULL,
  owner_role text,           -- electrical_supervisor | utilities | production ...
  attrs jsonb DEFAULT '{}'::jsonb,
  valid_from timestamptz NOT NULL DEFAULT now(), valid_to timestamptz  -- soft-versioned topology
);
CREATE TABLE graph.asset_edge (
  org_id uuid NOT NULL,
  from_asset uuid NOT NULL REFERENCES graph.asset(asset_id),
  to_asset   uuid NOT NULL REFERENCES graph.asset(asset_id),
  edge_type  text NOT NULL CHECK (edge_type IN
    ('feeds','drives','shares_electrical_bus','starts_with','thermal_coupling')),
  attrs jsonb DEFAULT '{}'::jsonb,
  PRIMARY KEY (from_asset, to_asset, edge_type)
);
CREATE INDEX ON graph.asset_edge (to_asset);   -- both directions indexed [14]
```

- **Traversal:** recursive CTE with `CYCLE` guard for API queries; the L3 attribution service keeps a per-plant in-memory mirror (rustworkx/NetworkX), invalidated by `LISTEN/NOTIFY` on topology change. At ≤ 500 nodes this rebuild is microseconds. The canonical attribution query — "all equipment sharing an electrical bus with asset X, plus what each drives" — in SQL:

```sql
WITH RECURSIVE bus_peers AS (
  SELECT e.to_asset AS asset_id, 1 AS depth
  FROM graph.asset_edge e
  WHERE e.from_asset = :asset_id AND e.edge_type = 'shares_electrical_bus'
  UNION
  SELECT e.to_asset, bp.depth + 1
  FROM graph.asset_edge e JOIN bus_peers bp ON e.from_asset = bp.asset_id
  WHERE e.edge_type IN ('shares_electrical_bus','feeds') AND bp.depth < 4
) CYCLE asset_id SET is_cycle USING path
SELECT DISTINCT a.asset_id, a.name, a.asset_class, a.owner_role
FROM bus_peers bp JOIN graph.asset a ON a.asset_id = bp.asset_id
WHERE NOT is_cycle;
```

  At Stamped's edge counts this executes in single-digit milliseconds — the in-memory mirror exists for the *many-times-per-hour* attribution loop, not because Postgres is slow here [14].
- **Vertical templates:** template subgraphs (forging, die casting, cement kiln, pharma HVAC) stored as ordinary rows under a reserved template org; onboarding clones and customises them.
- **Topology versioning `[!]`:** `valid_from/valid_to` soft versioning so that attribution replays and M&V use the topology *as it was* — cheap now, painful to retrofit.
- **Owner routing:** `owner_role` on equipment + a per-plant role→person map (kept in the workflow store at L5) closes the "Who" field of every prescription.

### 4.3 Commercial & production context

```sql
CREATE TABLE commercial.tariff_version (
  org_id uuid, plant_id uuid, tariff_version_id uuid PRIMARY KEY,
  discom text NOT NULL,                -- e.g. 'JVVNL', 'MSEDCL', 'UPCL'
  category text NOT NULL,              -- e.g. 'HT-2 Large Industrial'
  valid_from date NOT NULL, valid_to date,
  cmd_kva numeric NOT NULL,
  billing_demand_floor_pct numeric NOT NULL DEFAULT 75,  -- state-specific [25]
  demand_charge_inr_per_kva numeric,
  energy_charge_inr_per_kwh numeric,   -- base; TOD/FPPCA modify it
  kvah_billing boolean DEFAULT false,  -- several states bill kVAh, not kWh `[!]`
  source_doc text                      -- tariff order URL / bill reference
);
CREATE TABLE commercial.tod_window (
  tariff_version_id uuid REFERENCES commercial.tariff_version,
  season text, window_start time, window_end time,
  kind text CHECK (kind IN ('peak_surcharge','offpeak_rebate','normal')),
  pct_of_energy_charge numeric        -- e.g. +5% / −10% `[~]` per order
);
CREATE TABLE commercial.pf_slab (
  tariff_version_id uuid REFERENCES commercial.tariff_version,
  pf_from numeric, pf_to numeric,
  effect text CHECK (effect IN ('surcharge','incentive')),
  pct_per_step numeric, step numeric   -- e.g. 1% of EC per 0.01 below 0.90 [25]
);
CREATE TABLE commercial.surcharge_series (   -- FPPCA/FPPAS, regulatory riders
  tariff_version_id uuid, name text, period daterange, inr_per_kwh numeric
);
```

- `bill` / `bill_line` tables mirror the parsed DISCOM bill; each `bill_line` carries `(line_type, qty, rate, amount_inr)` and is validated against the tariff version in force — mismatch raises a *tariff misclassification finding* to L3.
- `shift_calendar` — per plant: shift A/B/C boundaries, breaks, planned maintenance windows, holiday lists; joined into shift-level features and idle detection.
- `production_record` — batch/SKU/tonnage/parts with time windows and `source` lineage (ERP, MES, manual upload); the SEC denominator.
- `emission_factor` — versioned rows: `(source, version, fiscal_year, factor_tco2_per_mwh, scope, published_on, override_of uuid NULL)`. Seed: CEA v20 FY23-24 = 0.727; CEA v21 FY24-25 ≈ 0.711 provisional [27][28]. New versions apply **forward only**.

### 4.4 Feature store (pattern, not product)

| Feature class | Materialisation | Freshness | Backfill |
|---|---|---|---|
| Rolling kW mean/variance, load factor, TOD exposure | Continuous aggregates (real-time union gives current-bucket reads for free) | ≤ refresh interval (15 min typical) | Automatic via cagg refresh over history |
| SEC (kWh/ton, kWh/part, kWh/batch), specific power, non-production ratio | dbt-style incremental SQL jobs joining `agg_15min` × `production_record` × `shift_calendar`, written to `features.*` tables with `computed_at` and `feature_set_version` | Job cadence (hourly/shift-end) | `--full-refresh` per plant; idempotent |
| Startup event catalogue | Stream/micro-batch ramp detector writing `telemetry.event` | Minutes | Replay from raw |

**Point-in-time correctness:** every feature row carries `event_time` (data time) and `computed_at` (processing time). Training-set construction uses the AS-OF join pattern (`ROW_NUMBER() OVER (PARTITION BY entity ORDER BY event_time DESC)` where `event_time <= label_time`) with tests asserting no future leakage — the dbt-timefence pattern [18]. This is a convention enforced by tests, which at < 10 models is cheaper and more transparent than operating Feast [16][17].

### 4.5 Baseline store

```sql
CREATE TABLE baselines.baseline (
  org_id uuid, plant_id uuid,
  baseline_id uuid PRIMARY KEY,
  scope jsonb NOT NULL,          -- {asset_id, shift, product/sku, metric}
  model_type text NOT NULL,      -- stl | regression | quantile_band | rule
  model_params jsonb NOT NULL,   -- coefficients, band quantiles — enough to reproduce
  feature_set_version text, rule_pack_version text,
  training_window tstzrange NOT NULL,
  expected_band jsonb,           -- materialised band per bucket where cheap `[~]`
  version int NOT NULL,
  supersedes uuid REFERENCES baselines.baseline(baseline_id),
  status text NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft','active','locked','retired')),
  locked_at timestamptz, locked_by_prescription uuid,
  created_at timestamptz NOT NULL DEFAULT now()
);
```

**Locking protocol (the IPMVP-critical part):**

1. L3 publishes baselines as `active`; they may be re-fit freely while `draft/active` — each re-fit is a **new version row** with `supersedes` lineage.
2. The moment L4 cites a baseline in a prescription's `mv_plan`, L5 flips it to `locked` (recording the citing prescription). A `BEFORE UPDATE` trigger rejects any change to a `locked` row except `status → retired`.
3. Non-routine adjustments (production line added, operating-hours change) are **separate `baselines.nra` rows** referencing the locked baseline with method, quantification and approver — mirroring IPMVP NRA documentation discipline [30][31]. The M&V computation reads `locked baseline ± NRAs`, never a mutated baseline.
4. Verification against a *newer* baseline version is a new M&V plan on a new prescription — history is never re-scored.

This gives Stamped an auditable answer to the classic Option C attack ("you moved the baseline") [29].

### 4.6 M&V & intensity ledger

```sql
CREATE TABLE ledger.mv_ledger (
  org_id uuid NOT NULL, plant_id uuid NOT NULL,
  entry_id uuid NOT NULL DEFAULT gen_random_uuid(),
  seq bigint NOT NULL,                           -- per-org monotonic
  prescription_id uuid NOT NULL,
  period tstzrange NOT NULL,
  mv_method text NOT NULL,                       -- IPMVP option A/B/C + method note
  baseline_id uuid NOT NULL,                     -- must be status='locked'
  potential_kwh numeric, realised_kwh numeric,
  potential_inr numeric, realised_inr numeric,
  avoided_tco2e numeric,
  emission_factor_id uuid REFERENCES commercial.emission_factor,  -- factor + vintage disclosed
  intensity_delta jsonb,                         -- {metric:'kwh_per_ton', before, after}
  bill_line_refs uuid[],                         -- DISCOM reconciliation anchors
  verification_status text NOT NULL
    CHECK (verification_status IN ('pending','verified','disputed','superseded')),
  superseded_by uuid, reason_code text,          -- corrections are new rows [21]
  prev_entry_hash bytea, entry_hash bytea,       -- hash chain, P1+ [19]
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (org_id, created_at, entry_id)     -- partition-friendly
) PARTITION BY RANGE (created_at);

REVOKE UPDATE, DELETE, TRUNCATE ON ledger.mv_ledger FROM PUBLIC;  -- [20][21]
-- + BEFORE UPDATE OR DELETE trigger raising exception (compliance artefact)
-- + appends serialised per org via pg_advisory_xact_lock(hashtext(org_id::text)) [19]
```

Dual currency is structural: `kWh` fields are the physical truth, `₹` fields are `kWh × the correct tariff line` (energy vs MD vs PF — computed by the L4 impact calculator against the tariff version in force), `tCO₂e = avoided grid kWh × versioned CEA factor` with the factor row referenced, not inlined [27][28]. `bill_line_refs` makes every verified entry reconcilable to a physical bill — the trust anchor (§9.4 of the technical architecture).

### 4.7 Tenancy, residency, backup

| Concern | Decision |
|---|---|
| Isolation model | Shared schema + `org_id` on every row + **RLS policies on all tenant-scoped tables**; app sets `SET LOCAL app.current_org` per transaction; composite indexes lead with `org_id` [22][23][24] |
| Enterprise escape hatch | Database-per-tenant clone path documented (whole L2 is one DB — clone, replay topic, cut over) for contracts demanding physical isolation / dedicated PITR [23] |
| Residency | Managed Postgres in **AWS ap-south-1 (Mumbai)**; S3 Mumbai for cold tier & backups; region-deny SCP so nothing lands outside India [32][33][34]. GCP/Azure India equivalents acceptable `[!]` |
| Backup | Automated snapshots + WAL PITR (RPO ≤ 5 min); monthly restore drill (§5.3); ledger partitions additionally exported to S3 with object lock (WORM) from P1 `[!]` |
| Encryption | TLS in transit, AES-256 at rest (provider-managed keys P0, CMK when an enterprise asks) |

### 4.8 Retention & downsampling policy (consolidated)

| Dataset | Store | Hot (rowstore) | Columnstore | Retention | After retention |
|---|---|---|---|---|---|
| Raw telemetry (1s–1min) | `measurement` hypertable | 7 days | 7 d → 13 months | **13 months** `[~]` (covers one full seasonal cycle + billing disputes) | Drop chunks; P2+: export to Parquet/S3 first `[!]` |
| Raw events/alarms | `event` hypertable | 30 days | → 13 months | 13 months | Drop |
| 1-min / 15-min aggregates | caggs | 30 days | → 36 months | **36 months** | Drop (day-level survives) |
| Hour / day / shift aggregates | caggs + feature tables | — | 36 months+ | Indefinite `[~]` (tiny) | Keep |
| Derived features (SEC etc.) | `features.*` | — | 36 months | 36 months | Keep day-level rollup |
| Anomaly scores / findings | L3-owned, stored here | — | 12 months | 12 months | Keep those cited by prescriptions **forever** |
| Baselines | `baselines.*` | n/a | n/a | Locked ones **never deleted** | — |
| Tariffs, bills, production, factors | `commercial.*` | n/a | n/a | Life of customer + 8 years `[~]` (statutory audit horizon) | Archive |
| M&V ledger | `ledger.*` | n/a | n/a | **Forever** (append-only; partitions archived to WORM S3, never dropped from lineage) | — |

Retention is enforced with Timescale retention policies per hypertable/cagg; the asymmetry is deliberate — evidence cited by money-bearing artefacts (prescriptions, ledger) is exempt from every drop policy.

### 4.9 Store-by-store summary (one screen)

| Store | Technology | Key structures | Write pattern | Immutability | Primary consumers |
|---|---|---|---|---|---|
| Time-series | TimescaleDB hypertables + hierarchical caggs + columnstore | `measurement`, `event`, `agg_1min…agg_day` | Streaming append, out-of-order tolerated | Mutable within retention (telemetry is evidence, corrections via quality flags) | L3 all engines, L4 tools, L6 |
| Energy graph | Postgres adjacency + recursive CTE; in-memory mirror in L3 | `asset`, `asset_edge` (typed), vertical templates | Rare, onboarding + change events | Soft-versioned (`valid_from/to`) | L3 attribution, L4 `traverse_graph`, owner routing |
| Commercial & production context | Postgres relational, versioned rate structures | `tariff_version` + `tod_window`/`pf_slab`/`surcharge_series`, `bill/bill_line`, `shift_calendar`, `production_record`, `emission_factor` | Low-frequency, validated writes | Versioned; bills and factors never edited, only superseded | L3 tariff/MD engines, L4 impact calc, L5 reconcile |
| Feature store | Caggs (simple) + dbt-style jobs (complex) — **no Feast** | `features.*` with `event_time`/`computed_at`/`feature_set_version` | Scheduled batch + event-triggered | Recomputable; version-stamped | L3 detectors, L4 ranker |
| Baseline store | Postgres, versioned rows + lock trigger | `baseline` (draft→active→locked→retired), `nra` | New version per re-fit | **Locked-on-cite, trigger-enforced** | L3 deviation, L5 M&V |
| M&V & intensity ledger | Postgres append-only, partitioned, hash-chained (P1+) | `mv_ledger` dual-currency entries with `bill_line_refs` | Append-only, advisory-lock serialised | **REVOKE + trigger + hash chain + WORM export** | L5, L6 exports, CFO/sustainability packs |

### 4.10 What L2 deliberately does not do

- **No stream processing** — windowing/detection logic lives in L3; L2 exposes data, not judgements.
- **No user-facing prose or scores** — findings and prescriptions are L3/L4 artefacts stored against L2 references.
- **No digital twin** — the graph is minimum-viable topology for attribution and routing, not an SLD/3D model (explicit non-goal per the [technical architecture](../02-technical-architecture.md) §16).
- **No write-back to plant systems** — nothing in L2 addresses OT; read-only stance holds.
- **No second query engine in v1** — ClickHouse/DuckDB sidecars are P2/P3 options gated on measured benchmark breaches (§5.4), not defaults.

---

## 5. How this layer is tested and evaluated

Testing philosophy: L2's failure modes are silent (a wrong tariff version, a leaked tenant row, a re-fit baseline) rather than loud (a crash). The test strategy therefore weights *invariant enforcement* and *evidence resolvability* over throughput testing.

### 5.1 Schema & contract tests (CI, every merge)

- **Canonical-schema round-trip:** golden files of `Measurement/Event/ProductionRecord/BillLine` (per connector family) must ingest and read back losslessly; unknown fields rejected at the boundary.
- **Migration tests:** every migration runs against a seeded copy with representative data; reversibility checked where claimed; `locked` baseline and ledger immutability triggers covered by tests that *attempt* UPDATE/DELETE and assert failure.
- **RLS tests:** cross-tenant probe suite — every tenant-scoped table gets an automated "query as org A, expect zero org-B rows" test; a new table without an RLS policy fails CI via catalog assertion.
- **Tariff-model tests:** for each supported DISCOM template, a worked bill from the actual tariff order (e.g. JVVNL HT industrial with 75% billing-demand floor, TOD rebate, PF surcharge, FPPCA) must recompute to the printed total within ±0.5% [25][26]. Example invariant test shape:

```sql
-- immutability invariant: locked baselines reject mutation
DO $$ BEGIN
  UPDATE baselines.baseline SET model_params = '{}'::jsonb
   WHERE baseline_id = :locked_fixture_id;
  RAISE EXCEPTION 'TEST FAILED: locked baseline accepted UPDATE';
EXCEPTION WHEN raise_exception THEN NULL;  -- trigger fired: pass
END $$;
```

- **Point-in-time leakage tests:** dbt tests on every `features.*` model asserting `event_time <= computed_at` and that training-set builders never join a feature with `event_time > label_time` (dbt-timefence pattern) [18].
- **Emission-factor discipline tests:** every ledger entry's `avoided_tco2e` must equal `realised_kwh × factor` for the *referenced* factor row; no entry may reference a factor published after the entry's period end (no retroactive factor application).

### 5.2 Data-quality SLIs (production, alerting to ops)

| SLI | Definition | Target `[~]` |
|---|---|---|
| Ingest lag | p95 event-time → queryable-time, per plant | ≤ 60 s streaming; ≤ 15 min file-drop |
| Tag staleness | % of expected-active tags with no point in 2× nominal interval | < 2% |
| Quality ratio | share of `estimated/bad` points per plant-day | < 5%; alert at 10% |
| Cagg freshness | `now() − watermark` per continuous aggregate | ≤ 2× refresh interval |
| Bill completeness | plants with parsed+validated bill within N days of bill date | 100% within 7 d |
| Baseline coverage | % of active assets with an `active`/`locked` baseline in scope | ≥ 90% by week 8 per plant |
| Ledger chain integrity | hash-chain verifier job result | 100% pass, daily |
| Out-of-order ratio | % rows with ts older than current cagg watermark | Tracked; alert on step change (connector regression signal) |

### 5.3 Restore & durability drills

- **Monthly PITR drill:** restore production to a scratch instance at a random timestamp; run an automated checksum suite (row counts per hypertable chunk, ledger chain verification, random prescription evidence-pointer resolution). Time-to-restore recorded as an SLO (target: < 4 h for P2-scale data `[~]`).
- **Evidence-resolution drill:** quarterly, pick 20 random verified ledger entries; resolve every `bill_line_ref`, `baseline_id`, and evidence tag window end-to-end. This is a rehearsal for a hostile customer audit.

### 5.4 Query performance benchmarks (regression-gated)

Representative query pack run nightly against a production-scale synthetic dataset (50 plants × 1,000 tags × 13 months):

| Query | Budget p95 |
|---|---|
| 30-day 15-min profile, one asset | < 200 ms |
| MD spike forensic: 1-min incomer kVA ± 30 min window | < 300 ms |
| Graph traversal ≤ 4 hops + co-windowed telemetry for ≤ 20 assets | < 1 s |
| Shift SEC series, 90 days, one line | < 500 ms |
| Fleet benchmark aggregate (all plants, day-level, 12 months) | < 3 s |
| Ledger rollup for dashboard (verified ₹/kWh/tCO₂e by month) | < 200 ms |

Budgets breached → release blocked; this is the tripwire that tells us when the "one engine" bet needs the ClickHouse/lakehouse escape hatch — measured, not vibes.

---

## 6. Build phasing P0–P3

| Phase | Scope delivered in L2 | Explicitly deferred |
|---|---|---|
| **P0 (weeks 1–8)** | Single managed Postgres+TimescaleDB, ap-south-1. `measurement` hypertable + 15-min/hour/day caggs + compression & retention policies. Minimal `graph.asset` (incomer + top feeders). `commercial`: tariff_version + TOD/PF/FPPCA for pilot DISCOMs, bill/bill_line, shift_calendar, CEA factor seed. Baseline table with locking protocol. Ledger with REVOKE+trigger immutability. RLS on all tables. Ingest API implementing topic schemas | Redpanda (unless pilot needs fan-out), hash chain, Parquet cold tier, 1-min cagg, event hypertable if no SCADA yet |
| **P1 (months 3–6)** | Full typed-edge graph + vertical templates + in-memory mirror for attribution. Redpanda in front of writers. `production_record` + SEC feature jobs (dbt) with PIT tests. 1-min cagg + event hypertable (SCADA/PLC live). Ledger hash chain + WORM export. NRA records | Feature-store product, graph DB, per-tenant DBs |
| **P2 (months 6–12)** | Fleet-scale hardening: query benchmark gate, tiered storage/Parquet export of aged raw chunks `[!]`, cross-plant benchmark aggregates, emission-factor annual update runbook (CEA v22 expected ~Dec 2026 [28]), database-per-tenant provisioning path for enterprise deals | — |
| **P3** | Only if measured need: ClickHouse or DuckDB-on-Parquet sidecar for fleet analytics; Apache AGE if cross-plant graph analytics materialise; real-time feature serving if predictive MD ships as an operator surface | Neo4j (still), Feast/Tecton (still, unless serving requirement appears) |

Phase exit criteria (L2-specific):

| Phase | Exit criteria |
|---|---|
| P0 | First prescription's evidence pointers resolve end-to-end (tag → window → baseline → ₹ line); pilot DISCOM worked-bill test passes ±0.5%; RLS probe suite green; PITR restore drill #1 completed |
| P1 | Attribution query pack < 1 s p95 on real pilot graph; SEC features passing PIT-leakage tests on real production records; ledger hash chain verifying daily; first *verified* ledger entry reconciled against an actual DISCOM bill line |
| P2 | Query benchmark gate live in CI; restore drill SLO (< 4 h) met at 30-plant data volume; tiered-storage export/read-back round-trip proven; second DISCOM state onboarded from template in < 2 weeks `[~]` |
| P3 trigger review | Any of: benchmark budget breached 2 consecutive months · fleet analytics queries > 30% of DB load · a signed enterprise contract requiring physical isolation · real-time serving requirement confirmed |

---

## 7. Open questions

1. **kVAh billing states `[!]`** — several DISCOMs bill energy in kVAh rather than kWh; the tariff model supports the flag but the impact calculator and SEC conventions need a worked treatment per state. Verify against pilot DISCOM before P0 exit.
2. **Redpanda timing** — is a broker warranted at 1–3 pilots, or does the ingest-API-with-topic-schemas stance hold until L3 stream processors exist? Decide on pilot #2 data volumes.
3. **Raw retention 13 months** — enough for year-on-year seasonal baselines? Cement/pharma seasonality may argue for 25 months of raw at 1-min (cost is modest); decide from pilot baseline quality `[~]`.
4. **Topology versioning depth** — is `valid_from/valid_to` soft versioning sufficient for M&V replay, or do we need full bitemporal modelling on `graph.*`? Current bet: soft versioning suffices below ~10 topology edits/plant/year `[~]`.
5. **Ledger hash-chain scope** — chain per org (current design) vs per plant; per-org serialises concurrent appends across plants of one group [19]. Likely irrelevant at our append rates; confirm.
6. **Managed provider** — Tiger Cloud (first-party Timescale features, but newer India presence `[!]`) vs self-managed extension on RDS/EC2 vs Azure Flexible Server. Verify current TimescaleDB version support per provider in ap-south region before committing.
7. **DPDP classification** — telemetry is non-personal, but operator names in workflow/audit records are personal data under DPDP; confirm the boundary sits in L5 stores and that L2 holds roles, not persons [33].
8. **Baseline artefact storage** — model params in JSONB claimed sufficient for reproducibility; validate on the first regression-class baseline that a re-fit from stored params reproduces the band within tolerance.

---

# Citations

1. https://www.tigerdata.com/blog/timescaledb-2-27 — TimescaleDB 2.27: `compress_after_refresh`, auto segmentby, vectorised columnstore
2. https://github.com/timescale/timescaledb/releases/tag/2.28.0 — TimescaleDB 2.28 (Jun 2026): first()/last() from batch metadata, incremental cagg refresh
3. https://www.tigerdata.com/blog/timescaledb-2-26 — vectorised time_bucket(), ColumnarIndexScan, bloom filters
4. https://www.tigerdata.com/docs/build/continuous-aggregates/compression-on-continuous-aggregates — caggs + columnstore policies
5. https://docs.influxdata.com/influxdb3/which-influxdb-3/ — InfluxDB 3 Core vs Enterprise positioning
6. https://docs.influxdata.com/influxdb3/enterprise/admin/license/ — per-CPU licensing; queries error on license expiry
7. https://docs.influxdata.com/influxdb3/core/plugins/library/official/downsampler/ — plugin-based downsampling
8. https://ar5iv.labs.arxiv.org/html/2204.09795 — SciTS IIoT TSDB benchmark (ClickHouse/InfluxDB/TimescaleDB/Postgres)
9. https://github.com/bioinformatics-ua/SmartCampus-databases-benchmark — six-DB ingest/query benchmark
10. https://trybuildpilot.com/538-clickhouse-vs-timescaledb-vs-questdb-2026 — 2026 comparison summary
11. https://docs.victoriametrics.com/victoriametrics/faq/ — VictoriaMetrics vs TimescaleDB; backfill; IoT positioning
12. https://docs.victoriametrics.com/keyconcepts/index.html — float64-only data model
13. https://db-news.com/the-case-against-neo4j-for-simple-hierarchies — decision rubric for hierarchies
14. https://medium.com/codex/graph-queries-with-recursive-ctes-you-dont-need-neo4j-3aade6fb7f85 — recursive CTE graph patterns, CYCLE, indexing both directions
15. https://hld.handbook.academy/curriculum/data-systems/graph-databases/ — when joins are the problem; 3–4 hop threshold
16. https://datarekha.com/mlops/feature-stores/ — feature stores: when needed, when not; PIT correctness
17. https://theneuralbase.com/feature-store/learn/advanced/when-feature-store-is-overkill/ — Feast overhead vs binding constraints
18. https://github.com/gauthierpiarrette/dbt-timefence — dbt PIT-join macro + leakage tests
19. https://tracehold.ai/blog/immutable-audit-log-hmac-hash-chain/ — hash-chained audit log, advisory-lock serialisation
20. https://anotherdimensioncreativegroup.com/blog/immutable-audit-trails-implementation — trigger + REVOKE defense in depth
21. https://cursa.app/en/page/modeling-append-only-event-tables-in-postgresql — append-only event tables; compensating events
22. https://clickhouse.com/resources/engineering/multi-tenant-saas-postgres-architecture — shared schema + RLS default; DB-per-tenant for regulated
23. https://cadence.withremote.ai/blog/multi-tenant-postgres-schema — tenancy pattern thresholds
24. https://hld.handbook.academy/curriculum/architecture-patterns/multi-tenancy/ — silo/pool spectrum; catalog bloat limits
25. https://cescrajasthan.co.in/kedl/pages/event/uploads/Tariff-2025%202.pdf — JVVNL tariff order: CMD, 75% billing-demand floor, TOD, PF slabs
26. https://aperc.gov.in/admin/upload/TariffOrderforFY202526.pdf — AP DISCOMs FY25-26: TOD for industrial ≥15 kW, FPPCA pass-through
27. https://batchwise.ai/compare/cea-factor-vs-iea-factor/ — CEA v21.0 factors (FY24-25: 0.7117 tCO₂/MWh weighted avg)
28. https://reclimatize.in/india-grid-emission-factor-cea-ccts/ — CEA version history v19–v21, WAEF trend
29. https://www.evo-world.org/en/m-v-community/mv-focus/858-magazine-issue-2/1094-stopping-m-v-adjustment-abuse — EVO on Option C adjustment abuse
30. https://www.energy.gov/sites/default/files/2024-10/mv_guide_5_0.pdf — FEMP M&V Guidelines 5.0: options, routine vs non-routine adjustments
31. https://c2e2.unepccc.org/kms_object/ipmvp-application-guide-on-non-routine-events-adjustments/ — IPMVP NRE/NRA application guide (EVO 2020)
32. https://aws.amazon.com/compliance/india-data-protection/ — AWS Mumbai region data protection & residency
33. https://opsiocloud.com/in/blogs/dpdpa-cloud-compliance-aws-azure/ — DPDPA compliance on AWS/Azure India regions
34. https://github.com/aws-samples/sample-aws-india-compliance-mcp — DPDP Rules 2025 / RBI / CERT-In control mapping, region-deny posture
