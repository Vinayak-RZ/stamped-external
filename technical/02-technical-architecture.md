---
type: Product Architecture
title: Stamped Energy — Detailed Technical Architecture v2
description: "Engineering-grounded architecture for delivering a verified 15–20% electricity bill reduction: seven-layer stack (L0–L6), explicit savings math, layer contracts, agentic L4, resolved technology decisions, production-readiness and evaluation gates."
tags: [stamped-energy, technical, architecture]
timestamp: "2026-07-09T01:45:00Z"
---
# Stamped Energy — Detailed Technical Architecture

*Version 2.0 | July 2026*
*Status: Pre-build — the architecture specification the product repo is built against*
*Companion docs in this pack:* [Product architecture](01-product-architecture.md) · [Master document](00-stamped-master-document.md) · Layer specs in [`layers/`](layers/) · Cross-cutting specs in [`cross-cutting/`](cross-cutting/)

> **Honesty convention:** `[~]` approximate / benchmark-derived · `[!]` evolving — verify before customer-facing claims
> **Outcome targets (architecture must enable):** 12–20% total electricity bill reduction `[~]` · 15–25% MD charge reduction `[~]` · 10–20% non-production energy flagged within 90 days `[~]` · auditable intensity / Scope 2 evidence from verified grid kWh reduction

---

## 1. Architecture intent

This document specifies **how Stamped is built layer by layer** so the platform can reliably:

1. **Deliver 15–20% class savings** by systematically closing six industrial waste categories (not one-off insights).
2. **Support operational sustainability** — SEC/intensity trends, Scope 2 from verified grid reduction, PAT/BRSR/OEM audit exports — **without** becoming a carbon accounting platform.
3. **Run production-grade in live plants** — continuous high-volume telemetry, sub-minute demand detection, graceful degradation when connectivity or model services fail.
4. **Prove itself** — every model, rule pack, and agent output is versioned, evaluated against gates, and traceable from prescription back to raw telemetry and bill line.

**Design constraint:** Every layer must either (a) improve detection of waste, (b) improve prescription quality or closure rate, (c) improve M&V defensibility, or (d) produce sustainability evidence from the same operational ledger. Layers that only add charts are rejected.

**What changed from v1.0:** explicit ₹ savings math (§3), resolved technology decisions (§4), formal inter-layer contracts (§5), L4 upgraded from "bounded agent" to a full agentic architecture with verifier loop (§10), and two new first-class sections — production readiness (§16) and evaluation & verification (§17) — expanded in the cross-cutting docs.

---

