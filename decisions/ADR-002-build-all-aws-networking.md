# ADR-002: Build-all software, plant networking, AWS cost-first deployment

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-09 |
| **Supersedes** | Buy-vs-build rows in [L1 spec §4.1](../technical/layers/L1-connect-and-normalise.md) class **(D)** and cost-upgrade rows that assumed Kepware/NeuronEX/EMQX Cloud |
| **Related** | [ADR-001](ADR-001-l1-repo-split-and-boundaries.md) |

---

## Context

Stamped will **build all L1 connector and transport software in-house** — no per-site Kepware, NeuronEX, or managed MQTT vendor purchases. The product must **deploy entirely on AWS**, run **cheaply at pilot scale**, and document **clear upgrade triggers** when scale or enterprise deals justify paid/managed alternatives.

This ADR does **not** change L1 functional scope or canonical contracts from ADR-001. It changes **how** we connect to plants, **what** we build vs license, and **which** cloud services we use at P0.

---

## Decision summary

| # | Topic | Decision |
| --- | --- | --- |
| 1 | Build vs buy | **Build all L1 software ourselves.** Open-source libraries allowed (pymodbus, open62541, gurux DLMS, etc.). No commercial OT gateway SKUs, no EMQX Cloud, no Kepware per site. |
| 2 | Plant networking | **No Stamped-owned Wi-Fi or plant LAN dependency for Path B.** Cellular-first uplink (4G gateway on RS-485). Plant LAN only when customer grants it (Path A). **Outbound-only** WAN — never require inbound ports or site VPN. |
| 3 | Cloud platform | **AWS only** (`ap-south-1` primary) for **`cloud` deployment mode** ([ADR-010](ADR-010-deployment-profiles-and-portability.md)). No multi-cloud P0. |
| 4 | Cloud cost posture | **Minimum viable managed footprint** — single small EC2/RDS/Fargate tasks, S3, no Kafka/MSK/Redpanda until trigger fires. Target **≤ ₹15–25k/month** AWS at ≤10 pilot plants `[~]`. |
| 5 | MQTT cloud broker | **Self-hosted Mosquitto on one `t4g.small` EC2** (or Fargate if ops prefers) with TLS + per-plant ACLs — **not** AWS IoT Core at fleet scale (message pricing), **not** EMQX Cloud. |
| 6 | Event backbone | **Postgres transactional outbox** on same RDS as L2 (per tech arch §4) — no message broker in cloud at P0. |
| 7 | Upgrade path | Every cheap default has a **documented trigger** (§6). Upgrade is transport/ops swap, not schema rewrite. |

---

## 1. Build-all connector strategy

### Decision

All connectors in the L1 matrix are **class (A) or (C) — build once, profile-driven** — except where physics/platform forces a constraint (OPC DA).

| Capability | P0 build | Notes |
| --- | --- | --- |
| Modbus TCP/RTU | **Yes** | pymodbus / custom stack + profile registry |
| MQTT + Sparkplug decode | **Yes** | Own subscriber + vendor JSON-path decoders |
| CSV/file/SFTP ingest | **Yes** | Cloud poller (Topology F) + edge filewatch |
| OPC UA client | **Yes** (P1) | open62541 or mature OSS client; cert runbook |
| DLMS/COSEM | **Yes** (P1) | Gurux or equivalent OSS; IS 15959 profiles |
| REST/OData poller | **Yes** (P1) | Generic poller + per-source profiles |
| Historian SQL read | **Yes** (P1) | Read-only incremental queries |
| MTConnect | **Yes** (P2) | HTTP/XML client |
| BACnet/IP | **Yes** (P2) | OSS BACnet stack |
| OPC DA (legacy SCADA) | **Stamped-built Windows sidecar** (P1) | Small agent customer runs on SCADA host → forwards to our edge agent via localhost MQTT/HTTP. **Not** Kepware. See §1.1 |
| S7comm / EtherNet-IP / MELSEC wire | **Yes, phased** (P1–P2) | OSS libs where stable (e.g. snap7-class); narrow read-only subset first |

**Profile library** (meter register maps, byte order, scaling) is the main asset — same as before, but **100% owned**.

