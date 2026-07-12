# ADR-004: Compliance-driven architecture

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-09 |
| **Related** | [India compliance register](../compliance/india-compliance-register.md) · [ADR-002](ADR-002-build-all-aws-networking.md) · [ADR-003](ADR-003-connectors-edge-monorepo.md) |

---

## Context

Stamped operates in Indian manufacturing plants (OT read-only tap), processes electricity bills and operational telemetry in AWS, and sells B2B to enterprises whose parents may face **BRSR**, **PAT**, and **ISO** procurement gates. Compliance is not a late add-on — several Indian rules **fix architecture** (log residency, incident timelines, metering standards).

This ADR turns the [compliance register](../compliance/india-compliance-register.md) into **binding engineering decisions** for connectors-edge, connectors-bill, and shared cloud.

---

## Decision summary

| ID | Decision | Primary driver |
| --- | --- | --- |
| C-01 | **Single AWS region `ap-south-1`** for production data, logs, backups | CERT-In 180-day logs in India |
| C-02 | **NTP sync** (NIC/NPL-traceable) on edge gateways and all cloud VMs | CERT-In Directions 2022 |
| C-03 | **Incident response runbook** — CERT-In report within **6 hours** of awareness; named PoC | CERT-In Directions 2022 |
| C-04 | **DPDP programme** — privacy notice, customer DPAs, sub-processor list, breach notification process | DPDP Act 2023 + Rules 2025 |
| C-05 | **Data minimisation** — no PII in MQTT telemetry; bill PDFs encrypted (S3 SSE); retention limits | DPDP |
| C-06 | **OT read-only + outbound-only** — no write-capable drivers; no inbound ports on edge | IEC 62443 posture, plant IT, CISA/NCSC OT guidance |
| C-07 | **Per-plant mTLS** for MQTT; broker ACLs per `org_id/plant_id` | DPDP safeguards, IEC 62443 conduit |
| C-08 | DLMS connector implements **BIS IS 15959** (+ IS 16444) Indian companion profiles | Indian metering / smart-meter ecosystem |
| C-09 | **Signed edge artefacts** — container images, OTA manifests; CI SBOM (Syft/Trivy) | ISO 27001 supply chain, enterprise questionnaires |
| C-10 | **Tenant isolation** — `org_id` on every record; Postgres RLS when shared DB | DPDP multi-tenant SaaS |
| C-11 | **WPC-certified cellular hardware** only in field BOM | DoT radio regulations |
| C-12 | **ISO 27001 controls from day one**; formal certification only when deal requires | Enterprise procurement |
| C-13 | **No US-only observability** for production — metrics/logs/traces primary store in `ap-south-1` | CERT-In log jurisdiction |
| C-14 | **Audit trail** on tag-mapping publishes, bill validations, connector config OTA | DPDP accountability, customer audits |

---

## 1. CERT-In & log residency (C-01, C-02, C-03, C-13)

### Decision

- All production **ICT logs** (application, broker, auth, API gateway, DB audit) retained **180 days** in **`ap-south-1`**.
- Edge gateways sync time via **chrony** to pools traceable to NIC/NPL.
- Maintain `docs/runbooks/cert-in-incident-6h.md` (to be created at implementation) with: classification tree, portal steps, PoC roster, legal notification parallel path for DPDP.

### Consequences

- Grafana Cloud / Sentry: use **India-region or self-hosted** endpoints; if US SaaS used, **duplicate** security-relevant logs to S3 in Mumbai.
- DR snapshot copies may exist in `ap-south-2` but **primary log query path** stays India.

---

## 2. DPDP (C-04, C-05, C-10, C-14)

### Decision

| Role | Data | Control |
| --- | --- | --- |
| **Processor** | Plant telemetry, bills under customer contract | DPA; process only per customer instructions |
| **Fiduciary** | Tag-mapping UI users, Stamped employees | Consent/notice; own retention policy |

**Technical:**

- RBAC on tag-mapping-api and future admin tools.
- Bill bucket: SSE-KMS, lifecycle policy, no public ACLs.
- Structured audit log: `{actor, action, plant_id, resource, timestamp}`.

### Out of scope for L1

WhatsApp phone numbers (L5) — separate DPIA when shipped.

---

## 3. OT / IEC 62443 alignment (C-06, C-07)

### Decision

Edge security architecture document (1-pager for plant IT) states:

1. Read-only protocol sessions.
2. No write function codes in Modbus/OPC UA stacks.
3. Outbound MQTT/TLS only.
4. Edge sits in **Level 3** DMZ / read-only VLAN.
5. Per-device certificates; 90-day rotation target.

Target **IEC 62443 Security Level 2** for the edge software component — proportionate to overlay risk.

### OPC UA (P1)

Enforce `SignAndEncrypt`, policy floor `Basic256Sha256` per L1 spec — aligns with IEC 62443 and OPC Foundation security guidance.

---

## 4. Metering standards (C-08)

### Decision

DLMS/COSEM connector (P1) certified against:

- **IS 15959** Parts 1–3 (Indian companion)
- **IEC 62056** base
- CPRI-style OBIS parameter verification before production

Modbus meter profiles are **vendor config**, not statutory, but **accuracy** ties to CEA metering norms and M&V defensibility.

---

## 5. Telecom / hardware (C-11)

### Decision

Field team uses only **WPC/ETA-certified** 4G DIN-rail gateways. Maintain approved hardware list in `external/compliance/approved-edge-hardware.md` (create when BOM fixed).

---

## 6. Certifications — when to spend (C-12)

| Certification | Trigger |
| --- | --- |
| **ISO 27001** | First enterprise/PSU deal requiring it OR >₹2Cr ARR |
| **SOC 2 Type II** | US-listed parent procurement |
| **QCI-NCIIPC CAF** | Designated CSE customer contract |
| **ISO 50001** | N/A for Stamped (customer plants) |

Until trigger: run **Sprinto-class** control checklist without audit cost.

---

## 7. Customer regulatory enablement (not Stamped compliance)

Stamped **enables** customer obligations without owning them:

| Customer regime | What L1/L2 must supply |
| --- | --- |
| **BEE PAT** | SEC, energy consumption, audit-trail exports |
| **SEBI BRSR** | Scope 2 grid kWh, methodology, CEA factors (L5/L6) |
| **State ERC open access** | 15-min capable metering ingest, timestamps |
| **OEM supplier audits** | M&V evidence, IPMVP-aligned boundaries |

Document export formats in L2/L5; L1 ensures **lineage and timestamp integrity**.

---

## 8. Deferred compliance items

| Item | Owner layer | When |
| --- | --- | --- |
| TRAI DLT SMS templates | L5 | Before SMS fallback live |
| Meta WhatsApp Business verification | L5 | Before prescription WhatsApp |
| Hazardous-area edge hardware (ATEX) | L1 hardware | First chemical plant in EX zone |
| Carbon Credit Trading Scheme (CCTS) | Product | When PAT successor affects customers |

---

## 9. Consequences for repo layout

Add to connectors-edge / connectors-bill when implementing:

```text
docs/
  runbooks/
    cert-in-incident-6h.md
  security/
    plant-it-one-pager.md          # OT read-only, outbound-only
external/compliance/
  india-compliance-register.md     # this register
  approved-edge-hardware.md        # when BOM fixed
```

---

## 10. Review cadence

- **Quarterly:** compliance register + ADR-004 still accurate?
- **Per new state DISCOM:** tariff template + bill compliance check
- **Per enterprise deal:** questionnaire → gap → ADR if architecture change