## 2. Master architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ L0  PLANT SYSTEMS (customer-owned, read-only tap)                           │
│     Incomer/feeder meters · SCADA historians · PLCs · CNC gateways          │
│     EMS/BMS exports · ERP/MES production · solar/WHR/DG meters · DISCOM bill│
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│ L1  CONNECT & NORMALISE                                                     │
│     Edge gateway (optional) · Protocol adapters · Schema normaliser         │
│     Tag mapper & discovery · Data-quality gate · Bill & tariff ingest       │
│     Event bus ingress                                                       │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│ L2  UNIVERSAL REPOSITORY (six stores)                                       │
│     Time-series · Energy graph · Commercial & production context            │
│     Feature store · Baseline store · M&V & intensity ledger                 │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│ L3  INTELLIGENCE CORE (numeric — signals, scores, structured findings)      │
│     Baseline & SEC · Anomaly & deviation · Attribution · Rules & physics    │
│     Demand & MD · Tariff & PF · Source-mix dispatch · Waste classifier      │
│     Per-plant calibration                                                   │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│ L4  KNOWLEDGE & REASONING (agentic — evidence-bound prescription drafting)  │
│     Industrial RAG · Prescription agent (planner → tools → verifier)        │
│     Impact calculator · Rx ranker & dedup · Sustainability narrative        │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│ L5  CLOSURE & VERIFICATION                                                  │
│     Workflow & work orders · Notification router (WhatsApp…) · M&V engine   │
│     Bill reconciliation · Intensity verify · Savings ledger · Audit trail   │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│ L6  EXPERIENCE & INTEGRATION                                                │
│     Plant dashboard · Prescription queue · WhatsApp · PDF/CSV export        │
│     Sustainability pack · REST API · Outbound webhooks · ERP/ESG connectors │
└─────────────────────────────────────────────────────────────────────────────┘
```

Each layer has a dedicated deep-research spec in this pack:

| Layer | Spec | One-line scope |
| --- | --- | --- |
| L1 | [L1 — Connect & normalise](layers/L1-connect-and-normalise.md) | Protocols, connectors, edge gateway, bill ingest, normalisation schema |
| L2 | [L2 — Universal Repository](layers/L2-universal-repository.md) | Six stores: TSDB, graph, context, features, baselines, ledger |
| L3 | [L3 — Intelligence core](layers/L3-intelligence-core.md) | Model families per engine, rules/physics packs, calibration, per-engine eval protocol |
| L4 | [L4 — Knowledge & reasoning](layers/L4-knowledge-and-reasoning.md) | Agentic RAG design, corpus, guardrails, eval harness |
| L5 | [L5 — Closure & verification](layers/L5-closure-and-verification.md) | Workflow, WhatsApp, IPMVP M&V, bill reconciliation, ledger |
| L6 | [L6 — Experience & integration](layers/L6-experience-and-integration.md) | Dashboard, exports, REST API, webhooks, custom-system integration |
| Cross | [Production engineering](cross-cutting/03-production-engineering.md) | Streaming backbone, reliability patterns, edge, tenancy, observability |
| Cross | [Evaluation, testing & quality](cross-cutting/04-evaluation-and-quality.md) | Testing pyramid, data-quality gates, ML/LLM evals, CI gates, shadow mode |

---

## 3. Savings architecture — how 15–20% is engineered

Savings are **not** a single model output. They are the **sum of closed prescription categories**, each with its own detection engine, M&V method, and contribution band `[~]`. The 15–20% headline only holds if the architecture (a) detects across all six categories, (b) converts detections into executed actions (closure rate), and (c) verifies on the bill.

### 3.1 Six waste categories → engines → savings band

| # | Waste category | Primary L3 engines | Typical bill impact `[~]` | Data minimum | Sustainability co-benefit |
| --- | --- | --- | --- | --- | --- |
| 1 | **Power quality & MD** | Demand/MD engine, tariff engine, attribution | **3–8%** of total bill (15–25% of MD line) | Incomer meter + bill | Lower peak grid draw → Scope 2 ↓ |
| 2 | **Furnaces & process heat** | Baseline/SEC, waste classifier, rules (holding/setback) | **2–5%** | Feeder meter or SCADA furnace tags | kWh/ton or kWh/batch ↓ |
| 3 | **Idle & auxiliary loads** | Waste classifier, shift calendar, anomaly | **2–4%** | Incomer + shift schedule | Non-production kWh ↓ |
| 4 | **Compressed air** | Rules (SP drift), anomaly, attribution | **1–3%** | Compressor feeder or proxy meter | Utility SEC ↓ |
| 5 | **Cooling / HVAC / chillers** | Baseline, COP rules, TOD engine | **1–3%** | Chiller meter or BMS export | Pharma/chemical intensity |
| 6 | **Source mix & VFD opportunities** | Source-mix dispatch, rules | **1–4%** | Multi-source meters + tariff | Renewable share ↑, grid Scope 2 ↓ |

**Architecture rule:** Each category has a **dedicated detection pipeline** feeding the prescription agent. Generic "energy is high" alerts are blocked at L4 — only category-tagged findings become prescriptions.

### 3.2 Worked savings math — reference plant `[~]`

Reference: North-India forging/auto-component plant, **₹50L/month** bill, HT connection, CMD 2000 kVA, bill composition typical of UPPCL/DHBVN HT industrial tariffs:

| Bill component | Share `[~]` | ₹/month |
| --- | --- | --- |
| Energy charges (incl. TOD) | ~62% | ₹31.0L |
| Demand charges (billing demand × MD rate) | ~18% | ₹9.0L |
| Fuel surcharge / FPPCA | ~10% | ₹5.0L |
| Electricity duty & taxes | ~8% | ₹4.0L |
| PF incentive/penalty, misc | ~2% | ₹1.0L |

Category-by-category, conservative vs expected, with the mechanism:

| Category | Mechanism | Conservative | Expected | ₹/month expected |
| --- | --- | --- | --- | --- |
| MD & power quality | Stagger co-starts, trim CMD, fix PF to incentive slab | 2.0% | 4.5% | ₹2.25L |
| Furnace / process heat | Holding-load setback, batch consolidation, preheat discipline | 1.5% | 3.5% | ₹1.75L |
| Idle & auxiliary | Off-shift shutdown discipline, idle-threshold alerts | 1.5% | 3.0% | ₹1.50L |
| Compressed air | Setpoint reduction, leak-proxy fixes, sequencing | 0.5% | 2.0% | ₹1.00L |
| HVAC / cooling | Schedule + setpoint discipline, COP drift fixes | 0.5% | 1.5% | ₹0.75L |
| Source mix / TOD | Load shift to off-peak/solar windows, dispatch Rx | 1.0% | 2.5% | ₹1.25L |
| **Stack (pre-closure)** | | **7.0%** | **17.0%** | **₹8.5L** |

Two discounts apply to the raw stack:

1. **Closure rate** — not every prescription is executed. At the ≥60% closure target on high-priority Rx, expected verified savings = 17.0% × ~0.75 effective-weighted closure `[~]` ≈ **12.75%**; at mature closure (>80%) the stack approaches **15–17%**.
2. **Overlap dedup** — categories share root causes (e.g. idle furnace holding counts once). The waste classifier + Rx deduplicator (§10.5) enforce single-counting; the bands above are post-overlap estimates from Zerowatt-pattern playbooks and vertical benchmarks.

**Conclusion the architecture is sized for:** 8–12% verified in the first two quarters (Path B entry), compounding to **15–20% at Path A maturity with ≥70% closure** `[~]`. The binding constraint is closure rate and M&V defensibility, not detection cleverness — which is why L5 is a first-class layer, not a notification afterthought.

### 3.3 Savings stack by integration path

| Path | Month 1–2 (fast wins) | Month 3–6 (compound) | Cumulative target `[~]` |
| --- | --- | --- | --- |
| **Path B** (meter + bill) | MD pattern, PF penalty, TOD exposure, off-shift incomer drift | Sub-meter attribution for top 2 areas | **8–12%** bill |
| **Path A** (full OT) | Above + machine-level SEC, shift-start attribution, compressor/furnace Rx | Source dispatch, cross-line benchmark, PdM fusion | **12–20%** bill |

### 3.4 Closure rate as architectural variable

| Lever | Layer | Mechanism |
| --- | --- | --- |
| Actionable format | L4 → L5 | What/Why/Who/Effort/₹/When — no interpretation needed |
| Floor delivery | L5 | WhatsApp to role, not dashboard-only |
| Effort gating | L4 ranker | Quick wins (dispatch change) ranked above capex (new VFD) |
| Owner routing | L2 graph | Asset → default role map (electrical, production, utilities) |
| Verification loop | L5 M&V | Done ≠ saved; bill line confirms |
| Defer/reject learning | L3 calibrate | Deferred Rx → lower confidence or different framing |
| Alert budget | L3/L4 | Cap open Rx per role; false-positive budget per plant/day |

**Target:** ≥60% of high-priority prescriptions acted within one billing cycle `[!]` — the workflow engine measures this natively (§11.1).

---

## 4. Resolved engineering decisions

v1.0 §17 left six decisions open. Defaults are now set (deep justification in the linked layer/cross-cutting specs). Each is a **default, revisitable with pilot evidence** — not dogma.

**Cost rule (binding):** at every fork, **ship the minimum-cost option that is production-correct at pilot scale**; document the paid or enterprise upgrade and the trigger to switch (see §4.1). Do not pay for hyperscale or vendor markup before the envelope demands it.

| # | Decision | Start now (min cost) | Upgrade when (better / paid) | Deep dive |
| --- | --- | --- | --- | --- |
| 1 | Time-series DB | **TimescaleDB on managed Postgres** (one engine for TS + relational + pgvector) | ClickHouse sidecar only if analytics queries breach Postgres SLOs at fleet scale `[!]` | [L2](layers/L2-universal-repository.md) |
| 2 | Graph DB vs relational | **Relational adjacency in Postgres** + in-memory cache | Dedicated graph DB only if traversal latency breaches SLO at >500 nodes/plant `[!]` | [L2](layers/L2-universal-repository.md) |
| 3 | MD spike detection latency | **Hybrid:** in-process 1-min hot path on incomer; 15-min batch elsewhere | Dedicated stream processor only if hot-path logic outgrows ingest service `[!]` | [Production engineering](cross-cutting/03-production-engineering.md) |
| 4 | WhatsApp integration | **Meta WhatsApp Cloud API direct** (~₹7/plant/month at utility rates; full API control) | **Indian BSP** (Gupshup, AiSensy, etc.) when an enterprise deal requires local support, managed template ops, or dual-vendor redundancy — BSP markup buys nothing at pilot volumes | [L5](layers/L5-closure-and-verification.md) |
| 5 | Emission factor library | **CEA grid factors**, versioned per vintage | Customer override with documented source (always allowed) | §15.4 |
| 6 | Production tagging minimum | **CSV/manual batch template** + ERP export where available | Named ERP connectors (SAP, Tally) as paid Tier-4 integrations when ≥3 customers request | [L1](layers/L1-connect-and-normalise.md) |
| 7 | Agent orchestration | **LangGraph-class** orchestration with Postgres checkpointing on existing L2 DB | Managed agent platform only if ops burden exceeds one engineer-day/month `[!]` | [L4](layers/L4-knowledge-and-reasoning.md) |
| 8 | Event backbone | **Postgres transactional outbox** + idempotent ingest writers (same DB as L2; at-least-once + `(plant, tag, timestamp)` keys) | **Redpanda or MSK** when fan-out to multiple independent consumers, sustained replay/backfill, or outbox drain exceeds ~5k msg/s sustained `[!]` | [Production engineering](cross-cutting/03-production-engineering.md) |
| 9 | Service architecture | **Modular monolith (FastAPI) + satellites** on managed containers (e.g. ECS Fargate) | Extract services or add K8s only when team or isolation needs justify the ops tax | [Production engineering](cross-cutting/03-production-engineering.md) |
| 10 | MQTT broker `[new]` | **Mosquitto** on edge gateway (free, outbound-only) | **EMQX Cloud / HiveMQ** when enterprise customers require vendor SLA, clustering, or managed bridge ops | [L1](layers/L1-connect-and-normalise.md) |
| 11 | OT protocol drivers `[new]` | **Build:** Modbus TCP/RTU profiles, CSV/file, bill PDF, generic MQTT | **Buy per site:** Kepware / EMQX NeuronEX when OPC-DA, S7comm, or exotic PLC protocols block onboarding | [L1](layers/L1-connect-and-normalise.md) |
| 12 | LLM inference `[new]` | **Frontier API** (pay-per-prescription; lowest fixed cost) | **Self-hosted** open-weight model when a data-residency contract forbids cloud LLM or API spend exceeds self-host break-even `[!]` | [L4](layers/L4-knowledge-and-reasoning.md) |

### 4.1 Cost-conscious defaults — full upgrade map

Every layer spec follows this pattern. Summary of the highest-impact forks:

| Area | Start now | Upgrade when | Why the paid option is better (later) |
| --- | --- | --- | --- |
| **Event backbone** | Postgres outbox + ingest API implementing topic schemas | Redpanda / MSK | Independent replay, many consumer groups, decoupled backfill without loading the OLTP DB |
| **WhatsApp** | Meta Cloud API direct + MSG91 DLT SMS fallback | Indian BSP | White-glove template management, local support desk, dual-vendor delivery redundancy |
| **Edge MQTT** | Mosquitto on DIN-rail 4G gateway | EMQX Cloud | Clustering, enterprise support, managed bridge to cloud |
| **OT connectivity** | Modbus profile library (built) | Kepware / NeuronEX per plant | 150+ drivers; OPC-DA tunnelling; air-gapped OT without Stamped building drivers |
| **Bill OCR** | Open-source layout parser (e.g. Docling) + vision-LLM fallback | Commercial doc-AI (LlamaParse, etc.) | Higher table-extraction accuracy on messy DISCOM PDFs when recompute gate failure rate > threshold |
| **Observability** | OpenTelemetry → Grafana Cloud free tier | Grafana Cloud Pro / Datadog | Longer retention, enterprise SSO, on-call integrations |
| **Workflow engine** | Postgres state machine + durable timer rows | Temporal.io | Cross-service durable workflows when satellites multiply beyond one DB |
| **Compliance** | ISO 27001 via Sprinto-class Indian path `[~]` | Full SOC 2 Type II | Enterprise procurement gate for listed-parent accounts |

**Module boundary to defend:** all event publication goes through one `events` module with versioned JSON schemas — swapping outbox → Redpanda is a relay change, not a rewrite.

---

## 5. Layer contracts

Layers communicate through four canonical, versioned schemas (Pydantic-modelled, JSON on the wire, schema-registry governed `[!]`). **A layer may only consume its upstream contract — never reach around it.** Contract tests at each boundary are CI-blocking (see [evaluation doc](cross-cutting/04-evaluation-and-quality.md)).

### 5.1 L1 → L2: `Measurement` (and siblings `Event`, `ProductionRecord`, `BillLine`)

```
Measurement {
  plant_id, asset_id, metric_type,     // active_power_kw, apparent_power_kva, energy_kwh, pf, ...
  timestamp_utc, value, unit,
  quality,                             // good | estimated | bad | stale
  source_system, source_tag,           // lineage — mandatory
  granularity,                         // raw | 1min | 15min | shift | day
  ingest_batch_id                      // idempotency + replay key
}
```

Guarantees L1 makes to L2: units normalised · timestamps UTC (plant TZ preserved in graph metadata) · quality-coded, never silently repaired · at-least-once delivery with idempotent keys · late/out-of-order data flagged, not dropped.

### 5.2 L3 → L4: `Finding`

```
Finding {
  finding_id, plant_id,
  category,                            // md_overlap | compressor_sp_drift | furnace_holding | ... (closed enum)
  waste_category,                      // one of the six (§3.1)
  assets[],
  evidence {                           // machine-checkable — L4 verifier re-derives these
    metric, baseline_value, actual_value, window,
    baseline_id, model_version, rule_version
  },
  confidence,                          // calibrated 0–1
  estimated_monthly_kwh, estimated_monthly_inr,
  urgency                              // low | medium | high
}
```

Guarantees L3 makes to L4: findings are category-tagged (generic alerts rejected) · every number traces to a versioned baseline/model/rule · confidence is calibrated, not raw model score.

### 5.3 L4 → L5: `Prescription`

```
Prescription {
  id, status, priority,
  what, why, who, effort, when,        // action template ID + parameters, not free text (§10.4)
  impact { inr_monthly, kwh_monthly, tco2e_monthly, confidence_interval },
  waste_category,
  finding_refs[], evidence_refs[],     // tag IDs, timestamps, baseline ID — mandatory
  sustainability_tags[],               // scope2_grid_reduction | sec_improvement | ...
  mv_plan { method, baseline_id, measurement_boundary, verification_window },
  provenance { agent_version, prompt_version, rule_versions[], model_versions[] }
}
```

Guarantees L4 makes to L5: passed rules-engine veto · impact numbers recomputed deterministically by the impact calculator (never LLM arithmetic) · action drawn from the approved template taxonomy · full provenance for reproducibility.

### 5.4 L5 → L6: `LedgerEntry`

```
LedgerEntry {
  entry_id, prescription_id, period_start, period_end,
  potential_kwh, realised_kwh, potential_inr, realised_inr,
  avoided_tco2e,                       // grid kWh × versioned emission factor
  mv_method, baseline_id,              // IPMVP option, locked baseline
  bill_line_refs[],                    // DISCOM bill reconciliation
  intensity_delta,                     // SEC change if production tagged
  verification_status                  // pending | verified | disputed
}
```

Guarantees L5 makes to L6: append-only (corrections are new entries, never edits) · baseline locked at prescription issue, immutable thereafter · disputed entries carry reason codes.

---

## 6. Layer 0 — Plant systems

### 6.1 Source inventory

| Source type | Examples | Signals extracted | Priority |
| --- | --- | --- | --- |
| **Incomer meter** | Schneider PM, Elmeasure, L&T, Secure | kW, kVA, kWh, PF, MD, harmonics `[!]` | P0 — mandatory |
| **Feeder/sub meters** | Process areas, utilities | Area kWh, load profile | P0–P1 |
| **SCADA/historian** | WinCC, FactoryTalk, iFIX, Ignition, AVEVA/PI | Tag values, alarms, equipment states | P1 |
| **PLC** | S7, ControlLogix, MELSEC | Machine state, cycle, spindle, faults | P1 |
| **EMS export** | Plant EMS, Schneider PME | Aggregates, existing baselines | P0 wedge |
| **ERP/MES** | SAP, Oracle, Tally | Production qty, SKU, batch ID, shift | P1 for SEC |
| **On-site generation** | Solar, WHR, DG meters | Export/import, availability | P1 |
| **BMS** `[!]` | HVAC zones | Temp, runtime, COP proxy | P2 |
| **DISCOM bill** | PDF | Energy, MD, PF, charges, tariff | P0 — mandatory |
| **Manual** | Logbooks, maintenance records, batch entry | Production fallback, last service, outages | P1 via upload |

### 6.2 Integration principles

- **Read-only** — no write to PLC/SCADA setpoints, architecturally enforced (no write-capable credentials ever provisioned)
- **Non-invasive** — no rip-and-replace of existing EMS
- **Progressive depth** — Path B → A without re-platforming customer
- **Evidence lineage** — every prescription links to source tag IDs and bill line items

---

## 7. Layer 1 — Connect & normalise

Full spec: [L1 — Connect & normalise](layers/L1-connect-and-normalise.md)

### 7.1 Components

| Component | Function | Details |
| --- | --- | --- |
| **Edge gateway** `[!]` | On-plant buffer + protocol termination | Containerized Linux agent; deploy when no cloud VPN, intermittent WAN, or IT mandates local buffer. Store-and-forward, outbound-only mTLS |
| **Protocol adapters** | OT/IT protocol translation | OPC UA, Modbus TCP/RTU, MQTT (Sparkplug-aware), BACnet/IP `[!]`, DLMS/COSEM for HT meters `[!]`, REST (EMS/ERP), file drop (CSV historian export) |
| **Schema normaliser** | Canonical data model | All sources → `Measurement`, `Event`, `ProductionRecord`, `BillLine` (§5.1) |
| **Tag mapper** | Vendor tag → semantic ID | `COMPRESSOR_2.kW` → `asset:compressor-2/metric:active_power` |
| **Tag discovery** `[!]` | Semi-automated mapping assist | LLM suggests mappings from tag names + vertical template; human confirms |
| **Data-quality gate** | Ingestion hygiene — **blocking, not advisory** | Physics checks (PF ∈ [0,1], kW ≤ kVA), stale-tag detection, gap detection, outlier flagging; bad data quarantined with quality codes, never silently fixed |
| **Bill ingest** | PDF → structured bill | Layout-aware OCR + LLM extraction → validated against tariff schema; human review queue for low-confidence extractions |
| **Tariff parser** | DISCOM order → rate rules | State/board templates (UPPCL, PVVNL, UPCL, MSEDCL, DHBVN, PSPCL …) `[!]` |
| **Event bus ingress** | Streaming entry point | MQTT at plant boundary → ingest service → Postgres outbox + Timescale writers (§4.1; Redpanda upgrade when fan-out trigger fires) |

### 7.2 Deployment topologies

| Topology | When | Data flow |
| --- | --- | --- |
| **Cloud-direct** | IT allows outbound HTTPS/MQTT | Plant → encrypted stream → cloud ingest |
| **Edge-buffered** | Air-gapped OT common | Plant → gateway buffer → batch/stream uplink |
| **File-sync** | Legacy EMS only exports CSV | Scheduled drop → poll ingest |

---

## 8. Layer 2 — Universal Repository

Full spec: [L2 — Universal Repository](layers/L2-universal-repository.md)

The repository is the **single source of truth** for intelligence, M&V, and sustainability evidence. Six coupled stores, all on the Postgres/Timescale core (§4 decision 1–2).

### 8.1 Time-series store

| Dataset | Retention | Granularity | Use |
| --- | --- | --- | --- |
| Raw telemetry | 13 months `[~]` | 1s–15min native → rolled up | Attribution, forensic MD |
| Aggregates | 36 months | 1 min, 15 min, hour, shift, day | Baselines, dashboards |
| Derived metrics | 36 months | SEC, specific power, load factor | Intelligence, sustainability |
| Anomaly scores | 12 months | per event | Rx evidence |
| Baseline bands | Rolling | per asset/shift/product | M&V reference |

### 8.2 Energy graph (topology)

Hierarchical asset model with **typed edges** stored relationally, cached in-memory by services:

```
Plant └── System └── Equipment └── MeasurementPoint
Edges: feeds · drives · shares_electrical_bus · starts_with · thermal_coupling [!]
```

Powers: MD spike attribution · owner routing · SEC normalisation · sustainability allocation. **Vertical templates** (forging, die casting, cement kiln, pharma HVAC) customised at onboarding — never drawn from scratch.

### 8.3 Commercial & production context store

| Entity | Contents |
| --- | --- |
| **TariffContract** | DISCOM, category, CMD, energy rate, MD rate, TOD windows, PF slabs, FPPCA — **versioned rate structures** |
| **ShiftCalendar** | Shift A/B/C times, breaks, planned maintenance windows |
| **ProductionContext** | Batch ID, SKU, tonnage, parts count, line speed — linked to time windows |
| **SourceMix** | Grid, solar, WHR, DG availability and meter mapping |
| **EmissionFactor** `[~]` | CEA grid factor per vintage — versioned; customer override with source |

### 8.4 Feature store

Continuous aggregates + scheduled transformation jobs (no dedicated feature-store product in v1 — §4): rolling kW stats per asset/shift · SEC (kWh/ton, kWh/part, kWh/batch) · specific power · load factor · startup event catalogue · non-production energy ratio · TOD exposure. Point-in-time correctness enforced for training reads.

### 8.5 Baseline store

Expected bands per asset/shift/product with **immutability rule:** once a baseline is cited by a prescription's `mv_plan`, it is locked — retraining produces a new baseline version; the old one remains for M&V audit.

### 8.6 M&V & intensity ledger

Append-only ledger of verified outcomes — dual currency (₹ + kWh + tCO₂e), schema at §5.4. Event-sourced design; this ledger is the **bridge between cost savings and sustainability reporting** and the ground truth for model calibration (§17.4).

---

## 9. Layer 3 — Intelligence core

Full spec: [L3 — Intelligence core](layers/L3-intelligence-core.md) — model-family research, per-engine evaluation protocol.

All engines output **structured `Finding` objects** (§5.2) — never user-facing prose.

### 9.1 Engine registry

| Engine | Default technique `[~]` | Output | Waste categories |
| --- | --- | --- | --- |
| **Baseline & SEC** | Regression with calendar/production covariates (TOWT-style), quantile bands; gradient boosting where interpretability budget allows; fleet priors for cold start | Expected kW/SEC band per asset/shift/product | Furnaces, idle, SEC drift |
| **Anomaly & deviation** | Residual-based (EWMA/CUSUM on baseline residuals) first; Isolation Forest for multivariate; contextual suppression (startup windows, mix changes) | Scored anomaly events | All six |
| **Attribution** | Ramp detection + graph traversal + temporal cross-correlation | Ranked cause list with confidence | MD overlap, co-starts |
| **Rules & physics** | Deterministic, versioned rule packs (declarative format, code-reviewed, unit-tested) | Findings + veto capability | Compressor SP, PF, holding, COP |
| **Demand & MD** | MD histogram, spike post-mortem, short-horizon MD forecast, stagger simulator (deterministic what-if) | MD findings + ₹ per spike | **MD (3–8% of bill)** |
| **Tariff & PF** | Deterministic bill-component mapping; marginal ₹ per line item | ₹ attribution for every Rx | MD, PF penalties |
| **Source-mix dispatch** `[P1]` | MILP or greedy rule solver `[~]` | Dispatch schedule Rx | Source mix (Scope 2) |
| **Waste classifier** | Rule-first mapping findings → six categories | Category tags | Reporting rollups |
| **Per-plant calibration** | Parameter layer (thresholds, SEC norms, suppression windows) — Bayesian updating, not per-plant retrains | Plant config | False-positive control |

### 9.2 Model discipline (binding)

- **Interpretability is mandatory** — findings feed plant engineers and M&V audits; black-box-only models are rejected for baseline/M&V roles.
- **Every model versioned in a registry**; finding evidence cites `model_version` + `baseline_id` + `rule_version`.
- **Per-engine evaluation protocol** (metrics, targets, backtests, drift triggers, champion/challenger) defined in [L3 spec §5](layers/L3-intelligence-core.md) and enforced per [evaluation doc](cross-cutting/04-evaluation-and-quality.md). Headline gates `[~]`: baseline CVRMSE/NMBE within ASHRAE G14 bounds; anomaly precision ≥ target on labelled incident set with a hard alert budget per plant/day.

---

## 10. Layer 4 — Knowledge & reasoning (agentic)

Full spec: [L4 — Knowledge & reasoning](layers/L4-knowledge-and-reasoning.md)

v2 upgrades L4 from "bounded prescription agent" to an explicit **agentic architecture**: a checkpointed state graph with planner, tool-using evidence gathering, drafting, and a **verifier loop** — bounded at every step.

### 10.1 Agent graph

```
Finding(s) ──► PLANNER ──► EVIDENCE GATHERER ──► DRAFTER ──► VERIFIER ──► RULES VETO ──► emit Prescription
                 │            (tool calls)          │            │              │
                 │                                  │            │ fail: revise │ fail: reject/flag
                 └── decides which tools/queries    └────────────┘  (max N loops)