### 1.1 OPC DA constraint (honest exception)

OPC DA requires DCOM on Windows. We **do not buy** Matrikon/Kepware tunnellers.

**Our approach:**

1. **Prefer OPC UA** — ask plant to enable S7-1500 UA server or upgrade path.
2. **CSV/historian export** — Path B fallback when UA blocked.
3. **Stamped OPC-DA Bridge** — minimal Windows service we build and ship: DCOM client → normalise → forward to edge agent or cloud file drop. One codebase, our installer, our updates.

This is still **our software**; it runs on customer Windows SCADA host, not a third-party SKU.

### Rationale

- Control roadmap and margins; no per-site licence tax.
- Aligns with product thesis: software-first overlay.
- Engineering cost is front-loaded; acceptable at seed stage.

### Consequences

- Larger connector engineering surface; need conformance rigs (L1 spec §5.1).
- OPC DA bridge adds a Windows build/release pipeline.
- Long-tail exotic PLCs may lag Kepware coverage — acceptable for ICP wedge (Modbus meters dominate).

---

## 2. Plant networking — how industries actually connect

### Decision: networking topologies (customer-side)

Stamped **does not install or operate Wi-Fi** at the plant. We support what the customer already has or what we ship on the gateway.

| Topology | Code | What the plant needs | What Stamped ships | WAN path | Typical ICP path |
| --- | --- | --- | --- | --- | --- |
| **File-only** | **F** | Email/SFTP/WhatsApp for bills + EMS CSV | Nothing on OT network | HTTPS upload to AWS (S3 presigned) | Fastest Path B; zero OT approval |
| **Cellular meter** | **C** | Physical RS-485 tap on incomer meter bus | DIN-rail **4G gateway** + our edge agent image | **4G/LTE outbound** MQTT/TLS 8883 or 443 | **Default Path B** — no plant Wi-Fi/LAN required |
| **Plant LAN** | **E** | Ethernet to meter/SCADA VLAN; IT allows outbound HTTPS | Industrial PC or VM with edge agent | Plant LAN → router → **internet outbound** | Path A when IT cooperates |
| **SCADA host bridge** | **E+DA** | Windows SCADA server | OPC-DA Bridge on SCADA + edge agent on same host or LAN | Same as E | Legacy WinCC/iFIX sites |
| **IDMZ broker** | **D** | Customer-hosted MQTT in DMZ | Our agent publishes to **their** broker; we consume from AWS via VPN/private link | Enterprise only | Defer until paying account demands |

### Wi-Fi — do industries need it?

| Question | Answer |
| --- | --- |
| Does Stamped need plant Wi-Fi? | **No** for Path B. Cellular gateway talks to cloud directly. |
| Do some meters have Wi-Fi? | Rare on incomer class; some IoT loggers use Wi-Fi **inside** the customer's LAN — we treat as MQTT/Modbus TCP once on LAN. |
| What if only Wi-Fi reaches the meter? | Customer provides Wi-Fi credentials for **their** network; edge box joins as STA. We document as variant of **E**, not a Stamped network product. |
| What about voice/cellular "voicing"? | Interpreted as **cellular voice/SIM data** — dual-SIM 4G is the Indian field pattern (SilTech-class loggers). **No dependency on plant telephone/PSTN.** |

### Security invariants (unchanged)

- **Read-only** on OT — no PLC writes.
- **Outbound-initiated** WAN only — CISA/NCSC-UK OT guidance.
- **No site VPN** required for standard tier.
- **TLS 1.2+** and per-plant MQTT credentials.

### Physical install pattern (Path B default)

```
[Incomer meter RS-485 bus] ──► [4G DIN-rail gateway + Stamped edge agent]
                                      │
                                      │ LTE outbound (dual-SIM optional)
                                      ▼
                               [AWS Mosquitto EC2] ──► [ingest → RDS]
```

Plant IT involvement: **often zero** for Topology C (only electrical contractor taps RS-485).

---

## 3. AWS cost-first architecture (P0 pilot)

### Design envelope

