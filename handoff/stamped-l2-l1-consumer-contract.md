# stamped-l2 — L1 consumer contract

> **Audience:** Agents implementing `packages/ingest` and connectors-cloud relay integrators.  
> **Authority:** [layer-interfaces-l2.md](../architecture/layer-interfaces-l2.md) §2–3  
> **Reference impl:** connectors-cloud `mocks/stamped-l2/` (must reach parity before prod cutover)

---

## 1. Endpoint

| Method | Path | Caller |
| --- | --- | --- |
| `POST` | `/v1/ingest/records` | connectors-cloud `packages/relay` |
| `GET` | `/health` | Load balancer, ECS, compose |

**Base URL (P0):** Set via connectors-cloud env `L2_INGEST_URL` — default `http://localhost:8090/v1/ingest/records`.

---

## 2. Authentication

| Header | Required | Value |
| --- | --- | --- |
| `Content-Type` | Yes | `application/json` |
| `X-Service-Key` | Yes (prod) | Shared secret — `L2_INGEST_SERVICE_KEY` on L2; configured on cloud relay |

Missing or invalid key → **401** `{"error":{"code":"unauthorized"}}`.

Local dev: accept `dev-key` when `L2_ENV=development`.

---

## 3. Request body

Single JSON object: **StampedRecordEnvelope** per [stamped-record-envelope.json](../contracts/schemas/stamped-record-envelope.json).

```json
{
  "schema_version": "1.0.0",
  "envelope_id": "550e8400-e29b-41d4-a716-446655440000",
  "record_type": "measurement",
  "org_id": "org_test",
  "plant_id": "plant_test",
  "dedupe_key": "sha256:adf837f03737541e77415b44eec6fae54f4418a5f0924f894cea36bebb6c15b8",
  "ingest_batch_id": "660e8400-e29b-41d4-a716-446655440001",
  "ingested_at": "2026-07-12T08:00:00Z",
  "late": false,
  "correlation_id": "770e8400-e29b-41d4-a716-446655440002",
  "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
  "payload": { }
}
```

| Field | Validation |
| --- | --- |
| `schema_version` | Must be `"1.0.0"` |
| `record_type` | One of: `measurement`, `event`, `production_record`, `bill_line` |
| `dedupe_key` | Pattern `^sha256:[a-f0-9]{64}$` |
| `payload` | Must validate against schema for `record_type` |

---

## 4. Response

### Success — new record

**HTTP 201**

```json
{
  "inserted": true,
  "dedupe_key": "sha256:..."
}
```

### Success — duplicate (idempotent)

**HTTP 200**

```json
{
  "inserted": false,
  "dedupe_key": "sha256:..."
}
```

Duplicates must **not** re-insert store rows. Inbox conflict is sufficient to return 200.

### Errors

| Status | Code | When |
| --- | --- | --- |
| 400 | `envelope_invalid` | Envelope schema fail |
| 400 | `payload_invalid` | Payload schema fail for record_type |
| 401 | `unauthorized` | Bad/missing service key |
| 422 | `routing_error` | Unknown record_type or unmappable payload |
| 500 | `internal_error` | DB unavailable — cloud relay retries |

---

## 5. Idempotency — `l1_processed_inbox`

```sql
CREATE SCHEMA IF NOT EXISTS ingest;

CREATE TABLE ingest.l1_processed_inbox (
  dedupe_key     text PRIMARY KEY,
  envelope_id    uuid NOT NULL,
  record_type    text NOT NULL,
  org_id         text NOT NULL,
  plant_id       text NOT NULL,
  ingested_at    timestamptz NOT NULL,
  processed_at   timestamptz NOT NULL DEFAULT now(),
  correlation_id uuid
);
```

**Algorithm:**

1. Validate envelope JSON Schema
2. Validate `payload` against L1 record schema
3. `INSERT INTO ingest.l1_processed_inbox ... ON CONFLICT (dedupe_key) DO NOTHING RETURNING dedupe_key`
4. If inserted → route to store writer(s) in same transaction
5. If conflict → return 200 `inserted: false` (no store write)

