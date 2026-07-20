# Layer interfaces — L1 ↔ L2 ↔ L3 boundaries

> **Authority:** Implementation contract for cross-repo agents.  
> **Supersedes:** Stub in connectors-bill `docs/architecture/layer-interfaces.md` for L2 work.  
> **Related:** [ADR-008](../decisions/ADR-008-layer-repo-topology-and-interfaces.md) · [ADR-009](../decisions/ADR-009-stamped-l2-repo-charter.md)

---

## 1. Patterns (all boundaries)

| Pattern | Application |
| --- | --- |
| Transactional outbox | connectors-cloud writes `l1_outbox`, relay publishes to L2 |
| Idempotent consumer | `ingest.l1_processed_inbox` PRIMARY KEY on `dedupe_key` |
| Contract-first JSON Schema | BACKWARD compatibility CI on `external/contracts/` |
| At-least-once delivery | Relay retries; L2 dedupe makes retries safe |
| Observability | `correlation_id`, `traceparent` on every envelope |

---

## 2. L1 publishers → connectors-cloud (MQTT)

### 2.1 Topics

| Record | Topic | Schema | Publishers |
| --- | --- | --- | --- |
| Measurement | `stamped/v1/{org_id}/{plant_id}/measurements` | `measurement.json` | connectors-edge, connectors-bill |
| Measurement (backfill) | `stamped/v1/{org_id}/{plant_id}/measurements/backfill` | `measurement.json` | connectors-edge |
| Event | `stamped/v1/{org_id}/{plant_id}/events` | `event.json` | connectors-edge, connectors-bill |
| ProductionRecord | `stamped/v1/{org_id}/{plant_id}/production` | `production-record.json` | connectors-edge, connectors-bill |
| BillLine | `stamped/v1/{org_id}/{plant_id}/bills` | `bill-line.json` | connectors-bill |
| Health | `stamped/v1/{org_id}/{plant_id}/health` | `event.json` | connectors-edge |

QoS **1**. Retain **false** for high-volume streams.

Full table: [TOPICS.md](../contracts/TOPICS.md).

### 2.2 Business dedupe keys (L1 → cloud → L2)

Computed by connectors-cloud; **reused unchanged** on envelope and L2 inbox.

| record_type | Dedupe formula | Golden hash |
| --- | --- | --- |
| `measurement` | `sha256(plant_id \| source_tag \| ts_utc \| granularity \| metric.type)` | See [dedupe_golden.json](../contracts/fixtures/dedupe_golden.json) |
| `event` | `sha256(plant_id \| event_type \| event_id)` | idem |
| `production_record` | `sha256(plant_id \| batch_id \| window_start)` | idem |
| `bill_line` | `sha256(plant_id \| bill_id \| line_type \| bill_month)` | idem |

Field paths for measurement: `lineage.source_tag`, `metric.type` from `measurement.json`.

### 2.3 L1 publish rules

- connectors-edge: quality gates applied before uplink; never silent repair
- connectors-bill: only `extraction.validated=true` BillLines to MQTT
- **P0 canonical:** one record per MQTT message (not batch array at L2)

---

## 3. connectors-cloud → stamped-l2 (HTTP)

### 3.1 Transport

| Phase | Transport | Endpoint |
| --- | --- | --- |
| **P0** | HTTP POST | `/v1/ingest/records` |
| P1+ | Redpanda topic `stamped.l1.records.v1` (optional parallel) | Same envelope schema |

Env: `L2_INGEST_URL` on cloud relay.

### 3.2 Envelope schema

`StampedRecordEnvelope` — [stamped-record-envelope.json](../contracts/schemas/stamped-record-envelope.json)

Required fields: `schema_version`, `envelope_id`, `record_type`, `org_id`, `plant_id`, `dedupe_key`, `ingest_batch_id`, `ingested_at`, `late`, `correlation_id`, `payload`.

Optional: `traceparent`.

### 3.3 L2 consumer idempotency

```sql
-- ingest.l1_processed_inbox
PRIMARY KEY (dedupe_key)
```

| POST result | HTTP | Meaning |
| --- | --- | --- |
| New record | 201 | `{inserted: true, dedupe_key}` |
| Duplicate | 200 | `{inserted: false, dedupe_key}` |

Store writes occur **only** when inbox insert succeeds (new dedupe_key).

Full API: [stamped-l2-l1-consumer-contract.md](../handoff/stamped-l2-l1-consumer-contract.md).

### 3.4 Authentication

`X-Service-Key` header — shared secret between cloud relay and L2 ingest.

---

## 4. stamped-l2 internal routing

| record_type | L2 destination |
| --- | --- |
| `measurement` | `telemetry.measurement` |
| `event` | `telemetry.event` |
| `production_record` | `commercial.production_record` |
| `bill_line` | `commercial.bill_line` (+ `commercial.bill` header) |

Late flag: preserve on envelope; do not reject.

---

## 5. stamped-l2 → L3+ (query API)

### 5.1 Rules

- L3, L4, L5, L6 **must not** connect to L2 database
- All reads via stamped-l2 HTTP query API
- L5 ledger **appends** via dedicated endpoint (P1) — not general L3 access

### 5.2 P0 query endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness |
| GET | `/v1/plants/{plant_id}/measurements` | Windowed telemetry |
| GET | `/v1/plants/{plant_id}/bills/{bill_id}/lines` | Bill reconciliation |
| GET | `/v1/plants/{plant_id}/assets` | Minimal graph |

Auth: `X-Service-Key` + `X-Org-Id`.

Full sketch: [stamped-l2-query-api-sketch.md](../handoff/stamped-l2-query-api-sketch.md).

### 5.3 Latency budgets (p95)

| Query | Budget |
| --- | --- |
| 30-day 15-min profile, one asset | < 200 ms |
| MD forensic 1-min window ±30 min | < 300 ms |
| Graph traverse ≤4 hops | < 1 s |
| Bill lines by id | < 200 ms |

---

## 6. L3 → L4 → L5 → L6 (downstream, reference)

| Boundary | Transport | Payload |
| --- | --- | --- |
| L2 → L3 | Query API | Aggregates, graph refs, baselines |
| L3 → L4 | Outbox / bus | `Finding` |
| L4 → L5 | Outbox | `Prescription` |
| L5 → L2 | HTTP | Query + baseline lock + **idempotent** `POST /v1/ledger/entries` ([ADR-019](../decisions/ADR-019-l5-runtime-and-consistency.md)) |
| L5 → L6 | Outbox + query | `WorkflowEvent`, `LedgerEntry` refs |

L5 runtime SSOT: [L5-closure-and-verification.md](../technical/layers/L5-closure-and-verification.md). L2 repo does **not** implement L4/L5/L6 app boundaries — documented for context only.

---

## 7. Non-negotiable rules

1. No shared database writes across repos
2. No cross-repo SQL joins
3. Schema changes additive within major version
4. Dedupe keys stable — business fields, not broker message IDs
5. `late: true` envelopes accepted; quality flags preserved

---

## 8. Compatibility CI

Each repo runs contract checks on PR:

```bash
./scripts/contract-check.sh
```

Breaking schema changes require major version bump + migration plan.

---

## Changelog

| Date | Change |
| --- | --- |
| 2026-07-12 | Full L1↔L2↔L3 boundary doc for stamped-l2 handoff |