| Parameter | P0 target |
| --- | --- |
| Plants | ≤ 10 pilots |
| Tags/plant | 200–800 (incomer + few feeders) |
| Cadence | 1-min polls |
| Bills | ~10 PDFs/month |
| Region | `ap-south-1` |

### Service map (cheap defaults)

| Function | P0 AWS choice | ~Cost driver `[~]` | Notes |
| --- | --- | --- | --- |
| **Cloud MQTT broker** | Mosquitto on **1× `t4g.small` EC2** + EIP + ACM TLS | ₹1.5–2.5k/mo | Cheaper than IoT Core at 1-min × hundreds of tags × many plants |
| **Ingest + outbox writer** | **1× Fargate task** (0.25 vCPU / 0.5 GB) or same EC2 as MQTT | ₹1–2k/mo | Single consumer; batch inserts |
| **Timescale + OLTP** | **RDS PostgreSQL** `db.t4g.small` + Timescale extension | ₹3–5k/mo | L1 ingest + L2 share one DB at pilot |
| **Bill PDF storage** | **S3** Standard | &lt; ₹100/mo | Versioned; lifecycle to IA after 90d |
| **Bill processing** | **Lambda** on S3 event + small Fargate for heavy OCR | ₹500–2k/mo | Spike on upload only |
| **Tag-mapping UI** | **S3 + CloudFront** static; API on Fargate or Lambda | ₹500–1.5k/mo | |
| **Secrets** | **SSM Parameter Store** / Secrets Manager | &lt; ₹500/mo | Per-plant MQTT creds |
| **Logs/metrics** | **CloudWatch** basic; optional Grafana Cloud free | &lt; ₹1k/mo | |
| **LLM (bill/tag suggest)** | **Frontier API pay-per-use** | Variable | Minimise via templates + rules first |

**Deliberately excluded at P0:** MSK, Amazon MQ, IoT Core (fleet), Redpanda, NAT Gateway per AZ (use single-AZ pilot VPC or public subnet + security groups carefully), multi-AZ RDS (accept brief downtime in pilot).

**Estimated pilot AWS total:** **₹12–22k/month** for ≤10 plants `[~]` — validate with AWS calculator after first deploy.

### Edge/cloud split (cost)

| Location | Software | Cost |
| --- | --- | --- |
| **Edge gateway** | Our container + **Mosquitto local** (optional bridge) | Customer or Stamped capex ₹8–35k hardware one-time |
| **AWS** | MQTT EC2 + RDS + minimal compute | Opex above |

No paid edge middleware licences.

### Network diagram (P0)

```
┌──────────────── Plant ────────────────┐
│  RS-485 ──► [4G gateway + edge agent] │
│       outbound MQTT/TLS :8883         │
└──────────────────┬────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │ EC2: Mosquitto      │
         │ (stamped-mqtt-p0)   │
         └─────────┬───────────┘
                   │
         ┌─────────▼───────────┐
         │ Fargate: ingest     │──► RDS Postgres/Timescale
         └─────────────────────┘
                   ▲
         ┌─────────┴───────────┐
         │ Lambda/Fargate:     │
         │ bill-ingest ◄── S3  │
         └─────────────────────┘
```

Topology **F** (files only) skips edge EC2 path — bills/CSV go **HTTPS → S3 → bill/ingest Lambda**.

---

## 4. Changes to ADR-001 / L1 spec interpretation

| Previous assumption | New rule |
| --- | --- |
| Kepware/NeuronEX per site for exotic PLCs | **Build** OSS drivers + profiles; narrow scope first |
| EMQX Cloud / managed MQTT | **Self-host** Mosquitto on AWS EC2 P0 |
| "12 built + 2 bought" connectors | **12+ built**; OPC DA via **our** Windows bridge |
| Redpanda at L1 landing | **Never at P0**; Postgres outbox only |

Research docs in `external/technical/` remain reference; **ADRs in `external/decisions/` override** on implementation choices.

---

## 5. Industry / vertical onboarding (networking lens)

