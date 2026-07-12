# India compliance register (Stamped L1 / connectors-edge)

Living register of regulations, standards, and compliance systems relevant to **Stamped Energy** and the **connectors-edge** / **connectors-bill** repos. Use with [../decisions/](../decisions/) ADRs.

**Last updated:** 2026-07-09  
**Scope:** Indian ICP manufacturing plants, HT electricity consumers, OT read-only integration, AWS cloud (`ap-south-1`).

---

## How to read this document

| Column | Meaning |
| --- | --- |
| **Applies to Stamped as** | Our legal/operational role |
| **L1 relevance** | Direct = build/control now · Indirect = customer or downstream layer · Future = L5/L6 |
| **P0** | Must design for before first pilot plant |
| **P1** | Before Path A scale or enterprise deal |
| **Trigger** | When it becomes mandatory beyond baseline |

**Stamped is NOT:** a DISCOM, utility, meter manufacturer, telecom operator, or CII-designated entity (unless later designated). Many rows are **customer obligations** we enable or **voluntary alignments** that shorten enterprise sales.

---

## 1. Summary matrix — what matters most for L1

| Priority | Domain | Key instruments | Stamped action (short) |
| --- | --- | --- | --- |
| **P0** | Cyber incident & logs | CERT-In Directions 2022 | 6h incident reporting runbook; **180-day logs in India** (`ap-south-1`); NTP sync; designated PoC |
| **P0** | Data protection | DPDP Act 2023 + Rules 2025 | Privacy notice, DPAs, breach process (~72h), minimal PII in telemetry; processor + fiduciary roles |
| **P0** | OT security posture | Read-only + outbound-only (CISA/NCSC pattern) | No PLC writes; no inbound plant ports; security note for plant IT |
| **P0** | Cloud residency | CERT-In log rule + DPDP | **All logs and primary data in `ap-south-1`**; document sub-processors (AWS) |
| **P0** | Metering standards | IS 15959, IS 16444, IEC 62056 | DLMS connector implements **Indian Companion Spec** OBIS/profile set |
| **P1** | OT standards | IEC 62443, NIST SP 800-82 | Zone/conduit design for edge agent; SL-2 target for our software |
| **P1** | Org security cert | ISO 27001 | Run controls from day 1; certify when enterprise deal requires (~₹5.5–8L) |
| **P1** | Energy customer regs | BEE PAT, Energy Conservation Act | Export SEC/M&V evidence formats PAT DCs need (L2/L5); not a PAT registrant ourselves |
| **P1** | Electricity metering law | CEA Metering Regulations 2006 | Timestamp/granularity discipline; main/check meter awareness in ingest |
| **Future** | CII / critical sector | NCIIPC, QCI CAF (IEC 62443 L3) | Align voluntarily; mandatory only if customer is designated CSE |
| **Future** | Messaging | TRAI DLT | L5 WhatsApp/SMS — not L1 |
| **Future** | Listed-co ESG | SEBI BRSR | L5/L6 export packs — Stamped enables Scope 2 evidence, not BRSR filing |

---

## 2. Cybersecurity & IT law

### 2.1 CERT-In Directions (April 2022) — **P0 mandatory**

| Field | Detail |
| --- | --- |
| **Instrument** | CERT-In Direction No. 20(3)/2022 under IT Act §70B |
| **Applies to** | All body corporates in India, including SaaS/cloud providers |
| **L1 relevance** | **Direct** — cloud ingest, MQTT broker, tag-mapping-api, bill service |

**Requirements:**

| Requirement | Implementation for Stamped |
| --- | --- |
| Report **20 categories** of cyber incidents within **6 hours** of awareness | Incident runbook; on-call; pre-filled CERT-In portal template |
| **ICT logs 180 days**, rolling, **stored in India** | CloudWatch/Loki in `ap-south-1`; no US-only log sink for production |
| **NTP sync** to NIC/NPL-traceable servers | EC2, edge gateways, RDS — chrony config in base AMI |
| Designated **Point of Contact** for CERT-In | Named security lead + backup in `external/compliance/contacts.md` (internal) |
| Respond to CERT-In info requests within **6 hours** | Legal + eng escalation path |

**Architecture decisions (see ADR-004):** single-region AWS Mumbai; no production telemetry to foreign-only observability stacks.

