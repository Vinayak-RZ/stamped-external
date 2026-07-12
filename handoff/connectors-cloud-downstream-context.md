# connectors-cloud — context for connectors-bill builders

> **Repo:** [Vinayak-RZ/connectors-cloud](https://github.com/Vinayak-RZ/connectors-cloud)  
> **Status (2026-07-11):** L1 cloud ingest **complete for pilot prep** (minus AWS deploy). Bill MQTT path **implemented and E2E-tested**.

This document tells the **connectors-bill** team exactly what the downstream consumer already does, so you publish the right payloads without re-reading the whole cloud codebase.

---

## 1. What connectors-cloud does for you

| Step | Behavior |
|------|----------|
| Subscribe | `stamped/v1/+/+/bills` (and `events`, `measurements`, etc.) |
| Parse | JSON UTF-8 |
| Validate | `jsonschema` against `bill-line.json` |
| Dedupe | `sha256(plant_id \| bill_id \| line_type \| bill_month)` |
| Envelope | Wrap in `StampedRecordEnvelope` + auto `traceparent` |
| Persist | `l1_outbox` + `l1_ingress_audit` (single transaction) |
| Relay | Sidecar POST to `stamped-l2` `/v1/ingest/records` |
| Duplicate | Same dedupe key → accepted but not re-inserted (`inserted: false` at HTTP; MQTT still ACKs) |
| Invalid | → `l1_dlq` + metric; never silently repaired |

**You do not need** to call connectors-cloud HTTP API for bill lines. **MQTT only** for P0.

---

## 2. MQTT publish contract

### Topic

```
stamped/v1/{org_id}/{plant_id}/bills
```

Example:

```
stamped/v1/org_acme/plant_ghaziabad_1/bills
```

### Payload

Single JSON object per message matching [bill-line.json](../contracts/schemas/bill-line.json).

Reference fixture: [bill_line.valid.json](../contracts/fixtures/bill_line.valid.json)

### QoS

**1** (at-least-once). Cloud dedupe makes retries safe.

### Batch option

E2E in cloud publishes **one message per line**. If you batch NDJSON, confirm cloud ingest supports it first — **default to one line per message for P0**.

---

## 3. Dedupe — must match exactly

Implementation reference (connectors-cloud): `packages/ingest/ingest/dedupe/keys.py`

```python
def dedupe_key_bill_line(payload):
    return sha256("|".join([
        payload["plant_id"],
        payload["bill_id"],
        payload["line_type"],
        payload["bill_month"],
    ]))
```

Golden test:

| Fixture | Expected dedupe_key |
|---------|---------------------|
| [bill_line.valid.json](../contracts/fixtures/bill_line.valid.json) | `sha256:2f855d00860753dc937837391d669e5bfd5ff7344f0ea9b788c9584205792dbb` |

**Bill repo CI must assert the same hash** before first MQTT integration test.

---

## 4. Validation failures you will see

| Error | Cause | Fix on bill side |
|-------|-------|------------------|
| `schema_invalid` | Missing required field, wrong enum | Fix JSON before publish |
| `envelope_invalid` | Internal cloud bug | Report to cloud team |
| Duplicate (no new outbox row) | Re-publish same line | Expected on retry — OK |

Cloud **never** fixes your payload. Bill repo owns extraction quality.

---

## 5. Local E2E verification (no bill repo needed yet)

Prove downstream works with manual publish:

```bash
# Start cloud stack (from connectors-cloud repo)
cd deploy && docker compose -f docker-compose.cloud.yml up --build --wait

# Publish golden fixture
mosquitto_pub -h 127.0.0.1 -p 1883 -q 1 \
  -t "stamped/v1/org_test/plant_test/bills" \
  -m "$(cat external/contracts/fixtures/bill_line.valid.json)"

# Wait ~10s for relay, then:
docker compose exec -T postgres psql -U postgres -d connectors_cloud -c \
  "SELECT record_type, dedupe_key FROM l1_processed_inbox;"
```

Or run cloud's full E2E (includes bill_line via MQTT):

```bash
./scripts/e2e-cloud-ingest.sh   # requires mosquitto-clients
```

---

## 6. Envelope shape (informational)

You publish **raw BillLine**. Cloud wraps:

```json
{
  "schema_version": "1.0.0",
  "envelope_id": "uuid",
  "record_type": "bill_line",
  "org_id": "...",
  "plant_id": "...",
  "dedupe_key": "sha256:...",
  "ingested_at": "ISO8601",
  "late": false,
  "correlation_id": "uuid",
  "traceparent": "00-...",
  "payload": { /* your BillLine */ }
}
```

stamped-l2 consumer sees the envelope, not your raw MQTT body.

---

## 7. Events topic (optional but recommended)

Publish bill lifecycle on:

```
stamped/v1/{org_id}/{plant_id}/events
```

Schema: [event.json](../contracts/schemas/event.json). Cloud maps to `record_type=event`.

Use for: `bill_received`, `bill_validated`, `bill_published` — helps ops/debugging in `l1_ingress_audit`.

---

## 8. What cloud does NOT do

- Store original PDFs (your S3)
- Run OCR or recompute (your extract/validate packages)
- Show review UI to customers (your web package)
- Parse DISCOM templates

---

## 9. Phase 2 joint E2E (future)

When both repos are on a developer machine:

```bash
# connectors-cloud running (compose)
# connectors-bill running (compose)
# bill: upload PDF → extract → publish MQTT
# assert: l1_processed_inbox count increases
```

Cloud repo documents coordination in `docs/plans/connectors-cloud-phase2-checklist.md` — bill section is your deliverable list.

---

## 10. Contacts / references in cloud repo

| Doc | Path in connectors-cloud |
|-----|--------------------------|
| Usage guide | `docs/how-to-use-connectors-cloud.md` |
| MQTT topic table | `external/contracts/TOPICS.md` |
| Handoff spec | `docs/handoff/connectors-cloud-spec.md` |
| Dedupe ADR | `docs/decisions/dedupe-formula-v1.md` |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-11 | Initial downstream context after cloud pilot gate work |
