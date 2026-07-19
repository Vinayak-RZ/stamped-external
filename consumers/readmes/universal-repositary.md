<!-- SNAPSHOT: mirrored from universal-repositary/README.md on 2026-07-19. Canonical README lives in the consumer repo — re-sync when that README changes. -->

> **Snapshot** of [`universal-repositary`](https://github.com/Vinayak-RZ/universal-repositary) root README (copied 2026-07-19).
> Canonical source: consumer repo `README.md`. Do not edit here for product truth — update the consumer repo, then re-copy.

---

# Stamped L2 — Universal Repository

> **What it is:** Stamped Energy's **Layer 2 (L2) canonical data store** — time-series telemetry, plant graph, commercial billing context, production features, baselines, and M&V ledger — exposed via HTTP APIs for L3–L6 intelligence layers.  
> **What it is not:** An L1 connector, a customer-facing dashboard (L6), or a platform contract owner (those live in `external/`).  
> **Primary interface:** HTTP ingest + read APIs; internal Next.js ops console on port **8092**.

## L2 Ops Console walkthrough

The internal ops console lives in [`packages/console`](packages/console/) (port **8092** in `local-dashboard` mode). After the local stack is up, run [`scripts/seed-public-plant.sh`](scripts/seed-public-plant.sh) (hybrid `jvvnl-riico` persona) to populate all **eleven** nav pages.

**Full walkthrough video** — [docs/assets/console/walkthrough.mp4](docs/assets/console/walkthrough.mp4) (Overview → Sources → Calibration → Telemetry → Commercial → Production → Graph → Ingest → Baselines → Ledger → Evidence). On GitHub, open the file to play inline in the repo browser.

| Page | Route | Screenshot |
| --- | --- | --- |
| Overview | `/` | ![Overview — KPI cards, demo tour, ingest funnel](docs/assets/console/overview.png) |
| Sources | `/sources` | ![Sources — public-data catalog (I-BLEND, CEEP, MoSPI, JVVNL tariff)](docs/assets/console/sources.png) |
| Calibration | `/calibration` | ![Calibration — CEEP reference vs scaled plant kWh](docs/assets/console/calibration.png) |
| Telemetry | `/telemetry` | ![Telemetry — 15-min active_power_kw with ToD bands](docs/assets/console/telemetry.png) |
| Commercial | `/commercial` | ![Commercial — LP/HT-5 bill lines (JVVNL)](docs/assets/console/commercial.png) |
| Production | `/production` | ![Production — MoSPI IIP-scaled batches](docs/assets/console/production.png) |
| Graph | `/graph` | ![Graph — RIICO asset hierarchy](docs/assets/console/graph.png) |
| Ingest | `/ingest` | ![Ingest — dedupe audit (~9.8k accepted)](docs/assets/console/ingest.png) |
| Baselines | `/baselines` | ![Baselines — draft and locked OLS models](docs/assets/console/baselines.png) |
| Ledger | `/ledger` | ![Ledger — M&V prescriptions and verification](docs/assets/console/ledger.png) |
| Evidence | `/evidence` | ![Evidence — compound ref resolver (telemetry ↔ bill)](docs/assets/console/evidence.png) |

Run locally: [`scripts/demo-walkthrough.sh`](scripts/demo-walkthrough.sh) · [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) · [local-stack operator guide](docs/local-stack-operator-guide.md) · [AGENTS.md](AGENTS.md) (Cursor Cloud caveats).

# Stamped platform — single source of truth

---

**TL;DR**

- **Six Postgres schemas** (`ingest`, `telemetry`, `graph`, `commercial`, `features`, `baselines`, `ledger`) on TimescaleDB — tenant-isolated via RLS
- **17 L2 API routes** across ingest (2), query-api (4), and admin-api (11)
- **Idempotent ingest** on `dedupe_key` — `201` new, `200` duplicate; routes `measurement`, `bill_line`, `event`, `production_record`
- **L1 reference packages** co-located under `l1/` (cloud, bill, edge) for local full-stack demos
- **Platform contracts** in git submodule `external/` — schemas, ADRs, dedupe golden; CI enforces via `contract-check.sh`
- **Three deployment modes** (`local`, `local-dashboard`, `cloud`) — same contracts, different compose profiles ([ADR-010](external/decisions/ADR-010-deployment-profiles-and-portability.md))
- **Demo seed toolkit** (`packages/seed`) — Faker + diurnal load curves; SQL bulk or HTTP replay
- **11 console pages** — Overview, Sources, Calibration, Telemetry, Commercial, Production, Graph, Ingest, Baselines, Ledger, Evidence
- **No AWS SDK in `packages/`** — Terraform stubs only under `deploy/terraform/aws/`
- **7 CI workflows** — contract, unit, smoke/e2e, fuzz nightly, L1 reference, console Playwright
- **Air-gap ready** — Docker Compose local stack; egress inventory enforced for `local` mode

---

## Table of contents

1. [Vision](#1-vision)
2. [Architecture](#2-architecture)
3. [Quickstart](#3-quickstart)
4. [Configuration](#4-configuration)
5. [Project structure](#5-project-structure)
6. [API reference](#6-api-reference)
7. [Data model](#7-data-model)
8. [Demo seed toolkit](#8-demo-seed-toolkit)
9. [Testing](#9-testing)
10. [Deployment](#10-deployment)
11. [Cookbook](#11-cookbook)
12. [Roadmap and changelog](#12-roadmap-and-changelog)
13. [FAQ and glossary](#13-faq-and-glossary)

---

## 1. Vision

### 1.1 What it is

**stamped-l2** is the **Universal Repository** in Stamped Energy's L0–L6 architecture. L1 connectors (edge, cloud, bill) publish `StampedRecordEnvelope` records; L2 validates, deduplicates, and persists them into a multi-schema TimescaleDB database. Downstream layers (L3 prescription, L4 M&V, L5/L6 customer surfaces) **read only through L2 APIs** — never direct database access.

This repository ships:

| Layer | Deliverable |
|-------|-------------|
| **L2 core** | `packages/ingest`, `query-api`, `admin-api`, `migrate`, `l2_common` |
| **L2 ops UI** | `packages/console` — internal dashboard for all six schemas |
| **L1 reference** | `l1/connectors_{cloud,bill,edge}` — copy/sync to private repos when access is available |
| **Deploy** | Docker Compose profiles, Dockerfiles, AWS Terraform stub |
| **Platform mount** | `external/` git submodule → [stamped-external](https://github.com/Vinayak-RZ/stamped-external) |

### 1.2 What it is not

| Out of scope | Where it lives |
|--------------|----------------|
| JSON schemas, MQTT topic contracts, dedupe golden | `external/contracts/` (submodule) |
| Customer-facing L6 dashboard | Separate `stamped-l6` repo (referenced in `local-dashboard` profile) |
| L3/L4 LLM intelligence | Separate layers; L2 has **no LLM dependency** |
| K3s / Harbor fleet orchestration | Deferred P2 — Docker Compose only for local modes |
| Redpanda / MSK messaging | Explicitly deferred per `.specify/constitution.md` |
| Production AWS apply | `deploy/terraform/aws/` is plan-only stub for P0 |

### 1.3 Who it is for

| Audience | Use case |
|----------|----------|
| **Platform engineers** | Extend ingest routers, migrations, query endpoints |
| **Integration engineers** | Wire L1 relays, validate envelope contracts, run E2E scripts |
| **Ops / M&V analysts** | Use L2 Ops Console for ingest audit, evidence resolution, ledger review |
| **Downstream L3–L6 teams** | Consume query-api with `X-Service-Key` + `X-Org-Id` |

### 1.4 Success criteria

- Envelope ingest is idempotent and contract-validated
- RLS enforces `org_id` tenancy on all tenant tables
- `scripts/run-smoke-e2e.sh` passes in CI (smoke + L1 ingest E2E)
- Demo data populates all schemas for console walkthrough
- Contracts invariant across `local`, `local-dashboard`, and `cloud` modes

---

## 2. Architecture

### 2.1 Layer topology

```mermaid
flowchart LR
  subgraph L1[L1_connectors]
    Edge[connectors_edge]
    Cloud[connectors_cloud]
    Bill[connectors_bill]
  end
  subgraph L2[stamped_l2_this_repo]
    Ingest[ingest_8090]
    Query[query_api_8091]
    Admin[admin_api_8093]
  end
  subgraph Store[TimescaleDB]
    DB[(stamped_l2)]
  end
  subgraph L3toL6[L3_L6_downstream]
    Intel[intelligence_layers]
  end
  Edge -->|MQTT| Cloud
  Bill -->|MQTT| Cloud
  Cloud -->|HTTP_envelope| Ingest
  Bill -->|HTTP_optional| Ingest
  Ingest --> DB
  Query --> DB
  Admin --> DB
  Intel -->|read_only| Query
  Console[console_8092] --> Query
  Console --> Admin
```

### 2.2 Ingest lifecycle

```mermaid
sequenceDiagram
  participant L1 as L1_connector
  participant Ing as ingest_8090
  participant Val as jsonschema
  participant Inbox as ingest.l1_processed_inbox
  participant Store as telemetry_commercial_features

  L1->>Ing: POST /v1/ingest/records + X-Service-Key
  Ing->>Val: validate envelope + payload
  alt new dedupe_key
    Ing->>Inbox: INSERT inbox
    Ing->>Store: route_record()
    Ing-->>L1: 201 inserted
  else duplicate
    Ing-->>L1: 200 duplicate
  else rejected
    Ing-->>L1: 4xx + audit row
  end
```

### 2.3 L2 packages

| Package | Path | Port | Role |
|---------|------|------|------|
| **ingest** | `packages/ingest/` | 8090 | POST envelopes; dedupe; route to store tables |
| **query-api** | `packages/query-api/` | 8091 | Read measurements, assets, bill lines for L3–L6 |
| **admin-api** | `packages/admin-api/` | 8093 | Ops: audit, graph, baselines, ledger, evidence |
| **console** | `packages/console/` | 8092 | Next.js 14 internal dashboard |
| **migrate** | `packages/migrate/` | — | SQL migrations via `apply.sh` |
| **l2_common** | `packages/l2_common/` | — | Config, DB connection, RLS `set_config` |
| **seed** | `packages/seed/` | — | Demo data generator (SQL + HTTP modes) |

**Stack:** Python 3.12, FastAPI, uvicorn, psycopg3, jsonschema, Pydantic v2. Console: TypeScript, Tailwind, ECharts.

### 2.4 L1 reference packages

Private L1 repos are not always cloneable in CI. Reference implementations live under `l1/`:

| Package | Path | Role |
|---------|------|------|
| **connectors_cloud** | `l1/connectors_cloud/` | MQTT ingest → Postgres outbox → relay to L2 |
| **connectors_bill** | `l1/connectors_bill/` | Bill PDF → extract → validate → MQTT publish |
| **connectors_edge** | `l1/connectors_edge/` | Go edge-agent: Modbus stub → MQTT QoS1 |
| **l1_common** | `l1/l1_common/` | Shared dedupe helpers, `SECRET_BACKEND` |

### 2.5 Platform submodule (`external/`)

Contracts and ADRs are **read-only** in this repo. Always init the submodule before build or test:

```bash
git submodule update --init --recursive
test -f external/VERSION || { echo "Run: git submodule update --init"; exit 1; }
```

| Path in `external/` | Purpose |
|---------------------|---------|
| `contracts/schemas/` | JSON Schema for envelopes and payloads |
| `contracts/fixtures/` | Canonical test fixtures |
| `decisions/` | ADRs (e.g. ADR-010 deployment modes) |
| `handoff/` | Cross-repo playbooks and L2 spec |
| `scripts/contract-check.sh` | Shared CI validation |

**Authority:** [ADR-011](external/decisions/ADR-011-stamped-platform-submodule-distribution.md) — PR in `stamped-external`, tag, submodule bump in consumers.

---

## 3. Quickstart

### 3.1 Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Git | 2.x+ | Submodule init |
| Docker + Compose | 24+ | Local stack |
| Python | 3.12+ | Services, tests, seed |
| Node.js | 18+ | Console dev/build |
| Go | 1.22+ | Edge agent tests (optional) |
| `psql` | PG16 client | Integration tests, migrate |

### 3.2 Clone

```bash
git clone --recurse-submodules https://github.com/Vinayak-RZ/universal-repositary.git
cd universal-repositary
git submodule update --init --recursive
```

### 3.3 L2-only stack (fastest)

```bash
export L2_INGEST_SERVICE_KEY=dev-local-key
docker compose -f deploy/docker-compose.l2.yml up --build -d
bash packages/migrate/apply.sh
./scripts/seed-demo-data.sh
```

**Verify:**

```bash
curl -sf http://localhost:8090/health
curl -sf http://localhost:8091/health
curl -sf http://localhost:8093/health
open http://localhost:8092   # Ops Console
```

### 3.4 Full L1 + L2 local stack

```bash
export STAMPED_DEPLOYMENT_MODE=local
export L2_INGEST_SERVICE_KEY=dev-local-key
docker compose -f deploy/profiles/local.yml up --build -d
./scripts/seed-demo-data.sh
```

With ops console + admin API (dashboard profile):

```bash
docker compose -f deploy/profiles/local.yml -f deploy/profiles/local-dashboard.yml up --build -d
```

### 3.5 Smoke test (CI-equivalent)

```bash
chmod +x scripts/*.sh packages/migrate/apply.sh
./scripts/run-smoke-e2e.sh
```

Runs: `verify-smoke-prereqs.sh` → `smoke-l2.sh` → `e2e-l1-ingest.sh bill_line` → `e2e-l1-ingest.sh measurement`.

### 3.6 Python dev install

```bash
pip install -e ".[test,seed]"
export L2_DATABASE_URL=postgresql://l2:l2@localhost:5433/stamped_l2
pytest -m "unit or contract" packages/ -q
```

---

## 4. Configuration

### 4.1 L2 environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `L2_DATABASE_URL` | Yes (services) | `postgresql://l2:l2@localhost:5433/stamped_l2` | TimescaleDB connection |
| `L2_INGEST_SERVICE_KEY` | Yes | `dev-local-key` | Shared secret for ingest + read APIs |
| `L2_INGEST_URL` | No | `http://localhost:8090/v1/ingest/records` | Ingest endpoint for relay/seed |
| `L2_QUERY_API_URL` | No | `http://localhost:8091` | Console → query-api |
| `L2_ADMIN_API_URL` | No | `http://localhost:8093` | Console → admin-api |
| `L2_SERVICE_KEY` | No | `dev-local-key` | Console service key header |

Config source: [`packages/l2_common/config.py`](packages/l2_common/config.py).

### 4.2 L1 environment variables

See [`l1/connectors_cloud/.env.example`](l1/connectors_cloud/.env.example) and [`l1/connectors_edge/.env.example`](l1/connectors_edge/.env.example).

| Variable | Example | Used by |
|----------|---------|---------|
| `STAMPED_DEPLOYMENT_MODE` | `local` | Profile selector |
| `MQTT_BROKER_URL` | `mqtt://mosquitto:1883` | Cloud, bill, edge |
| `DATABASE_URL` | `postgresql://cloud:cloud@...` | connectors_cloud |
| `SECRET_BACKEND` | `env` | L1 secrets (`l1_common`) |
| `RELAY_POLL_INTERVAL_SEC` | `8` | Cloud relay worker |
| `ORG_ID` / `PLANT_ID` | `org_test` / `plant_test` | Edge agent, seed defaults |
| `STORAGE_BACKEND` | `minio` | Bill document storage |
| `MINIO_ENDPOINT` | `http://minio:9000` | Bill API |

### 4.3 Deployment mode selector

```bash
export STAMPED_DEPLOYMENT_MODE=local           # air-gap, no dashboard
export STAMPED_DEPLOYMENT_MODE=local-dashboard # air-gap + L2 console + admin-api
export STAMPED_DEPLOYMENT_MODE=cloud           # Stamped AWS (pilots)
```

Profile docs: [`deploy/profiles/ARCHITECTURE.md`](deploy/profiles/ARCHITECTURE.md).

### 4.4 Script-only variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `SKIP_INTEGRATION` | unset | Skip DB integration tests in `full-validation.sh` |
| `SKIP_SMOKE` | unset | Skip Docker smoke in `full-validation.sh` |
| `SIM_INTERVAL_SEC` | `30` | `simulate-ingest.sh` loop interval |
| `SIM_ROUNDS` | `10` | `simulate-ingest.sh` iteration count |

---

## 5. Project structure

```text
universal-repositary/
├── packages/                    # L2 application code (7 packages)
│   ├── ingest/                  # POST /v1/ingest/records
│   ├── query-api/               # Read API for downstream layers
│   ├── admin-api/               # Internal ops API
│   ├── console/                 # Next.js ops dashboard
│   ├── migrate/sql/             # 8 SQL files (7 migrations + tariff seed)
│   ├── l2_common/               # Shared config + db_conn
│   └── seed/                    # Demo data toolkit
├── l1/                          # L1 reference packages
│   ├── connectors_cloud/
│   ├── connectors_bill/
│   ├── connectors_edge/
│   └── l1_common/
├── deploy/
│   ├── docker-compose.l2.yml    # L2-only compose (5 services)
│   ├── profiles/                # local, local-dashboard, cloud
│   ├── Dockerfile.*             # Per-service images
│   └── terraform/aws/           # Plan-only AWS stub
├── external/                    # Git submodule (stamped-external)
├── mocks/                       # Envelope fixtures + dedupe golden
├── scripts/                     # 16 operational scripts
├── docs/                        # Repo-specific runbooks + research
├── .github/workflows/           # 7 CI workflows
├── .specify/                    # Spec Kit artifacts (L2 P0 spec)
├── AGENTS.md                    # Cursor agent workflow
└── pyproject.toml               # Python 3.12 project + pytest config
```

**Related docs (not duplicated here):**

| Document | Path |
|----------|------|
| Project overview | [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) |
| Implementation plan | [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) |
| Decisions log | [DECISIONS.md](DECISIONS.md) |
| Operator guide | [docs/local-stack-operator-guide.md](docs/local-stack-operator-guide.md) |
| Console design system | [packages/console/DESIGN.md](packages/console/DESIGN.md) |
| L2 handoff spec | [external/handoff/stamped-l2-spec.md](external/handoff/stamped-l2-spec.md) |

---

## 6. API reference

**Authentication:**

| API | Headers |
|-----|---------|
| ingest | `X-Service-Key` |
| query-api, admin-api | `X-Service-Key` + `X-Org-Id` |

**Total L2 routes: 17**

### 6.1 Ingest (`packages/ingest`) — port 8090

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| POST | `/v1/ingest/records` | Accept `StampedRecordEnvelope`; idempotent on `dedupe_key` |

**Supported `record_type` values:** `measurement`, `bill_line`, `event`, `production_record`

**Responses:** `201` inserted · `200` duplicate · `4xx` validation/audit rejection

Router: [`packages/ingest/routers/store.py`](packages/ingest/routers/store.py)

### 6.2 Query API (`packages/query-api`) — port 8091

| Method | Path | Query params |
|--------|------|--------------|
| GET | `/health` | — |
| GET | `/v1/plants/{plant_id}/measurements` | `asset_id`, `metric`, `from`, `to`, `granularity` |
| GET | `/v1/plants/{plant_id}/bills/{bill_id}/lines` | — |
| GET | `/v1/plants/{plant_id}/assets` | — |

Default demo IDs: `org_test`, `plant_test`, `incomer_1`, `active_power_kw`.

### 6.3 Admin API (`packages/admin-api`) — port 8093

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| GET | `/admin/v1/overview` | Measurement/bill counts, ingest funnel (7d) |
| GET | `/admin/v1/ingest/audit` | Audit trail (`limit`, `status`) |
| GET | `/admin/v1/ingest/funnel` | Ingest funnel summary |
| GET | `/admin/v1/ingest/inbox` | Processed inbox (`limit`) |
| GET | `/admin/v1/evidence/resolve` | Resolve evidence refs (`ref`) |
| GET | `/admin/v1/graph` | Asset hierarchy (`plant_id`) |
| GET | `/admin/v1/baselines` | Baseline list (`limit`) |
| GET | `/admin/v1/baselines/{baseline_id}/lineage` | Baseline lineage |
| GET | `/admin/v1/ledger` | M&V ledger stream (`limit`) |

### 6.4 Console UI (`packages/console`) — port 8092

| Route | Page | Data source |
|-------|------|-------------|
| `/` | Overview | admin `/admin/v1/overview` |
| `/telemetry` | Telemetry Explorer | query `/v1/plants/.../measurements` |
| `/commercial` | Commercial & Bills | query bill lines |
| `/graph` | Plant Topology | admin `/admin/v1/graph` |
| `/ingest` | Ingest & Dedupe | admin `/admin/v1/ingest/audit` |
| `/baselines` | Baseline Registry | admin `/admin/v1/baselines` |
| `/ledger` | M&V Ledger | admin `/admin/v1/ledger` |
| `/evidence` | Evidence Resolver | admin `/admin/v1/evidence/resolve` |

Internal health: `GET /api/health`

Design tokens: [`packages/console/DESIGN.md`](packages/console/DESIGN.md) — Stamped coral `#f75440`, forest sidebar `#051f13`.

---

## 7. Data model

### 7.1 Schemas overview

**7 Postgres schemas** on database `stamped_l2`:

| Schema | Purpose |
|--------|---------|
| `ingest` | Dedupe inbox + ingest audit |
| `telemetry` | Measurements, events, 15min continuous aggregate |
| `graph` | Asset hierarchy |
| `commercial` | Tariffs, bills, bill lines |
| `features` | Production records (batch/window) |
| `baselines` | M&V baseline registry (lock trigger) |
| `ledger` | Append-only M&V ledger (immutability trigger) |

### 7.2 Tables and views

| Schema | Object | Type |
|--------|--------|------|
| `ingest` | `l1_processed_inbox` | table |
| `ingest` | `l1_ingest_audit` | table |
| `telemetry` | `measurement` | Timescale hypertable |
| `telemetry` | `event` | Timescale hypertable |
| `telemetry` | `agg_15min` | continuous aggregate |
| `graph` | `asset` | table |
| `commercial` | `tariff_version` | table |
| `commercial` | `bill` | table |
| `commercial` | `bill_line` | table |
| `features` | `production_record` | table |
| `baselines` | `baseline` | table |
| `ledger` | `mv_ledger` | table (append-only) |

**Migrations:** [`packages/migrate/sql/`](packages/migrate/sql/) — applied by [`packages/migrate/apply.sh`](packages/migrate/apply.sh).

**Extensions:** `timescaledb`, `pgcrypto`

### 7.3 Tenancy and security

- **RLS** on 11 tenant tables — policy: `org_id = current_setting('app.current_org', true)`
- App sets org via `SELECT set_config('app.current_org', %s, true)` in [`packages/l2_common/db.py`](packages/l2_common/db.py)
- **Roles:** `l2_app` (read/write), `l2_readonly` (read)
- **Ledger immutability:** UPDATE/DELETE rejected by trigger
- **Baseline lock:** locked baselines cannot be edited (only retired)

### 7.4 L1 cloud database (`connectors_cloud`)

Separate Postgres DB for cloud connector:

| Table | Purpose |
|-------|---------|
| `l1_processed_inbox` | Dedupe inbox |
| `l1_ingress_audit` | Ingress audit |
| `l1_outbox` | Relay outbox (JSONB envelopes) |
| `l1_dlq` | Dead letter queue |

Migration: [`l1/connectors_cloud/migrate/001_cloud.sql`](l1/connectors_cloud/migrate/001_cloud.sql)

### 7.5 Dedupe keys

Computed in [`packages/ingest/dedupe/keys.py`](packages/ingest/dedupe/keys.py); golden expectations in [`mocks/dedupe-canonical.json`](mocks/dedupe-canonical.json).

| Record type | Key material |
|-------------|--------------|
| `measurement` | plant_id, source_tag, ts_utc, granularity, metric type |
| `bill_line` | plant_id, bill_id, line_type, bill_month |
| `event` | plant_id, event_type, event_id |
| `production_record` | plant_id, batch_id, window.start_utc |

---

## 8. Demo seed toolkit

**Package:** [`packages/seed/`](packages/seed/)  
**Entry:** `python3 -m seed` (requires `pip install -e ".[seed]"` or `pip install Faker`)

### 8.1 What it seeds

| Schema | Data |
|--------|------|
| `telemetry` | I-BLEND Academic curve (scaled) or synthetic diurnal `active_power_kw` on `incomer_1` |
| `commercial` | JVVNL HT-I bill lines from metered aggregates (`jvvnl-riico` persona) |
| `graph` | RIICO Jaipur HT hierarchy (`jvvnl-riico`) or generic plant template |
| `baselines` | 1 draft + 1 locked baseline |
| `ledger` | 5 M&V entries linked to locked baseline |
| `ingest` | L1 HTTP audit trail (`hybrid` mode) or sample SQL audit rows |
| `features` | Production batch scaled by MoSPI IIP fixture |
| L1 `l1_outbox` | Optional pending envelopes (`--l1-cloud`) |

**Personas:** `--persona synthetic` (default tests) or `--persona jvvnl-riico` (public-data virtual RIICO plant). See [`packages/seed/DATA_PROVENANCE.md`](packages/seed/DATA_PROVENANCE.md).

**Generator approach:** I-BLEND 1-min CSV → 15-min resample + calibration; JVVNL tariff math for bills; Faker for synthetic persona. Reproducible via `--seed 42`.

### 8.2 Public data demo (recommended)

**5-minute walkthrough:** `./scripts/demo-walkthrough.sh` then follow [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md).

```bash
docker compose -f deploy/docker-compose.l2.yml up -d
./scripts/seed-public-plant.sh   # hybrid: SQL aux + L1 HTTP ingest + cagg refresh
# Console: http://localhost:8092
./scripts/simulate-ingest.sh     # ongoing L1 ingest (live window)
```

I-BLEND full CSV is downloaded to `packages/seed/sources/raw/iblend/` (gitignored). CI uses `sources/fixtures/iblend/acad_build_7d.csv`.

### 8.3 CLI reference

```bash
PYTHONPATH=packages:packages/ingest python3 -m seed --dry-run --persona jvvnl-riico
PYTHONPATH=packages:packages/ingest python3 -m seed --apply --mode hybrid --reset --persona jvvnl-riico
PYTHONPATH=packages:packages/ingest python3 -m seed --apply --mode sql --reset --days 30 --seed 42
PYTHONPATH=packages:packages/ingest python3 -m seed --apply --mode http --persona jvvnl-riico
```

| Flag | Default | Description |
|------|---------|-------------|
| `--dry-run` | — | Print envelope count JSON; no writes |
| `--apply` | — | Apply seed data |
| `--mode` | `sql` | `sql`, `http` (POST ingest), or `hybrid` (SQL aux + HTTP + cagg) |
| `--persona` | `synthetic` | `jvvnl-riico` for public-data virtual plant |
| `--reset` | false | Clear `org_test` demo rows first |
| `--days` | 30 | Measurement history window |
| `--seed` | 42 | RNG seed |
| `--aux-only` | false | SQL graph/baselines/ledger only |
| `--l1-cloud` | false | Also seed L1 outbox |
| `--l1-database-url` | `postgresql://cloud:cloud@localhost:5434/connectors_cloud` | L1 DB |

### 8.4 Wrapper scripts

| Script | Purpose |
|--------|---------|
| [`scripts/seed-public-plant.sh`](scripts/seed-public-plant.sh) | **Recommended** — hybrid seed for full console demo |
| [`scripts/seed-demo-data.sh`](scripts/seed-demo-data.sh) | Migrate + SQL seed (smoke + quick local) |
| [`scripts/simulate-ingest.sh`](scripts/simulate-ingest.sh) | Continuous HTTP replay loop for L1 ingest page |

---

## 9. Testing

### 9.1 Pytest configuration

From [`pyproject.toml`](pyproject.toml):

| Setting | Value |
|---------|-------|
| Python | `>=3.12` |
| testpaths | `packages`, `l1/connectors_cloud/tests`, `l1/connectors_bill/tests`, `packages/l2_common/tests` |
| Markers | `unit`, `contract`, `integration`, `smoke`, `e2e`, `rls`, `fuzz` |

### 9.2 Common commands

```bash
# Fast — no external services
pytest -m "unit or contract" packages/ -q

# Seed dry-run (CI gate)
PYTHONPATH=packages:packages/ingest python3 -m seed --dry-run

# Integration — requires TimescaleDB
bash packages/migrate/apply.sh
pytest -m integration packages/ -q

# Dedupe golden
pytest packages/ingest/tests/test_dedupe_golden.py -q

# Fuzz (nightly CI)
pytest -m fuzz packages/ingest -q

# L1 reference
pytest l1/connectors_cloud/tests -m "unit or contract" -q
pytest l1/connectors_bill/tests -m unit -q
bash l1/connectors_edge/scripts/full-validation.sh

# Full orchestrator
SKIP_SMOKE=1 bash scripts/full-validation.sh
./scripts/e2e-local-stack.sh
```

### 9.3 Console E2E (Playwright)

```bash
cd packages/console
npm install
npm run build
npx playwright install --with-deps chromium
npm run test:e2e
```

Workflow: [`.github/workflows/console-e2e.yml`](.github/workflows/console-e2e.yml) — triggers on `packages/console/**` PR changes.

### 9.4 Test layout

| Area | Path |
|------|------|
| Ingest unit/contract/fuzz | `packages/ingest/tests/` |
| Seed unit/contract | `packages/seed/tests/` |
| Migration integration + RLS | `packages/migrate/tests/` |
| l2_common | `packages/l2_common/tests/` |
| L1 cloud | `l1/connectors_cloud/tests/` |
| L1 bill | `l1/connectors_bill/tests/` |
| L1 edge (Go) | `l1/connectors_edge/packages/edge-agent/main_test.go` |
| Console E2E | `packages/console/e2e/console.spec.ts` |

---

## 10. Deployment

### 10.1 Docker Compose services

**L2-only** ([`deploy/docker-compose.l2.yml`](deploy/docker-compose.l2.yml)) — **5 services:**

| Service | Host port |
|---------|-----------|
| `timescaledb` | 5433 |
| `stamped-l2-ingest` | 8090 |
| `stamped-l2-query-api` | 8091 |
| `stamped-l2-admin-api` | 8093 |
| `stamped-l2-console` | 8092 |

**Full local stack** ([`deploy/profiles/local.yml`](deploy/profiles/local.yml)) — **14 services** including Mosquitto, MinIO, L1 cloud/bill/edge, L2 core.

### 10.2 Port map (local development)

| Service | Port |
|---------|------|
| MQTT (Mosquitto) | 1883 |
| L2 ingest | 8090 |
| L2 query-api | 8091 |
| L2 console | 8092 |
| L2 admin-api | 8093 |
| Bill API | 8080 |
| Bill web | 3001 |
| MinIO | 9000 |
| L2 Postgres (standalone compose) | 5433 |
| L1 cloud Postgres (standalone) | 5434 |

### 10.3 CI workflows

| Workflow | Trigger | Jobs |
|----------|---------|------|
| [`ci.yml`](.github/workflows/ci.yml) | push `main`, `cursor/**`; PRs | contract · unit+seed dry-run · smoke (main) |
| [`contract-check.yml`](.github/workflows/contract-check.yml) | push/PR `main` | Submodule + schema validation |
| [`smoke-pr.yml`](.github/workflows/smoke-pr.yml) | PR to `main` | `run-smoke-e2e.sh` |
| [`e2e-local.yml`](.github/workflows/e2e-local.yml) | push `main` | Full smoke + L1 ingest E2E |
| [`console-e2e.yml`](.github/workflows/console-e2e.yml) | PR (console paths) | Playwright |
| [`fuzz-nightly.yml`](.github/workflows/fuzz-nightly.yml) | cron 02:00 UTC | Hypothesis fuzz |
| [`l1-reference.yml`](.github/workflows/l1-reference.yml) | push/PR | L1 unit, egress-check, Go tests |

### 10.4 AWS (`cloud` mode)

Terraform stub: [`deploy/terraform/aws/main.tf`](deploy/terraform/aws/main.tf) — plan-only for P0. Reference env map: [`deploy/profiles/cloud.yml`](deploy/profiles/cloud.yml).

**Constraint:** No `boto3` or AWS SDK imports in `packages/` (enforced by `full-validation.sh` static audit).

---

## 11. Cookbook

### 11.1 Ingest a measurement manually

```bash
export L2_INGEST_SERVICE_KEY=dev-local-key
PAYLOAD=$(python3 scripts/build_envelope.py measurement mocks/envelope-fixtures/measurement.valid.json)
curl -s -X POST http://localhost:8090/v1/ingest/records \
  -H "Content-Type: application/json" \
  -H "X-Service-Key: $L2_INGEST_SERVICE_KEY" \
  -d "$PAYLOAD"
```

### 11.2 Query telemetry

```bash
curl -s -H "X-Service-Key: dev-local-key" -H "X-Org-Id: org_test" \
  "http://localhost:8091/v1/plants/plant_test/measurements?asset_id=incomer_1&metric=active_power_kw&from=2026-06-01T00:00:00Z&to=2026-07-12T00:00:00Z&granularity=15min" | jq '.points | length'
```

### 11.3 Reset and reseed demo data

```bash
./scripts/seed-demo-data.sh
# equivalent:
PYTHONPATH=packages:packages/ingest python3 -m seed --apply --mode sql --reset --days 30 --seed 42
```

### 11.4 Run L1 → L2 bill line path

```bash
./scripts/e2e-l1-ingest.sh bill_line
# or full MQTT path:
./scripts/e2e-cloud-ingest.sh bill_line
```

### 11.5 Apply migrations on empty DB

```bash
export L2_DATABASE_URL=postgresql://l2:l2@localhost:5433/stamped_l2
bash packages/migrate/apply.sh
```

### 11.6 Build console for production

```bash
cd packages/console
npm install
npm run build
npm start   # listens on 8092
```

### 11.7 Validate contracts after submodule bump

```bash
./scripts/contract-check.sh
```

---

## 12. Roadmap and changelog

### 12.1 Build phases (completed)

| Phase | Theme | Status |
|-------|-------|--------|
| R | Research + portability docs (ADR-010, playbooks) | Done |
| L2 P0 | Ingest, query-api, admin-api, console, migrations, RLS | Done |
| L1 P0 | Reference packages under `l1/` | Done |
| Completion | Seed toolkit, console UI polish, production_record | Done |
| Smoke hardening | `run-smoke-e2e.sh`, RLS `set_config`, schema verify | Done |

### 12.2 Possible future directions

| Priority | Item |
|----------|------|
| P1 | `docs/egress-inventory.md` per L1 package |
| P1 | Bill web Stamped styling (`l1/connectors_bill/packages/web`) |
| P1 | Sparkplug / CSV adapters (connectors_cloud) |
| P1 | Copy `l1/` reference to private repos when access available |
| P2 | `local-llm` compose service for L3/L4 |
| P2 | `connectors-ingest` local lab package |
| P2 | K3s + Harbor fleet orchestration |
| P2 | Signed air-gap tarball distribution |
| P2 | Full AWS Terraform apply (ECS/RDS) |

### 12.3 Changelog

| Date | Change |
|------|--------|
| 2026-07-13 | Merged smoke reliability fixes + L2 completion (seed, UI, production_record) to `main` |
| 2026-07-12 | `packages/seed` demo toolkit; console DESIGN.md; baselines/ledger wired |
| 2026-07-12 | L2 P0 complete — ingest, query, admin, console, six schemas |
| 2026-07-12 | L1 reference packages under `l1/`; master `local.yml` wired |
| 2026-07-12 | R-phase: ADR-010, deployment profiles, egress template |

---

## 13. FAQ and glossary

### 13.1 FAQ

**Why is the repo named `universal-repositary`?**  
Historical naming; product name is **stamped-l2**. GitHub repo: `Vinayak-RZ/universal-repositary`.

**Why do I need the `external/` submodule?**  
JSON schemas, fixtures, and ADRs are shared across L1/L2/L3 repos. CI fails without it: `git submodule update --init --recursive`.

**Can L3 call the database directly?**  
No. ADR-008 layer topology — L3–L6 use query-api only.

**Why two seed modes (`sql` vs `http`)?**  
SQL is fast for local reset and integration fixtures. HTTP exercises the full ingest path (validation, dedupe, audit).

**What org/plant IDs does demo data use?**  
`org_test` / `plant_test` / asset `incomer_1` — consistent across seed, console, and smoke scripts.

**Is the console customer-facing?**  
No. Internal ops only (port 8092). Customer UI is L6 (`stamped-l6`, separate repo).

### 13.2 Glossary

| Term | Definition |
|------|------------|
| **StampedRecordEnvelope** | Versioned wrapper around L1 payloads with `dedupe_key`, `org_id`, `plant_id`, `record_type` |
| **Dedupe key** | `sha256:` hash of canonical fields — idempotency token |
| **RLS** | Row-Level Security — Postgres policy filtering by `org_id` |
| **CAGG** | Timescale continuous aggregate — `telemetry.agg_15min` |
| **M&V** | Measurement & Verification — energy savings ledger |
| **DISCOM** | Distribution company (Indian utility context for bills/tariffs) |
| **L1 / L2 / L3…** | Stamped layer architecture (L0 reference in `external/technical/`) |
| **ADR** | Architecture Decision Record in `external/decisions/` |
| **P0 / P1 / P2** | Priority tiers — P0 shipped, P1 next, P2 deferred |

---

## Companion repositories

| Repo | Role |
|------|------|
| [stamped-external](https://github.com/Vinayak-RZ/stamped-external) | Platform SSOT (submodule at `external/`) |
| [cursor-config-coding](https://github.com/Vinayak-RZ/cursor-config-coding) | Cursor engineering config source |
| [cursor-config-buisness](https://github.com/Vinayak-RZ/cursor-config-buisness) | PM/GTM/research config |
| [cursor-config-design](https://github.com/Vinayak-RZ/cursor-config-design) | Design/deck config |

---

## Cursor AI config (installed)

This repo ships Cursor agent configuration for engineering workflows:

| Component | Location |
|-----------|----------|
| Agent guide | [AGENTS.md](AGENTS.md) |
| Rules | `.cursor/rules/` |
| Skills | `.cursor/skills/` (ponytail, nawab-plans, speckit-*, impeccable, …) |
| MCP | `.cursor/mcp.json` (agent-patterns catalog) |

Upstream docs: [README-cursor-config-coding.md](README-cursor-config-coding.md)

---

## License and contribution

Platform contracts in `external/` follow the stamped-external repo license. Application code in `packages/` and `l1/` is Stamped Energy internal — confirm contribution policy with maintainers before external PRs.

**Before opening a PR:**

1. `git submodule update --init --recursive`
2. `pytest -m "unit or contract" packages/ -q`
3. `./scripts/contract-check.sh`
4. Update this README if you change ports, env vars, API routes, or schema counts
