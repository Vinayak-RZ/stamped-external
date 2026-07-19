<!-- SNAPSHOT: mirrored from connectors-cloud/README.md on 2026-07-19. Canonical README lives in the consumer repo — re-sync when that README changes. -->

> **Snapshot** of [`connectors-cloud`](https://github.com/Vinayak-RZ/connectors-cloud) root README (copied 2026-07-19).
> Canonical source: consumer repo `README.md`. Do not edit here for product truth — update the consumer repo, then re-copy.

---

# connectors-cloud — L1 cloud ingest for Stamped Energy

> **What it is:** The **L1 cloud** portion of Connect & Normalise — a two-service Python stack that ingests plant MQTT/HTTP streams, validates JSON Schema contracts, deduplicates, writes a transactional outbox, and relays `StampedRecordEnvelope` records to **stamped-l2**.  
> **What it is not:** Edge protocol drivers, tag-mapping UI, DISCOM bill PDF parsing, or L2–L6 intelligence. Those live in sibling repos (`connectors-edge`, `connectors-bill`, `stamped-l2`…`stamped-l6`).  
> **Primary interface:** MQTT QoS 1 subscriber + **3 HTTP routes** on `packages/ingest`; outbox drain via **`packages/relay`** sidecar.

**Deploy target (P0):** Docker Compose locally · ECS Fargate `ap-south-1` (stub in `deploy/terraform/`) · Postgres 16 for outbox/audit only (not Timescale).

---

**TL;DR**

- Subscribes to **6 MQTT topic patterns** under `stamped/v1/{org}/{plant}/…` (measurements, backfill, events, production, health, bills).
- Validates **4 canonical record types** at the boundary: `measurement`, `event`, `production_record`, `bill_line`.
- Fail-closed **jsonschema** validation — invalid payloads go to `l1_dlq`, never silently repaired.
- Stable **business dedupe keys** (`sha256:…`) per [layer-interfaces.md §2.2](docs/architecture/layer-interfaces.md).
- **Transactional outbox** — `l1_ingress_audit` + `l1_outbox` in one Postgres transaction; no direct L2 table writes.
- **Relay sidecar** drains outbox with `FOR UPDATE SKIP LOCKED` → HTTP `POST` to stamped-l2.
- **Quality gates v1:** stale/late flag, `active_power_kw` range sanity, clock-unsynced passthrough.
- **3 ingest HTTP routes** only — not 16 (those belong to `tag-mapping-api` in edge).
- Contract CI on **9 JSON schemas** in `external/contracts/schemas/`.
- **26 automated tests** (25 ingest + 1 relay) with ~71% coverage on ingest core.
- Mock L2 consumer in `mocks/stamped-l2/` for full-stack E2E without stamped-l2 deployed.

---

## Table of contents

1. [Vision](#1-vision)
2. [Architecture](#2-architecture)
3. [Quickstart](#3-quickstart)
4. [Configuration](#4-configuration)
5. [Project structure](#5-project-structure)
6. [HTTP API (ingest)](#6-http-api-ingest)
7. [MQTT ingress](#7-mqtt-ingress)
8. [Data model](#8-data-model)
9. [L1→L2 boundary](#9-l1l2-boundary)
10. [Testing](#10-testing)
11. [Deployment & CI](#11-deployment--ci)
12. [Cookbook](#12-cookbook)
13. [Documentation map](#13-documentation-map)
14. [Roadmap & changelog](#14-roadmap--changelog)
15. [FAQ & glossary](#15-faq--glossary)

---

## 1. Vision

### 1.1 What it is

`connectors-cloud` is the **cloud half of L1** in Stamped's eight-repo layer topology. It sits between plant publishers (`connectors-edge`, future `connectors-bill`) and the universal repository (`stamped-l2`).

Its job ends at the **L1→L2 boundary**: every accepted record becomes a `StampedRecordEnvelope` in `l1_outbox`, then the relay publishes to L2 over HTTP (P0).

### 1.2 What it is not

| Out of scope | Owner repo |
|--------------|------------|
| Modbus, OPC UA, edge buffer, OTA | `connectors-edge` |
| Tag mapping CRUD, harvest, mapping UI | `connectors-edge` |
| DISCOM PDF → BillLine (AI/templates) | `connectors-bill` (separate cloud repo) |
| Timescale hypertables, graph, baselines | `stamped-l2` |
| Intelligence, prescriptions, dashboard | `stamped-l3` … `stamped-l6` |
| Direct `measurements_raw` writes | Lab shortcut only — **rejected in production** |

### 1.3 Who it is for

- **Platform engineers** operating L1 cloud ingest and outbox relay.
- **Layer repo agents** implementing stamped-l2 consumer against the same envelope contract.
- **SRE/on-call** debugging ingest lag, schema rejects, or outbox depth.

### 1.4 Success criteria (L1 cloud complete)

- All plant MQTT topics (except `cmd/config`) ingested and validated.
- Outbox → L2 HTTP relay operational with p95 lag < 60s under pilot load.
- Contract CI green; three consecutive E2E passes (see [hardening log](docs/plans/connectors-cloud-hardening-log.md)).

---

## 2. Architecture

### 2.1 Ecosystem placement

```mermaid
flowchart LR
  subgraph L1 [L1 Connect and normalise]
    Edge[connectors-edge]
    Bill[connectors-bill]
    Cloud[connectors-cloud]
  end
  L2[stamped-l2]
  Edge -->|MQTT QoS1| Cloud
  Bill -->|MQTT bills| Cloud
  Cloud -->|HTTP StampedRecordEnvelope| L2
```

### 2.2 Internal services (this repo)

```mermaid
flowchart TB
  subgraph ingest_svc [packages/ingest]
    MQTT[MQTT client]
    HTTP[FastAPI]
    Val[jsonschema validator]
    Acc[AcceptService]
  end
  subgraph relay_svc [packages/relay]
    W[RelayWorker]
    L2C[L2 HTTP client]
  end
  PG[(Postgres)]
  Broker[Mosquitto]
  L2API[stamped-l2 or mock-l2]

  Broker --> MQTT
  HTTP --> Acc
  MQTT --> Val --> Acc
  Acc --> PG
  W -->|SKIP LOCKED| PG
  W --> L2C --> L2API
```

| Service | Package | Process | Responsibility |
|---------|---------|---------|----------------|
| **Ingest** | `packages/ingest` | `python -m ingest.main` | Subscribe MQTT, HTTP backfill, validate, dedupe, write outbox |
| **Relay** | `packages/relay` | `python -m relay.main` | Poll outbox, POST to L2, DLQ on max retries |
| **Mock L2** | `mocks/stamped-l2` | dev/E2E only | Minimal `POST /v1/ingest/records` + inbox dedupe |

**Bulkhead (ADR):** Relay runs as a **separate sidecar** — relay failures or L2 slowness do not stop MQTT subscription in ingest.

### 2.3 Accept path (single transaction)

```mermaid
sequenceDiagram
  participant Src as MQTT or HTTP
  participant Ing as AcceptService
  participant PG as Postgres
  Src->>Ing: JSON payload
  Ing->>Ing: jsonschema validate
  Ing->>Ing: quality gates + dedupe key
  Ing->>Ing: build StampedRecordEnvelope
  Ing->>PG: BEGIN audit + outbox INSERT
  Ing->>PG: COMMIT
  Ing-->>Src: ACK / 201 or 200
  Note over Ing,PG: Schema fail → DLQ + audit reject, no outbox row
```

Entry point: [`packages/ingest/ingest/accept.py`](packages/ingest/ingest/accept.py)

---

## 3. Quickstart

### 3.1 Prerequisites

- **Docker** + Docker Compose v2 (for full stack)
- **Python 3.12+** (for local tests without Docker)
- **Git** — initialize the platform submodule before build or test:

```bash
git submodule update --init --recursive
test -f external/VERSION || { echo "Run: git submodule update --init"; exit 1; }
```

Platform contracts and ADRs live in [`stamped-external`](https://github.com/vinayak-rz/stamped-external) at `external/` (ADR-011). Edit platform files only in that repo.

- **Git** (optional: clone [cursor-config-coding](https://github.com/Vinayak-RZ/cursor-config-coding) for agent rules)

### 3.2 Run full stack (Docker)

```bash
cd deploy
docker compose -f docker-compose.cloud.yml up --build
```

| Service | Port | URL |
|---------|------|-----|
| Ingest HTTP | 8081 | http://localhost:8081 |
| Mock L2 | 8090 | http://localhost:8090 |
| Postgres | 5432 | `postgresql://postgres:pass@localhost:5432/connectors_cloud` |
| Mosquitto | 1883 | `mqtt://localhost:1883` |

### 3.3 Smoke test — HTTP measurement

```bash
curl -sS http://localhost:8081/health

curl -sS -X POST http://localhost:8081/v1/measurements \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d @packages/ingest/tests/fixtures/measurement.valid.json
```

Expected: HTTP **201** with `"inserted": true`. Repeat → **200** with `"inserted": false` (idempotent dedupe).

After ~8s, relay drains outbox → mock L2 `l1_processed_inbox` receives the envelope.

### 3.4 Run tests locally (no Docker)

```bash
cd packages/ingest && pip install -e ".[dev]"
pytest tests/unit tests/contract -q

cd ../relay && pip install -e ".[dev]"
pytest tests/unit -q
```

### 3.5 Cursor agent setup (one-time)

```bash
./scripts/setup-cursor-config.sh
```

Links `.cursor` → [cursor-config-coding](https://github.com/Vinayak-RZ/cursor-config-coding) (ponytail, backend-architecture skills, MCP). Reload Cursor after setup. Project-specific notes: [AGENTS.md](AGENTS.md).

---

## 4. Configuration

### 4.0 Deployment modes (ADR-010)

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `STAMPED_DEPLOYMENT_MODE` | `local` \| `local-dashboard` \| `cloud` | `local` | Selects compose profile and egress policy |
| `SECRET_BACKEND` | `env` \| `file` \| `ssm` | `env` | Secret resolution (`ssm` only when mode is `cloud`) |

Copy [`.env.example`](.env.example) for a full template. Profiles live under [`deploy/profiles/`](deploy/profiles/).

### 4.1 Ingest (`packages/ingest`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `STAMPED_DEPLOYMENT_MODE` | No | `local` | See §4.0 |
| `SECRET_BACKEND` | No | `env` | See §4.0 |
| `DATABASE_URL` | Yes (prod) | `postgresql://postgres:pass@localhost:5432/connectors_cloud` | Postgres for audit + outbox |
| `MQTT_BROKER` | Yes (prod) | `localhost` | Plant MQTT broker hostname |
| `MQTT_PORT` | No | `1883` | MQTT port |
| `HTTP_INGEST_PORT` | No | `8081` | FastAPI listen port |
| `INGEST_API_KEY` | Recommended | `""` (open) | `X-API-Key` for `POST /v1/measurements` |
| `APP_ENV` | No | `dev` | Set `prod` to require `INGEST_API_KEY` at startup |
| `SCHEMA_DIR` | No | `{repo}/external/contracts/schemas` | JSON Schema directory |
| `LATE_THRESHOLD_S` | No | `300` | Seconds after which measurement flagged `late` |
| Metrics | No | `:9090` | Prometheus via `/metrics` mount |

Source: [`packages/ingest/ingest/config.py`](packages/ingest/ingest/config.py)

### 4.2 Relay (`packages/relay`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `STAMPED_DEPLOYMENT_MODE` | No | `local` | See §4.0 |
| `SECRET_BACKEND` | No | `env` | See §4.0 |
| `DATABASE_URL` | Yes | same as ingest | Shared Postgres |
| `L2_INGEST_URL` | Yes (prod) | `http://localhost:8090/v1/ingest/records` | stamped-l2 ingest endpoint |
| `L2_SERVICE_KEY` | Yes (prod) | `test-service-key` | `X-Service-Key` header to L2 |
| `APP_ENV` | No | `dev` | Set `prod` to require `L2_SERVICE_KEY` at startup |
| `RELAY_POLL_MS` | No | `500` | Outbox poll interval |
| `RELAY_WORKER_ID` | No | `relay-1` | Lock owner label |
| `RELAY_MAX_ATTEMPTS` | No | `10` | Attempts before DLQ |
| `RELAY_BATCH_SIZE` | No | `100` | Rows per poll batch |

Source: [`packages/relay/relay/config.py`](packages/relay/relay/config.py)

---

## 5. Project structure

```text
connectors-cloud/
├── AGENTS.md                          # L1 cloud agent onboarding
├── README.md                          # This file
├── external/
│   ├── contracts/schemas/             # 9 JSON schemas (L1 + envelope)
│   ├── decisions/                     # ADR-007, ADR-008, …
│   └── technical/                     # L1–L6 specs (reference)
├── packages/
│   ├── ingest/                        # Deployable: MQTT + HTTP → outbox
│   │   ├── ingest/
│   │   │   ├── main.py                # FastAPI + MQTT lifecycle
│   │   │   ├── accept.py              # Transactional accept path
│   │   │   ├── mqtt/                  # client.py, router.py
│   │   │   ├── http/routes.py         # 3 routes
│   │   │   ├── validation/            # jsonschema registry
│   │   │   ├── dedupe/keys.py         # sha256 dedupe formulas
│   │   │   ├── envelope/builder.py    # StampedRecordEnvelope
│   │   │   ├── quality/gates.py       # stale, range
│   │   │   └── persistence/db.py      # migrations + pool
│   │   └── tests/                     # unit, contract, integration
│   └── relay/                         # Deployable: outbox → L2 HTTP
│       └── relay/worker.py            # SKIP LOCKED loop
├── mocks/stamped-l2/                  # Dev L2 consumer
├── deploy/
│   ├── docker-compose.cloud.yml       # 5 services
│   └── terraform/                     # ECS stub (ADR-002)
├── scripts/
│   ├── setup-cursor-config.sh
│   ├── e2e-cloud-ingest.sh
│   ├── repo-scan.sh
│   ├── hardening-loop.sh
│   └── contract-check.sh
└── docs/
    ├── handoff/connectors-cloud-spec.md
    ├── architecture/layer-interfaces.md
    └── plans/                         # implementation + hardening logs
```

---

## 6. HTTP API (ingest)

**Total routes: 3** (by design — see handoff spec §5.5).

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | None | Liveness — always 200 if process up |
| `GET` | `/ready` | None | Readiness — DB + MQTT connected |
| `POST` | `/v1/measurements` | `X-API-Key` if `INGEST_API_KEY` set | Topology F backfill; same pipeline as MQTT |

**Response (`POST /v1/measurements`):**

```json
{ "inserted": true, "dedupe_key": "sha256:…" }
```

- **201** — new outbox row  
- **200** — duplicate (idempotent)  
- **400** — schema/range rejection  
- **401** — invalid API key  

Prometheus metrics: `GET /metrics` (FastAPI mount).

Implementation: [`packages/ingest/ingest/http/routes.py`](packages/ingest/ingest/http/routes.py)

---

## 7. MQTT ingress

### 7.1 Subscriptions (6 patterns)

| Pattern | Record type | Schema |
|---------|-------------|--------|
| `stamped/v1/+/+/measurements` | `measurement` | `measurement.json` |
| `stamped/v1/+/+/measurements/backfill` | `measurement` | `measurement.json` |
| `stamped/v1/+/+/events` | `event` | `event.json` |
| `stamped/v1/+/+/production` | `production_record` | `production-record.json` |
| `stamped/v1/+/+/health` | `event` | `event.json` |
| `stamped/v1/+/+/bills` | `bill_line` | `bill-line.json` |

**Never subscribed:** `stamped/v1/+/+/cmd/config` (edge OTA wake-up only).

Canonical topic doc: [external/contracts/TOPICS.md](external/contracts/TOPICS.md)

### 7.2 Dedupe keys (stable — do not change without major version)

| Record type | Formula |
|-------------|---------|
| Measurement | `sha256(org_id \| plant_id \| source_tag \| ts_utc \| aggregation \| metric.type)` |
| Event | `sha256(plant_id \| event_type \| ts_utc \| source_tag \| seq)` |
| ProductionRecord | `sha256(plant_id \| batch_id \| window.start_utc \| line_id)` |
| BillLine | `sha256(plant_id \| bill_id \| line_type \| bill_month)` |

Implementation: [`packages/ingest/ingest/dedupe/keys.py`](packages/ingest/ingest/dedupe/keys.py)

---

## 8. Data model

Postgres **lightweight** — outbox pattern only. No Timescale.

| Table | Writer | Purpose |
|-------|--------|---------|
| `l1_ingress_audit` | ingest | Every receive attempt (accepted, duplicate, rejected) |
| `l1_outbox` | ingest | `StampedRecordEnvelope` JSON pending relay |
| `l1_dlq` | ingest + relay | Schema failures + max-retry publish failures |

Migrations run at ingest startup via [`packages/ingest/ingest/persistence/db.py`](packages/ingest/ingest/persistence/db.py) (`run_migrations`).

**Rule:** This repo never writes L2 tables (`measurements_raw`, etc.).

---

## 9. L1→L2 boundary

Every accepted record is wrapped:

```json
{
  "schema_version": "1.0.0",
  "envelope_id": "uuid",
  "record_type": "measurement",
  "org_id": "…",
  "plant_id": "…",
  "dedupe_key": "sha256:…",
  "ingest_batch_id": "uuid",
  "ingested_at": "2026-07-10T12:00:00Z",
  "late": false,
  "correlation_id": "uuid",
  "payload": { }
}
```

| Phase | Transport | Endpoint |
|-------|-----------|----------|
| **P0 (now)** | HTTP POST | `{L2_INGEST_URL}` default `/v1/ingest/records` |
| P1 (future) | Redpanda | topic `stamped.l1.records.v1` |

L2 consumer idempotency: `l1_processed_inbox` with `dedupe_key` PRIMARY KEY — see [layer-interfaces.md §3.3](docs/architecture/layer-interfaces.md).

---

## 10. Testing

### 10.1 Commands

```bash
# Ingest — unit + contract (CI)
cd packages/ingest
pytest tests/unit tests/contract -q --cov=ingest --cov-report=term-missing

# Ingest — integration (requires Docker)
pytest tests/integration -m integration -q

# Relay
cd packages/relay
pytest tests/unit -q

# Contracts (repo root)
./scripts/contract-check.sh

# Full hardening iteration
./scripts/hardening-loop.sh 1
```

### 10.2 Coverage (current)

| Package | Tests | Coverage |
|---------|-------|----------|
| ingest | 25 | ~71% on core modules |
| relay | 1 | L2 client HTTP mock |

Golden fixtures: [`packages/ingest/tests/fixtures/`](packages/ingest/tests/fixtures/)

### 10.3 CI workflows

| Workflow | Trigger path | Steps |
|----------|--------------|-------|
| [ingest.yml](.github/workflows/ingest.yml) | `packages/ingest/**` | ruff → pytest |
| [relay.yml](.github/workflows/relay.yml) | `packages/relay/**` | ruff → pytest |
| [contracts.yml](.github/workflows/contracts.yml) | `external/contracts/**` | jsonschema lint |

---

## 11. Deployment & CI

### 11.1 Three deployment modes

Per [ADR-010](external/decisions/ADR-010-deployment-profiles-and-portability.md):

| Mode | Compose profile | Orchestration | L2 target |
|------|-----------------|---------------|-----------|
| `local` | [`deploy/profiles/local.yml`](deploy/profiles/local.yml) | Docker Compose (air-gap production path) | stamped-l2-ingest or mock-l2 |
| `local-dashboard` | [`deploy/profiles/local-dashboard.yml`](deploy/profiles/local-dashboard.yml) | Master compose in stamped-l2 repo | + stamped-l6 UI |
| `cloud` | [`deploy/profiles/cloud.yml`](deploy/profiles/cloud.yml) (reference) | ECS Fargate + RDS | stamped-l2 on AWS |

```bash
# Preferred local / air-gap path
docker compose -f deploy/profiles/local.yml up -d --build --wait

# Backward-compatible dev alias (includes local profile)
docker compose -f deploy/docker-compose.cloud.yml up -d --build --wait
```

**5 services** in the local profile: `postgres`, `mosquitto`, `ingest` (:8081), `relay`, `mock-l2` (:8090).

### 11.2 Cloud production (P1 Terraform)

Per [ADR-002](external/decisions/ADR-002-build-all-aws-networking.md):

- **ECS Fargate** `ap-south-1` — separate tasks for ingest and relay  
- **RDS Postgres** — lightweight (not Timescale)  
- **Mosquitto** on EC2 — plant MQTT ingress  
- **mTLS or `X-Service-Key`** between relay → stamped-l2  
- **`SECRET_BACKEND=ssm`** at task boot (no boto3 in request hot path)

Terraform stub: [`deploy/terraform/`](deploy/terraform/)

### 11.3 Egress and validation

- Egress inventory: [`docs/architecture/egress-inventory.md`](docs/architecture/egress-inventory.md)
- CI gate: `./scripts/egress-check.sh`
- Env validation: `./scripts/validate-env.sh`

### 11.4 E2E scripts

```bash
./scripts/e2e-local-profile.sh    # deploy/profiles/local.yml
./scripts/e2e-cloud-ingest.sh     # alias compose (same stack)
```

Requires Docker. Publishes measurement, asserts insert + idempotent duplicate, waits for relay drain.

---

## 12. Cookbook

### 12.1 Post a measurement via HTTP

```bash
export INGEST_URL=http://localhost:8081
export API_KEY=test-key

curl -X POST "$INGEST_URL/v1/measurements" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "schema_version": "1.0.0",
    "org_id": "org_demo",
    "plant_id": "plant_demo",
    "metric": {"type": "active_power_kw", "unit": "kW"},
    "ts_utc": "2026-07-09T12:00:00Z",
    "ts_source": "poller",
    "value": 142.5,
    "quality": "good",
    "aggregation": "instant",
    "lineage": {
      "source_system": "modbus-1",
      "source_tag": "incomer.kw",
      "connector_id": "modbus-1",
      "ingest_ts": "2026-07-09T12:00:01Z"
    },
    "seq": 1
  }'
```

### 12.2 Publish via MQTT (mosquitto_pub)

```bash
mosquitto_pub -h localhost -t "stamped/v1/org_demo/plant_demo/measurements" \
  -m @packages/ingest/tests/fixtures/measurement.valid.json
```

### 12.3 Check outbox depth

```sql
SELECT count(*) FROM l1_outbox WHERE published_at IS NULL;
```

### 12.4 Inspect DLQ

```sql
SELECT id, error_code, error_detail, first_seen_at FROM l1_dlq ORDER BY id DESC LIMIT 10;
```

### 12.5 Run repo boundary scan

```bash
./scripts/repo-scan.sh
```

Fails if `measurements_raw`, MQTT in relay, or silent `except: pass` appear in production paths.

---

## 13. Documentation map

| Document | Purpose |
|----------|---------|
| [AGENTS.md](AGENTS.md) | Cursor agent onboarding for this repo |
| [docs/handoff/connectors-cloud-spec.md](docs/handoff/connectors-cloud-spec.md) | L1 cloud charter + copy manifest |
| [docs/how-to-use-connectors-cloud.md](docs/how-to-use-connectors-cloud.md) | Developer + operator usage guide |
| [docs/architecture/layer-interfaces.md](docs/architecture/layer-interfaces.md) | Cross-repo boundary authority |
| [docs/plans/connectors-cloud-implementation-plan.md](docs/plans/connectors-cloud-implementation-plan.md) | Build plan + hardening loop |
| [docs/plans/connectors-cloud-hardening-log.md](docs/plans/connectors-cloud-hardening-log.md) | Iteration pass log |
| [external/decisions/ADR-007-connectors-cloud-repo-charter.md](external/decisions/ADR-007-connectors-cloud-repo-charter.md) | Repo charter |
| [packages/ingest/README.md](packages/ingest/README.md) | Ingest runbook (DLQ, alerts) |

**Sibling repos:** [connectors-edge](https://github.com/Vinayak-RZ/connectors-edge) · `connectors-bill` (future) · `stamped-l2` (future)

---

## 14. Roadmap & changelog

### 14.1 Build phases

| Phase | Theme | Status |
|-------|-------|--------|
| 0 | Handoff docs + contracts | Done |
| 1 | Ingest + relay + mock L2 + tests | Done (v0.1.0) |
| 2 | stamped-l2 real consumer + Path B E2E | Planned |
| 3 | ECS Fargate production deploy | Planned |
| P1 | Redpanda relay transport | Planned |

### 14.2 Recent changelog

| Date | Change |
|------|--------|
| 2026-07-11 | Comprehensive README; cursor-config-coding setup script |
| 2026-07-11 | CI ruff lint fixes |
| 2026-07-10 | L1 cloud ingest + relay sidecar; contracts 0.4.0 |
| 2026-07-10 | Initial handoff bootstrap |

Full contract history: [external/contracts/CHANGELOG.md](external/contracts/CHANGELOG.md)

---

## 15. FAQ & glossary

### FAQ

**Why two services (ingest + relay)?**  
Bulkhead isolation — relay backoff or L2 outages must not block MQTT subscription. See ADR-007 trade-off B.

**Why doesn’t bill PDF parsing live here?**  
`connectors-bill` is a separate repo (AI/templates/review). This repo only **consumes** `BillLine` on MQTT once published.

**Can I write directly to Timescale?**  
No in production. Lab MVP in edge did this; production path is outbox → stamped-l2 only.

**What if `INGEST_API_KEY` is empty?**  
HTTP ingest accepts requests without auth (dev only). Set a key in production.

### Glossary

| Term | Meaning |
|------|---------|
| **L1** | Connect & Normalise — canonical record ingress |
| **StampedRecordEnvelope** | L1→L2 wrapper schema (`stamped-record-envelope.json`) |
| **Outbox** | `l1_outbox` — transactional publish queue |
| **Dedupe key** | Stable `sha256:…` business idempotency key |
| **Topology F** | File-sync plants — HTTP backfill without edge hardware |
| **Path B** | Lab E2E: edge → cloud → L2 with real plant data |

---

## License & contact

Part of **Stamped Energy** internal platform. See org repos under [Vinayak-RZ](https://github.com/Vinayak-RZ) for related layers.