```

| Node | Role | Bounded by |
| --- | --- | --- |
| **Planner** | Decompose finding(s) → evidence needed, playbook queries, action-template candidates | Closed action-template taxonomy |
| **Evidence gatherer** | Tool calls: `query_timeseries`, `get_baseline`, `traverse_graph`, `lookup_playbook` (RAG), `calculate_impact`, `assign_owner`, `check_rule_violation` | Read-only tools; step budget |
| **Drafter** | Fill prescription template with evidence-bound values | Structured output (JSON schema enforced) |
| **Verifier** | Re-derive every numeric claim from evidence; check citation coverage; groundedness score | Max revision loops, then human queue |
| **Rules veto** | Deterministic physics/tariff/safety constraint check — can kill any Rx | Non-overridable by agent |

### 10.2 Industrial RAG corpus

| Corpus slice | Contents | Used for |
| --- | --- | --- |
| **Waste playbooks** | Six-category action guides, vertical guides | What action, effort, safety notes |
| **SEC benchmarks** | Published industry SEC ranges (BEE/PAT) | Cold start + credibility |
| **DISCOM tariffs** | Tariff orders, worked examples | ₹ impact narrative |
| **IPMVP / M&V** | Measurement & verification methods | Verification defensibility |
| **OEM / audit** | Supplier intensity request patterns | Sustainability export wording |
| **Plant SOPs** `[customer]` | Uploaded maintenance procedures — **untrusted input, injection-scanned** | Customer-specific steps |

**Retrieval:** hybrid (BM25 + dense + metadata filters: vertical, asset type, waste category, DISCOM). pgvector default `[~]`.
**Grounding rule:** agent may not state maintenance steps unsupported by a playbook or plant-SOP chunk.

### 10.3 Guardrails (non-negotiable)

1. Rules engine **veto** on every output — deterministic, versioned, cannot be argued with by the agent.
2. **Evidence mandatory** — every prescription cites tag IDs, timestamps, baseline IDs; verifier checks coverage.
3. **No LLM arithmetic** — all ₹/kWh/tCO₂e from the deterministic impact calculator; LLM only narrates.
4. **Bounded action space** — agent selects + parameterises approved action templates; free-form actions rejected at schema level.
5. **Human approval gate** for capex, high-risk, or low-confidence prescriptions before send.
6. **Prompt-injection defence** — customer SOPs and WhatsApp replies are untrusted; retrieval content sandboxed from instruction context; red-teamed per [evaluation doc](cross-cutting/04-evaluation-and-quality.md).
7. **No SCADA writes** — no write-capable pathway exists in any layer.

### 10.4 Impact calculator, ranker, narrative engine

- **Impact calculator:** ₹ (tariff-line-correct) + kWh (baseline delta) + tCO₂e (grid kWh × versioned CEA factor). Deterministic, property-tested.
- **Rx ranker:** `(inr_impact × confidence) / effort_weight × urgency_multiplier`; dedup overlapping root causes; cap open Rx per role; quick-wins queue for first billing cycle.
- **Sustainability narrative engine:** audit-ready text blocks from ledger + SEC trends — templated, not creative prose.

### 10.5 L4 evaluation harness (summary — full detail in layer spec)

Golden prescription set (curated finding→Rx pairs per waste category) · retrieval metrics (recall@k, context precision) · faithfulness/groundedness scoring · **numeric-consistency check** (every ₹ claim re-derived) · prompt regression suite in CI (blocking) · online labels from supervisor accept/reject/defer codes.

---

## 11. Layer 5 — Closure & verification

Full spec: [L5 — Closure & verification](layers/L5-closure-and-verification.md)

### 11.1 Workflow engine

| State | Meaning | Triggers |
| --- | --- | --- |
| Open | Rx issued | Agent + ranker |
| In Progress | Owner acknowledged | WhatsApp / dashboard |
| Done | Action reported complete | Supervisor marks done |
| Verified | M&V confirmed | M&V engine + bill |
| Deferred / Rejected | Not actioned | User + reason code |

Reason codes feed L3 calibration: wrong owner, capex blocked, production constraint, already fixed. Reminders, escalation, and SLA timers are native; closure rate per plant/role is a first-class product metric.

### 11.2 Notification router

| Channel | User | Content |
| --- | --- | --- |
| WhatsApp (Meta Cloud API direct, §4) | Supervisor, electrician | Full prescription card + interactive ack/done/defer buttons |
| Dashboard | Plant head, energy manager | Queue, ledger, trends |
| Email | Sustainability lead | Monthly intensity pack |
| Webhook | Corporate ESG system | Ledger JSON |
| SMS fallback `[!]` | DLT-registered | Critical alerts when WhatsApp undelivered |

### 11.3 M&V engine

IPMVP-aligned `[~]` using **standard EVO option naming** (see [L5](layers/L5-closure-and-verification.md) §3.3 for full methodology). Two-tier verification:

1. **Tier 1 — Account truth (Option C):** whole-facility avoided use, production-normalised, reconciled to DISCOM bill lines — the customer-facing "verified on the bill" number.
2. **Tier 2 — Per-prescription attribution (Option A/B):** boundary-level estimates where metered; engineering allocation elsewhere. Hard constraint: `Σ per-Rx attributed savings ≤ Tier-1 account savings` for the period.

| IPMVP option | What it measures (EVO standard) | Stamped application | Verification source |
| --- | --- | --- | --- |
| **Option A** | Retrofit isolation — **key parameter** measured, others stipulated | PF correction, CMD right-sizing, pure tariff arithmetic where one parameter dominates | Bill PF/MD lines + incomer interval |
| **Option B** | Retrofit isolation — **all parameters** measured at the boundary | Per-Rx verification on feeder/sub-meter: compressor SP, furnace holding, chiller COP (Path A) | Feeder meter + production tags |
| **Option C** | **Whole facility** — regression on facility consumption vs independent variables | Account-level bill truth; Path B from day one; also caps the portfolio total | DISCOM bill + incomer (+ production covariates) |
| **Option D** | Calibrated simulation | **Not used** — industrial process loads; no simulation budget | — |

**Path defaults:** Path B enters with **Option C** (bill + incomer). As sub-meters arrive, **Option B** attributes individual prescriptions; Option A covers deterministic tariff-only wins. Interval data (hourly/daily incomer) makes sub-10% portfolio savings detectable within a billing cycle `[~]` — monthly bill alone cannot verify a single 1–2% Rx.

Process: lock pre-action baseline (production/weather adjusted, ASHRAE G14 gates) → action done → verification window (≥1 billing cycle) → actual vs adjusted baseline → reconcile with DISCOM bill lines → `LedgerEntry` verified/disputed. Non-routine adjustments (NREs) are signed, versioned artifacts — never silent baseline drift.

### 11.4 Bill reconciliation

Modelled savings vs actual bill-line movement; flags tariff change, FPPCA swing, production surge, seasonality — baseline adjusted before crediting. **Bill is final authority** for customer trust.

### 11.5 Savings ledger (dual outcome)

Running potential vs realised — ₹, kWh, tCO₂e, SEC trend, closure rate. Exposed to L6 and to the evaluation loop (predicted vs realised calibration, §17.4).

---

## 12. Layer 6 — Experience & integration

Full spec: [L6 — Experience & integration](layers/L6-experience-and-integration.md)

### 12.1 Dashboard modules

| Module | Data source | Primary user |
| --- | --- | --- |
| Savings ledger | L5 ledger | Plant head, CFO |
| 30-day trend vs baseline | L2 TS + baseline store | Energy manager |
| Equipment health map | L3 anomaly scores | Operations |
| Live anomaly feed | L3 findings stream | All |
| Prescription queue | L4 + L5 workflow | Supervisors |
| Top consumers vs benchmark | L2 feature store | Energy manager |
| TOD / 24h demand profile | L3 MD engine | Utilities |
| Intensity chart | SEC engine + production | Sustainability |
| CO₂ equivalent card | Impact calculator | Sustainability (derivative) |

### 12.2 Integration surface ("connect to any custom system", scoped)

| Tier | Mechanism | Effort |
| --- | --- | --- |
| **Tier 1 — self-serve** | Outbound webhooks (signed, retried, dead-lettered) + REST API (OpenAPI, API keys/OAuth2) + CSV export | Product-included |
| **Tier 2 — templated** | Named connectors: ERP (SAP export/IDoc `[!]`, Tally), ESG platform formats, email/SFTP drops | Configuration engagement |
| **Tier 3 — custom** | Bespoke integration built on Tier 1 primitives | Paid services `[!]` |

Event catalogue: `prescription.created`, `prescription.status_changed`, `prescription.verified`, `ledger.entry.added`, `anomaly.raised`, `bill.ingested`.

### 12.3 Sustainability export pack `[!]`

Verified savings summary (₹/kWh/tCO₂e) · SEC/intensity report by line · prescription audit trail · methodology note (IPMVP option, emission factor source, limitations) · BRSR/PAT adjunct tables (CSV). Feeds corporate ESG tools — does not replace them.

---

## 13. Sustainability architecture (operational, not ESG SaaS)

### 13.1 Principle

> Every verified ₹ saving from reduced grid draw **is** a Scope 2 operational reduction. Intensity improvement **is** a production-normalised sustainability outcome. One ledger, two audiences (CFO and sustainability lead).

### 13.2 What Stamped produces

| Output | Method | Audit strength |
| --- | --- | --- |
| **Grid kWh reduction** | M&V vs baseline | High — meter + bill |
| **Scope 2 (location-based)** | kWh × grid factor | Medium-high — factor transparency required |
| **SEC / energy intensity** | kWh / production unit | High if production tagged |
| **Prescription traceability** | Workflow audit trail | High — who did what when |
| **Renewable share** | Source meters | Medium — needs sub-metering |
| **Product carbon footprint** | — | **Out of scope** |
| **Scope 3** | — | **Out of scope** |

### 13.3 Sustainability-tagged prescription types

| Tag | Example Rx | Reporting use |
| --- | --- | --- |
| `scope2_grid_reduction` | Stagger MD, reduce holding load | Scope 2 evidence |
| `sec_improvement` | Compressor SP fix on production line | kWh/part for OEM |
| `renewable_dispatch` | Shift load to solar/WHR window | Renewable % narrative |
| `pat_intensity` | Kiln SEC drift correction | PAT / efficiency scheme |
| `iso14001_energy_review` | Documented energy review actions | ISO surveillance audit |

### 13.4 Emission factor management

CEA grid database default `[~]` · customer override with documented source · versioned — new factor applies forward, never rewrites history · every tCO₂e figure discloses factor value + source + vintage.

---

## 14. AI / ML component registry

| ID | Component | Layer | Technique | Savings role | Sustainability role |
| --- | --- | --- | --- | --- | --- |
| ML-01 | Shift baseline | L3 | TOWT-style regression + decomposition | Expected consumption | SEC reference |
| ML-02 | SEC regression | L3 | Multivariate regression / GBM | Production-normalised waste | Intensity tracking |
| ML-03 | Anomaly detector | L3 | Residual EWMA/CUSUM + Isolation Forest | Find drift | — |
| ML-04 | Startup detector | L3 | Ramp detection | MD attribution | — |
| ML-05 | Attribution correlator | L3 | Graph + correlation | Root cause | Process allocation |
| ML-06 | Fleet priors | L3 | Aggregated benchmarks | Cold-start | Vertical SEC norm |
| ML-07 | Plant calibrator | L3 | Bayesian parameter tuning | Reduce false positives | — |
| ML-08 | Bill OCR/extract | L1 | Layout-aware OCR + LLM | Tariff accuracy | — |
| ML-09 | Tag suggester | L1 | LLM + vertical template | Faster onboarding | — |
| ML-10 | RAG retriever | L4 | Hybrid (BM25 + dense + metadata) + rerank | Playbook grounding | Audit text |
| ML-11 | Prescription agent | L4 | Checkpointed agent graph (planner/tools/verifier) | Rx quality | Dual impact text |
| ML-12 | Dispatch optimiser | L3 | MILP / rules `[P1]` | Source mix ₹ | Grid kWh ↓ |
| ML-13 | Narrative generator | L4 | Template + LLM | — | Export pack |
| ML-14 | MD forecaster | L3 | GBM with lag features `[~]` | Predictive MD | — |
| RULE-01–N | Physics/rule packs | L3 | Deterministic, versioned | Explainable Rx + veto | Category tags |
| MV-01 | Baseline adjustment | L5 | IPMVP regression | Verified ₹ | Verified kWh |

Every component: registered version, eval gate before promotion, drift monitor in production ([evaluation doc](cross-cutting/04-evaluation-and-quality.md)).

---

## 15. End-to-end flows

### 15.1 Flow A — Monday MD spike → savings + Scope 2

```
06:55  PLC tags: HT_FURNACE_3.state = PREHEAT
07:05  FORGING_LINE_2.state = RAMP
07:12  INCOMER.kVA = 1180 (CMD = 1100)          ← 1-min streaming path (§4 decision 3)
       │
       ├─ L3 MD engine: spike event, cost ₹45k–80k/month MD component
       ├─ L3 Attribution: furnace ∩ line (graph + time)
       ├─ L3 Rules: stagger ≥10 min pattern match
       ├─ L4 Agent: plan → gather evidence → draft → verify → rules veto pass
       ├─ L5 WhatsApp card with ack/done buttons
       │
