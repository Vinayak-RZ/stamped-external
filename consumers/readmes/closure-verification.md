<!-- SNAPSHOT: mirrored from closure-verification/README.md on 2026-07-21. Canonical README lives in the consumer repo — re-sync when that README changes. -->

> **Snapshot** of [`closure-verification`](https://github.com/Vinayak-RZ/closure-verification) root README (copied 2026-07-21).
> Canonical source: consumer repo `README.md`. Do not edit here for product truth — update the consumer repo, then re-copy.
> Product package: `stamped-l5` (GitHub repo may remain `closure-verification` per DEC-002).

---

# closure-verification — Stamped L5 Closure & Verification

> **What it is:** The L5 modular monolith that turns L4 prescriptions into acted-on, **ops-proven** closures — workflow, EMS alarms, WhatsApp/SMS, telemetry clearance, calculated ledger intents, evidence, and an L6-ready query/event API.  
> **What it is not:** A plant dashboard (that is L6), an L3 detector, an L2 timeseries/ledger store, or a system that claims “verified on DISCOM bill” without the optional bill path.  
> **Primary interface:** FastAPI HTTP API (`stamped-l5-api`) + durable worker (`stamped-l5-worker`)  
> **Runtime:** Python 3.12 · Postgres (or SQLite for tests) · Alembic · fixture-first adapters for CI

---

**TL;DR**

- **Ops-first verification** — `ops_confirmed` means telemetry clearance held, not bill M&V (ADR-020).
- **Signal engine v2** — `relative_to`, density gates, `data_insufficient` fail-closed, `false_clear` vs `ops_regressed`.
- **L6-connect surface** — OpenAPI, scoped API keys, prescription queue/ack, events poll, Standard Webhooks outbox.
- **Dual labels** — every queue DTO exposes `ops_label` and `bill_label` so the UI cannot confuse telemetry with bill.
- **Hash-chained audit** — per-org `workflow_events` chain + verifier job.
- **Dispute + optional bill** — `disputed` lifecycle; FixtureBill dual-label without ungating ops.
- **No L2 DB URL** — measurements and ledger only via HTTP ports / fixtures (ADR-019).
- **Platform SSOT** — `external/` submodule → [stamped-external](https://github.com/Vinayak-RZ/stamped-external); this repo implements, it does not redefine.
- **Validate gate** — `./scripts/validate.sh` = contracts + ruff + OpenAPI smoke + **42** pytest.
- **Engineering OS** — ponytail (minimal diffs) · nawab-plans · Spec Kit · core-engineering rules under `.cursor/`.

---

## Table of contents

1. [Vision](#1-vision)
2. [Architecture](#2-architecture)
3. [Quickstart](#3-quickstart)
4. [Configuration](#4-configuration)
5. [Project structure](#5-project-structure)
6. [HTTP API catalog](#6-http-api-catalog)
7. [Domain & data model](#7-domain--data-model)
8. [Core algorithms](#8-core-algorithms)
9. [Testing & validation](#9-testing--validation)
10. [Deployment & operations](#10-deployment--operations)
11. [Connect L6](#11-connect-l6)
12. [Core engineering practices](#12-core-engineering-practices)
13. [Cookbook](#13-cookbook)
14. [Roadmap & changelog](#14-roadmap--changelog)
15. [FAQ & glossary](#15-faq--glossary)
16. [Authority & further reading](#16-authority--further-reading)

---

## 1. Vision

### 1.1 What it is

Stamped’s **Layer 5 — Closure & Verification**. Given an L4 `Prescription` that cites Findings with `ops_clearance`, L5:

1. Accepts intake (or hard-gates incomplete clearance back toward L4)
2. Raises an EMS-style alarm and notifies the owner (WhatsApp, SMS fallback)
3. Tracks workflow (`open` → `in_progress` → `done` → `verified` / `deferred` / `rejected` / `disputed`)
4. Polls L2 measurements until clearance predicates hold (or data is insufficient)
5. Appends **ledger intents** to L2 (`pending` → `ops_confirmed`; opportunity cost as `modeled`)
6. Emits **WorkflowEvents** to L6 (outbox + poll) and stores evidence bundles

Product target (platform): high-priority prescriptions acted within a billing cycle, with trustworthy ops clearance — see `external/technical/layers/L5-closure-and-verification.md`.

### 1.2 What it is not

| Not this | Why |
|----------|-----|
| Plant dashboard / SSE / Forge UI | Owned by **L6** (`stamped-l6`) |
| Anomaly / Finding detectors | Owned by **L3** |
| Financial SoR / timeseries DB | Owned by **L2** — L5 only HTTP-appends ledger intents |
| IPMVP Option C auditor pack as hard gate | Deferred; bill path is optional dual-label only |
| Temporal / Redis / Kafka runtime | Forbidden through P2 (ADR-019) — Postgres state machine + timers |
| Direct OT / SCADA writes | Out of layer |

### 1.3 Who it is for

| Audience | Use |
|----------|-----|
| L6 engineers | Consume OpenAPI + events; render dual labels correctly |
| L5 / platform engineers | Extend workflow, clearance, outbox, adapters |
| Plant ops (via WA / future UI) | Ack / done / defer via WhatsApp or dashboard ack |
| Agents / contributors | Follow [AGENTS.md](AGENTS.md) + `.cursor/` skills before coding |

### 1.4 Success criteria (shipped)

- Missing `ops_clearance` → bounce (`blocked` / `missing_ops_clearance`)
- Dense good telemetry → Workflow `verified` + ledger `ops_confirmed` (never bill claim by default)
- Sparse/gap series → `data_insufficient` (no `ops_confirmed`)
- Meta failure → SMS recorded; SLA escalate works; silence auto-unsilences
- L6 FakeReceiver gets signed webhooks; list/detail/ack/events work under API keys
- Hash-chain verifies; dispute + bill dual-label green in tests
- `./scripts/validate.sh` green; CI on `main` and `cursor/**`

---

## 2. Architecture

### 2.1 High-level diagram

```mermaid
flowchart TB
  L4[L4_Prescription] --> API[stamped_l5_api]
  WA[Meta_or_FakeMeta] --> API
  API --> App[ClosureApp]
  App --> WF[workflow]
  App --> AL[alarms]
  App --> NT[notification]
  App --> VR[verification]
  App --> LD[ledger]
  App --> EV[evidence]
  App --> QY[query]
  WRK[stamped_l5_worker] --> App
  VR -->|measurements| L2[Fixture_or_L2_HTTP]
  LD -->|append_intent| L2
  WF --> OB[(outbox)]
  WRK -->|StandardWebhooks| L6[FakeL6_or_L6_BFF]
  QY -->|REST_API_key| L6
  App --> PG[(Postgres_or_SQLite)]
```

### 2.2 Lifecycle (Rx → ops_verified)

```mermaid
sequenceDiagram
  participant L4
  participant API
  participant WF as Workflow
  participant AL as Alarms
  participant NT as Notify
  participant VR as Clearance
  participant L2
  participant L6

  L4->>API: POST /v1/prescriptions/ingest
  API->>WF: accept_prescription
  WF->>AL: raise_alarm
  AL->>NT: issue template WA/SMS
  NT-->>L6: WorkflowEvent outbox
  Note over API,WF: Owner ack via WA webhook or dashboard acknowledge
  API->>WF: done
  WF->>VR: schedule clearance_poll
  VR->>L2: query_measurements
  alt hold + density OK
    VR->>WF: verified
    VR->>L2: realised_savings ops_confirmed
    VR-->>L6: ops_verified event
  else gaps / sparse
    VR-->>WF: stay done data_insufficient
  end
```

### 2.3 Runtime processes

| Process | Entry | Role |
|---------|-------|------|
| API | `stamped-l5-api` → [`packages/api/stamped_l5_api/main.py`](packages/api/stamped_l5_api/main.py) | HTTP, auth, fixtures, L6 query routes |
| Worker | `stamped-l5-worker` → [`packages/worker/stamped_l5_worker/main.py`](packages/worker/stamped_l5_worker/main.py) | Timers (SKIP LOCKED), clearance poll, SLA escalate, unsilence, ledger flush, L3/L6 outbox, audit verify |
| Domain | [`packages/domain/stamped_l5_domain/`](packages/domain/stamped_l5_domain/) | All business logic; API/worker stay thin |
| Migrate | Alembic in [`packages/migrate/`](packages/migrate/) | `0001_initial` → `0002_p1_ops` → `0003_p2_l6` |

### 2.4 Trust boundaries

| Boundary | Rule |
|----------|------|
| Tenancy | Every row carries `org_id` / `plant_id`; transitions reject mismatches |
| L2 | **No** `L2_DATABASE_URL` in product code (`validate.sh` forbids it) |
| Secrets | Env only (`L5_*`); API keys stored as SHA-256 hashes |
| Auth | Scoped keys fail closed when `L5_AUTH_REQUIRED=true` |
| Claims | UI must not show DISCOM bill verified unless `bill_label=verified` |
| Contracts | Wire shapes from `external/contracts/`; local OpenAPI for L5 HTTP |

### 2.5 Key domain modules

| Module | Path | Owns |
|--------|------|------|
| App façade | `stamped_l5_domain/app.py` | Wires ingest → alarm → notify → verify → ledger |
| Workflow | `…/workflow/` | State machine, dashboard ack, dispute, event emit + outbox |
| Alarms | `…/alarms/` | Raise / ack / escalate / silence / clear + SLA schedule |
| Notification | `…/notification/` | Templates, Meta→SMS fallback, WA webhook |
| Verification | `…/verification/` | Clearance engine v2, poll schedule, false_clear monitor |
| Ledger | `…/ledger/` | Append intents (potential, ops_confirmed, bill verified, opportunity_cost) |
| Evidence | `…/evidence/` | v2 JSON bundles + ZIP/PDF export |
| Query | `…/query/` | L6 list/detail/events DTOs + dual labels |
| Auth | `…/auth/` | API key mint/resolve, scopes, problem+json helpers |
| Outbox | `…/outbox/` | Standard Webhooks sign/verify + L6 deliverer |
| Audit | `…/audit/` | Hash-chain assign + verify |
| Bill | `…/bill/` | Non-blocking reconcile (DEC-007) |
| Integration | `…/integration/` | Ports + FakeMeta/FakeSms/FixtureL2/L3/Bill/FakeL6 |
| Timers | `…/timers/` | Claim due `scheduled_actions` |

---

## 3. Quickstart

### 3.1 Prerequisites

- Python **3.12+**
- Git with submodule support
- Optional: Docker (Postgres 16 + MinIO profile)

### 3.2 Install

```bash
git clone --recurse-submodules https://github.com/Vinayak-RZ/closure-verification.git
cd closure-verification
# if clone without submodules:
git submodule update --init --recursive

python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### 3.3 Verify (required gate)

```bash
./scripts/validate.sh
# submodule pin · forbid L2 DB URL · contract-check · ruff · openapi smoke · pytest (42)
```

### 3.4 Run locally (SQLite)

```bash
mkdir -p data
export L5_DATABASE_URL=sqlite+pysqlite:///./data/stamped_l5.db
export L5_EVIDENCE_DIR=./data/evidence
export L5_BOOTSTRAP_API_KEY=stk_dev_bootstrap_key
export L5_AUTH_REQUIRED=true
export L5_L6_WEBHOOK_SECRET=whsec_dev

alembic upgrade head
stamped-l5-api      # http://0.0.0.0:8080
stamped-l5-worker   # separate terminal
```

### 3.5 Run with Postgres

```bash
docker compose up -d postgres
pip install -e ".[dev,postgres]"
export L5_DATABASE_URL=postgresql+psycopg://stamped:stamped@localhost:5432/stamped_l5
alembic upgrade head
stamped-l5-api
```

Optional evidence MinIO: `docker compose --profile evidence up -d minio` (API still defaults to local FS under `L5_EVIDENCE_DIR`).

### 3.6 Smoke (curl)

```bash
curl -s http://localhost:8080/health
curl -s -H "X-API-Key: stk_dev_bootstrap_key" http://localhost:8080/v1/openapi.json | head
```

---

## 4. Configuration

All settings use prefix **`L5_`** ([`stamped_l5_domain/settings.py`](packages/domain/stamped_l5_domain/settings.py)). See [`.env.example`](.env.example).

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `L5_DATABASE_URL` | Yes (prod) | `sqlite+pysqlite:///:memory:` | SQLAlchemy URL |
| `L5_EVIDENCE_DIR` | No | `./data/evidence` | Local evidence root (S3-shaped keys under it) |
| `L5_META_ENABLED` | No | `false` | Live Meta Cloud API (CI uses FakeMeta) |
| `L5_SMS_ENABLED` | No | `false` | Live MSG91 (CI uses FakeSms) |
| `L5_MSG91_API_KEY` | If SMS live | `""` | MSG91 credential |
| `L5_L3_OUTBOX_URL` | No | `""` | Reserved for live L3 HTTP |
| `L5_L6_WEBHOOK_URL` | No | `""` | Live L6 receiver URL (CI uses in-proc FakeL6) |
| `L5_L6_WEBHOOK_SECRET` | No | `whsec_dev` | HMAC secret for Standard Webhooks |
| `L5_BOOTSTRAP_API_KEY` | Dev | `stk_dev_bootstrap_key` | Seeded into `api_keys` on API startup |
| `L5_BOOTSTRAP_ORG_ID` | Dev | `org_acme` | Org for bootstrap key |
| `L5_AUTH_REQUIRED` | No | `true` | When false, principals get all scopes (tests may set false) |
| `L5_LOG_JSON` | No | `true` | Structured logging |
| `L5_SERVICE_NAME` | No | `stamped-l5` | Health payload |

**Forbidden:** any `L2_*DATABASE*URL` style secret in product code — CI greps and fails.

---

## 5. Project structure

```text
closure-verification/
├── packages/
│   ├── api/stamped_l5_api/          # FastAPI app (19 routes)
│   ├── worker/stamped_l5_worker/    # durable tick loop
│   ├── domain/stamped_l5_domain/    # domain modules (see §2.5)
│   └── migrate/                     # Alembic env + versions/
├── tests/
│   ├── unit/ · golden/ · integration/ · e2e/ · tenancy/
│   └── conftest.py                  # in-memory SQLite + fixtures
├── docs/
│   ├── openapi/l5-v1.json           # OpenAPI snapshot
│   ├── SPEC_KIT.md · INDUSTRY_PRACTICES.md · …
├── scripts/validate.sh              # single CI/local gate
├── external/                        # stamped-external submodule (SSOT)
├── docker-compose.yml               # postgres (+ minio profile)
├── pyproject.toml                   # stamped-l5 0.1.0 · requires-python >=3.12
├── IMPLEMENTATION_PLAN.md           # nawab P0–P2 lived plan
├── DECISIONS.md                     # DEC-001…007
├── PROGRESS.md · PROJECT_OVERVIEW.md · AGENTS.md
└── .cursor/                         # ponytail · nawab · core-engineering skills
```

Package discovery: setuptools finds `stamped_l5_domain*`, `stamped_l5_api*`, `stamped_l5_worker*` under `packages/{domain,api,worker}`.

---

## 6. HTTP API catalog

**Total: 19 routes** (verified from [`packages/api/stamped_l5_api/main.py`](packages/api/stamped_l5_api/main.py)).  
Auth: `X-API-Key` or `Authorization: Bearer …` except `/health`, `/v1/openapi.json`, `/docs`, `/redoc`.  
Errors: RFC 9457-ish **problem+json** (`type`, `title`, `status`, `detail`, `code`).

### 6.1 Platform & fixtures (4)

| Method | Path | Scope | Purpose |
|--------|------|-------|---------|
| GET | `/health` | public | Liveness |
| GET | `/v1/openapi.json` | public | OpenAPI 3 document |
| POST | `/v1/fixtures/findings` | `write:admin` | Seed Finding fixture |
| POST | `/v1/fixtures/plant-escalation` | `write:admin` | Seed SLA policy |
| POST | `/v1/fixtures/bill-match` | `write:admin` | Seed FixtureBill match |

### 6.2 Intake & workflow writes (4)

| Method | Path | Scope | Purpose |
|--------|------|-------|---------|
| POST | `/v1/prescriptions/ingest` | `write:admin` | Accept L4 Prescription |
| POST | `/v1/prescriptions/{id}/transition` | `write:acknowledgements` | Analyst transition / dispute |
| POST | `/v1/webhooks/whatsapp` | `write:acknowledgements` | Button allowlist webhook |
| POST | `/v1/prescriptions/{id}/verify` | `write:admin` | Done → clearance eval |

### 6.3 Alarms (2)

| Method | Path | Scope | Purpose |
|--------|------|-------|---------|
| GET | `/v1/plants/{plant_id}/alarms` | `read:alarms` | List (+ cursor) |
| POST | `/v1/alarms/{alarm_id}/silence` | `write:admin` | Policy-bounded silence |

### 6.4 L6 query & ack (5)

| Method | Path | Scope | Purpose |
|--------|------|-------|---------|
| GET | `/v1/plants/{plant_id}/prescriptions` | `read:prescriptions` | Queue list |
| GET | `/v1/plants/{plant_id}/prescriptions/{rx_id}` | `read:prescriptions` | Detail + dual labels |
| POST | `/v1/plants/{plant_id}/prescriptions/{rx_id}/acknowledge` | `write:acknowledgements` | Dashboard ack (`Idempotency-Key`) |
| GET | `/v1/events` | `read:events` | Cursor poll of WorkflowEvents |
| GET | `/v1/plants/.../evidence` | `read:evidence` | Evidence meta + ZIP key |

### 6.5 Evidence, bill, audit (3)

| Method | Path | Scope | Purpose |
|--------|------|-------|---------|
| GET | `/v1/evidence/{bundle_id}/download` | `read:evidence` | ZIP bytes |
| POST | `/v1/prescriptions/{id}/bill-reconcile` | `write:admin` | Dual-label bill path |
| POST | `/v1/admin/verify-audit-chain` | `write:admin` | Hash-chain verify |

### 6.6 API key scopes

`read:prescriptions` · `write:acknowledgements` · `read:alarms` · `read:events` · `read:evidence` · `read:ledger_refs` · `write:admin` (superset).

Checked-in OpenAPI: [`docs/openapi/l5-v1.json`](docs/openapi/l5-v1.json) (regenerated by `validate.sh` smoke).

---

## 7. Domain & data model

### 7.1 Persistence tables (20)

| Table | Role |
|-------|------|
| `inbox_processed` | L4/Meta ingest dedupe |
| `prescription_snapshot` | Accepted Rx JSON + timestamps |
| `workflow_state` | Status + optimistic `version` |
| `workflow_events` | Append-only events + **hash chain** (`seq`, `prev_entry_hash`, `entry_hash`) |
| `alarms` | EMS alarm rows |
| `scheduled_actions` | Durable timers (reminder, clearance_poll, escalate_sla) |
| `notification_log` / `sms_notification_log` | WA / SMS send logs |
| `verification_case` | Clearance outcomes + traces |
| `ledger_append_intent` | Pending/acked L2 ledger payloads |
| `evidence_bundle` | Content hash + object key |
| `outbox` / `dead_events` / `outbox_delivery_attempt` | Downstream delivery |
| `opportunity_cost_mark` | One-shot modeled delay cost |
| `plant_escalation_policy` / `silence_policy` | Ops depth policies |
| `api_keys` | Hashed keys + scopes |
| `idempotency_record` | Dashboard ack idempotency |
| `bill_reconciliation` | Dual-label bill state |

Migrations: [`packages/migrate/versions/`](packages/migrate/versions/) — `0001_initial` → `0002_p1_ops` → `0003_p2_l6` (`revision` id `0002_p2_l6`).

### 7.2 Workflow status vocabulary

`blocked` · `open` · `in_progress` · `done` · `verified` (ops-cleared) · `deferred` · `rejected` · `disputed`

Illegal transitions raise `WorkflowError` with stable `code`. Optimistic concurrency via `expected_version`.

### 7.3 Ledger verification_status values L5 writes

| Status | When |
|--------|------|
| `pending` | potential_savings @ accept |
| `ops_confirmed` | realised after ops clearance |
| `modeled` | opportunity_cost (counterfactual delay) |
| `verified` | **only** after bill reconcile (DEC-007); does not erase ops_confirmed |

### 7.4 Dual labels (L6 DTOs)

| Field | Examples |
|-------|----------|
| `ops_label` | `pending_ops` · `ops_confirmed` · `disputed` |
| `bill_label` | `unverified` · `verified` · `disputed` |

---

## 8. Core algorithms

### 8.1 Clearance engine v2 (DEC-005)

Implemented in [`stamped_l5_domain/verification/`](packages/domain/stamped_l5_domain/verification/__init__.py).

1. **LOAD** Finding `ops_clearance` (`related_tag_ids`, predicate, `stabilize_window`, reopen policy)
2. **WAIT** until Rx `done` (early clear allowed if window already holds)
3. **POLL** L2 measurements for each tag (`asset_id/metric` split)
4. **RESOLVE** `relative_to`: `absolute` | `baseline` | `actual_at_detect`
5. **HOLD** every `quality=good` sample in window must pass; density `max(3, ceil(window_minutes/10))`
6. **OUTCOMES**
   - `ops_verified` → workflow VERIFIED + ledger + clear alarm
   - `data_insufficient` → stay DONE; reschedule poll; **never** ops_confirm
   - `not_cleared` → stay DONE; SLA may escalate
   - after VERIFIED: `ops_regressed` vs `false_clear` → reopen + L3 calib outbox

Golden corpus: [`tests/golden/test_clearance_predicates.py`](tests/golden/test_clearance_predicates.py) (MD / idle / compressor / SEC / gaps).

### 8.2 Outbox → L6 (DEC-006)

- Every workflow emit writes `outbox` row `destination=l6` with WorkflowEvent-shaped payload + `links.self`
- Worker `OutboxDeliverer` signs with Standard Webhooks (`webhook-id`, `webhook-timestamp`, `webhook-signature`)
- CI: [`FakeL6Receiver`](packages/domain/stamped_l5_domain/integration/__init__.py) verifies HMAC in-process
- Exhausted retries → `dead_events`

### 8.3 Hash chain (WS-H)

Per `org_id`: monotonic `seq`; `entry_hash = H(prev ‖ canonical_row)`. Canonical timestamps normalize SQLite’s tz-stripping. Verifier: `verify_org_chain` / worker tick / `POST /v1/admin/verify-audit-chain`.

---

## 9. Testing & validation

### 9.1 Commands

```bash
./scripts/validate.sh          # full gate (what CI runs): unit → integration → fuzz → e2e
pytest -q                      # ~73 tests
pytest -m unit -q
pytest -m fuzz -q              # Hypothesis property tests
pytest -m e2e -q               # domain + HTTP TestClient
ruff check packages tests
```

### 9.2 Test layout

| Tier | Path | Focus |
|------|------|-------|
| unit | `tests/unit/` | Workflow edges, auth, outbox retries, query/bill, SMS/silence, obs |
| golden | `tests/golden/` | Clearance predicates; hash chain + dual labels |
| fuzz | `tests/fuzz/` | Hypothesis: density, durations, holds, webhooks, hash chain |
| integration | `tests/integration/` | Timers, verify/ledger, P1 ops, P2 L6 connect |
| e2e | `tests/e2e/` | Domain path + **HTTP** auth/queue/ack/verify/events/evidence |
| tenancy | `tests/tenancy/` | org/plant isolation |

Fixtures load contract JSON from `external/contracts/fixtures/` via [`tests/conftest.py`](tests/conftest.py).

### 9.3 CI

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) — on `push` to `main` / `cursor/**` and PRs to `main`:

1. Checkout with submodules → Python 3.12 (pip cache) → `pip install -e ".[dev]"`
2. `./scripts/validate.sh` (contracts, private-key grep, ruff, openapi, unit/integration/fuzz/e2e)
3. Extra Hypothesis fuzz stress (`HYPOTHESIS_PROFILE=ci`)
4. Advisory `pip-audit` job on project deps (`continue-on-error`)

---

## 10. Deployment & operations

### 10.1 Local compose

[`docker-compose.yml`](docker-compose.yml): Postgres 16 on `:5432`; optional MinIO profile on `:9000` / console `:9001`.

### 10.2 Process model (prod sketch)

| Unit | Notes |
|------|-------|
| API | Stateless FastAPI behind load balancer; sticky not required |
| Worker | Single or multi-instance with SKIP LOCKED on `scheduled_actions` |
| DB | Managed Postgres; run `alembic upgrade head` before traffic |
| Evidence | Local FS or S3-compatible; keys look like `ap-south-1/{org}/{plant}/{rx}/…` |
| Region | Platform default India (`ap-south-1`) for customer data |

AWS ECS/RDS cutover is documented as a bridge checklist (P0 decision) — not a hard CI gate.

### 10.3 Observability

Structured JSON logs (`L5_LOG_JSON`); correlation IDs on WorkflowEvent envelopes. Prefer OTel hooks as they land; do not invent a second metrics stack in P2.

### 10.4 DLT / MSG91 (before live SMS)

- [ ] TRAI DLT PE / header / templates registered  
- [ ] MSG91 account + `L5_MSG91_API_KEY`  
- [ ] `L5_SMS_ENABLED=true` only after approval  

---

## 11. Connect L6

L5 is **source of closure truth**. L6 owns Next.js UI, SSE fan-out, and Forge design. Do not put dashboard code in this repo.

### 11.1 Integration checklist for L6 engineers

1. Import OpenAPI from `/v1/openapi.json` or [`docs/openapi/l5-v1.json`](docs/openapi/l5-v1.json)
2. Authenticate with scoped API key
3. Poll `GET /v1/plants/{id}/prescriptions` for the queue
4. Use `POST …/acknowledge` with `Idempotency-Key` for dashboard ack
5. Subscribe to outbox webhooks **or** poll `GET /v1/events?since=`
6. Render **both** `ops_label` and `bill_label`; never imply DISCOM verification from ops alone
7. Fetch ledger ₹ series from **L2**, not L5 (L5 returns `ledger_entry_refs` only)
8. Show opportunity-cost rows with modeled disclaimer ([L6 stub](external/handoff/l6-counterfactual-display-stub.md))

### 11.2 Example: list + ack

```bash
KEY=stk_dev_bootstrap_key
ORG=org_acme
PLANT=plant_ghaziabad_1

curl -s -H "X-API-Key: $KEY" \
  "http://localhost:8080/v1/plants/$PLANT/prescriptions?org_id=$ORG" | jq .

curl -s -H "X-API-Key: $KEY" -H "Idempotency-Key: ack-$(date +%s)" \
  -H "Content-Type: application/json" \
  -d "{\"org_id\":\"$ORG\"}" \
  "http://localhost:8080/v1/plants/$PLANT/prescriptions/RX_ID/acknowledge"
```

---

## 12. Core engineering practices

This repo follows the **cursor-config-coding** engineering OS vendored under [`.cursor/`](.cursor/) and summarized in [AGENTS.md](AGENTS.md). Contributors (human or agent) should treat these as binding, not optional etiquette.

### 12.1 Authority stack

| Layer | Rule |
|-------|------|
| Platform SSOT | `external/` submodule — do not fork L5/L6 ADRs or contracts |
| Lived plan | [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) (nawab Parts A–D) |
| Decisions | [`DECISIONS.md`](DECISIONS.md) DEC-001…007 |
| Agent guide | [`AGENTS.md`](AGENTS.md) |

### 12.2 Coding workflow

```text
ponytail → nawab-plans (Plan mode) → (spec-kit for large features)
  → research → plan → approve → implement → validate → commit → learn
```

| Practice | Skill / rule | Intent |
|----------|--------------|--------|
| **Minimal diffs** | `ponytail` + `ponytail.mdc` | YAGNI ladder; no gold-plating; never skip validation/security |
| **Executable plans** | `nawab-plans` + `planning.mdc` | Full sectioned plans; approve before multi-file work |
| **Spec-driven features** | Spec Kit (`docs/SPEC_KIT.md`) | Optional for greenfield; still apply ponytail on implement |
| **Core engineering** | `core-engineering.mdc` + user rules | Plan → code-review → tradeoffs → phase tracking → conventional commits |
| **Learn / research** | `learn-and-research` | Cite sources for unfamiliar APIs before architecture bets |
| **Backend** | `backend-architecture.mdc` | Thin handlers; validate at boundary; service-layer authZ |
| **Security** | `security-baseline.mdc` | Fail closed; no secrets in git; parameterized SQL |

### 12.3 Design invariants (L5-specific)

1. **Fail closed on data quality** — sparse telemetry never becomes `ops_confirmed`
2. **Append-only money truth** — ledger corrections are compensating intents, not UPDATEs
3. **Fixture-first CI** — FakeMeta / FakeSms / FixtureL2 / FixtureL3 / FakeL6 / FixtureBill; live vendors behind flags
4. **Layer isolation** — no L2 DB credentials; no L6 UI in-tree
5. **Contract discipline** — `external/scripts/contract-check.sh` in validate; additive event types preferred

### 12.4 Commit & PR hygiene

- Conventional commits: `feat|fix|refactor|docs|test|chore|perf(scope): …`
- Validate before claiming done
- Feature branches: `cursor/<name>-<suffix>` (cloud agents use assigned suffix)
- Draft PRs against `main`; do not force-push `main`

---

## 13. Cookbook

### 13.1 Ingest fixture Rx end-to-end (domain tests)

Use pytest fixtures in [`tests/conftest.py`](tests/conftest.py) — preferred over manual HTTP for unit/integration. Pattern: seed Finding → `app_svc.ingest_prescription` → dense `l2.seed_series` → `mark_done_and_verify` → assert ledger statuses.

### 13.2 Force SMS fallback

Set Meta `fail_next=True` (FakeMeta) or break live Meta; notification catches `RuntimeError` and routes to FakeSms / MSG91.

### 13.3 Open a dispute

```http
POST /v1/prescriptions/{id}/transition
{"org_id":"…","plant_id":"…","to_status":"disputed","reason_code":"customer_dispute"}
```

Allowed reason codes: `bill_mismatch` · `ops_challenge` · `customer_dispute` · `data_quality` · `other`.

### 13.4 Bill dual-label without breaking ops

1. `POST /v1/fixtures/bill-match` with `prescription_id`  
2. `POST /v1/prescriptions/{id}/bill-reconcile`  
3. Detail shows `ops_label=ops_confirmed` (if verified on signals) and `bill_label=verified`  
4. L2 ledger contains **both** `ops_confirmed` and `verified` realised rows when applicable  

### 13.5 Replay / drain L6 outbox

Run worker tick (`stamped-l5-worker` or `tick_once()` in tests). Pending `destination=l6` rows deliver to FakeL6 or configured webhook.

---

## 14. Roadmap & changelog

### 14.1 Build phases (completed)

| Phase | Theme | Status |
|-------|-------|--------|
| P0 | Scaffold, workflow, FakeMeta, thin clearance, ledger, e2e | Done |
| P1 | Signal engine v2, SMS, SLA, L3 calib, silence, evidence v2 | Done |
| P2 | L6 connect, hash audit, dispute, bill dual-label, ZIP | Done |

### 14.2 Possible future directions (P3 / ops)

- Portfolio rollups; WhatsApp Flows closeout; predictive stall scoring (SSOT P3)
- Live Meta / MSG91 / L2 HTTP / L6 webhook cutover behind flags
- Magic deep-link auth productization (open L6↔L5 security question)
- Temporal only if ADR-019 upgrade triggers fire
- Full IPMVP Option C / G14 auditor pack — still **not** an ops gate

### 14.3 Recent changelog

| Date | Change |
|------|--------|
| 2026-07-21 | P2: OpenAPI + API keys + query/ack/events + FakeL6; hash chain; dispute; FixtureBill; evidence ZIP; extensive README |
| 2026-07-21 | P1: clearance engine v2, SMS fallback, SLA, L3 outbox, silence, evidence v2 |
| 2026-07-21 | P0: modular monolith scaffold, workflow/alarms/FakeMeta/ledger, validate.sh + CI |
| 2026-07-21 | Platform submodule `external/` + DEC-001/002 charter |

Track live status in [`PROGRESS.md`](PROGRESS.md).

---

## 15. FAQ & glossary

### FAQ

**Q: Can I start L6 now?**  
A: Yes. P0–P2 L5 surface is the intended plug-in contract. Optional P3 work in this repo does not block the dashboard.

**Q: Why is workflow status `verified` if bill isn’t done?**  
A: Historical wire name for **ops-cleared**. Display as “Ops-confirmed (telemetry)”. Bill uses `bill_label` / ledger `verification_status=verified`.

**Q: Where do savings charts come from?**  
A: L2 ledger + timeseries APIs. L5 only supplies refs and events.

**Q: Why fixtures in CI?**  
A: DEC-003/004/007 — no vendor credentials or live L2/L6 required for green builds.

**Q: SQLite hash-chain flake?**  
A: Timestamps are normalized in canonical hashing for SQLite’s tz-naive roundtrip.

### Glossary

| Term | Meaning |
|------|---------|
| Ops-confirmed | Telemetry clearance held → ledger `ops_confirmed` |
| `data_insufficient` | Gaps / density fail — no ops confirm |
| `false_clear` | Cleared then fails without regress predicate fire |
| `ops_regressed` | Reopen predicate fires after verified |
| WorkflowEvent | L5→L6 append-only closure/alarm event |
| Dual-label | Separate ops vs bill badges on L6 DTOs |
| Outbox | Durable downstream delivery table |
| SSOT | Platform truth in `external/` submodule |

---

## 16. Authority & further reading

Read in order before changing L5 semantics:

1. [`external/technical/layers/L5-closure-and-verification.md`](external/technical/layers/L5-closure-and-verification.md)  
2. [`external/technical/layers/L6-experience-and-integration.md`](external/technical/layers/L6-experience-and-integration.md) §3–4 (consumer expectations)  
3. ADR-019 · ADR-020 · ADR-021 · ADR-013 under `external/decisions/`  
4. [`external/handoff/stamped-l5-architecture-handoff.md`](external/handoff/stamped-l5-architecture-handoff.md)  
5. [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) · [`DECISIONS.md`](DECISIONS.md) · [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md)  
6. [`AGENTS.md`](AGENTS.md) — agent/human contributor contract  

License / product branding: Stamped Energy L5 consumer (`stamped-l5` package name; GitHub repo may remain `closure-verification` per DEC-002).
