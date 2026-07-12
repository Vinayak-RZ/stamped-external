# stamped-l2 — Query API sketch (L3/L4/L6)

> **Audience:** Agents building `stamped-l3` and implementing `packages/query-api` in stamped-l2.  
> **Rule:** L3+ **never** receive `L2_DATABASE_URL`. All reads go through this API.  
> **P0 scope:** Thin read surface — expand in P1 when first L3 engine ships.

---

## 1. Principles

| Principle | Detail |
| --- | --- |
| Internal only | Not exposed to plant customers — L6 dashboard calls L6 API which may proxy L2 |
| Read-only P0 | No writes except via dedicated ledger append endpoint (P1, owned by L5 path) |
| Tenancy | Every request scoped by `org_id`; reject cross-tenant params |
| Pagination | Cursor-based for time-series; offset OK for small bill line lists |
| Latency budgets | From L2 research §2.2 |

---

## 2. Authentication

| Header | Required | Notes |
| --- | --- | --- |
| `X-Service-Key` | Yes (prod) | Per-consumer keys in SSM (P1); shared dev key locally |
| `X-Org-Id` | Yes | Must match data scope — sets `app.current_org` for RLS |

Future P1: mTLS between ECS services in same VPC.

---

## 3. P0 endpoints

### 3.1 Health

```
GET /health
```

**200:** `{"status":"ok","db":"connected","timescale":"enabled"}`

---

### 3.2 Measurements — windowed profile

```
GET /v1/plants/{plant_id}/measurements
```

| Query param | Required | Description |
| --- | --- | --- |
| `asset_id` | Yes | Graph asset |
| `metric` | Yes | e.g. `active_power_kw`, `apparent_power_kva` |
| `from` | Yes | ISO8601 start |
| `to` | Yes | ISO8601 end |
| `granularity` | No | `raw` (default ≤7d), `15min`, `hour`, `day` |

**200 response:**

```json
{
  "org_id": "org_acme",
  "plant_id": "plant_ghaziabad_1",
  "asset_id": "incomer_1",
  "metric": "active_power_kw",
  "granularity": "15min",
  "points": [
    {"ts": "2026-07-01T00:00:00Z", "value": 412.5, "quality": 0}
  ]
}
```

**Latency budget:** p95 < 200 ms for 30-day 15-min profile (synthetic benchmark).

**Implementation P0:** Query `telemetry.agg_15min` for `granularity=15min`; raw hypertable for short windows.

---

### 3.3 Bill lines

```
GET /v1/plants/{plant_id}/bills/{bill_id}/lines
```

**200:**

```json
{
  "bill_id": "bill_2025_06",
  "bill_month": "2025-06-01",
  "lines": [
    {
      "line_type": "energy_charge",
      "qty": 125000,
      "rate": 7.30,
      "amount_inr": 912500,
      "dedupe_key": "sha256:..."
    }
  ]
}
```

---

### 3.4 Bill by month (convenience)

```
GET /v1/plants/{plant_id}/bills?bill_month=2025-06
```

Returns latest bill header + line count for M&V reconciliation entry point.

---

### 3.5 Asset list (minimal graph)

```
GET /v1/plants/{plant_id}/assets
```

**200:** List of `asset_id`, `name`, `level`, `asset_class` for incomer + top feeders (P0 seed).

---

## 4. P1 endpoints (document, do not build in P0)

| Endpoint | Consumer | Latency budget |
| --- | --- | --- |
| `GET /v1/plants/{plant_id}/graph/traverse?from={asset_id}&edge_types=...` | L3 attribution | < 1 s |
| `GET /v1/baselines/{baseline_id}` | L3, L5 | < 500 ms |
| `GET /v1/tariffs/active?plant_id=...` | L4 impact calc | < 500 ms |
| `GET /v1/features/sec?plant_id=...&window=...` | L3 SEC engine | < 500 ms |
| `POST /v1/ledger/entries` | L5 append | transactional |

---

## 5. Error envelope

```json
{
  "success": false,
  "error": {
    "code": "not_found",
    "message": "No bill bill_2025_06 for plant plant_test",
    "details": {}
  }
}
```

| HTTP | code | When |
| --- | --- | --- |
| 400 | `invalid_params` | Missing/invalid query params |
| 401 | `unauthorized` | Bad service key |
| 403 | `forbidden` | org_id mismatch |
| 404 | `not_found` | Plant/bill/asset unknown |
| 500 | `internal_error` | DB error |

---

## 6. L3 engine data contracts (reference)

| L3 engine | L2 reads needed |
| --- | --- |
| MD/demand | 1-min incomer kVA raw + 15-min cagg, last 90 days |
| SEC | agg_15min × production_record join (P1 feature job) |
| Attribution | Graph traverse + co-windowed telemetry |
| Tariff misclassification | bill_line vs tariff_version in force |

Full L3 spec: [L3-intelligence-core.md](../technical/layers/L3-intelligence-core.md).

---

## 7. L4 agent tools (P1)

Narrow HTTP tools — no direct SQL:

- `query_timeseries(asset_id, metric, window)`
- `get_baseline(baseline_id)`
- `traverse_graph(from_asset, edge_types, max_depth=4)`
- `calculate_impact(prescription_draft)` — reads tariff_version server-side

---

## 8. Deployment note (P0 cost mode)

Query API runs **in same Fargate task** as ingest on port 8091 (or shared port with route prefix). Split when query load causes ingest p95 lag >2 min.

---

## Changelog

| Date | Change |
| --- | --- |
| 2026-07-12 | Initial query API sketch for stamped-l2 P0 |
