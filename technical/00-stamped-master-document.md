---
type: Product Master Document
title: "Stamped Energy — Master Product & Company Document"
description: "A prescriptive energy intelligence platform for energy-intensive Indian manufacturers — turning existing plant data into assigned actions and verified savings on the DISCOM bill, without replacing…"
tags: [stamped-energy, product]
timestamp: "2026-06-27T11:51:48Z"
---
# Stamped Energy — Master Product & Company Document

*Version 1.4 | June 2026*
*Status: Pre-validation — core assumptions flagged. Treat as a living document and update after every 5 discovery calls.*

> **Canonical index:** For the full repository map and “where to find what,” see [`README.md`](/README.md) at repo root. This document is the **product & company** source of truth; it links to but does not duplicate every research artifact.

> **Honesty Convention (carried over from project documents):**
> `[~]` = Approximate or benchmark-derived figure — not yet validated on our own customer base
> `[!]` = Actively evolving — verify before using in customer conversations

---

## 1. Identity & Positioning

**Company Name:** Stamped Energy

**One-Line Position:**
A prescriptive energy intelligence platform for **energy-intensive Indian manufacturers** — turning existing plant data into **assigned actions and verified savings on the DISCOM bill**, without replacing EMS, without PLC control writes, and without enterprise procurement cycles.

> **ICP Scope Note (authoritative):** Primary ICP is **large North India manufacturers** — **≥ ₹30 lakh/month** electricity per plant, **₹300–5,000 crore** revenue, across automotive, cement, steel, pharma, and chemical verticals. See `customer-profile/ICP-North-India-Large-Manufacturer-v2.md`. Auto component NCR remains a **priority wedge** within that profile; the platform is industry-agnostic. National conglomerates (Tata, Mahindra group OEMs, etc.) are **out of scope** for current GTM. Sub-₹30L/month accounts are **nurture-only** unless strategic reference.

**Working Tagline (customer-facing):**
*From plant data to verified savings.*

**Internal tagline:**
*Precision energy intelligence. Verified savings. Built for manufacturers.*

**GTM category (June 2026):**
**Bill-verified operational decision layer** — not an EMS replacement, not an ESG/carbon accounting platform. Enemy positioning: **insight without closure** (dashboards and audits that never become assigned, bill-verified ₹).

