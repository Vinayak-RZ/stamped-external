# stamped-l2 — Upstream L1 context (what L1 already guarantees)

> **Purpose:** Tell the stamped-l2 agent what **connectors-edge**, **connectors-cloud**, and **connectors-bill** already do — so L2 does not reimplement L1 concerns.  
> **Sources:** Connector READMEs (2026-07-11), handoff docs in this folder.

---

## 1. Division of responsibility

| Concern | Owner | L2 assumes |
| --- | --- | --- |
| MQTT subscribe | connectors-cloud | Receives HTTP envelopes only |
| JSON Schema validation (L1 records) | connectors-cloud | Envelope + payload already validated at L1; L2 re-validates defensively |
| Business dedupe key computation | connectors-cloud | `dedupe_key` on envelope is authoritative |
| Quality gates (stale, range) | connectors-cloud (measurements); edge (pre-uplink) | `quality` flag preserved on measurement |
| Bill ₹ recompute gate | connectors-bill | Only `extraction.validated=true` lines published |
| Outbox + relay retry | connectors-cloud | At-least-once POST to L2 |
| OT protocol drivers | connectors-edge | Not L2's problem |
| DISCOM OCR/templates | connectors-bill | L2 stores parsed `bill_line` rows |

---

## 2. connectors-cloud (L1 cloud) — ready for pilot

**Repo:** `Vinayak-RZ/connectors-cloud`

| Capability | Status |
| --- | --- |
| MQTT topics (6 patterns) | Implemented |
| jsonschema fail-closed | Implemented → `l1_dlq` |
| Transactional outbox | `l1_outbox` + `l1_ingress_audit` |
| Relay sidecar | POST to `L2_INGEST_URL` default `/v1/ingest/records` |
| Mock L2 | `mocks/stamped-l2/` — **stamped-l2 must reach parity** |
| Bill MQTT path | E2E tested |
| Postgres | `connectors_cloud` DB — **not** L2 tables |

**Environment:**

| Var | Default | L2 action |
| --- | --- | --- |
| `L2_INGEST_URL` | `http://localhost:8090/v1/ingest/records` | Run L2 ingest on `:8090` for drop-in |
| Relay poll interval | ~8s | Expect ingest within ~10s in E2E |

**What cloud sends:** `StampedRecordEnvelope` — never raw MQTT body. See [connectors-cloud-downstream-context.md](./connectors-cloud-downstream-context.md).

**What cloud does NOT do:**

- Write Timescale / L2 tables
- Store bill PDFs
- Run OCR

---

## 3. connectors-edge (L1 plant)

**Repo:** `Vinayak-RZ/connectors-edge` (GitHub: Connectors)

| Capability | Transport |
| --- | --- |
| edge-agent | MQTT publish measurements, events, production, health |
| tag-mapping-api | HTTPS — mapping OTA, not L2 |
| connectors-ingest | **Valid in `local` mode** — MQTT → local stack; **deprecated for `cloud` mode** once L2 E2E green |

**MQTT topics published:**

- `stamped/v1/{org}/{plant}/measurements`
- `stamped/v1/{org}/{plant}/measurements/backfill`
- `stamped/v1/{org}/{plant}/events`
- `stamped/v1/{org}/{plant}/production`
- `stamped/v1/{org}/{plant}/health`

**Production path:** edge → MQTT → connectors-cloud → HTTP → stamped-l2.

**`local` mode lab path:** edge → MQTT → `connectors-ingest` → local Timescale **or** full compose stack per [deployment-profiles.md](./deployment-profiles.md). Valid when `STAMPED_DEPLOYMENT_MODE=local`.

**Deprecated for `cloud` mode:** `connectors-ingest` writing `measurements_raw` directly. Disable when L2 joint E2E passes in `cloud` deployments.

**L2 implication:** Measurements arrive with `asset_id`, `metric.type`, `ts_utc`, `quality`, `lineage.source_tag` per `measurement.json`. Seed `graph.asset` incomer rows matching pilot plant asset IDs.

---

## 4. connectors-bill (L1 bill)

**Repo:** `Vinayak-RZ/connectors-bill`

| Capability | Transport |
| --- | --- |
| PWA upload + camera | HTTPS → api |
| Extract + validate | Internal — recompute gate before publish |
| MQTT publish | `BillLine` on `stamped/v1/{org}/{plant}/bills` |
| Lifecycle events | `stamped/v1/{org}/{plant}/events` |

**Publish rule:** Only validated bill lines (`extraction.validated=true`) hit MQTT.

**Dedupe (must match L2 inbox):**

```text
sha256(plant_id | bill_id | line_type | bill_month)
```

Golden: `sha256:2f855d00860753dc937837391d669e5bfd5ff7344f0ea9b788c9584205792dbb`

**Canonical P0:** **One BillLine per MQTT message.** Do not expect batch arrays at L2 unless cloud ingest adds support.

**Optional publishes:** `Measurement`, `ProductionRecord` from document intake — same cloud path as edge.

**What bill does NOT do:**

- Subscribe MQTT
- Write L2 tables
- Call connectors-edge

See [connectors-bill-ecosystem-integration.md](./connectors-bill-ecosystem-integration.md).

---

## 5. Record types L2 must handle (P0 minimum)

| record_type | Typical source | P0 store |
| --- | --- | --- |
| `measurement` | edge, occasionally bill | `telemetry.measurement` |
| `bill_line` | bill | `commercial.bill_line` |
| `event` | edge, bill | `telemetry.event` (Phase B) |
| `production_record` | edge, bill | `commercial.production_record` (Phase B) |

---

## 6. Joint E2E prerequisites

| Step | Repo | Command / check |
| --- | --- | --- |
| 1 | connectors-cloud | `docker compose -f deploy/docker-compose.cloud.yml up` |
| 2 | stamped-l2 | `docker compose -f deploy/docker-compose.l2.yml up` |
| 3 | cloud env | `L2_INGEST_URL=http://stamped-l2:8090/v1/ingest/records` |
| 4 | Publish | MQTT golden `bill_line.valid.json` or cloud HTTP measurement |
| 5 | Assert | Row in `stamped_l2.ingest.l1_processed_inbox` + store table |
| 6 | Query | `GET /v1/plants/.../bills/.../lines` returns line |

---

## 7. Contract CI alignment

Both connectors-cloud and stamped-l2 must run:

```bash
./scripts/contract-check.sh   # jsonschema on external/contracts/
```

Dedupe tests must match [dedupe_golden.json](../contracts/fixtures/dedupe_golden.json) exactly.

---

## 8. What L2 should NOT rebuild

- MQTT client / topic ACLs
- L1 jsonschema validators (copy schemas, validate at boundary for defence in depth)
- Outbox pattern (cloud owns through relay)
- Bill OCR, recompute, review UI
- Edge Modbus, OTA mapping

---

## Changelog

| Date | Change |
| --- | --- |
| 2026-07-12 | Initial upstream context distilled from L1 READMEs |
| 2026-07-12 | ADR-010: connectors-ingest valid in `local` mode only |
