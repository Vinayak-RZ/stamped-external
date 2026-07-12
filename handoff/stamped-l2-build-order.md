# stamped-l2 — P0 build order

> **Aligned with:** [ADR-008 §4](../decisions/ADR-008-layer-repo-topology-and-interfaces.md), [ADR-009](../decisions/ADR-009-stamped-l2-repo-charter.md), [L2 spec §6](../technical/layers/L2-universal-repository.md)  
> **Scope:** Staged bootstrap — Phase A (weeks 1–4), Phase B (weeks 5–8)

---

## Exit criterion (P0 complete)

- connectors-cloud relay targets **real** stamped-l2 (not mock-l2)
- Golden dedupe keys match [dedupe_golden.json](../contracts/fixtures/dedupe_golden.json)
- First **evidence pointer** resolves: incomer measurement window ↔ `commercial.bill_line`
- RLS probe suite green
- `./scripts/e2e-l1-ingest.sh` green **3× consecutive** with connectors-cloud stack

---

## Phase A — Ingest core (weeks 1–4)

| Step | Deliverable | Work items | Exit test |
| --- | --- | --- | --- |
| **A1** | Repo scaffold | Init `stamped-l2`, copy `external/`, `AGENTS.md`, CI stub | `git status` clean structure |
| **A2** | Local stack | `deploy/docker-compose.l2.yml`: TimescaleDB pg16, ingest :8090 | `psql` + `\dx timescaledb` |
| **A3** | Migrations bootstrap | `packages/migrate`: schemas, `ingest.l1_processed_inbox` | Migration applies cleanly |
| **A4** | Dedupe tests | `test_dedupe_golden.py` vs fixtures | 4/4 hashes match cloud |
| **A5** | POST handler | Envelope validate, inbox insert, 201/200 responses | Parity with mock-l2 |
| **A6** | Measurement router | Demux → `telemetry.measurement` hypertable | Golden measurement round-trip |
| **A7** | Bill_line router | Demux → `commercial.bill` + `bill_line` | Golden bill_line queryable |
| **A8** | 15min cagg | `telemetry.agg_15min` + refresh policy | 30-day profile query works |
| **A9** | Query API (thin) | GET measurements, GET bill lines, GET health | curl smoke tests pass |

### Phase A commands

```bash
# Local stack
docker compose -f deploy/docker-compose.l2.yml up --build --wait

# Migrations
cd packages/migrate && ./apply.sh

# Unit + contract
cd packages/ingest && pytest tests/unit tests/contract -q
cd packages/query-api && pytest tests/unit -q

# E2E (L2 only)
./scripts/e2e-l1-ingest.sh
```

---

## Phase B — Platform hardening (weeks 5–8)

| Step | Deliverable | Work items | Exit test |
| --- | --- | --- | --- |
| **B1** | Graph seed | `graph.asset` incomer per pilot plant | measurement.asset_id FK valid |
| **B2** | JVVNL tariff | `seed_jvvnl_tariff.sql` | Worked bill ±0.5% test |
| **B3** | Baselines stub | `baselines.baseline` + lock trigger | UPDATE locked row raises |
| **B4** | Ledger immutability | `ledger.mv_ledger` + REVOKE + trigger | DELETE fails in test |
| **B5** | RLS suite | Policies on all `org_id` tables | Cross-tenant probe = 0 rows |
| **B6** | Event router | `telemetry.event` if SCADA events flowing | Optional — skip if no events |
| **B7** | Joint E2E | `./scripts/e2e-l1-ingest.sh --with-cloud` | 3× green |
| **B8** | AWS stub | Terraform ECS + shared RDS data source | Plan-only OK for P0 |
| **B9** | Deprecate lab path | Doc: disable edge `connectors-ingest` direct Timescale | Runbook updated |

---

## E2E with connectors-cloud

### Setup

```bash
# Terminal 1 — L2
cd stamped-l2
docker compose -f deploy/docker-compose.l2.yml up --build

# Terminal 2 — cloud (point at L2)
cd connectors-cloud
export L2_INGEST_URL=http://host.docker.internal:8090/v1/ingest/records
cd deploy && docker compose -f docker-compose.cloud.yml up --build
```

### Manual smoke (bill path)

```bash
mosquitto_pub -h 127.0.0.1 -p 1883 -q 1 \
  -t "stamped/v1/org_test/plant_test/bills" \
  -m "$(cat external/contracts/fixtures/bill_line.valid.json)"

# Wait ~10s for relay, then:
psql "$L2_DATABASE_URL" -c \
  "SELECT record_type, dedupe_key FROM ingest.l1_processed_inbox;"

curl -s "http://localhost:8091/v1/plants/plant_test/bills/<bill_id>/lines"
```

### Automated

```bash
./scripts/e2e-l1-ingest.sh --with-cloud
```

Script must assert:

1. HTTP 201 on first envelope POST
2. HTTP 200 on duplicate POST
3. Row count in inbox = 1
4. Row in `commercial.bill_line` or `telemetry.measurement` as appropriate
5. Query API returns inserted data

---

## Test gates (CI)

| Gate | Command | Blocks merge if |
| --- | --- | --- |
| Contracts | `./scripts/contract-check.sh` | Schema break |
| Dedupe golden | `pytest packages/ingest/tests/test_dedupe_golden.py` | Hash mismatch vs cloud |
| Ingest unit | `pytest packages/ingest/tests/unit` | Logic fail |
| RLS probes | `pytest packages/migrate/tests/test_rls.py` | Cross-tenant leak |
| E2E local | `./scripts/e2e-l1-ingest.sh` | Ingest regression |

---

## Mock-l2 parity checklist

Before cutting cloud over from `mocks/stamped-l2`:

- [ ] Same port 8090 default
- [ ] Same response body shape `{inserted, dedupe_key}`
- [ ] Same status codes 201/200/400
- [ ] Inbox table semantics identical
- [ ] cloud `./scripts/e2e-cloud-ingest.sh` passes against real L2

---

## P1 preview (after P0 exit — do not start early)

| Item | Trigger |
| --- | --- |
| Split Fargate ingest vs query | Ingest lag >2 min |
| `production_record` + SEC features | L3 SEC engine starts |
| Redpanda ingress | L3 stream processor needs fan-out |
| Ledger hash chain | First customer-billing-relevant entry |
| Read replica | Dashboard query CPU >30% |

---

## Risks during build

| Risk | Mitigation |
| --- | --- |
| Timescale extension missing on RDS | Verify in ap-south-1 before Terraform apply |
| asset_id FK failures | Seed incomer before measurement E2E |
| Shared RDS CPU contention | Monitor; split instance per ADR-002 trigger |
| Bill batch NDJSON | Implement single-line only; match cloud P0 |

---

## Changelog

| Date | Change |
| --- | --- |
| 2026-07-12 | Initial P0 build order for stamped-l2 |