**External properties:**
- Marketing site: [stamped.work](https://stamped.work/)
- Demo dashboard: [stamped-energy.vercel.app](https://stamped-energy.vercel.app/) `[!]`
- Research knowledge base: this repository (`Research+DOcs/`)

**What Stamped Energy is:**
A software-first energy decision and optimization platform that integrates with a manufacturing plant's existing infrastructure — SCADA systems, PLCs, CNCs, energy meters, and production data — to identify specific energy inefficiencies, prescribe exact corrective actions with rupee-denominated impact, track execution, and verify that savings materialize on the next electricity bill.

**What Stamped Energy is not:**
A monitoring dashboard. An ESG reporting tool. A sustainability compliance platform. A hardware company. A PLC control system. Stamped Energy does not surface data — it closes the loop from insight to **assigned action** to **verified savings on the HT electricity invoice**.

**Dual outcome (enterprise messaging):** Primary hero remains **₹ on the DISCOM bill**. Secondary column — **operational sustainability** (plant-level intensity evidence, audit-ready M&V) — supports listed/global subsidiaries without rebranding as an ESG platform. See `marketing/content-strategy/stamped-website-sustainability-positioning-strategy.md`.

---

## 2. Core Hypothesis

**Initial ICP focus:** Large North India manufacturers — **≥ ₹30 lakh/month** electricity per plant, **₹300–5,000 crore** revenue `[~]` — in automotive components, cement, steel, pharma, and chemical plants. These companies already run SCADA, EMS, PLCs, and feeder-level metering as standard infrastructure. They are losing **₹3–40 lakh every month** `[~]` to avoidable energy waste (10–20% of a ₹30L–2Cr bill). Auto component manufacturing in NCR remains the **priority wedge** within this profile. Demand charges triggered by simultaneous machine startups that nobody coordinated. Compressors consuming 20% more energy than their baseline because the inlet filter hasn't been flagged. Furnaces holding temperature through the weekend because no setback schedule was programmed. CNCs idling at full spindle power between batches because nobody built an auto-sleep routine.

The data to find and fix all of this already exists in their systems. The problem is that it is fragmented across SCADA, PLCs, energy meters, ERP, and utility bills — and no software layer sits across all of it to turn that data into specific, rupee-denominated actions that someone actually executes and tracks.

They will pay for a software-first layer that connects to what they already have, tells them exactly where the money is going in rupees per month, turns that insight into specific assigned actions, and verifies that the savings appear on the next electricity bill.

**The primary question this hypothesis rests on:**
Is energy cost pain acute enough in this segment — and is the gap between available data and optimized decisions wide enough — that a lean, prescriptive software product at the right price point delivers an obvious, fast-ROI purchase? This is what discovery calls must confirm or refute.

---

## 3. The Core Insight

Indian **large manufacturers** (primary ICP) do not primarily suffer from a lack of data.

They suffer from **fragmented decision-making, delayed visibility, and no clear path from insight to action.**

Most mid-sized auto component plants already have:

- SCADA systems collecting real-time machine and process data
- PLCs controlling key equipment — compressors, presses, furnaces, die casting cells
- CNC machines with spindle load, cycle, and idle state data available
- Energy meters at the incomer and, increasingly, at feeder level
- Monthly electricity bills with full tariff breakdowns
- An electrical engineer or plant manager who already knows something is wrong
- Maintenance staff who can act if told exactly what to do

The problem is that:

- All of this data lives in separate systems that never talk to each other
- SCADA data and energy meter data are never synthesized against the electricity bill
- Production context (what was being made, at what rate) is never cross-referenced with energy consumption
- No one is continuously watching for deviations from normal consumption patterns
- When the bill arrives, the month's waste has already happened and cannot be recovered
- Inefficiencies are known by intuition but never quantified in rupees
- Recommendations made internally never get prioritized, tracked, or verified
- The decision loop from "something is wrong" to "we fixed it and saved ₹X" never fully closes

Most existing energy software monitors. Stamped Energy **optimizes decisions.**

The key distinction — borrowed from the best practices of Zerowatt and Greenovative, then adapted for **Band A North India plants**:

> Insight is only valuable if it reliably causes action. Action is only credible if it is measured. Measurement is only trusted if it is in rupees **on the bill**.

---

## 4. The Market Gap: Large Plant, No Prescriptive Layer

Both Zerowatt (stated ICP: **₹50 lakh/month** energy spend minimum) and Greenovative (ICP: large multi-plant conglomerates) have validated that Indian manufacturers will pay for prescriptive energy intelligence. Both have real enterprise customers and documented outcomes.

Stamped’s **primary ICP (v2, June 2026)** sits in the **overlap and near-adjacent band**: plants spending **₹30 lakh–₹2 crore/month** on electricity — large enough for undeniable ROI, often with EMS/SCADA already installed, but still able to decide at **plant or BU level** without a 18-month group IT procurement cycle.

**Who we target:**
- **Large regional manufacturers** in North India — not national conglomerates (Tata, Mahindra group OEMs, etc.)
- **₹300–5,000 crore** revenue `[~]`, **500–5,000** employees per site
- Verticals: auto components, cement, steel, pharma, chemical

**Why existing solutions leave a gap for this band:**

- **Enterprise platforms (Greenovative):** Built for **70+ plant groups** and **₹3,000+ crore/year** energy spend — sales motion and pricing assume enterprise CoE
- **Full-stack EMS + M&V (Zerowatt):** Strong at **₹50L+/month**; Stamped competes at **₹30L+** with faster plant pilot and EMS **layer** positioning
- **Legacy EMS dashboards:** Monitoring without **assigned prescriptions** and **bill verification** — the Greenovative auto conglomerate case explicitly notes dashboards failed to explain variance

**White space statement:** Hundreds of **large, independent** North India plants have the data infrastructure and the bill pain, but no prescriptive layer that closes the loop in **rupees on the DISCOM bill** at a **90-day plant pilot** cadence.

> **Legacy note:** The earlier SME wedge (50–1,000 employees, ₹3–25L/month bills) validated product mechanics. v2 ICP **raises the floor** to **₹30L/month** for active GTM; sub-threshold accounts are nurture-only.

> **Geographic focus:** North India first (NCR, Haryana, UP, Rajasthan, Punjab, HP/Uttarakhand industrial belts). Same product applies nationally after proof.

---

## 5. Why Now

Several forces have converged to make this moment the right time to build for this segment:

**Rising electricity tariffs:** Industrial electricity tariffs in Haryana, UP, and other NCR-belt states have increased meaningfully over the past 3–5 years `[~]`. Energy, once 5–8% of operating cost for lighter processes, is now 12–20% for process-intensive segments like die casting, forging, and heat treatment `[~]`. Every tariff revision makes the problem more acute.

**OEM price reduction pressure:** Auto component OEMs impose 2–5% annual cost-reduction targets on their suppliers `[~]`. Suppliers absorb tariff hikes rather than passing them through. Energy is one of the few remaining controllable cost lines — making energy optimization not a "nice to have" but a margin defense imperative.

**SME digital maturity is rising:** Band C companies now routinely have ERPs, and smart energy meters are increasingly being installed at main incomers across mid-sized plants — often because of DISCOM mandates or OEM audit requirements. The minimum data floor required to start is now accessible to a larger share of the target segment than it was 3–5 years ago.

**AI development velocity:** Building a prescriptive energy platform no longer requires a 5-year product development cycle. AI-native tooling and modern infrastructure enable rapid iteration, fast deployment, and intelligent pattern recognition at a cost structure that makes SME pricing viable.

**Regulatory tailwinds:** BEE's PAT scheme, BRSR requirements for listed parent companies, and ISO 50001 mandates from global OEM customers are pushing energy management up the agenda for Tier 1 and Tier 2 suppliers. These mandates create urgency that didn't exist 3 years ago `[!]`.

---

## 6. Product Vision

Stamped Energy is a **prescriptive energy and operational optimization engine for large North India manufacturers.**

> **Scope:** Primary ICP is plants with **≥ ₹30 lakh/month** electricity, **₹300–5,000 crore** company revenue `[~]`, across automotive, cement, steel, pharma, and chemical manufacturing — **North India geography first**. Auto components in NCR remain the priority wedge. National conglomerates (Tata, Mahindra group at OEM/conglomerate level) are out of scope for current GTM.

The system:

1. **Connects** to a plant's existing infrastructure — for customers with SCADA, PLCs, and CNCs, this means direct system integration from day one; for customers with basic meters only, it means starting with meter and utility bill data and deepening integration over time
2. **Builds a baseline** of what the plant should be consuming under normal production conditions
3. **Identifies deviations** — continuously, in near-real time — finding where energy is being wasted, what is causing it, and what the monthly rupee impact is
4. **Generates specific prescriptions:** not "energy is high this week" but "your demand charge spiked at 07:15 on Monday because Compressor 1 and Press Line 3 started simultaneously — stagger them by 10 minutes to save ₹38,000 this month"
5. **Routes prescriptions into a workflow** — assigned to the right person, status tracked, delivered via WhatsApp and dashboard
6. **Verifies outcomes** — after the action is marked complete, monitors whether the saving materialized and builds a running ₹ savings ledger

The platform delivers **measurable, verified cost reduction** — not software features.

---

## 7. The Product

### 7.1 Infrastructure-Adaptive Integration Model

Stamped Energy meets each customer at the level of infrastructure they already have. **Band A ICP plants** (≥ ₹30L/month bill) typically already operate **EMS, SCADA, PLCs**, and feeder-level metering — **Path A direct integration** is the default entry. Path B (meter + bill first) applies when EMS exists but data access is limited initially.

Two integration paths exist. Both deliver real value from day one.

---

**Path A — Direct System Integration**
*For customers with SCADA, PLCs, and CNCs already in operation*

This is the primary integration path for most Medium Organized and Larger Mid-Market customers, and for many smaller IATF-certified plants that have invested in automation to meet OEM quality requirements.

*What we connect to:*
- **SCADA systems** (Siemens WinCC, Wonderware/AVEVA, Rockwell FactoryTalk, GE iFIX, and others) via OPC-UA or Modbus TCP
- **PLCs** (Siemens S7, Allen-Bradley ControlLogix, Mitsubishi MELSEC, and others) for machine-level energy draw, operational state, and cycle data
- **CNC machines** for spindle load, cycle time, idle state, and coolant system consumption
- **Smart energy meters** at incomer and feeder levels via Modbus TCP/RTU or MQTT
- **ERP production schedule data** (SAP, Oracle, Tally Prime Enterprise) where accessible — for production-normalized baseline calculation
- **Compressed air system instruments** — pressure transmitters, flow meters where present

*What this delivers from week 1:*
- Machine-level energy attribution — exactly which machine or process is consuming what, and when
- Production-normalized baselines — energy per part produced, adjusted for product mix and machine configuration
- Real-time anomaly detection against equipment-specific baselines
- Demand spike attribution with machine-level specificity ("the demand spike at 06:45 Monday is caused by Compressor 1, CNC Line 3, and the heat treatment furnace starting simultaneously — stagger by 8 minutes to save ₹35,000 this month")
- Shift-level and batch-level Specific Energy Consumption (SEC) tracking
- Full prescription engine active and producing actionable outputs from week 1

---

**Path B — Progressive Meter-Up Integration**
*For customers with energy meters but no SCADA or PLC data access*

Applicable to smaller organized suppliers and owner-operated plants with basic electrical infrastructure but limited automation.

*Entry requirement:* One connected smart energy meter at the main incomer + last 6 months of electricity bills.

**Stage 1 — Meter + Bill (Weeks 1–2):**
- Baseline monthly cost structure (energy charges, demand charges, power factor adjustment)
- MD pattern analysis — when peaks occur, estimated causes, ₹ cost per peak event
- Power factor penalty quantification
- Time-of-use waste identification
- First actionable prescriptions delivered within 2 weeks

**Stage 2 — Sub-Meters Added (Months 2–3):**
*Added:* Sub-meters at 2–3 high-consumption areas (compressor house, furnace bay, press line)
- Area-level energy attribution — where the energy goes within the plant
- Equipment-level anomaly detection where sub-metered
- Shift and batch-level consumption visibility

**Stage 3 — PLC/SCADA Integration (Month 4+, where available):**
*Added:* PLC or SCADA data feeds where the plant has them
- Full production-normalized baselines
- Machine-level attribution and root-cause analysis
- Transitions from Path B to Path A capability level

---

**The governing principle:** Every customer gets real, verified prescriptions from day one at their integration level. We do not gate insights behind infrastructure upgrades. A Path A customer gets richer prescriptions faster. A Path B customer gets meaningful bill-level prescriptions immediately. The depth grows with the integration; the value starts immediately.

---

### 7.2 Core Capabilities

**1. Demand Intelligence and Maximum Demand Reduction**

Real-time and historical analysis of electricity demand patterns. Identifies when and why demand peaks occur — at shift start, during equipment startups, at certain production states. Quantifies the ₹ cost of each demand event. Prescribes specific scheduling changes (startup staggering, load sequencing, non-critical load shedding during peak windows) to reduce maximum demand (MD) charges.

MD charges represent 30–50% of a large Indian industrial electricity bill `[~]` and are triggered by often-avoidable demand spikes. This is typically the fastest win available — identifiable from bill and incomer meter data alone, actionable within the first billing cycle.

**2. Tariff Structure Optimization**

Analyzes the plant's actual consumption profile against its tariff structure (MSEDCL, DHBVN, PVVNL, or other state DISCOM tariff orders). Identifies whether the contracted maximum demand (CMD) is sized appropriately, whether time-of-use opportunities are being exploited, and whether power factor is attracting penalties or qualifying for rebates. Prescribes specific adjustments with ₹ impact figures.

**3. Utility Waste Detection**

Identifies energy consumption that cannot be attributed to productive work: machines running at idle, compressed air being consumed during non-production periods (a proxy signal for leaks), HVAC and heating systems running outside shift hours, motors running unloaded. At Stage 2, this becomes equipment-level with specific machine attribution.

Compressed air leaks alone typically account for 15–25% of compressed air system energy in poorly maintained plants `[~]` — identifiable from meter trend analysis even without dedicated flow meters.

**4. Prescription Engine**

Every identified inefficiency generates a specific prescription:

| Field | Content |
|---|---|
| **What** | Exact action required (e.g., "Clean inlet filter on Compressor 2 in the north compressor room") |
| **Why** | Root cause and evidence ("Compressor 2 specific power has increased 18% over the past 3 weeks — inlet differential pressure rising") |
| **Who** | Role responsible ("Electrical maintenance team") |
| **Effort** | Time and difficulty estimate ("2-hour job, no specialized tools") |
| **₹ Impact** | Monthly saving if done ("₹42,000/month at current operating hours") |
| **When** | Urgency ("Schedule in next maintenance window; if delayed beyond 2 weeks, efficiency will continue degrading") |

**5. Workflow and Execution Tracking**

Prescriptions do not stop at the alert. They become work items assigned to a specific person or role, with status tracking (Open → In Progress → Completed / Deferred / Rejected). Plant operator notification via WhatsApp. Plant head and owner visibility via dashboard. No prescription disappears into a report that nobody reads.

This is the layer that separates a real optimization engine from another monitoring platform. The insight-to-action gap is where most energy savings are lost.

**6. Savings Verification (Potential vs. Realized)**

After each prescription is marked complete, the system monitors post-action energy consumption against the adjusted baseline. Calculates whether the expected saving materialized — and by how much. Builds a running savings ledger: **"Since deployment, Stamped Energy has delivered ₹X in verified savings."**

This is the number the owner, the CFO, and any OEM sustainability auditor will ask for. It must be real, defensible, and attributable.

---

### 7.3 The Workflow Loop

```
CONNECT              OBSERVE           DECIDE            EXECUTE           MEASURE
────────────         ────────          ────────          ────────          ────────
SCADA / PLC /      Baseline           Prescription      Work order        Saving
CNC / Meters   →   + anomaly    →     with ₹         →  assigned     →    verified
+ Bill data        detection          impact            and tracked        in ₹
```

---

## 8. Outcomes We Deliver

The following outcome ranges are derived from industry benchmarks established by Zerowatt (20–30% average energy cost reduction across their fleet) and Greenovative (8–10% average). SME-specific validation is pending and will be updated as our own customer data accumulates. `[~]`

**Outcome 1 — Electricity Bill Reduction**
Target range: 12–20% reduction in total monthly electricity cost. `[~]`

What this means in rupees for **primary ICP (Band A)** `[~]`:

| Monthly bill | 12% reduction | 20% reduction | Annual (at 15% mid) |
| --- | --- | --- | --- |
| ₹30 lakh | ₹3.6L/month | ₹6L/month | ~₹54L/year |
| ₹50 lakh | ₹6L/month | ₹10L/month | ~₹90L/year |
| ₹1 crore | ₹12L/month | ₹20L/month | ~₹1.8 Cr/year |

**Legacy Band B/C bands** (nurture-only): Band B ₹5L/month bill → ₹60K–1L/month saved; Band C ₹20L/month → ₹2.4–4L/month saved `[~]`.

**Outcome 2 — Maximum Demand Charge Reduction**
Target range: 15–25% reduction in MD charges specifically. `[~]`

MD charges are typically the largest single avoidable cost item on an Indian industrial electricity bill. This outcome is often deliverable from Stage 1 data alone — no sub-metering required — and can appear in the first billing cycle after prescription execution.

**Outcome 3 — Utility Waste Identification and Elimination**
Target range: Identify and begin eliminating 10–20% of non-production-linked energy consumption within 90 days. `[~]`

This includes compressed air leaks (largest single waste source in most auto component plants), idle machine loads, and HVAC and heating systems running outside production hours.

**Platform payback target:** Subscription cost recovered within 3–6 months of deployment. `[~]`

**Time to first insight:** Within 2 weeks of first meter connection.

**Time to first verified saving:** Within the first complete billing cycle after the first prescription is executed.

*These outcome ranges will be updated to reflect our own validated customer data as it accumulates. They are targets, not guarantees, at this stage.*

---

## 9. Who We Serve (ICP)

> **Authoritative ICP document:** `customer-profile/ICP-North-India-Large-Manufacturer-v2.md` — use that file for firmographics, buyer map, disqualifiers, and lead-search rules. This section summarises; it does not supersede v2.

### 9.1 Primary ICP — Band A (active GTM)

| Dimension | Criteria |
| --- | --- |
| **Geography** | **North India** — NCR, Haryana, UP, Rajasthan, Punjab, HP/Uttarakhand industrial belts |
| **Electricity bill** | **≥ ₹30 lakh/month** per plant (HT connection) — hard minimum |
| **Sweet spot** | **₹30 lakh – ₹2 crore/month** per plant `[~]` |
| **Revenue** | **₹300 – ₹5,000 crore** `[~]` |
| **Employees (plant)** | **500 – 5,000** `[~]` |
| **Verticals** | Auto & components · Cement · Steel & metals · Pharma · Chemical & paint |
| **Infrastructure** | EMS/SCADA/PLCs and feeder metering common — **Path A** default |
| **Decision** | Plant Head / VP Ops + Electrical or Energy Head; CFO for commercial terms |
| **Positioning line** | *Large enough that every MD spike costs lakhs. Small enough that decisions happen at the plant, not a global procurement committee.* |

**Priority wedge within Band A:** Auto component manufacturers, Delhi NCR belt (Faridabad, Manesar, Bawal, Noida, Greater Noida, Ghaziabad, Bhiwadi) — deepest domain research and lead density to date.

**Out of scope:** National conglomerates (Tata/M&M group OEM level), HQ-only offices, plants under ₹30L/month bill (nurture only).

### 9.2 Buyer personas (Band A)

| Role | Function in purchase |
| --- | --- |
| **Plant Head / VP Operations** | Economic buyer; cares about margin, MD spikes, OEM price-down pressure |
| **Electrical HOD / Energy Manager** | Champion & technical validator; cares about actionable prescriptions, not another portal |
| **CFO** | Mobiliser for commercial terms; cares about verified ₹ and payback |
| **Corporate Sustainability / QA** | Secondary mobiliser at listed/global suppliers; cares about intensity evidence `[!]` |

Persona draft (legacy Band C scale — update pending): `customer-profile/Persona-RajeshMehta-BandC-AutoComponent-Delhi-NCR.md`

### 9.3 Lead research & geography (June 2026)

**~158 unique companies indexed** across auto, chemical, and cluster scans. Always check `leads/lead-research-master-company-index.md` before new lead generation.

| Cluster / batch | Leads | File |
| --- | --- | --- |
| Auto NCR + batches 2–4 | 90+ | `leads/auto-components/` |
| Chemical Band A (Roorkee/UK) | 18 | `leads/chemical/lead-research-chemical-roorkee-uttarakhand-2026-06.md` |
| Chemical SME (Path B nurture) | 22 | `leads/chemical/lead-research-chemical-sme-roorkee-uttarakhand-2026-06.md` |
| Ramnagar Industrial Estate, Roorkee | 14 | `leads/roorkee/` |
| Rudrapur / Pantnagar SIDCUL | 16 | `leads/rudrapur/` |

**Active sales accounts** (not in leads index): `prospective-clients/shivam-autotech/`, `prospective-clients/lubrizol/`

### 9.4 Legacy segments — Band B/C (nurture only)

The following segments informed early product mechanics and remain valid for **Path B** (meter + bill first) positioning at lower bill bands. They are **not** the primary GTM target since ICP v2 (June 2026). See `customer-profile/ICP-AutoComponent-LeadSearch-Criteria.md` for legacy search templates.

| Segment | Bill band | Status |
| --- | --- | --- |
| Small Organized (50–200 emp.) | ₹2–10L/month | Nurture / Path B only |
| Medium Organized (200–500 emp.) | ₹8–35L/month | Nurture unless ≥ ₹30L verified |
| Larger Mid-Market (500–1,000 emp.) | ₹25–80L/month | Overlaps Band A when bill ≥ ₹30L |

---

## 10. Go-to-Market, Marketing & Sales Motion

*June 2026 — pre-validation stage. No published customer case study yet; first verified ₹ on own letterhead is the critical GTM unlock.*

### 10.1 Stage & motion

| Element | Current state |
| --- | --- |
| **Stage** | Pre-validation — discovery calls, warm accounts, demo-led |
| **Primary motion** | Founder-led outbound + LinkedIn → scoping call → **90-Day Bill Verification Program** |
| **Channels** | Direct (WhatsApp/email) to indexed leads; founder LinkedIn; stamped.work; plant visits |
| **Not yet scaled** | Paid ads, SEO content farm, channel partners |
| **Proof gap** | Benchmark outcomes cite Zerowatt/Greenovative `[~]` — own verified case pending |

### 10.2 Flagship commercial offer

**90-Day Bill Verification Program** — structured engagement (not a “cheap pilot”):

- **Purpose:** One verified savings line on the DISCOM bill, or clear kill criteria at Day 90
- **Duration:** ~90 days (connect → prescribe → assign → verify)
- **Band A fee (working):** **₹2–5 lakh** fixed `[~]` — signals seriousness vs legacy ₹25k–50k SME pilot framing
- **Optional:** ₹1L credit toward Year 1 if verified savings exceed 3× program fee `[!]`
- **Leave-behind:** `marketing/content-strategy/90-day-bill-verification-program-one-pager.md`

### 10.3 Messaging framework (June 2026)

| Layer | Message |
| --- | --- |
| **Hero (website)** | *From plant data to verified savings.* — keep unchanged |
| **Category** | Bill-verified operational decision layer |
| **Enemy** | Insight without closure |
| **Reframes (outbound)** | **Margin Defense** (OEM price-down years) + **Bill Referee** (trust/conversion) |
| **LinkedIn** | AIDA-structured posts — ICP + general audience; see `marketing/content-strategy/linkedin-posts.md` |
| **Strategic marketing audit** | `marketing/content-strategy/stamped-energy-rory-sutherland-marketing-interrogation-2026-06.md` |

### 10.4 Website & content

| Asset | Location |
| --- | --- |
| Content roadmap (SEO/GEO/AEO) | `marketing/content-strategy/stamped-content-roadmap.md` |
| Sustainability + Industry 4.0 (second column) | `marketing/content-strategy/stamped-website-sustainability-positioning-strategy.md` |
| Enterprise blog drafts | `marketing/content-strategy/drafts/` (chemical, cement) |
| Legacy blog drafts | `outputs/` |
| Multi-vertical website IA | `industry-market-research/Multi-Vertical-Expansion-and-Website-Strategy.md` |

### 10.5 Competitive positioning (summary)

| Competitor | Their ICP | Stamped wedge |
| --- | --- | --- |
| **Greenovative** | 70+ plant conglomerates | Regional Band A plants; faster plant-level decision |
| **Zerowatt** | ₹50L+/month cited floor | ₹30L+; EMS **layer**; software-only, no proprietary meters |
| **Legacy EMS** | Monitoring | Prescriptions + workflow + bill verification |

Full intel: `competitor-research/` + `external-learning/zerowatt/` + `external-learning/greenovative/`

---

## 11. Revenue Model

### Entry Phase — 90-Day Bill Verification Program (Band A — primary)

The entry offer exists for one purpose: **remove career risk from the first purchase and generate the first verified savings data point on the DISCOM bill.**

- **Duration:** ~90 days
- **Band A pricing (working):** **₹2–5 lakh** fixed fee `[~]` — scoped to plant size and integration depth; calibrate in discovery
- **Legacy Band B/C pilot (nurture):** ₹10,000–50,000 fixed or pay-as-you-save cap `[~]` — see historical estimates below; not primary GTM
- **Goal:** Deliver at least one **verified ₹ saving** on invoice. Use that number to convert to subscription or multi-site expansion.
- **Sales asset:** `marketing/content-strategy/90-day-bill-verification-program-one-pager.md`

### Pilot Phase (Legacy Band B/C — nurture)

- **Duration:** 4–8 weeks
- **Band C:** ₹25,000–50,000 fixed `[~]`
- **Band B:** ₹10,000–20,000 fixed or pay-as-you-save (% of first verified month, capped)
- **Goal:** Same — one verified ₹ saving; convert only if bill proof delivered

### Monthly Subscription (Post-Verification)

- Month-to-month initially; no long-term lock-in required at conversion
- **Band A (working):** **₹15,000–75,000/month** per site depending on bill scale and integration depth `[~]`
- **Band B legacy (working):** ₹8,000–25,000/month `[~]`
- Customer exits if savings stop materializing

### Annual Contract (Multi-site / listed accounts)

- Annual commitment with quarterly savings reviews
- **Band A (working):** **₹3–15 lakh/year** per site `[~]`
- Includes IPMVP-aligned savings verification documentation (ISO 50001, OEM audit, BRSR-adjacent plant evidence) `[!]`

*All pricing figures above are working estimates based on target economics. They will be calibrated against what customers are willing to pay during discovery conversations and pilot results — not imposed in advance.*

---

## 12. Operating Bets

These are the current strategic beliefs underlying product and go-to-market decisions. They are **assumptions requiring validation**, not proven truths.

**Bet 1: The data floor at Stage 1 is sufficient.**
One smart meter + utility bill history is enough to generate meaningful prescriptions — specifically on demand charges, power factor, and time-of-use patterns — before any sub-metering or PLC integration is required. If discovery shows this is not true, we need to reassess the entry point or add a lightweight hardware component.

**Bet 2: Prescriptive + workflow outperforms prescriptive-only.**
The Insight → Action → Savings loop fails without workflow tracking. Recommendations that are not tracked are not executed. For SMEs, this is even more important than for enterprises — there is no dedicated energy manager whose job it is to chase down work orders. The workflow must be lightweight enough not to add friction, but structured enough to close the loop.

**Bet 3: INR-denominated outcomes are the only language that works.**
This audience makes decisions based on rupees saved per month — not kWh reduced, not percentage improvement, not carbon credits. Every prescription, every dashboard metric, every case study must lead with ₹. This is not a presentation choice; it is a product architecture principle.

**Bet 4: The 90-Day Bill Verification Program is the conversion unlock (Band A).**
The biggest barrier is not price — it is **skepticism from previous dashboard failures** and **career risk** on the Plant Head. A structured verification program with kill criteria and bill-matched proof eliminates this more effectively than feature demos. Premium program pricing signals enterprise-safe seriousness; overly cheap pilots signal desperation.

**Bet 5: The Band A segment is genuinely underserved.**
Hundreds of North India plants sit between Zerowatt's ₹50L+ motion and Greenovative's conglomerate motion. Discovery calls confirm or disconfirm within the first 10 Band A conversations.

**Bet 6: Speed and plant-level decision are durable early advantages.**
Win on **90-day plant proof** before incumbents' enterprise cycles. Cross-plant benchmarking becomes the moat after first logos.

---

## 13. Risks and Honest Unknowns

**Risk 1: Stage 1 data may be too thin for useful prescriptions in some plant types.**
A plant with only an incomer meter and a bill provides limited machine-level signal. For certain plant types (precision machining, wiring harness assembly) where energy cost is lower and less process-intensive, Stage 1 may produce few or no high-value prescriptions. The ICP must be filtered to prioritize energy-intensive processes (die casting, forging, heat treatment, rubber moulding) where the signal-to-noise ratio at Stage 1 is higher.

**Risk 2: Action closure may be harder in Band B than assumed.**
In Band B, the owner is the only executor, approver, and champion simultaneously. If he is in production, traveling, or simply disengaged for a week, the prescription queue sits. The workflow must be designed with this reality in mind — minimum steps, WhatsApp-native, and designed to re-surface if not actioned within 48 hours.

**Risk 3: Band B at the low end may not sustain the unit economics.**
A Band B plant spending ₹2 lakh/month on electricity where we achieve 15% savings generates ₹30,000/month in savings. If our subscription is ₹15,000/month, the ROI is real but thin. Band B qualification should prioritize plants with electricity bills above ₹4–5 lakh/month and process-intensive operations (die casting, heat treatment) where higher savings percentages are achievable.

**Risk 4: Integration friction is unknown until tested.**
"Pure software, no hardware" assumes the smart meter is readable. The actual ease of reading a meter via Modbus, MQTT, or a utility-provided API varies significantly by meter brand, model, age, and plant IT maturity. Real deployment friction per customer is unknown until 3–5 actual installations are attempted. This risk does not block moving forward — it means being honest about deployment timelines in early conversations.

**Risk 5: No published Stamped-verified case study yet.**
Marketing and sales cite industry benchmarks `[~]` — sufficient for discovery, insufficient for skeptical Band A buyers. **First verified ₹ on own letterhead** is launch-blocking for scale; prioritize one flagship account (e.g. Shivam Autotech, Lubrizol, or top Rudrapur lead).

**Risk 6: ICP v2 remains partially validated.**
Band A North India multi-vertical is the best-formed hypothesis — grounded in research, lead index, and warm accounts — but not yet confirmed at scale through paid deployments.

---

## 14. Founder Context

Stamped Energy is founded by an Electrical Engineering graduate of IIT Roorkee, with academic research background in energy systems from the same institution. The problem is understood from first principles — not from consulting reports. The founder is AI-native, with a genuine technical understanding of what modern AI tooling can and cannot do in industrial settings. The operating thesis is that the combination of deep domain knowledge, AI-native product development velocity, and a focus on the **underserved Band A regional plant** segment creates an advantage over enterprise incumbents and hardware-heavy IoT players.

---

## 15. The North Star

There is one thing the customer buys: **a verified reduction in their electricity bill, measured in rupees per month.**

Not software. Not AI. Not a dashboard. Not sustainability reporting.

Every product decision, every pricing decision, every communication should be tested against one question:

> *Does this make it faster and more certain that the customer receives a verified reduction in their electricity cost, measured in rupees per month?*

If it does: build it, price it, communicate it. If it does not: remove it.

---

## 16. Repository Map & Document Links

**Start here:** [`README.md`](/README.md) — full navigation index for this knowledge base.

### Core product & architecture

| Document | Purpose |
| --- | --- |
| **`Stamped_Energy_Master_Document_v1.3.md`** | **This file** — identity, ICP summary, GTM, revenue, bets, north star |
| `Stamped_Product_Definition_and_Architecture.md` | High-level product definition + architecture layers |
| `Stamped_Technical_Architecture_v1.md` | Detailed technical architecture, engines, M&V |
| `Stamped_Tech_Archi_Core.md` | Condensed six-layer reference |
| `Energy-Decision-Optimization-Engine.md` | Decision engine concept |

### ICP, personas & leads

| Document | Purpose |
| --- | --- |
| **`customer-profile/ICP-North-India-Large-Manufacturer-v2.md`** | **Authoritative ICP** (Band A) |
| `customer-profile/ICP-AutoComponent-LeadSearch-Criteria.md` | Legacy Band B/C search templates |
| `customer-profile/Persona-RajeshMehta-BandC-AutoComponent-Delhi-NCR.md` | Buyer persona draft `[!]` |
| **`leads/lead-research-master-company-index.md`** | **Check before any lead search** (~158 cos.) |
| `leads/README.md` | Lead folder layout by vertical/cluster |

### Marketing & GTM

| Document | Purpose |
| --- | --- |
| `marketing/content-strategy/90-day-bill-verification-program-one-pager.md` | Sales leave-behind |
| `marketing/content-strategy/linkedin-posts.md` | LinkedIn post bank (AIDA) |
| `marketing/content-strategy/stamped-energy-rory-sutherland-marketing-interrogation-2026-06.md` | Positioning strategy audit |
| `marketing/content-strategy/stamped-website-sustainability-positioning-strategy.md` | Website sustainability / Industry 4.0 |
| `marketing/content-strategy/stamped-content-roadmap.md` | SEO/GEO/AEO content roadmap |
| `marketing/content-strategy/drafts/` | Enterprise blog drafts (chemical, cement) |

### Industry & vertical research

| Document | Purpose |
| --- | --- |
| `industry-market-research/vertical-industry-xray-index.md` | Index + cross-vertical cheat sheet |
| `industry-market-research/india-cement-industry-analysis.md` | Cement X-ray |
| `industry-market-research/india-steel-industry-analysis.md` | Steel X-ray |
| `industry-market-research/india-pharma-manufacturing-industry-analysis.md` | Pharma X-ray |
| `industry-market-research/india-chemical-industry-analysis.md` | Chemical X-ray |
| `industry-market-research/indian-auto-component-industry-analysis.md` | Auto components X-ray |
| `industry-market-research/energy_auto_india.md` | Auto manufacturing energy domain |
| `industry-market-research/Multi-Vertical-Expansion-and-Website-Strategy.md` | Multi-vertical GTM + website IA |

### Competitors & external learning

| Document | Purpose |
| --- | --- |
| `competitor-research/Greenovative_Comprehensive_AI_Profile.md` | Greenovative reference |
| `competitor-research/Zerowatt_Comprehensive_Knowledge_Base.md` | Zerowatt reference + IPMVP |
| `competitor-research/*_Research_Report.md` | Business reports per competitor |
| `external-learning/zerowatt/` | Industry waste patterns, SEC benchmarks |
| `external-learning/greenovative/` | Platform patterns, expansion implications |

### Active sales accounts

| Account | Folder |
| --- | --- |
| Shivam Autotech | `prospective-clients/shivam-autotech/` |
| Lubrizol | `prospective-clients/lubrizol/` |

---

*Update log:*
*v1.0 — June 2026 — Initial document. All outcome figures are benchmark-derived, not customer-validated.*
*v1.2 — June 2026 — ICP scope clarified: auto component NCR wedge; multi-vertical expansion noted.*
*v1.3 — June 2026 — Positioning language professionalised for SaaS-grade tone.*
*v1.4 — June 2026 — **ICP v2 authoritative** (Band A ≥ ₹30L/mo); new §10 GTM/marketing; 90-Day Bill Verification Program; outcomes/pricing for Band A; repository map; links to `marketing/`, lead clusters (Roorkee/Rudrapur), sustainability dual-ROI; legacy Band B/C marked nurture-only.*