07:25  Supervisor delays furnace preheat 12 min (production sign-off)
       │
       ├─ L5 Workflow: In Progress → Done
       ├─ L3 MD engine: next 4 Mondays — peak kVA 1060
       ├─ L5 M&V: realised MD reduction vs locked baseline
       ├─ L5 Bill reconcile: MD line ↓ on DISCOM bill
       └─ L5 Ledger: ₹62k/month verified, 8,200 kWh/month, 5.8 tCO₂e
```

### 15.2 Flow B — SEC drift → OEM intensity evidence

```
Weekly SEC kWh/ton drifts +9% on Cement Mill 1 (production stable)
       ├─ L3 SEC engine: residual exceeds band
       ├─ L3 Anomaly: load factor 112% sustained
       ├─ L3 Rules: overload OR PF degradation
       ├─ L4 Rx: PF correction + load optimisation
       ├─ L5 Verify: SEC 112 → 98 kWh/ton over 6 weeks
       └─ L6 Export: intensity report for OEM supplier audit
```

### 15.3 Flow C — Degraded mode (plant offline / LLM down)

```
Plant WAN drops 6 hours:
  Edge gateway buffers (store-and-forward) → backfill on reconnect →
  late-data reprocessing window → baselines recompute → no data silently lost

LLM API outage:
  L3 findings queue at L4 → rule-templated fallback prescriptions for
  high-urgency categories (MD, PF) → full agent drafting resumes on recovery
