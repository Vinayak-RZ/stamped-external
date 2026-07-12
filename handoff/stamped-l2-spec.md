# stamped-l2 — Repo charter (Universal Repository)

> **What it is:** Stamped **L2** — the Universal Repository: six data stores (time-series, graph, commercial, features, baselines, M&V ledger) in one Postgres+TimescaleDB database, plus L1 HTTP ingest consumer and internal query API for L3–L6.  
> **What it is not:** L1 MQTT ingest, edge agents, bill OCR, intelligence engines, prescriptions, or customer dashboard.  
> **Primary interface:** `POST /v1/ingest/records` (from connectors-cloud relay) + read-only query API for downstream layers.

**GitHub (target):** `Vinayak-RZ/stamped-l2`  
**Deploy target (P0):** Docker Compose locally · ECS Fargate + shared RDS `ap-south-1`

---

## TL;DR

- **One repo, one database** (`stamped_l2`) — six logical Postgres schemas, not six repos
- **RDS PostgreSQL 16 + TimescaleDB**, shared `db.t4g.small` with connectors-cloud (separate DB)
- **HTTP L1 ingest** — idempotent inbox on `dedupe_key`; demux to store routers
- **P0 stores:** telemetry (measurement hypertable + caggs), commercial (bill_line), ingest inbox; Phase B adds graph, baselines, ledger, RLS
- **Query API (thin P0):** measurements profile, bill lines, health
- **Cost ceiling:** ~₹3–4.5k/month L2 slice on AWS
- **Exit:** connectors-cloud relay replaces mock-l2; first evidence pointer resolves end-to-end

---

## 1. Vision

### 1.1 What it is

`stamped-l2` is the **evidence layer** for Stamped Energy. Every verified bill reduction flows through L2 twice: raw evidence in (telemetry, bills, production), verified outcomes out (ledger). L3–L6 read via query API; only L2 ingest writes.

Primary research spec: [L2-universal-repository.md](../technical/layers/L2-universal-repository.md).

### 1.2 What it is not

| Out of scope | Owner repo |
| --- | --- |
| MQTT subscribe, jsonschema at L1 boundary, outbox | `connectors-cloud` |
| Modbus, tag mapping, edge buffer | `connectors-edge` |
| DISCOM PDF OCR, review UI, MQTT publish | `connectors-bill` |
| Findings, SEC engines, MD detection | `stamped-l3` |
| Prescription agent | `stamped-l4` |
| Workflow, M&V verification UI | `stamped-l5` |
| Customer dashboard, exports | `stamped-l6` |
| Direct L1 → L2 table writes from any other repo | **Forbidden** (ADR-008) |

### 1.3 Who it is for

- **Platform engineers** operating L2 ingest and query APIs
- **L3–L6 repo agents** consuming documented read contracts
- **SRE/on-call** debugging ingest lag, dedupe rejects, or query latency

### 1.4 Success criteria (L2 P0 complete)

- connectors-cloud relay POST succeeds; `l1_processed_inbox` dedupes correctly
- Measurement and bill_line golden fixtures round-trip to queryable rows
- RLS probe suite green (zero cross-tenant leakage)
- Joint E2E with connectors-cloud green 3× consecutive runs
- First evidence pointer resolves: incomer tag window ↔ bill_line anchor

---

## 2. Architecture

### 2.1 Ecosystem placement

```mermaid
flowchart LR
  subgraph L1 [L1]
    Edge[connectors-edge]
    Bill[connectors-bill]
    Cloud[connectors-cloud]
  end
  L2[stamped-l2]
  L3[stamped-l3]

  Edge -->|MQTT| Cloud
  Bill -->|MQTT| Cloud
  Cloud -->|HTTP envelope| L2
  L2 -->|Query API| L3
```

See [stamped-l2-ecosystem-integration.md](./stamped-l2-ecosystem-integration.md) for full eight-repo map.

### 2.2 Internal packages

```mermaid
flowchart TB
  subgraph ingest_svc [packages/ingest]
    HTTP[FastAPI POST /v1/ingest/records]
    Inbox[l1_processed_inbox]
    Router[Record demux routers]
  end
  subgraph query_svc [packages/query-api]
    QAPI[GET read endpoints]
  end
  PG[(stamped_l2 Postgres+Timescale)]

  CloudRelay[connectors-cloud relay] --> HTTP
  HTTP --> Inbox --> Router
  Router --> PG
  QAPI --> PG
  L3Consumer[stamped-l3] --> QAPI
```

| Package | Process | Responsibility |
| --- | --- | --- |
| **ingest** | `python -m ingest.main` | L1 consumer: validate envelope, dedupe, route payload to stores |
| **query-api** | `python -m query_api.main` | Internal read API for L3/L4/L6 — no direct DB access from other repos |
| **migrate** | SQL migrations / alembic | Schema DDL, RLS policies, Timescale hypertables |
| **jobs** | cron / scheduled (P1) | Cagg refresh, SEC feature batch, ledger hash verifier |