---

## 6. Dedupe keys (must match connectors-cloud)

Golden expected hashes: [dedupe_golden.json](../contracts/fixtures/dedupe_golden.json).

| record_type | Formula | Golden fixture |
| --- | --- | --- |
| `measurement` | `sha256(plant_id \| source_tag \| ts_utc \| granularity \| metric.type)` | `measurement.valid.json` |
| `event` | `sha256(plant_id \| event_type \| event_id)` | `event.valid.json` |
| `production_record` | `sha256(plant_id \| batch_id \| window_start)` | `production_record.valid.json` |
| `bill_line` | `sha256(plant_id \| bill_id \| line_type \| bill_month)` | `bill_line.valid.json` |

**CI requirement:** `packages/ingest/tests/test_dedupe_golden.py` must assert exact hashes from `dedupe_golden.json`.

Implementation reference (connectors-cloud): `packages/ingest/ingest/dedupe/keys.py`.

---

## 7. Demux routing table

After successful inbox insert, route `payload` to store writer:

| record_type | Target schema.table | Notes |
| --- | --- | --- |
| `measurement` | `telemetry.measurement` | Hypertable insert; map quality enum → smallint |
| `event` | `telemetry.event` | P0: optional defer if no SCADA events yet |
| `production_record` | `commercial.production_record` | Phase B |
| `bill_line` | `commercial.bill_line` | Upsert parent `commercial.bill` if needed |

**Transaction boundary:** inbox insert + store write(s) in **one DB transaction**. Rollback on store failure → relay retries (at-least-once safe due to dedupe).

### Field mapping — measurement (P0)

| L1 payload field | L2 column |
| --- | --- |
| `plant_id` | `plant_id` (+ `org_id` from envelope) |
| `asset_id` | `asset_id` — must exist in `graph.asset` or use plant incomer seed |
| `metric.type` | `metric` |
| `ts_utc` | `ts` |
| `value` | `value` |
| `quality` | `quality` (0=good, 1=estimated, 2=bad) |
| `lineage.source_tag` | `source_tag` |
| `lineage.source_system` | `source_system` |

### Field mapping — bill_line (P0)

| L1 payload field | L2 column |
| --- | --- |
| `bill_id` | `bill_id` |
| `bill_month` | `bill_month` |
| `line_type` | `line_type` |
| `qty`, `rate`, `amount_inr` | same |
| `extraction.validated` | must be `true` at L1; L2 rejects `false` with 422 |

---

## 8. Late data

When envelope `late: true`:

- Insert normally — do not reject
- Preserve `quality` flags on measurements
- Timescale caggs handle invalidation on out-of-order timestamps

---

## 9. Bill publish canonical behavior

**P0 canonical:** connectors-cloud publishes **one BillLine per MQTT message**. TOPICS.md mentions array/NDJSON — **do not implement batch array ingest in L2 P0** unless connectors-cloud ingest explicitly adds support. L2 accepts **one envelope per POST** only.

---

## 10. Parity checklist vs mock-l2

Before replacing connectors-cloud `mocks/stamped-l2`:

| Test | Expected |
| --- | --- |
| Valid envelope first POST | 201, `inserted: true` |
| Same dedupe_key POST | 200, `inserted: false` |
| Invalid envelope | 400 |
| Golden bill_line dedupe | Matches `dedupe_golden.json` |
| Relay retry storm (10× same) | Single inbox row |

---

## 11. Observability

| Metric / log field | Purpose |
| --- | --- |
| `correlation_id` | Cross-service trace with cloud audit |
| `traceparent` | OpenTelemetry propagation (P1 export) |
| `record_type`, `org_id`, `plant_id` | Structured log dimensions |
| Counter `l2_ingest_inserted_total` | New records |
| Counter `l2_ingest_duplicate_total` | Dedupe hits |

---

## Changelog

| Date | Change |
| --- | --- |
| 2026-07-12 | Initial L1 consumer contract for stamped-l2 |