Sources: [CERT-In Directions PDF](https://beta.medianama.com/wp-content/uploads/2022/04/CERT-In_Directions_70B_28.04.2022.pdf), IT Act §70B.

---

### 2.2 Digital Personal Data Protection Act, 2023 + Rules 2025 — **P0 mandatory**

| Field | Detail |
| --- | --- |
| **Instrument** | DPDP Act 2023; DPDP Rules 2025 (notified Nov 2025) |
| **Enforcement** | Phased; penalties up to **₹250 crore** for safeguard failures; consent manager registration window 2026 |
| **Applies to Stamped as** | **Data Fiduciary** (employees, customer admins, marketing) + **Data Processor** (plant data under customer contract) |

**Personal data Stamped may touch in L1:**

| Data | Source | Minimisation |
| --- | --- | --- |
| Plant staff names / phones | WhatsApp, workflow (L5) | Out of L1 scope |
| Customer admin users | Tag-mapping UI, dashboards | Email, name — consent + notice |
| Bill PDFs | Bill ingest | May contain consumer name, address, account number — **treat as sensitive operational data** |
| Telemetry | Edge | Usually **not** personal data if asset-level only |

**Requirements:**

| Requirement | Action |
| --- | --- |
| Privacy notice (English + Indian languages mechanism) | Website + in-product |
| **Data Processing Agreements** with every enterprise customer | MSA schedule |
| Sub-processor list (AWS, LLM APIs, etc.) | Public page + DPA |
| Reasonable security safeguards | Encryption TLS/at-rest, RBAC, audit logs |
| **Breach notification** to Data Protection Board + affected individuals | Align internal SLA with CERT-In 6h / DPDP "as soon as practicable" (~72h) |
| Grievance redressal officer | Appoint when scaling |
| Significant Data Fiduciary obligations | DPIA, DPO if designated — unlikely at seed stage |

**L1-specific:** do not store bill PDFs longer than needed; redact PII in logs; tenant isolation (`org_id` RLS).

---

### 2.3 Information Technology Act, 2000 (amended) — **P0 baseline**

| Section | Relevance |
| --- | --- |
| §43, §66 | Computer misuse — our systems must prevent unauthorised access to customer OT data |
| §43A / reasonable security | Precursor to DPDP safeguard duty |
| §70A | NCIIPC mandate for **Critical Information Infrastructure** — see §4 |

---

### 2.4 ISO/IEC 27001:2022 — **P1 certify when deal requires; P0 controls**

| Field | Detail |
| --- | --- |
| **Status** | Not law, but **enterprise procurement gate** |
| **Sized cost (India)** | ~₹5.5–8L, 4–6 months `[~]` per production-engineering doc |
| **Decision** | **Implement controls now** (access reviews, IaC, secrets, audit logs); **certify when first enterprise customer requires** |

Maps to: CERT-In, DPDP safeguards, SOC 2 prep.

---

### 2.5 SOC 2 Type II — **P2 optional**

Relevant for US-parent or global OEM customers. Indian SOC 2 ~₹8–14L via Indian auditors. Defer until contract demands; controls overlap ISO 27001.

---

## 3. OT / ICS / industrial cybersecurity

### 3.1 IEC 62443 (ISA/IEC industrial cybersecurity) — **P1 align; build to SL-2**

| Field | Detail |
| --- | --- |
| **Status** | BIS-adopted; referenced by NCIIPC CAF |
| **Applies to** | IACS vendors and integrators |
| **L1 relevance** | **Direct** — we build edge agent + connectors |

**Practical requirements for connectors-edge:**

| IEC 62443 concept | Stamped implementation |
| --- | --- |
| **Zones & conduits** (62443-3-3) | Edge agent in Level 3 DMZ; single outbound conduit to cloud |
| **Security Level 2** target | Protection against intentional casual attack — realistic for software overlay |
| **Component requirements** (62443-4-2) | Secure coding, signed updates, no hidden services |
| **Read-only** | No write function codes / OPC UA write access — architectural |
| **Defence in depth** | Documented in plant IT security one-pager |

---

### 3.2 NCIIPC + QCI CAF for Critical Sector Entities — **P2 / customer-driven**

| Field | Detail |
| --- | --- |
| **Instrument** | IT Act §70A; NCIIPC guidelines; QCI-NCIIPC CAF (2025) |
| **Sectors** | Energy, power, transport, telecom, banking, government, strategic |
| **Applies to Stamped** | **Indirect** unless we are declared CII or sell to designated CSEs under CAF audit |

**CAF levels:**

| Level | Content | Stamped note |
| --- | --- | --- |
| BTC L1 | ISO 27001 + extras | Voluntary alignment |
| STC L2 | ISO 27019 + sector CSMS | Power-sector customers may ask |
| ATC L3 | IEC 62443 control system requirements | Cement/steel PSU tier |

**Decision:** document **voluntary alignment** with IEC 62443 + outbound-only; full CAF audit only when **paying CSE customer** contract requires.

---

### 3.3 NIST SP 800-82 Rev 3 — **P1 reference**

US guidance, widely cited in Indian OT assessments. Use for zone diagrams and threat model documentation.

---

### 3.4 CISA / NCSC-UK OT guidance (2026) — **P0 sales + design**

Not Indian law but cited in L1 spec. **Outbound-initiated connections only** — implement and document for every plant install.

---

## 4. Energy, electricity & metering regulations

### 4.1 Electricity Act, 2003 + State ERC regulations — **Indirect (customer)**

| Field | Detail |
| --- | --- |
| **Relevance** | HT industrial consumers under state DISCOMs (UPPCL, MSEDCL, etc.) |
| **Stamped role** | Software overlay — does not supply electricity |

**Implications for L1:**

- Bill ingest must respect **tariff orders** per state ERC (already in L1 spec).
- **Open access / green energy** rules may require 15-min meters + communication to SLDC — our ingest should support **15-min granularity** and quality flags.
- We do not perform scheduling or deviation settlement — customer/DISCOM domain.

---

### 4.2 CEA (Installation and Operation of Meters) Regulations, 2006 — **P1 awareness**

| Field | Detail |
| --- | --- |
| **Authority** | Central Electricity Authority |
| **Relevance** | Main/check meters, sealing, communication to SLDC for OA consumers |

**L1 action:** support **main vs check** meter tagging in lineage; timestamp integrity for settlement-grade data; do not break meter seals.

---

### 4.3 BIS IS 15959 (Parts 1–3) + IS 16444 — **P1 mandatory for DLMS connector**

| Standard | Scope |
| --- | --- |
| **IS 15959 Part 1** (2011) | DLMS/COSEM companion spec — static meters |
| **IS 15959 Part 2** (2016) | Smart meters (with IS 16444 Part 1) |
| **IS 15959 Part 3** (2017) | Transformer-operated HT meters |
| **IS 16444** | Smart meter physical/spec requirements |

**L1 action:** DLMS client must implement **Indian OBIS parameter set** and association profiles (PC, MR, US, PUSH per meter class). Conformance testing against CPRI/Gurux rigs before production.

---

### 4.4 IEC 62056 (DLMS/COSEM) — **P1 technical base**

International base standard; IS 15959 is the Indian companion. Build to both.

---

### 4.5 Bureau of Energy Efficiency — PAT scheme — **Indirect (customer value)**

| Field | Detail |
| --- | --- |
| **Instrument** | Energy Conservation Act; PAT cycles (VII active 2022–25, VIII 2023–26) |
| **Applies to** | **Designated Consumers** in 9+ energy-intensive sectors (cement, steel, textiles, etc.) |
| **Stamped role** | Enable SEC reporting, M&V documentation — **not a PAT registrant** |

Many ICP plants (auto components) may **not** be PAT DCs; cement/steel often are. Product should export **SEC, baseline, M&V** artifacts compatible with PAT M&V norms (L3/L5).

---

### 4.6 Energy Conservation Act, 2001 + ECBC — **Indirect**

Large commercial buildings / designated consumers. Relevant for pharma HVAC vertical; L1 may ingest BMS data.

---

## 5. Telecom & connectivity

### 5.1 TRAI DLT (SMS) — **Future (L5)**

Mandatory for **commercial SMS** in India: Principal Entity ID, header, content templates on operator DLT portal. Applies to **MSG91/SMS fallback**, not L1 edge MQTT.

**Note:** WhatsApp Business uses **Meta Cloud API** — separate from TRAI DLT; still needs business verification.

---

### 5.2 WPC / DOT — **P1 if shipping cellular gateways**

| Field | Detail |
| --- | --- |
| **Authority** | Wireless Planning & Coordination Wing, DoT |
| **Relevance** | 4G/LTE modules in edge gateways must use **WPC-approved** radio hardware |
| **Stamped action** | Source gateways with valid ETA/WPC certification; document in hardware BOM |

---

### 5.3 SIM / M2M connectivity — **P1 operational**

Use M2M SIMs from licensed Indian telcos; APN configs for outbound-only; TRAI commercial communication rules don't apply to MQTT device telemetry.

---

## 6. Corporate sustainability & reporting (customer-driven)

### 6.1 SEBI BRSR — **Indirect (L5/L6 export)**

| Field | Detail |
| --- | --- |
| **Mandate** | Top 1,000 listed companies (by market cap) |
| **Needs** | Scope 1 & 2 GHG mandatory; Scope 3 encouraged; assurance phasing |
| **Stamped delivers** | Verified grid kWh reduction, SEC trends, CEA emission factors — **evidence export**, not BRSR filing |

Listed parents of ICP suppliers drive demand; Stamped is **enabler**, not reporter.

---

### 6.2 ISO 50001 — **Indirect**

Energy management system certification some OEMs require. Stamped operational data can support ISO 50001 audits; we don't certify plants.

---

### 6.3 IPMVP — **P0 methodology (not regulation)**

International Performance Measurement and Verification Protocol. Referenced throughout Stamped specs for savings claims. Implement M&V Option C/D patterns in L5; L1 provides **measurement boundary integrity**.

---

### 6.4 ASHRAE Guideline 14 — **P0 methodology**

Baseline model statistics (CVRMSE, NMBE) for M&V certification — L3/L5, but L1 data quality gates enable it.

---

## 7. Factory, labour & safety (tangential)

| Regulation | L1 touch |
| --- | --- |
| Factories Act / state rules | No direct — we don't operate plant equipment |
| OHSAS 18001 / ISO 45001 | Customer programs only |
| Explosive/hazardous area (CEAG) | If edge hardware in hazardous zone — **P2** gateway certification (ATEX/IECEx) for chemical plants |

---

## 8. Contractual & procurement compliance

| Type | Examples | Action |
| --- | --- | --- |
| **Customer MSAs** | Data residency, OT read-only, audit rights, liability caps | Standard MSA + DPA templates |
| **OEM supplier audits** | IATF 16949 sites with energy clauses | M&V evidence quality |
| **Insurance** | Cyber insurance | After ISO controls baseline |
| **Export control** | Typically N/A for energy SaaS in India | Revisit if hosting foreign crypto/ML on restricted lists |

---

## 9. Compliance-driven architecture decisions (→ ADR-004)

Consolidated decisions that **must** appear in ADRs and implementation:

| ID | Decision | Driven by |
| --- | --- | --- |
| C-01 | Production in **AWS `ap-south-1` only**; logs never US-only | CERT-In §180-day India logs |
| C-02 | **NTP** on all edge + cloud systems | CERT-In time sync |
| C-03 | **6-hour incident runbook** + CERT-In PoC | CERT-In |
| C-04 | **DPA + privacy notice** before first paying customer | DPDP |
| C-05 | **Minimise PII** in telemetry; bill PDFs encrypted at rest | DPDP |
| C-06 | **Read-only OT**, outbound-only WAN | IEC 62443, plant IT, CISA guidance |
| C-07 | **mTLS per plant**, no shared MQTT credentials | IEC 62443, DPDP safeguards |
| C-08 | DLMS implements **IS 15959** profile set | Indian metering law / DISCOM interoperability |
| C-09 | **Signed edge OTA** + SBOM | ISO 27001 supply chain, enterprise questionnaires |
| C-10 | **Tenant RLS** in shared DB | DPDP, multi-customer SaaS |
| C-11 | WPC-certified **4G hardware** in BOM | DoT radio regulations |
| C-12 | ISO 27001 **controls without cert** until deal trigger | Enterprise sales |

Full ADR: [ADR-004-compliance-driven-architecture.md](../decisions/ADR-004-compliance-driven-architecture.md).

---

## 10. Compliance roadmap by phase

| Phase | Compliance deliverables |
| --- | --- |
| **Before first pilot** | C-01–C-08, C-10; plant IT security one-pager; incident runbook draft |
| **Before Path A (OPC UA) plant** | OPC UA security policy matrix (IEC 62443); cert management runbook |
| **Before 5th paying customer** | DPA template live; sub-processor page; grievance officer |
| **Before enterprise / PSU deal** | ISO 27001 cert; CAF alignment doc; SOC 2 if US parent |
| **Before L5 WhatsApp at scale** | Meta Business verification; TRAI DLT if SMS fallback |

---

## 11. What Stamped does NOT need (common misconceptions)

| Misconception | Reality |
| --- | --- |
| "We need DISCOM licence" | No — we don't sell electricity |
| "We must be PAT registered" | No — customers may be; we supply evidence |
| "We need TRAI DLT for MQTT" | No — DLT is for commercial SMS |
| "We need NCIIPC clearance to start" | No — unless designated CII or contract requires CAF |
| "BRSR filing is our job" | No — we export data for listed customers' filings |
| "Plant Wi-Fi licence from Stamped" | No — we use customer LAN or cellular |

---

## 12. References & official sources

| Topic | Source |
| --- | --- |
| CERT-In Directions | https://www.cert-in.org.in |
| DPDP Act | MeitY / Digital India |
| NCIIPC | https://nciipc.gov.in |
| QCI CAF CSE | https://padd.qci.org.in |
| BEE PAT | https://beeindia.gov.in |
| IS 15959 / 16444 | Bureau of Indian Standards |
| SEBI BRSR | https://www.sebi.gov.in |
| TRAI DLT | https://trai.gov.in |
| CEA metering | https://cea.nic.in |
| IEC 62443 | https://www.isa.org/standards-and-publications/isa-standards/isa-iec-62443-series-of-standards |

---

## 13. Maintenance

- Review this register **quarterly** or when entering a new state/vertical.
- Each new regulation → row here + ADR if architecture changes.
- Copy `external/compliance/` into `connectors-bill` and L2+ repos.