```

Degraded-mode behaviour is specified per component in [production engineering](cross-cutting/03-production-engineering.md).

### 15.4 Flow D — Sustainability monthly pack

```
Month-end job:
  L5 ledger → aggregate verified kWh, ₹, tCO₂e
  L2 SEC store → intensity trends by line
  L4 narrative engine → methodology + tables
  L6 email/webhook → sustainability lead + corporate ESG tool
```

---

## 16. Production readiness

Full spec: [Production engineering — patterns, streaming, reliability](cross-cutting/03-production-engineering.md). Summary of the binding decisions:

### 16.1 Scale envelope (honest sizing)

Design point: **10s of plants (headroom ~100) · 200–2000 tags/plant · 1s–15min granularity.** Worst-case sustained ingest is a few thousand messages/sec — modest. The architecture must be **reliable and replayable**, not hyperscale.

### 16.2 Backbone

**Production path at Stamped's scale (10s of plants, ~k msg/s):** MQTT at plant boundary (Mosquitto on edge) → **ingest service** → batched idempotent writes to TimescaleDB + **Postgres transactional outbox** for domain events (findings, prescriptions, ledger entries). MD hot-path detection runs in-process inside the ingest service (< 60 s spike→finding). Continuous aggregates handle rollups. At-least-once delivery with idempotent keys `(plant_id, tag_id, timestamp)` — no exactly-once machinery.

**Upgrade path:** when fan-out to multiple independent consumers, sustained replay, or outbox drain exceeds ~5k msg/s sustained, introduce **Redpanda** (or MSK) as a Kafka-compatible relay — schemas and topic names are fixed from day one so this is a transport swap, not a rewrite (§4.1). Do **not** run a message broker at pilot scale; it adds cost and ops burden with no production benefit until the trigger fires.

### 16.3 Reliability patterns (applied, not aspirational)

| Pattern | Where |
| --- | --- |
| Store-and-forward + backfill | Edge gateway; late-data reprocessing windows in L2/L3 |
| Outbox + idempotent consumers | Every service that emits events |
| Dead-letter queues | Ingest, agent runtime, notification delivery |
| Circuit breakers + timeouts | LLM API, WhatsApp Cloud API, customer webhooks |
| Graceful degradation | Rule-only prescription mode; stale-data banners in dashboard |
| Bulkheads | Per-tenant processing isolation; noisy-plant quarantine |

### 16.4 Service architecture & deployment

Modular monolith (FastAPI) + satellites: edge agent, ingest writers, ML batch workers (job queue), agent runtime. Managed Postgres/Timescale. Containerized, IaC, CI/CD with canary-by-plant rollout (feature flags per plant). India-region cloud (data residency).

**Deployment modes** ([ADR-010](../../decisions/ADR-010-deployment-profiles-and-portability.md)):

| Mode | `STAMPED_DEPLOYMENT_MODE` | Orchestration | Internet |
| --- | --- | --- | --- |
| Fully local | `local` | Docker Compose on customer host | None |
| Local + dashboard | `local-dashboard` | Compose + stamped-l6 internal UI | None |
| Cloud (pilot default) | `cloud` | AWS ECS/RDS `ap-south-1` | Stamped managed |

Same container images and layer contracts in all modes; mode selects compose profile + env. Local modes require on-prem LLM for L3/L4 intelligence; L1 connectors may use `LLM_BACKEND=rules-only`.

### 16.5 Observability & SLOs

| SLO | Target `[~]` |
| --- | --- |
| Data freshness per plant (incomer) | < 2 min for demand path; < 20 min batch |
| Pipeline lag alert | > 5 min sustained |
| Finding → WhatsApp latency (high urgency) | < 10 min |
| Tag staleness detection | < 30 min |
| Monthly uptime (ingest + dashboard) | 99.5% `[!]` |

Domain observability is product-critical: tag staleness, Rx closure rate, M&V dispute rate, false-positive rate per plant are monitored like infrastructure metrics.

### 16.6 Security & tenancy

| Concern | Approach |
| --- | --- |
| **Tenancy** | `org_id` → `plant_id` isolation; row-level security; no cross-tenant queries |
| **OT security** | Read-only credentials only; outbound-only edge connections; no inbound ports on plant network |
| **Encryption** | TLS/mTLS in transit; AES-256 at rest |
| **RBAC** | Operator / supervisor / plant head / sustainability / admin |
| **Audit** | Immutable log: prescription issued, viewed, acted, verified |
| **Data residency** | India region default |
| **Compliance path** | ISO 27001 → SOC 2 as enterprise-scale milestone `[!]` |

---

## 17. Evaluation & verification (the quality spine)

Full spec: [Evaluation, testing & quality](cross-cutting/04-evaluation-and-quality.md). The product's promise is *verified* savings; the same discipline applies to the product itself. Summary of the binding gates:

### 17.1 Gate map

| Gate | Layer | Blocks |
| --- | --- | --- |
| Contract tests (schemas §5) | Every boundary | Merge |
| Data-quality gate (physics/range/gap checks) | L1 | Bad data enters L2 (quarantined instead) |
| Per-engine eval (CVRMSE/NMBE, precision/recall, MAPE targets) | L3 | Model promotion |
| Rule-pack validation suite | L3 | Rule-pack publish |
| Golden prescription set + faithfulness + numeric-consistency | L4 | Agent/prompt deploy |
| Prompt regression suite | L4 | Merge (CI) |
| Shadow mode graduation criteria | Whole pipeline | Plant go-live |
| Predicted-vs-realised calibration (ledger feedback) | L5 | Quarterly model review trigger |

### 17.2 Shadow mode (mandatory for every new plant)

Full pipeline runs; prescriptions generated but **not sent**. Internal review against graduation criteria: data-quality SLIs green ≥ 2 weeks · baseline eval within gates · Rx precision spot-check by engineer ≥ threshold · alert volume within budget. Only then does WhatsApp delivery switch on — per-plant feature flag.

### 17.3 Eval assets are product assets

Golden telemetry fixtures (replayed plant data), labelled incident sets, golden prescription pairs, and red-team prompt suites are versioned in-repo and grow with every pilot. **The eval set for the agent ships before the agent does.**

### 17.4 The ledger closes the loop

The M&V ledger is the ultimate ground truth: predicted impact vs realised savings per prescription → calibration curves per engine and per waste category → confidence recalibration and threshold tuning in L3. A model that overpromises gets its confidence discounted automatically.

---

## 18. Build phases mapped to outcomes

| Phase | Architecture | Savings target `[~]` | Quality infrastructure shipped |
| --- | --- | --- | --- |
| **P0** (weeks 1–8) | L1 incomer+bill, L2 TS+context, L3 MD+tariff+rules, L4 agent (MD/PF templates), L5 workflow+M&V Option C, L6 dashboard+WhatsApp | **5–10%** MD+tariff wins | Contract tests, data-quality gate, baseline eval, golden Rx set v1, shadow mode |
| **P1** (months 3–6) | Full graph, SCADA/PLC connectors, SEC engine, waste classifier, all 6 categories, agentic verifier loop | **+5–8%** asset-level | Per-engine eval protocol, drift monitors, prompt regression CI, labelled incident set |
| **P2** (months 6–12) | Source dispatch, fleet benchmark, sustainability pack, webhooks/API | **+2–5%** dispatch+fleet | Champion/challenger, predicted-vs-realised calibration, red-team suite |
| **P3** | Conversational analyst, PdM fusion, advanced COP/HVAC | Marginal + reliability | Full lineage reproducibility |

**Cumulative architecture target:** 12–20% bill reduction at Path A maturity with ≥60% closure on top-quartile Rx `[~]`.

---

## 19. Explicit boundaries

| In scope | Out of scope |
| --- | --- |
| Verified grid kWh and ₹ reduction | Full ESG/carbon accounting platform |
| Scope 2 from operational grid reduction | Scope 3, product LCA/PCF |
| SEC / intensity when production tagged | Replacement for corporate GRI authoring |
| PAT/BRSR **evidence export** | PAT scheme registration / legal filing |
| Read-only OT integration | Autonomous SCADA control (no write path exists) |
| IPMVP-style M&V narrative | Guaranteed savings insurance |
| Bounded, evidence-cited agentic drafting | Free-form autonomous agents, unbounded chat |

---

## 20. Remaining open questions `[!]`

1. Sparkplug B adoption in Indian ICP plants — worth first-class support at P0 or P1? (validate in first 3 pilots — [L1](layers/L1-connect-and-normalise.md))
2. DLMS/COSEM direct HT-meter reads vs always going through plant meters/EMS — feasibility per DISCOM ([L1](layers/L1-connect-and-normalise.md))
3. Overlapping-prescription M&V attribution — per-Rx boundary vs portfolio-level crediting policy ([L5](layers/L5-closure-and-verification.md))
4. Self-hosted vs API LLM for data-residency-sensitive enterprise accounts ([L4](layers/L4-knowledge-and-reasoning.md))
5. Minimum viable fleet size before fleet priors beat published benchmarks ([L3](layers/L3-intelligence-core.md))
6. BRSR adjunct format — which tables customers' ESG teams actually paste ([L6](layers/L6-experience-and-integration.md))

---

## 21. References

| Document | Path |
| --- | --- |
| Master product doc | [00-stamped-master-document.md](00-stamped-master-document.md) |
| Product architecture (summary) | [01-product-architecture.md](01-product-architecture.md) |
| Layer specs L1–L6 | [layers/](layers/) |
| Production engineering | [cross-cutting/03-production-engineering.md](cross-cutting/03-production-engineering.md) |
| Evaluation & quality | [cross-cutting/04-evaluation-and-quality.md](cross-cutting/04-evaluation-and-quality.md) |
| Demo dashboard | [https://stamped-energy.vercel.app/](https://stamped-energy.vercel.app/) |
