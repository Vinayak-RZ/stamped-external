# MQTT topic layout (v1)

Draft — aligns with [ADR-001](../decisions/ADR-001-l1-repo-split-and-boundaries.md) and [ADR-002](../decisions/ADR-002-build-all-aws-networking.md).

**P0 broker:** self-hosted Mosquitto on AWS EC2 (`ap-south-1`), TLS via ACM or Let's Encrypt on instance.

## Conventions

- Prefix: `stamped/v1/`
- Tenant: `{org_id}/{plant_id}/`
- Payload: JSON, UTF-8, validated against `external/contracts/schemas/*.json`
- QoS: **1** for measurements, events, production, bills
- Retain: **false** for high-volume streams; **true** only for last-will / health if needed

## Topics

| Topic | Publisher | Payload schema | Notes |
| --- | --- | --- | --- |
| `stamped/v1/{org_id}/{plant_id}/measurements` | edge-agent | `measurement.json` | High volume; edge batches if needed |
| `stamped/v1/{org_id}/{plant_id}/measurements/backfill` | edge-agent | `measurement.json` | Late data beyond buffer horizon; same schema |
| `stamped/v1/{org_id}/{plant_id}/events` | edge-agent, bill-ingest | `event.json` | Includes connector health, gaps, `bill_received`, `tag_remapped?` |
| `stamped/v1/{org_id}/{plant_id}/production` | edge-agent | `production-record.json` | Lower volume |
| `stamped/v1/{org_id}/{plant_id}/bills` | bill-ingest | `bill-line.json` (array or NDJSON) | One bill → many BillLine records |
| `stamped/v1/{org_id}/{plant_id}/health` | edge-agent | `event.json` | Birth/death/heartbeat; 60s |
| `stamped/v1/{org_id}/{plant_id}/cmd/config` | cloud (tag-mapping-api) | `{"manifest_version":"N"}` | Wake-up only; edge pulls signed manifest via HTTPS |

> **Note:** `v1/{plant_id}/live/` from production-engineering doc is **deprecated**; use `stamped/v1/...` prefix.

## Idempotency

Consumers dedupe using payload fields:

- Measurements: `(plant_id, lineage.source_tag, ts_utc, granularity, metric.type)`
- BillLine: `(plant_id, bill_id, line_type, bill_month, …)` per schema

## Security

- TLS 1.2+ mandatory
- Per-plant client certificates or username/password per broker ACL
- ACL: plant client may **publish only** to its `{org_id}/{plant_id}/*` topics
