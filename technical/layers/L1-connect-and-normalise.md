---
type: Product Architecture
title: "L1 — Connect & Normalise (Connectors)"
description: "Deep research and build spec for Stamped's Layer 1: OT/IT protocol adapters, edge gateway, schema normaliser, tag mapping, DISCOM bill/tariff ingest, data-quality gates, and event-bus ingress for Indian ICP plants."
tags: [stamped-energy, technical, layer-spec]
timestamp: "2026-07-09T00:00:00Z"
---

# L1 — Connect & Normalise (Connectors)

*Layer owner doc · v1.0 · July 2026 · Status: research-complete, pre-build*

> **Honesty convention:** `[~]` approximate / benchmark-derived · `[!]` needs verification in pilots
> **Siblings:** [L0 — Plant systems](../02-technical-architecture.md#6-layer-0--plant-systems) · [L2 — Universal Repository](L2-universal-repository.md) · [Technical architecture](../02-technical-architecture.md) · [Master doc](../00-stamped-master-document.md)
> **Repo context:** `core-product/Stamped_Technical_Architecture_v1.md` §4–5 · `external-learning/discom/` bill structure templates

---

## 1. Role in the 15–20% target

L1 is the layer that determines **which savings categories are even reachable**. Every rupee of the 15–20% target traces back to a data stream that L1 either delivers or fails to deliver:

| Waste category (from [technical architecture](../02-technical-architecture.md) §3.1) | Bill impact `[~]` | Minimum L1 stream required |
|---|---|---|
| Power quality & MD | 3–8% | Incomer meter kVA/kW at ≤1-min granularity + parsed bill MD line |
| Furnaces & process heat | 2–5% | Feeder meter or SCADA furnace tags |
| Idle & auxiliary loads | 2–4% | Incomer + shift calendar (file/manual ingest) |
| Compressed air | 1–3% | Compressor feeder meter or historian export |
| Cooling / HVAC / chillers | 1–3% | Chiller meter or BMS export (BACnet/CSV) |
| Source mix & VFD | 1–4% | Solar/DG/WHR meters + tariff model |

Four consequences shape everything below:

1. **The bill is the verification anchor.** M&V at L5 reconciles model output against the DISCOM bill. If bill ingest mis-parses a TOD slot or the billing-demand line, the entire savings claim is disputable. Bill ingest is therefore a **P0, accuracy-critical** connector — not an OCR afterthought.
2. **Time-to-first-prescription ≤ 2 weeks (Path B)** means the P0 connector set must be installable without OT-network change requests: incomer meter (Modbus, or DLMS on HT meters), bill PDFs, and CSV exports. Anything that needs a plant IT ticket (OPC UA certificates, firewall rules) is Path A / P1.
3. **MD spike detection needs ≤1-min data with trustworthy timestamps.** Modbus carries no timestamps [9][10] — the poller stamps values on read. L1's timestamping discipline directly bounds the accuracy of the attribution engine at L3.
4. **Data-quality gates protect the baseline.** A stale tag silently repeating its last value flattens a baseline and produces false "savings". Quality codes (`good | estimated | bad | stale`) attached at L1 are what let L3 exclude poisoned windows.

**Design rule for this layer:** every component must either widen source coverage (more plants connectable), improve evidence fidelity (timestamps, quality, lineage), or reduce onboarding time. Nothing else belongs in L1.

---

## 2. Requirements from the architecture

### 2.1 Inputs from L0 (what L1 must accept)

From the [technical architecture](../02-technical-architecture.md) §4.1 source inventory, restated as ingestion contracts:

| L0 source | Physical reach | Cadence | L1 obligation |
|---|---|---|---|
| Incomer/feeder meters (Schneider PM, Elmeasure, L&T, Secure, HPL) | RS-485 Modbus RTU, Modbus TCP, some DLMS/BACnet/IEC 61850 on premium models [12][14] | 1 s–1 min poll | P0 — mandatory; kW, kVA, kWh/kVAh, PF, MD registers |
| HT/DISCOM boundary meter | DLMS/COSEM per IS 15959 (optical port / RS-485) [7][8] | Block load profile 15/30-min | P1 — read-only pull where DISCOM/consumer access allows `[!]` |
| SCADA/historian (WinCC, FactoryTalk, iFIX, Ignition, AVEVA/Wonderware, PI) | OPC UA, OPC DA (legacy), SQL/CSV export | 1 s–15 min | P1 — prefer OPC UA; DA via tunneller; CSV export as fallback |
| PLC (Siemens S7, Allen-Bradley, Mitsubishi, Delta) | S7comm / EtherNet-IP / MELSEC via gateway software | event/poll | P1 — **never direct**; reach via OPC UA server or commercial gateway |
| CNC (FANUC and machine tools) | FOCAS over Ethernet → MTConnect XML [24][25] | poll | P2 — energy + state via MTConnect agent |
| EMS/BMS export | CSV/Excel on schedule, FTP drop, occasional REST | 15 min–daily | P0 wedge — file-based ingest |
| ERP/MES (SAP, Oracle, Tally) | REST/OData, DB view, CSV | shift/daily | P1 — production quantities for SEC |
| Solar/WHR/DG meters | Modbus RTU/TCP, inverter cloud APIs | 1–15 min | P1 |
| DISCOM bill | PDF (portal download or emailed scan) | monthly | P0 — mandatory |
| Manual context (shift calendar, logbooks) | Upload/form | ad hoc | P0 — structured upload |

### 2.2 Contract to L2 (what L1 must emit)

L1 publishes exactly four canonical record types onto the event bus; L2 writers and L3 stream processors consume them. Nothing schema-specific to any vendor crosses the L1→L2 boundary.

1. **`Measurement`** — time-series point with quality and lineage (§4.4).
2. **`Event`** — state changes, alarms, connector health (birth/death), bill-arrival events.
3. **`ProductionRecord`** — batch/shift/SKU quantities bound to time windows.
4. **`BillLine`** — validated, tariff-checked bill line items (one record per economic bucket per bill).

Non-functional contract:

| Property | Requirement |
|---|---|
| Latency (streaming path) | Source → bus ≤ 60 s for metered electrical tags `[~]`; ≤ 15 min for file-based |
| Ordering | Per-tag ordering preserved within a partition; late data flagged, not dropped |
| Durability | No inbound-WAN loss: edge store-and-forward ≥ 72 h buffer `[~]` |
| Idempotency | Replays (edge flush, file re-drop) deduplicated by `(plant_id, source_tag, ts, granularity)` |
| Lineage | Every record carries `source_system`, `source_tag`, `connector_id`, `ingest_ts` |
| Security | Read-only on OT; outbound-only from plant (CISA/NCSC-UK 2026 guidance: all OT connections initiated from inside OT [40]); TLS 1.2+; per-plant credentials |
| Tenancy | `org_id`/`plant_id` on every record; enforced at broker ACL level |

---

## 3. Researched landscape

### 3.1 Protocol landscape (full OT/IT matrix)

| Protocol | Version(s) to support | Where it appears in Indian ICP plants | Practical notes for Stamped | Verdict |
|---|---|---|---|---|
| **Modbus RTU** | Modbus over RS-485 serial | Ubiquitous — nearly every panel meter (Schneider EM/PM, Elmeasure, Secure Elite, L&T, HPL) exposes it [12][13][14][15][16] | 16-bit registers only; 32-bit floats/counters span 2 registers with **vendor-specific byte order** (ABCD/CDAB/BADC/DCBA) [11]; no timestamps, units, or quality in-protocol [9][10]; max 247 nodes per bus, and slow (9.6–38.4 kbaud typical on meters [12]) | **P0** — via serial-to-TCP converter or gateway serial port |
| **Modbus TCP** | Port 502, MBAP framing [10] | Newer meters, PLC gateways, inverters | Same data-model poverty as RTU; polling model; keep per-device register-map profiles | **P0** |
| **OPC UA** | 1.04/1.05 binary (opc.tcp) | S7-1500 embedded servers, Kepware/Ignition/WinCC OA aggregation servers, newer historians | Security: enforce `SignAndEncrypt`; policy floor `Basic256Sha256`, prefer `Aes256Sha256RsaPss`; disable `None`, `Basic128Rsa15`, `Basic256` (SHA-1-era, flagged by IEC 62443) [1][3]. Use **subscriptions** (monitored items) not bulk polling — Telegraf-style polling degrades past a few hundred nodes [47][48]. Certificate exchange is the #1 onboarding friction: plan a certificate runbook per plant | **P1** — the single highest-leverage Path A connector |
| **OPC UA PubSub** | Part 14 (UDP/MQTT mappings) | Rare in Indian brownfield; some new Siemens deployments | Not worth building for now; the client/server profile reaches the same servers | **Defer** |
| **OPC DA / Classic** | DA 2.x/3.0 over DCOM | Legacy WinCC/iFIX/Wonderware installs (pre-2015 plants — common in forging/auto-comp belts) | DCOM hardening (CVE-2021-26414, enforced March 2023) broke remote DA; no registry workaround remains [41][42]. **Do not write a DA client.** Buy/deploy a UA tunneller or DA→UA gateway (Kepware, Matrikon UAT, Softing) on the SCADA host and consume UA | **P1 via wrapper — buy, don't build** |
| **MQTT** | 3.1.1 and 5.0 | IoT-retrofit meters, Indian 4G loggers (SilTech, Embedos, Konnecto publish MQTT/JSON) [51] | Transport, not a data model — payloads vary per vendor; MQTT 5 adds reason codes, message expiry, shared subscriptions (useful for scaling consumers) | **P0** — broker-side ingest with per-vendor payload decoders |
| **MQTT Sparkplug B** | v3.0 (Eclipse spec, Nov 2022) [4] | Ignition Edge/Cirrus Link installs; gateway vendors (NeuronEX) ship it [22] | Birth/death certificates give free connector-health semantics; protobuf payloads compact. Constraints: core message types mandated **QoS 0, retain=false** [6]; rigid 4-level topic hierarchy conflicts with deeper ISA-95 models [5]; protobuf debugging overhead [5] | **P0 ingest support; internal transport "Sparkplug-aware" not Sparkplug-strict** (see §3.6) |
| **DLMS/COSEM (IEC 62056)** | HDLC + TCP profiles; **IS 15959 Parts 1–3** Indian Companion Specification | DISCOM boundary meters, ABT/HT meters, smart-meter rollout (IS 16444 meters) | IS 15959 defines the Indian OBIS parameter set: instantaneous, block load profile, daily load profile, billing profile, name-plate [7][52]; Part 3 covers transformer-operated (CT/PT) HT meters [7]. Security: LLS/HLS association secrets; access often gated by the DISCOM `[!]` | **P1** — unlocks billing-grade profile data without touching plant OT |
| **BACnet/IP** | ASHRAE 135, Annex J | BMS/HVAC in pharma/chemical plants; premium meters (PM5560, Secure Elite 500 optional module) speak it [12][14][43] | Object model (AI/AV/BI…) with engineering units — richer than Modbus; COV subscriptions reduce polling; MS/TP field devices reachable only via BACnet/IP routers [43] | **P2** — pharma/HVAC vertical trigger |
| **IEC 61850 (MMS)** | Ed. 2, MMS over TCP 102 | Plant HT substations & IEDs (SIPROTEC, Relion, Sepam); premium meters optional [14][44] | Logical-node model (MMXU measurement units etc.); SCL/CID file import gives self-describing point lists [44]; heavyweight client to build | **P3** — buy a gateway/driver when a cement/steel account demands it |
| **DNP3** | Subset level 2 | Rare inside Indian factories (utility/SCADA-facing) | PM5560 offers DNP3-over-Ethernet [12] but Modbus reaches the same registers | **Skip** — revisit only on utility-interface projects |
| **Serial/pulse meters** | S0 pulse, proprietary serial | Old sub-meters, water/gas/air meters | Pulse → counter via cheap DI module or 4G logger; treat as Modbus once digitised | **P1** — hardware pattern, not software connector |
| **Profinet / EtherNet-IP** | — | Drive/PLC networks | **Never connect directly** — real-time control networks; reach the same data via the PLC's OPC UA server or a Kepware/NeuronEX driver [20][22] | **Skip direct; reach via gateway** |
| **FOCAS / MTConnect** | FOCAS2 over Ethernet; MTConnect 2.x XML/HTTP | FANUC-controlled CNC shops (auto components) | FANUC FASMTC adapter converts FOCAS → MTConnect XML on a machine-side PC [24]; FOCAS2 exposes the CNC power-consumption monitor (per-axis and peripheral kW, per-program energy) [26]; open-source agents exist (TrakHound) | **P2** — MTConnect client only; never raw FOCAS in v1 |
| **REST / file** | HTTPS JSON/OData; CSV/XLSX; FTP/SFTP drop | EMS exports, ERP (SAP OData, Tally XML/ODBC), inverter clouds, historian scheduled exports | Cheapest coverage per engineering hour; schema drift is the failure mode — version every file profile | **P0** |

### 3.2 What Indian plants actually run (source → protocol reality)

**Meters.** The panel-meter installed base in the ICP verticals is dominated by Schneider (EM6400/EM6400NG series and PM5000/PM8000 on incomers), Elmeasure (LG/EN multifunction series), L&T (Quasar/Vega), Secure Meters (Elite 100/300/500), and HPL. The common denominator across all five is **Modbus RTU on RS-485** [12][13][14][15][16]; Ethernet Modbus TCP appears on incomer-class meters (PM5560 has dual Ethernet + BACnet/IP + DNP3 [12]); DLMS appears on revenue/utility-grade meters (HPL ships DLMS on optical + Modbus on RS-485 in the same meter [15]). Practical consequence: **one good Modbus stack + a per-meter register-map profile library covers ~90% of metering points** `[~]`. The profile library (register map, scaling, byte order, CT/PT multiplier handling) is where the real work is — byte-order errors are the classic silent data corruption [11].

**SCADA/historians.** India-specific pattern [17][18][19]: WinCC dominates wherever Siemens PLCs dominate (pharma, chemicals, cement, textiles); FactoryTalk in MNC-parent automotive; Ignition growing fast on licensing economics (unlimited tags); AVEVA/Wonderware + PI strong in refining/petchem/power. Four platforms ≈ 80% of deployments [18]. Reach strategy: all four expose OPC UA (modern versions) or OPC DA (legacy); AVEVA Historian and PI have SQL/ODBC query surfaces; **every historian can schedule a CSV export**, which is the universal Path B fallback that requires no OT change approval.

**PLCs.** Siemens S7-1200/1500 has the largest installed base outside automotive; Allen-Bradley in MNC plants; Mitsubishi MELSEC and Delta in SME/discrete [19]. S7-1500 ships an embedded OPC UA server (licence-gated) — where enabled, it is the cleanest read path. Otherwise a commercial gateway (Kepware ~150 drivers [20], EMQX NeuronEX with per-brand southbound drivers [22][23]) terminates the proprietary protocol. **Stamped should never implement S7comm/EtherNet-IP/MELSEC wire protocols in-house.**

**CNC.** FANUC controls dominate Indian machine-tool floors. FOCAS is a Windows DLL library — awkward to embed in a Linux agent. The sane path is FANUC's own MTConnect server (FASMTC) or the open-source TrakHound agent on a machine-side PC, then Stamped consumes MTConnect XML over HTTP [24][25]. FANUC's power-consumption monitor (2023+) exposes per-program energy via FOCAS2 [26] — a differentiating SEC signal for auto-component accounts `[!]`.

**EMS exports.** Incumbent EMS (Schneider PME/PMEC, Elmeasure eWatch [16], local SI-built dashboards) almost always offer scheduled CSV/Excel email or FTP. This is the **P0 wedge**: it monetises the customer's existing metering investment with zero OT footprint.

### 3.3 Edge gateway options

| Option | Type | Strengths | Weaknesses for Stamped | Fit |
|---|---|---|---|---|
| **EMQX Neuron / NeuronEX** | Commercial OSS-core, C, containerised | Lightweight (runs on ARM), ~broad southbound driver set incl. Siemens/Mitsubishi/Delta/Modbus/OPC UA/BACnet/IEC 61850/DLT645, northbound MQTT + **Sparkplug B** + Kafka [22][23]; free 30-tag tier; C SDK for custom drivers [23] | Per-tag commercial licensing at scale `[!]`; driver quality varies by brand | **Primary candidate for the Stamped edge runtime's driver layer** `[!]` — evaluate licence economics at 500–2,000 tags/plant |
| **Kepware KEPServerEX** | Commercial, Windows | Industry-standard 150+ drivers [20]; Sparkplug B publishing; the answer when a plant has exotic PLCs | Windows host requirement; suite licensing per protocol (low-hundreds to low-thousands USD/site) [21]; per-site ops burden | **Buy per-site when driver coverage demands it** — pass through cost or absorb in enterprise deals |
| **Ignition Edge IIoT** | Commercial, JVM | $945 perpetual/site, unlimited tags/devices, MQTT Transmission with disk-backed store-and-forward (35 days / 10M points) [45][46] | JVM footprint; heavier box; another vendor UI to manage | **Good default where the customer already runs Ignition**; competitive standalone option |
| **Telegraf** | OSS agent (Go) | Trivial to deploy; Modbus + OPC UA input plugins; huge output ecosystem | OPC UA plugin has documented reconnection/memory issues and degrades at high node counts in polling mode [47][48]; no store-and-forward guarantees beyond output buffer; no register-map management UI | **Acceptable for MVP pilots on simple Modbus sites; not the long-term edge** |
| **Node-RED** | OSS flow tool | Fastest prototyping; every protocol has a community node | Production concerns: single-threaded event loop, 3–5× memory overhead, flow sprawl is unauditable, community-node quality variance [48] | **Prototyping and one-off integrations only — never the fleet standard** |
| **FUXA** | OSS SCADA/HMI | Web HMI + Modbus/OPC UA | HMI-centric, thin ingestion story | Skip |
| **Custom agent on balena / k3s** | Build | Full control of buffering, fleet OTA, observability | Engineering cost; driver work duplicated | **Yes for the shell (fleet mgmt, buffering, uplink), no for drivers** — wrap Neuron/Telegraf-class drivers inside a Stamped-managed container runtime |

**Buffering / offline resilience.** The store-and-forward pattern is settled practice: local disk queue at the edge, flush on reconnect, dedupe on ingest. Ignition Edge's 35-day disk buffer [46] is the reference bar; Stamped's agent should target ≥72 h at full tag rate as the minimum `[~]`, with monotonic sequence numbers per tag so L2 can detect gaps vs. genuine zero-activity.

**OT network segregation.** The Purdue/IDMZ pattern to follow, per current guidance [37][38][39][40]:

- Edge agent sits at Level 3 (or on a mirrored port / read-only VLAN), polls southbound protocols.
- **All WAN traffic is outbound-initiated** — MQTT over TLS 8883 (or 443) to Stamped's broker. Zero inbound ports on the plant firewall. This directly implements the Jan-2026 CISA/NCSC-UK OT guidance [40] and is the strongest possible answer to plant-IT security review.
- Where the customer mandates it, the broker can sit in their IDMZ with Stamped consuming from there `[!]` (enterprise pattern; adds ops cost).
- Hardware data diode only if a customer demands it (cement/PSU tier) — don't design for it by default.

**Indian plant IT constraints (field reality).** No inbound ports is non-negotiable; site VPNs are typically refused or take months; plant Wi-Fi/LAN for third parties is often denied outright. The working pattern — proven by the Indian 4G-logger ecosystem (SilTech BusLog, Embedos, Konnecto: RS-485 in, MQTT/JSON out over 4G with local buffering, made-in-India, DIN-rail) [51] — is a **cellular-first uplink with plant-LAN as bonus**: dual-SIM industrial router or 4G-native gateway, automatic APN, store on total network failure. This entirely bypasses the plant IT approval chain for Path B installs `[~]`.

### 3.4 DISCOM bill & tariff ingest

**Bill structure reality.** There is no national bill format. Anatomy is stable at the *economic-bucket* level (identity, tariff class, demand assessment, kVAh/TOD energy, PF, fuel surcharge, duty, arrears) but field labels, layout, language mix (Hindi+English in UP), and TOD slot definitions vary per DISCOM and per FY tariff order — see the repo's [UP HT bill template](/external-learning/discom/UP-HT-DISCOM-Bill-Structure.md) and [HT bill structures index](/external-learning/discom/HT-Industrial-Bill-Structures-Index.md). Key parsing hazards already documented there:

- UP HV-2 bills are **kVAh-billed** with four seasonal TOD slots; billing demand = MAX(recorded MD, 75% × CD).
- MSEDCL adds wheeling and tax-on-sale lines; Gujarat duty can be far higher than UP's 7.5%.
- Bills arrive as portal PDFs (text layer present) or **photographed/scanned copies over WhatsApp** — the pipeline must handle both.

**Extraction approach (2026 state of the art).** Benchmarks converge on a hybrid pipeline [27][28][29][30]:

1. **Native-text PDFs skip OCR** — extract the text layer directly.
2. **Layout-aware doc-AI as primary** for scans: Azure Document Intelligence-class services hit 93–99% field accuracy on structured documents with per-field confidence, at ~$0.01/page [28][30]; per-field confidence drives the human-review queue.
3. **Vision-LLM as extractor/fallback**: current vision models with a strict JSON schema + image + OCR text achieve 95–99% field accuracy at $0.01–0.04/document, but require deterministic validators because they make arithmetic mistakes [29].
4. **Deterministic validation is the accuracy multiplier**: recompute the bill from extracted fields (the repo's §13 computation worksheet — billing demand, TOD slot math, duty %) and reject/flag any bill where recomputed ≠ printed total beyond ₹1 rounding. This converts extraction from "trust the model" to "trust the arithmetic".

Bill volume is tiny (1 bill/plant/month; even 500 plants = 500 pages/month), so **cost is irrelevant; accuracy and auditability are everything**. Keep bounding boxes from the OCR pass for the human-review UI [29].

**Tariff order parsing cadence.** Tariff orders change per FY (state ERC annual orders, e.g. UPERC FY 2025-26), with intra-year FCA/fuel-surcharge revisions quarterly or ad hoc. This is a **curated, human-in-the-loop knowledge base, not an automated pipeline**: one analyst-day per DISCOM per year to encode the rate schedule into the tariff schema, LLM-assisted extraction from the order PDF, plus a validation harness that replays last month's bills against the new schema. Per-DISCOM templates needed at launch: UPPCL (DVVNL/MVVNL/PVVNL/PuVVNL/KESCO), UPCL, MSEDCL, DHBVN/UHBVN, PSPCL, GUVNL four, TANGEDCO, TSSPDCL `[~]` — ~10 tariff templates covers the ICP geography.

### 3.5 Transport & backbone: validating the architecture defaults

**Default 1 — MQTT (Sparkplug-aware) edge→cloud: AGREE, with one precision.** MQTT's outbound-only, single-port, pub/sub model is exactly the Purdue-compliant plant exit [37][38]. Sparkplug B adds birth/death session state (free connector health) and metric auto-discovery [4][5]. But strict Sparkplug compliance mandates QoS 0 + retain=false on core message types [6] — wrong for billing-grade meter data where at-least-once delivery matters more than HMI liveness. **Recommendation: speak Sparkplug B natively when ingesting from third-party Sparkplug sources (Ignition Edge, NeuronEX), but Stamped's own agent publishes a Sparkplug-inspired namespace (`stamped/v1/{org}/{plant}/{connector}/{message_type}`) with QoS 1, persistent sessions, and protobuf payloads.** Sparkplug-aware, not Sparkplug-shackled.

**Default 2 — Kafka/Redpanda cloud backbone: AGREE; pick Redpanda first.** For a seed-stage team, Redpanda's single-binary, no-JVM/no-ZooKeeper operational profile is the deciding factor; it is Kafka-API-compatible so consumers/producers don't fork, and the ecosystem argument for Kafka (Connect catalogue, Streams) matters little because Stamped writes its own consumers anyway [31][32]. Revisit only if a managed-Kafka price beats self-run Redpanda at scale `[!]`. Bridge pattern: MQTT broker (EMQX) → rule-engine/bridge → Redpanda topics (`measurements.raw`, `events.raw`, `bills.parsed`, per-plant partitioning by `plant_id`).

**Default 3 — TimescaleDB landing TSDB: AGREE.** Postgres compatibility keeps the commercial-context store and TSDB in one operational surface; hypertables + columnar compression give 90–95% storage reduction on cold chunks [34]; continuous aggregates map directly to the 1-min/15-min/shift/day rollups L2 requires [33]. Critical config informed by L1's late-data reality: **`compress_after` must exceed the maximum edge-buffer flush horizon** (≥72 h buffer → compress after ≥7 days), because inserts into compressed chunks are expensive [35][36]. Late data inside the window lands cheaply; later-than-window data goes through a slow-path backfill job.

**Default 4 — containerized Linux edge agent only when needed: AGREE.** §4.3 decision tree formalises "when needed".

---

## 4. Recommended approach

### 4.1 Connector matrix — what Stamped actually builds

Distinguishing four classes: **(A)** protocol adapters (build once, reuse), **(B)** vendor profiles (config, not code), **(C)** file/API ingest (build once, per-source profiles), **(D)** bought/embedded third-party (deploy, don't build).

**Answer to the sizing question: 12 built connectors + 2 bought integrations reach ~85–90% of Indian ICP plants** `[~]`. The long tail is covered by vendor profiles (config) and per-site Kepware/gateway purchases, not new code.

| # | Connector | Class | Priority | Coverage contribution `[~]` | Notes |
|---|---|---|---|---|---|
| 1 | Modbus TCP adapter | A | **P0** | Very high — most Ethernet meters, gateways, inverters | Incl. register-map profile engine (data type, byte order, scaling, CT/PT MF) |
| 2 | Modbus RTU adapter (serial + serial-over-TCP) | A | **P0** | Very high — the RS-485 meter universe [12]–[16] | Same profile engine; RS-485 bus scan utility for onboarding |
| 3 | DISCOM bill ingest (PDF → BillLine) | C | **P0** | 100% of plants — mandatory | Doc-AI + LLM + deterministic recompute (§3.4); per-DISCOM templates |
| 4 | CSV/Excel file ingest (drop folder / email / SFTP) | C | **P0** | High — every EMS/historian can export CSV | Versioned file profiles; schema-drift detection |
| 5 | Generic MQTT ingest + payload decoders | A | **P0** | Medium-high — 4G loggers, IoT meters [51] | JSON-path mapping per vendor payload |
| 6 | Sparkplug B ingest | A | **P0** | Medium — Ignition/NeuronEX estates | Birth/death → connector-health events for free |
| 7 | Manual/structured upload (shift calendar, production, logbook) | C | **P0** | 100% — context data | Web form + XLSX template |
| 8 | OPC UA client (subscriptions, cert mgmt) | A | **P1** | High — the Path A unlock: WinCC, Ignition, S7-1500, Kepware endpoints | `SignAndEncrypt`, `Basic256Sha256` floor [1][3]; per-plant cert runbook |
| 9 | DLMS/COSEM client (IS 15959 profile) | A | **P1** | Medium — HT/ABT meters, billing-grade profiles [7][52] | Block load profile + billing profile OBIS sets first |
| 10 | Generic REST/API poller (OData, JSON) | C | **P1** | Medium — SAP OData, inverter clouds, modern EMS | Per-source auth + mapping profiles; Tally via ODBC/XML export `[!]` |
| 11 | Historian SQL puller (AVEVA/PI/Ignition DB views) | C | **P1** | Medium — where OPC UA is blocked but DB access granted | Read-only DB credentials; incremental watermark queries |
| 12 | MTConnect client (XML/HTTP) | A | **P2** | Low-medium — FANUC CNC shops via FASMTC/TrakHound [24][25] | Never raw FOCAS in v1 |
| 13 | BACnet/IP client | A | **P2** | Low-medium — pharma/chemical BMS [43] | COV subscriptions; MS/TP via customer's router |
| — | OPC DA reach (via UA tunneller) | D | **P1** | Medium — legacy SCADA | **Buy** Kepware/Matrikon UAT per site [41]; consume via #8 |
| — | Exotic PLC reach (MELSEC, Delta, old AB) | D | P1–P2 | Site-specific | **Buy/deploy** Kepware suite or NeuronEX drivers per site [20][22] |
| — | IEC 61850 MMS | A/D | **P3** | Low — direct substation IED reads | Buy gateway/driver on first paying demand [44] |
| — | DNP3, Profinet/EtherNet-IP direct, OPC UA PubSub, LoRaWAN | — | **Skip** | — | Reachable via gateways or not present in ICP |

**Build order logic:** P0 = everything Path B needs (meter + bill + files + MQTT) → first prescription in ≤2 weeks with zero OT change requests. P1 = the Path A unlock (OPC UA + DLMS + ERP). P2 = vertical-triggered (CNC for auto components, BACnet for pharma). P3 = account-triggered purchases.

### 4.2 Edge topology decision tree

```
START: new plant onboarding
│
├─ Q1: Only bills + existing EMS/historian CSV exports available?
│   └─ YES → **Topology F (file-sync)** — no hardware. SFTP/email drop → cloud ingest.
│            Path B live in days. Upgrade later.
│
├─ Q2: Meters on RS-485/Modbus but no usable plant LAN/WAN for us?
│   └─ YES → **Topology C (cellular gateway)** — DIN-rail 4G gateway
│            (dual-SIM, local buffer) wired to the meter bus [51].
│            No plant-IT ticket. The default Path B hardware install.
│
├─ Q3: Plant LAN available + IT allows outbound 443/8883?
│   └─ YES → **Topology E (edge agent on LAN)** — Stamped containerised agent
│            (industrial PC or customer VM), outbound-only MQTT/TLS,
│            ≥72 h disk store-and-forward. The default Path A install.
│
├─ Q4: SCADA/PLC data needed AND plant runs exotic protocols?
│   └─ YES → Topology E + **bought driver layer** (Kepware / NeuronEX / customer's
│            Ignition Edge) feeding the agent via OPC UA or Sparkplug.
│
└─ Q5: Customer mandates IDMZ/data-diode architecture (PSU/cement tier)?
    └─ YES → **Topology D (IDMZ broker)** — customer-hosted broker in IDMZ,
             OT publishes outbound to it, Stamped consumes from IDMZ [39][40].
             Enterprise pricing only.
```

Rules of thumb: cloud-direct (no edge box) is allowed only for Topology F and cloud-API sources; every streaming install gets store-and-forward; the agent is **one container image** with connector plugins enabled per site config, fleet-managed via OTA channel `[!]` (balena-class or k3s + GitOps — decide in P1).

### 4.3 Edge agent minimal spec

| Aspect | Spec |
|---|---|
| Base | Containerised Linux (arm64 + amd64); runs on ₹15–35k industrial PC or ₹8–15k 4G gateway class hardware `[~]` |
| Southbound | Connector plugins from §4.1 matrix (Modbus, MQTT-local, OPC UA, DLMS, file-watch) |
| Buffering | Disk-backed queue, ≥72 h at full rate; per-tag sequence numbers; watermark on flush |
| Uplink | MQTT/TLS QoS 1, persistent session, outbound-only; compression on backlog flush |
| Time | NTP sync; **flag `clock_unsynced` quality when drift > 2 s** `[~]`; all timestamps UTC + plant TZ recorded in plant metadata |
| Health | Birth/death (Sparkplug-style) + 60 s heartbeat with poll-success ratios per connector |
| Security | Read-only device credentials; per-plant client certs; no inbound listeners; signed OTA updates |
| Config | Declarative site config (tags, profiles, poll rates) pushed from cloud, versioned |

### 4.4 Canonical normalisation schema (refined)

Refinements over the v1 sketch in the [technical architecture](../02-technical-architecture.md) §5.2 — additions marked ★:

```jsonc
Measurement {
  org_id, plant_id, asset_id,          // graph binding (asset_id nullable until mapped ★)
  metric: {
    type,                              // active_power_kw | apparent_power_kva | energy_kwh |
                                       // energy_kvah ★ | pf | reactive_energy_kvarh ★ |
                                       // frequency_hz | voltage_v | current_a | md_kva ★ | ...
    unit,                              // canonical SI-derived unit, fixed per type
  },
  ts_utc,                              // source timestamp if trustworthy, else poll timestamp
  ts_source: "device|poller|file",     // ★ timestamp provenance — device RTC vs edge clock
  value: float64,
  quality: "good|estimated|bad|stale|clock_unsynced",  // ★ extended enum
  aggregation: "instant|interval_sum|interval_avg|counter_delta", // ★ semantics of the value
  interval_s,                          // for interval/rollup records (null for instant)
  lineage: { source_system, source_tag, connector_id, register_profile_ver ★, ingest_ts },
  seq: int64                           // ★ per-tag monotonic sequence from edge (gap detection)
}

Event {
  org_id, plant_id, asset_id?, ts_utc,
  event_type,                          // state_change | alarm | connector_birth | connector_death |
                                       // data_gap ★ | bill_received ★ | tag_remapped ★
  severity, payload{}, lineage{}
}

ProductionRecord {
  org_id, plant_id, line_id, window: {start_utc, end_utc},
  sku?, batch_id?, quantity, unit,     // ton | pieces | batches
  shift_code ★, source: "erp|mes|manual", lineage{}
}

BillLine {
  org_id, plant_id, bill_id, discom, bill_month, tariff_code,   // e.g. "UPPCL-HV2-H21A"
  line_type,                           // demand | energy_tod_slot | pf_adjustment | fca |
                                       // duty | arrears | penalty_excess_cd | rebate | other
  qty, qty_unit,                       // kVA, kVAh per slot ...
  rate, amount_inr,
  extraction: { confidence, method: "doc_ai|llm|manual",        // ★ audit trail
                validated: bool, recompute_delta_inr ★ },
  source_doc_ref                       // object-store pointer to original PDF + bbox map
}
```

**kVAh first-class:** UP and Maharashtra HT bills are kVAh-billed — treating kWh as the only energy metric breaks bill reconciliation. Both `energy_kwh` and `energy_kvah` are canonical metric types.

**Timestamps.** Everything stored UTC; plant IANA TZ (`Asia/Kolkata` today, but keep per-plant) held in plant metadata for shift/TOD windowing. Modbus values get poller timestamps (`ts_source: poller`) [9]; DLMS load profiles and historian exports carry device timestamps (`ts_source: device`) — L3 must know the difference when correlating MD spikes.

**Late/out-of-order handling.** Three tiers: (a) within edge-buffer horizon (≤72 h) — normal path, lands in uncompressed Timescale chunks [35]; (b) within compress_after window (≤7 d) — normal insert, flagged `late=true` in ingest metrics; (c) beyond — routed to a backfill queue that decompresses/recompresses affected chunks off-peak and triggers L3 baseline-recompute notifications `[!]`. Per-tag `seq` gaps distinguish "no data produced" from "data lost in transit".

### 4.5 Tag mapping & semi-automated discovery

Pipeline (maps to ML-09 in the [technical architecture](../02-technical-architecture.md) §12):

1. **Harvest** — connector browses the namespace (OPC UA browse, Modbus profile, Sparkplug DBIRTH metric list, CSV headers) → raw tag inventory with names, units, sample values.
2. **Template match** — vertical templates (forging, die casting, cement, pharma) carry expected asset/metric structures; deterministic rules match obvious patterns (`*_KW`, `INCOMER*`, `COMP*`).
3. **LLM suggestion** — for the residue, an LLM proposes `(asset_id, metric_type, unit)` with confidence, given tag name + engineering unit + value statistics + the vertical template as context. Research status check: LLM/GraphRAG methods generate accurate mappings for **simple** target models but underperform domain-specific algorithms on complex hierarchies [49][50] — so LLM output is a **suggestion queue, never auto-applied**.
4. **Human confirm** — onboarding engineer approves/edits in a mapping UI; every confirmed pair becomes training/few-shot data for the next plant in the same vertical.
5. **Drift watch** — value-statistics fingerprint per tag; if a tag's distribution shifts radically (e.g. CT ratio changed, meter swapped), raise `tag_remapped?` event instead of silently ingesting garbage.

Target metric: **≤ 2 engineer-days tag mapping per Path A plant of ~500–1,500 tags** `[~]`, trending down with template maturity.

### 4.6 Data-quality gates (the L1→L2 firewall)

| Gate | Rule | On failure |
|---|---|---|
| Staleness | Same value + no device-ts advance for N poll cycles (N per metric type) | quality→`stale`; suppress from baselines |
| Range | Value outside physical plausibility (PF ∉ [0,1], kW > connected load × 1.2) | quality→`bad`; alert on persistence |
| Counter sanity | Energy counter decreases (non-rollover) or jumps > max feasible interval energy | quality→`bad`; probable MF/byte-order error — page onboarding |
| Clock | Edge NTP drift > 2 s, or device ts vs ingest ts skew > threshold | quality→`clock_unsynced` |
| Gap | `seq` discontinuity | emit `data_gap` Event with window |
| Bill recompute | Extracted bill fails arithmetic recompute (§3.4) | BillLine `validated=false`; human review queue — **never feeds M&V unvalidated** |
| Completeness SLO | Per-plant daily: % expected points received, % good-quality | Dashboard + alert < 95% `[~]` |

Interpolation policy: L1 **never fills gaps**. Gap-filling is an L2/L3 concern with explicit `estimated` quality; L1's job is honest raw data + honest flags.

---

## 5. How this layer is tested and evaluated

### 5.1 Protocol conformance & simulator rigs

| Rig | Purpose | Implementation |
|---|---|---|
| Modbus simulator farm | Register-profile correctness incl. byte-order/scaling permutations | pymodbus/diagslave servers seeded with golden register maps per meter model; property tests over all 4 byte orders [11] |
| OPC UA test server | Cert exchange, security-policy matrix, subscription behaviour, reconnect | open62541/Prosys simulation server; kill/restart chaos tests; assert no session leaks (the documented Telegraf failure mode [47][48]) |
| Sparkplug conformance | Birth/death ordering, sequence numbers, rebirth handling | Eclipse Tahu reference + Sparkplug TCK against our ingest [4] |
| DLMS meter simulator | OBIS profile reads per IS 15959 block/daily/billing profiles | Gurux-class DLMS simulator `[!]`; validate scaler/unit handling |
| Replay rig | End-to-end: recorded real-plant streams replayed at 1×–100× speed | Golden datasets from pilot plants (anonymised); every release must reproduce identical L2 contents (hash-compare) |
| WAN chaos | Store-and-forward under 4G flap, 24 h outage, clock drift | toxiproxy/netem profiles; assert zero loss ≤ buffer horizon, correct `late` flags beyond |
| Bill corpus | Extraction accuracy per DISCOM | ≥30 real bills per DISCOM template `[~]` (portal PDFs + phone scans); field-level precision/recall vs hand-labelled truth; recompute-pass rate |

### 5.2 Data-quality gate metrics (release + fleet SLOs)

| Metric | Target `[~]` |
|---|---|
| Point completeness (expected vs received, per plant per day) | ≥ 99% streaming; ≥ 95% file-based |
| Good-quality ratio (good / total, excluding planned outages) | ≥ 97% |
| Timestamp integrity (points with `clock_unsynced`) | < 0.5% |
| Edge buffer loss beyond horizon | 0 tolerated ≤ 72 h outage |
| Bill field accuracy (validated fields vs truth) | ≥ 99% on core fields (MD, billing demand, TOD kVAh, total) after recompute gate |
| Bill straight-through rate (no human touch) | ≥ 80% by P1, ≥ 90% by P2 |
| Tag-mapping precision (LLM suggestions accepted unchanged) | ≥ 70% by third plant per vertical |
| Onboarding time | Path B ≤ 5 working days; Path A ≤ 15 `[!]` |

### 5.3 Connector certification checklist (per new connector/profile before production)

1. Conformance suite green (protocol rig + security matrix where applicable).
2. Chaos suite green (disconnect/reconnect/burst/backlog flush, no dupes no loss).
3. Golden-replay hash-identical into L2.
4. Quality gates verified: forced stale/range/counter faults produce correct flags.
5. Lineage complete: every emitted record resolves to `connector_id` + profile version.
6. Resource envelope: CPU/RAM/disk on reference edge hardware within budget.
7. Runbook written: onboarding steps, failure modes, rollback.
8. Security review: read-only credentials confirmed, no inbound listener, TLS pinned.

---

## 6. Build phasing P0–P3

| Phase | Timeline `[~]` | L1 deliverables | Unlocks |
|---|---|---|---|
| **P0** (wks 1–8) | Pilot wedge | Modbus TCP/RTU adapter + profile engine (top ~10 meter models); bill ingest v1 (UPPCL + UPCL + MSEDCL templates) with recompute gate; CSV/file ingest; generic MQTT + Sparkplug ingest; manual upload; cellular-gateway topology (C) + file topology (F); EMQX broker → Redpanda → Timescale landing path; quality gates v1; canonical schema v1 | Path B live: MD/PF/TOD prescriptions verified on the bill |
| **P1** (mo 3–6) | Path A unlock | OPC UA client (subscriptions + cert runbook); DLMS/IS 15959 client; historian SQL puller; REST poller (SAP OData first); edge agent fleet mgmt (OTA, site config); tag-discovery pipeline with LLM suggestions + mapping UI; DHBVN/PSPCL/GUVNL/TANGEDCO bill templates; Kepware/UA-tunneller playbook for OPC DA sites | Machine-level SEC, shift attribution, ERP-normalised baselines |
| **P2** (mo 6–12) | Vertical depth | MTConnect client (FANUC shops); BACnet/IP client (pharma/BMS); bill straight-through ≥90%; tariff-order parsing harness (annual ERC cycle); connector certification automated in CI; multi-plant fleet dashboards for connector health | Auto-component CNC energy; pharma HVAC category; fleet ops at 50+ plants |
| **P3** (demand-driven) | Long tail | IEC 61850 via bought driver on first paying account; IDMZ/enterprise topology (D); DNP3 only if a utility-side integration appears; edge-side pre-aggregation for very high-frequency tags `[!]` | Cement/steel EHV accounts; PSU-grade security postures |

---

## 7. Open questions `[!]`

1. **NeuronEX licence economics** at 500–2,000 tags/plant × 100+ plants — per-tag pricing may force the custom-driver path earlier than planned. Get a quote before P1 commit.
2. **DLMS access rights on DISCOM boundary meters** — is consumer-side read access (MR association) legally/practically available per DISCOM, or do we need parallel check-metering? Validate in first UP pilot.
3. **Sub-minute vs 15-min MD detection** — is 1-min polling of the incomer sufficient for MD attribution, or do 15-min integrating meters force us to model within-block ramps? (Interacts with L3 real-time-vs-batch open question.)
4. **WhatsApp-scanned bill quality floor** — what share of pilot bills arrive as photos vs portal PDFs, and does the doc-AI path hold ≥99% on photos?
5. **Tally reach** — ODBC vs XML export vs manual upload for SME-adjacent accounts; unclear how often Tally holds usable production quantities.
6. **Edge hardware standard** — single reference 4G gateway SKU (Indian vendor [51]) vs industrial-PC class for Path A; spares/RMA logistics across states.
7. **Fleet management substrate** — balena-class managed OTA vs self-run k3s+GitOps; decision gates P1 agent work.
8. **Per-plant clock discipline** — NTP reachability on cellular-only sites; do we need GPS-time on the gateway for MD forensics?
9. **S7-1500 OPC UA licence prevalence** — what fraction of Indian S7 estates have the OPC UA server licence enabled vs requiring Kepware? Field-check in first three Path A plants.
10. **IDMZ-hosted broker demand** — how many ICP accounts will actually mandate Topology D vs accept outbound-only agent? Determines enterprise-tier engineering.

---

# Citations

1. FlowFuse — OPC UA Security: Defensible Architecture (Jun 2026): https://flowfuse.com/blog/2026/06/opc-ua-security-best-practices/
2. php-opcua docs — OPC UA security policies & modes matrix: https://www.php-opcua.com/documentation/opcua-client/v4.5.x/security/policies
3. OPC Foundation — Practical Security Guidelines for OPC UA Applications: https://opcconnect.opcfoundation.org/2018/06/practical-security-guidelines-for-building-opc-ua-applications/
4. Eclipse Sparkplug Specification v3.0.0: https://sparkplug.eclipse.org/specification/version/3.0/documents/sparkplug-specification-3.0.0.pdf
5. i-flow — What is Sparkplug B (pros and cons): https://i-flow.io/en/ressources/what-is-sparkplug-b-pros-and-cons-of-the-standard/
6. HiveMQ — Beyond MQTT: Fit and Limitations of Other Technologies in a UNS: https://www.hivemq.com/blog/beyond-mqtt-fit-and-limitations-other-technologies-in-uns/
7. CPRI — Metering Protocol Laboratory (IS 15959 Parts 1–3, IS 16444, DLMS conformance): https://cpri.res.in/en/content/metering-protocol-laboratory
8. Electrical India — Qualitative Testing of DLMS/COSEM ICS-compliant Energy Meters: https://www.electricalindia.in/qualitative-testing-of-dlms-cosem-ics-compliant-energy-meters/
9. Merobix — How Modbus Works (limitations: no timestamps/units/quality): https://www.merobix.com/blog/how-modbus-works-plain-english-guide.html
10. Software Toolbox — What is Modbus (RTU, TCP, ASCII): https://softwaretoolbox.com/resources/what-is-modbus
11. Chipkin — Modbus Data Types & Byte Order Reference: https://docs.chipkin.com/articles/modbus-data-types-byte-order-reference/
12. Schneider Electric — PM5560 communication protocols (Modbus RTU/TCP, BACnet/IP, DNP3): https://www.se.com/ae/en/faqs/FA320614/
13. Schneider Electric India — EM6400NG features (RS-485 models): https://www.se.com/in/en/faqs/FA332977/
14. Secure Meters — Elite 500 multifunction meter (Modbus RTU/TCP, BACnet, Profinet, IEC 61850 options): https://www.securemeters.com/product/multifunction-panel-meters/elite-500/
15. HPL India — Smart prepaid metering with RS-485 (DLMS optical + Modbus RS-485): https://www.hplindia.com/product/meters/smart-prepaid-metering-solution-with-rs-485-communication/
16. Elmeasure — Multi-Functional Energy Meters (RS-485, configurable register map): https://www.elmeasure.com/energy-and-power-monitors/multi-function-energy-meter
17. EDWartens — WinCC vs FactoryTalk vs Ignition in Indian industry: https://edwartens.co.in/blog/wincc-vs-factorytalk-vs-ignition-scada-comparison
18. JRS Innovation — SCADA System Selection Guide (4 platforms ≈ 80% of deployments): https://ifactory.jrsinnovation.com/greenfield-consulting/scada-system-selection-guide
19. Palladium Dynamics — PLC & SCADA Integration Guide 2026 (India Siemens/AB split, PI in Indian process): https://palladiumdynamics.com/whitepapers/palladium-dynamics-plc-scada-integration-guide-2026.pdf
20. Allied Solutions — KEPServerEX overview (150+ drivers, Sparkplug B, suite licensing): https://www.alliedsolutionsglobal.com/en/products/kepserverex
21. Allied Solutions — Kepware pricing 2026 (suite licensing bands): https://www.alliedsolutionsglobal.com/en/news/kepware-pricing-2026-kepserverex-licensing-guide
22. EMQ — Comparing NeuronEX and Kepware: https://www.emqx.com/en/blog/comparing-neuronex-and-kepware
23. EMQX Neuron docs — FAQ (30-tag free tier, driver list, C SDK): https://docs.emqx.com/en/neuronex/latest/faq/faq_basic.html
24. FANUC America — MTConnect Server/Adapter (FASMTC over FOCAS): https://www.fanucamerica.com/products/cnc/cnc-software/connectivity-software-for-machine-tools/mtconnect-server-adapter
25. MachineMetrics — How to use FANUC FOCAS: https://www.machinemetrics.com/connectivity/protocols/focas
26. FANUC — Improved power consumption monitor via FOCAS2 (2023): https://www.fanuc.co.jp/en/product/new_product/2023/202306_monitor.html
27. RaftLabs — OCR vs LLM for invoice processing (accuracy/cost bands): https://www.raftlabs.com/blog/ocr-vs-llm-invoice-processing
28. Tensoria — Invoice OCR with AI: stacks and validation 2026 (Azure DI 97–99%, HITL): https://tensoria.fr/en/blog/invoice-ocr-ai-validation-b2b
29. LLMversus — Invoice structured extraction reference architecture (vision-LLM + deterministic validators): https://llmversus.com/architecture/invoice-structured-extraction
30. BusinessWare — Textract vs Google vs Azure vs GPT-4o invoice benchmark: https://www.businesswaretech.com/blog/research-best-ai-services-for-automatic-invoice-processing
31. IoT Digital Twin PLM — Kafka vs Redpanda vs WarpStream: Edge Telemetry ADR (2026): https://iotdigitaltwinplm.com/kafka-vs-redpanda-vs-warpstream-edge-telemetry-adr-2026/
32. Modern Data Tools — Redpanda review 2026 (Kafka-API compatible, single binary): https://www.modern-datatools.com/tools/redpanda
33. OneUptime — TimescaleDB for IoT data (MQTT→broker→hypertable pattern): https://oneuptime.com/blog/post/2026-01-27-timescaledb-iot/view
34. JusDB — TimescaleDB 2026: hypertables, continuous aggregates, compression: https://www.jusdb.com/blog/timescaledb-hypertables-continuous-aggregates-guide
35. Timescale docs — Compression and out-of-order data (compress only after late data settles): https://github.com/timescale/docs.timescale.com-content/blob/master/using-timescaledb/compression.md
36. Dev.to — Choosing the right chunk_time_interval (compress_after ≥ 1–2× chunk interval): https://dev.to/philip_mcclarence_2ef9475/choosing-the-right-chunktimeinterval-for-your-workload-2gdp
37. Software Toolbox — What is the Purdue Model (iDMZ MQTT broker, outbound-only): https://softwaretoolbox.com/resources/what-is-purdue-model
38. Cirrus Link — MQTT and the Purdue Model: IIoT security best practices: https://cirrus-link.com/mqtt-and-the-purdue-model-iiot-security-best-practices/
39. Cybele — Secure IT/OT network architecture for manufacturing (IDMZ guide): https://blog.cybelesoft.com/secure-it-ot-network-architecture-manufacturing/
40. TerraZone — Zero Trust for the Purdue Model (Jan-2026 CISA/NCSC-UK outbound-only guidance): https://terrazone.io/zero-trust-purdue-model-it-ot-convergence/
41. Allied Solutions — DCOM for remote OPC connectivity: why it breaks, UA tunnelling fix: https://www.alliedsolutionsglobal.com/en/news/dcom-remote-opc-connectivity-explained
42. Prosys OPC — Windows DCOM hardening (CVE-2021-26414) impact on OPC Classic: https://prosysopc.com/blog/dcom-server-security-bypass/
43. Software Toolbox — What is BACnet (BACnet/IP, MS/TP, COV): https://softwaretoolbox.com/resources/what-is-bacnet
44. Baudrate — IEC 61850 MMS driver (logical nodes, SCL, port 102): https://baudrate.io/iec-61850-mms-niagara
45. Inductive Automation — Ignition Edge pricing ($945 perpetual, unlimited tags): https://inductiveautomation.com/pricing/edge
46. Inductive Automation — Ignition Edge IIoT (MQTT Transmission, 35-day/10M-point store-and-forward): https://links.inductiveautomation.com/ignition/edge/iiot
47. Telegraf — OPC UA input plugin README (cert management, polling vs listener): https://github.com/influxdata/telegraf/blob/master/plugins/inputs/opcua/README.md
48. W. Kheshfeh — OPC UA data pipeline architecture performance deep dive (Telegraf/Node-RED production limits): https://medium.com/@waeel.nono3719876/why-your-opc-ua-data-pipeline-architecture-matters-a-performance-deep-dive-d2bcae9022e8
49. IEEE CASE 2025 — Automatic discovery and modeling of industrial assets (LLM/GraphRAG vs domain algorithms): https://doi.org/10.1109/case58245.2025.11164146
50. IEEE ICMIMT 2025 — AI-powered semantic matching for OPC UA & Asset Administration Shells: https://doi.org/10.1109/icmimt65123.2025.11091954
51. SilTech India — BusLog 4G industrial Modbus-to-MQTT gateway (made-in-India, buffer, auto-APN): https://siltech.in/products/buslog-4g
52. BIS — IS 15959 Amendment 2 (ICS parameter tables: instantaneous, block/daily load, billing profiles): https://www.scribd.com/document/756625218/15959A2
53. Repo — UP HT DISCOM Bill Structure Template (UPPCL/UPERC FY 2025-26): /external-learning/discom/UP-HT-DISCOM-Bill-Structure.md
54. Repo — HT Industrial Bill Structures Index (MSEDCL sample format, TANGEDCO/TSSPDCL real bills): /external-learning/discom/HT-Industrial-Bill-Structures-Index.md
