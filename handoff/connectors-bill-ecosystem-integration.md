# Stamped ecosystem — how connectors-bill connects to sibling repos

> **Master context:** [Stamped master document](../technical/00-stamped-master-document.md) §4–5  
> **Topology ADR:** [ADR-008](../decisions/ADR-008-layer-repo-topology-and-interfaces.md)  
> **Interface authority:** layer-interfaces.md (copy from connectors-cloud `docs/architecture/`)

---

## 1. Eight-repo layer map

Stamped L1–L6 is **one GitHub repo per layer** (plus L1 split into three deployables):

| Repo | Layer | Role | Deployables |
|------|-------|------|-------------|
| **connectors-edge** | L1 plant | OT/IT streaming, tag mapping, edge buffer | edge-agent, tag-mapping-api, tag-mapping-ui |
| **connectors-cloud** | L1 cloud | MQTT/HTTP ingest, validate, outbox, relay → L2 | ingest, relay |
| **connectors-bill** | L1 bill | Document ingest, extract, review UI, BillLine publish | web, api, extract, publish |
| **stamped-l2** | L2 | Universal repository, Timescale, graph | repository API, L1 consumer |
| **stamped-l3** | L3 | Intelligence, findings | workers |
| **stamped-l4** | L4 | Prescriptions | agent |
| **stamped-l5** | L5 | Workflow, M&V, ledger | workflow API |
| **stamped-l6** | L6 | Dashboard, customer experience, exports | Next.js app, public API |

**Communication rule:** documented interfaces only — no shared database writes across repos.

---

## 2. Data flow — bill path (P0)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ CUSTOMER (plant staff / energy manager)                                      │
│   • Photograph DISCOM bill on phone                                          │
│   • Or upload portal PDF                                                     │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ HTTPS
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ connectors-bill                                                              │
│   web (PWA) → api → S3 (original) → extract → validate (recompute)          │
│   → review UI if needed → publish (MQTT QoS 1)                               │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ MQTT
                                    │ topic: stamped/v1/{org}/{plant}/bills
                                    │ schema: bill-line.json
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ connectors-cloud (DONE — do not reimplement in bill repo)                    │
│   ingest: validate → dedupe → StampedRecordEnvelope → l1_outbox              │
│   relay:  outbox → POST stamped-l2 /v1/ingest/records                       │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ HTTP + envelope
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ stamped-l2                                                                   │
│   l1_processed_inbox → bill_lines store → query API                          │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
            ┌───────────────┐               ┌───────────────┐
            │ stamped-l5    │               │ stamped-l6    │
            │ M&V vs bill   │               │ Savings ledger│
            │ verification  │               │ CFO exports   │
            └───────────────┘               └───────────────┘
```

---

## 3. Parallel path — edge measurements (context)

Bill savings verification **cross-checks** against incomer meter data from edge:

```text
connectors-edge ──MQTT measurements──► connectors-cloud ──► stamped-l2
                                              ▲
connectors-bill ──MQTT bill_lines─────────────┘
                                              │
                         L5 reconciles model vs bill lines
```

connectors-bill does **not** talk to connectors-edge directly. Shared context is **org_id + plant_id + bill_month** in L2.

---

## 4. Shared contracts package

All L1 publishers share:

| Artifact | Location | Consumers |
|----------|----------|-----------|
| JSON Schemas | `external/contracts/schemas/` | edge, bill, cloud, l2 |
| MQTT topics | `external/contracts/TOPICS.md` | all L1 + cloud |
| CHANGELOG | `external/contracts/CHANGELOG.md` | CI backward-compat |

**Schema ownership:** canonical in **connectors-edge**; bill and cloud **copy/submodule** sync. Bill repo must run contract CI before merge.

When bill schema evolves (e.g. new `line_type`), update:

1. `external/contracts/schemas/bill-line.json`
2. `CHANGELOG.md`
3. Golden fixtures + dedupe tests
4. connectors-cloud contract CI (downstream)

---

## 5. MQTT broker topology

Per [ADR-002](../decisions/ADR-002-build-all-aws-networking.md):

| Environment | Broker | Publishers | Subscribers |
|-------------|--------|------------|-----------|
| Local dev | Mosquitto in compose | edge (sim), **bill**, test scripts | **connectors-cloud ingest** |
| Pilot/prod | EMQX or Mosquitto on AWS | edge agents, **bill service** | **connectors-cloud ingest** |

**ACL:** bill service credentials may **publish only** to `stamped/v1/{org}/{plant}/bills` and `.../events` for its plants — mirror edge ACL pattern in [TOPICS.md](../contracts/TOPICS.md).

---

## 6. Event types bill repo should emit

On `stamped/v1/{org}/{plant}/events` (schema: `event.json`):

| event_type | When |
|------------|------|
| `bill_received` | Document uploaded and queued |
| `bill_extracted` | OCR/template parse complete |
| `bill_validated` | Recompute pass; lines approved for publish |
| `bill_rejected` | Unrecoverable parse failure |
| `bill_published` | All lines MQTT-published |

These events flow through the same cloud ingest path as edge health events.

---

## 7. Authentication & tenancy boundaries

| Boundary | Mechanism |
|----------|-----------|
| User → bill web | Cognito / Auth0 / custom JWT with `org_id`, `plant_id` claims |
| Bill api → S3 | IAM role; keys scoped per org prefix `s3://bills/{org_id}/{plant_id}/` |
| Bill publish → MQTT | Per-plant client cert or username mapped to org/plant |
| Cloud → L2 | `X-Service-Key` (not bill's concern) |

**Multi-plant users:** UI plant switcher; all API calls scoped by selected plant.

---

## 8. What each repo expects from connectors-bill

| Downstream repo | Expectation |
|-----------------|-------------|
| **connectors-cloud** | Valid `bill-line.json` on bills topic; QoS 1; stable dedupe keys |
| **stamped-l2** | Envelope with `record_type=bill_line`; idempotent inbox |
| **stamped-l5** | Validated lines only; `extraction.validated=true` for M&V |
| **stamped-l6** | Optional: REST webhook `bill.published` for dashboard refresh (P1) |

---

## 9. Deployment independence

| Property | connectors-bill | connectors-cloud |
|----------|-----------------|------------------|
| Release cadence | Weekly+ (templates, UI) | Stable ingest path |
| Failure domain | OCR/LLM/vendor APIs | MQTT/outbox lag |
| Scale driver | Human review queue depth | MQTT message rate |
| Customer-facing | **Yes — primary UI** | No — backend only |

Bill service outages **must not** stop edge measurements — separate repos enforce this.

---

## 10. Bootstrap checklist for new workspace agent

- [ ] Read [connectors-bill-spec.md](./connectors-bill-spec.md)
- [ ] Read [connectors-cloud-downstream-context.md](./connectors-cloud-downstream-context.md)
- [ ] Add **stamped-platform** submodule at `external/` ([SUBMODULE.md](../SUBMODULE.md))
- [ ] Clone connectors-cloud for E2E compose reference
- [ ] Implement dedupe tests first (proves contract alignment)
- [ ] MQTT publish fixture → cloud inbox before building UI polish

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-11 | Initial ecosystem map for bill repo handoff |