| Vertical | Typical L0 reach | Default topology | Build priority |
| --- | --- | --- | --- |
| Auto components / forging | Modbus incomer + EMS CSV | **C** or **F** | Modbus profiles (Schneider, Elmeasure, Secure) |
| Cement / steel | HT meter + SCADA OPC | **E** + OPC UA P1 | OPC UA + DLMS |
| Pharma / chemical | BMS BACnet + meters | **E** | BACnet P2 after Modbus P0 |
| Any Path B wedge | Bill PDF + incomer only | **C** + bill S3 upload | Bill ingest + Modbus P0 |

**No vertical requires Stamped to provision Wi-Fi.** If production data only exists behind SCADA, move **F → E** after IT approval.

---

## 6. Upgrade triggers (when to spend more)

| Component | P0 (cheap) | Upgrade when | Upgrade to |
| --- | --- | --- | --- |
| Cloud MQTT | Mosquitto on single EC2 | &gt;50 plants OR broker SLO breaches OR ops &gt;2h/week | EMQX cluster on ECS, or IoT Core + rules (re-evaluate cost model) |
| Event backbone | Postgres outbox | Sustained &gt;5k msg/s OR multiple independent consumer groups need replay | Redpanda on ECS or MSK |
| RDS | Single `db.t4g.small` | Storage &gt;80% or CPU &gt;70% sustained OR &gt;30 plants | `db.t4g.medium` + Multi-AZ |
| Ingest | Single Fargate task | Lag &gt;2 min sustained | Horizontal Fargate + partition by plant_id |
| Bill OCR | Docling + vision-LLM | Recompute failure rate &gt;15% on scans | Commercial doc-AI API (per-page) |
| OPC DA | Our Windows bridge | Bridge unstable on &gt;3 sites | Revisit **only then** — still prefer UA migration |
| Edge fleet | Manual OTA / SSH | &gt;20 edge devices | balena/k3s GitOps (self-hosted, no vendor per-device fee if possible) |
| Observability | CloudWatch | On-call needed | Grafana Cloud Pro |

**Rule:** upgrade is **trigger-driven**, not premature. Document trigger hit in new ADR before spending.

---

## 7. Open questions

1. **AWS IoT Core** — use only for a **single-demo** plant if EC2 ops burden blocks launch? (Cost cap experiment.)
2. **Hardware SKU** — standardise one Indian 4G DIN-rail gateway BOM for field team.
3. **S7comm scope** — read-only DB areas for which CPU families in P1?
4. **Single-AZ pilot** — acceptable downtime window for RDS in pilot contracts?

Edge language / monorepo — **decided in [ADR-003](ADR-003-connectors-edge-monorepo.md).**

---

## 8. Consequences

- Connector team owns **full driver long tail** — roadmap must sequence P0 Modbus/MQTT/file before OPC UA.
- Field playbook emphasises **Topology C** (cellular) to avoid plant IT — aligns with cheap, fast Path B.
- AWS bill monitoring alarm at **₹25k/month** until triggers fire.
- Next ADR: **ADR-004** — first P0 implementation slice (Modbus + contracts + minimal ingest) when build starts.

---

## 9. ADR-010 addendum — deployment modes (2026-07-12)

ADR-002 remains **authoritative for `cloud` mode** (AWS cost-first, Mosquitto on EC2, RDS, Fargate). [ADR-010](ADR-010-deployment-profiles-and-portability.md) adds **`local`** and **`local-dashboard`** modes without changing build-all connector strategy or plant networking invariants.

| Topic | `cloud` (this ADR) | `local` / `local-dashboard` |
| --- | --- | --- |
| Orchestration | ECS Fargate + RDS | Docker Compose on customer host |
| MQTT broker | Mosquitto on EC2 | Compose `mosquitto` service |
| Postgres | RDS shared instance | Container Postgres + Timescale |
| Cost ceiling | ≤ ₹15–25k/month AWS | Customer hardware; no AWS bill |
| OTA | HTTPS deploy | Signed release bundle (P1) |
| LLM | Frontier API default | Local LLM required for L3/L4 |

**Selector:** `STAMPED_DEPLOYMENT_MODE=cloud|local|local-dashboard`. Same container images and contracts; mode changes compose profile + env only.

**Pilot default:** `cloud` until customer contract requires air-gap. Upgrade triggers in §6 apply to `cloud` mode only.