**P0 cost mode:** ingest + query-api colocated in one Fargate task. Split when ingest lag >2 min.

### 2.3 Six stores (schemas)

| Schema | Store | P0 minimum |
| --- | --- | --- |
| `ingest` | Idempotency | `l1_processed_inbox` |
| `telemetry` | Time-series | `measurement` hypertable, 15min cagg |
| `graph` | Energy topology | `asset` (incomer seed) |
| `commercial` | Tariffs + bills | `bill`, `bill_line`, JVVNL `tariff_version` seed |
| `features` | Derived metrics | Cagg reads only; tables P1 |
| `baselines` | M&V reference | `baseline` table + lock trigger stub |
| `ledger` | Verified savings | `mv_ledger` append-only |

DDL authority: [stamped-l2-database-schema.md](./stamped-l2-database-schema.md).

---

## 3. Project structure

```text
stamped-l2/
├── external/                 # COPY FROM HANDOFF — specs, ADRs, contracts
├── packages/
│   ├── ingest/
│   ├── query-api/
│   ├── migrate/
│   └── jobs/                 # P1
├── mocks/
│   └── envelope-fixtures/    # Golden StampedRecordEnvelope JSON
├── deploy/
│   ├── docker-compose.l2.yml
│   └── terraform/
├── scripts/
│   ├── e2e-l1-ingest.sh
│   └── contract-check.sh
├── docs/architecture/
│   └── layer-interfaces.md   # Copy from external/architecture/layer-interfaces-l2.md
└── AGENTS.md                 # From stamped-l2-agent-onboarding.md
```

---

## 4. Configuration (P0)

| Variable | Required | Default (local) | Purpose |
| --- | --- | --- | --- |
| `L2_DATABASE_URL` | Yes | `postgresql://postgres:pass@localhost:5433/stamped_l2` | Postgres+Timescale |
| `L2_INGEST_SERVICE_KEY` | Yes (prod) | `dev-key` | Validates connectors-cloud relay |
| `L2_INGEST_PORT` | No | `8090` | Match mock-l2 port for drop-in E2E |
| `L2_QUERY_PORT` | No | `8091` | Query API (same task P0) |

AWS sizing: [stamped-l2-aws-deployment.md](./stamped-l2-aws-deployment.md).

---

## 5. Build phases

### Phase A (weeks 1–4)

| Deliverable | Exit |
| --- | --- |
| docker-compose + Timescale enabled | `psql` + `\dx timescaledb` |
| `ingest.l1_processed_inbox` migration | Golden dedupe insert once |
| POST `/v1/ingest/records` | 201/200 parity with mock-l2 |
| Demux: measurement, bill_line | Fixtures round-trip |
| `telemetry.measurement` + 15min cagg | 30-day profile query works |
| Minimal query API | GET measurements, bill lines |

### Phase B (weeks 5–8)

| Deliverable | Exit |
| --- | --- |
| `graph.asset` incomer seed | FK from measurement.asset_id |
| JVVNL tariff_version seed | Bill recompute test ±0.5% |
| `baselines.baseline` + lock trigger | UPDATE on locked row fails |
| `ledger.mv_ledger` immutability | REVOKE + trigger tests |
| RLS on all tenant tables | Cross-org probe returns 0 rows |
| Joint E2E with connectors-cloud | 3× green |

Full step list: [stamped-l2-build-order.md](./stamped-l2-build-order.md).

---

## 6. Testing

```bash
# Migrations + unit
cd packages/migrate && ./apply.sh
cd packages/ingest && pytest tests/unit tests/contract -q

# Dedupe golden (must match connectors-cloud)
pytest packages/ingest/tests/test_dedupe_golden.py

# Local stack
docker compose -f deploy/docker-compose.l2.yml up --build --wait
./scripts/e2e-l1-ingest.sh

# With connectors-cloud (joint)
# cloud: L2_INGEST_URL=http://stamped-l2:8090/v1/ingest/records
./scripts/e2e-l1-ingest.sh --with-cloud
```

---

## 7. Documentation map

| Doc | Path |
| --- | --- |
| Charter (this file) | `external/handoff/stamped-l2-spec.md` |
| Ecosystem wiring | `external/handoff/stamped-l2-ecosystem-integration.md` |
| L1 consumer API | `external/handoff/stamped-l2-l1-consumer-contract.md` |
| Database schema | `external/handoff/stamped-l2-database-schema.md` |
| Query API | `external/handoff/stamped-l2-query-api-sketch.md` |
| AWS deployment | `external/handoff/stamped-l2-aws-deployment.md` |
| Build order | `external/handoff/stamped-l2-build-order.md` |
| Upstream L1 context | `external/handoff/stamped-l2-upstream-context.md` |
| Layer interfaces | `external/architecture/layer-interfaces-l2.md` |
| ADR | `external/decisions/ADR-009-stamped-l2-repo-charter.md` |

---

## Changelog

| Date | Change |
| --- | --- |
| 2026-07-12 | Initial repo charter for stamped-l2 bootstrap |
