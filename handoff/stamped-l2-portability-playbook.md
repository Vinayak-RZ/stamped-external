# stamped-l2 — Cloud + air-gap portability playbook

> **Authority:** [ADR-010](../decisions/ADR-010-deployment-profiles-and-portability.md) · [ADR-009](../decisions/ADR-009-stamped-l2-repo-charter.md)  
> **Repo:** `Vinayak-RZ/universal-repositary`

---

## 1. Current state (from README + audit)

**Repo:** This workspace (`universal-repositary`) — handoff package present; **no `packages/` yet**.

| Area | `cloud` mode today | Gap for `local*` |
|------|-------------------|------------------|
| ingest | Designed for ECS Fargate | Compose service `:8090` |
| query-api | Colocated Fargate | Compose service `:8091` |
| Database | RDS + Timescale | `timescale/timescaledb` container |
| AWS SDK | Terraform narrative only | Enforce zero boto3 in `packages/` |
| Backup | RDS PITR | `pg_dump` + volume snapshots |
| Joint E2E | mock-l2 in cloud repo | `deploy/profiles/local.yml` full stack |

### Audit appendix

```text
Audit checklist (stamped-l2)
├── README stated deployment model     → AWS cost-first (ADR-009)
├── deploy/ directory inventory        → profiles/ sketch pending
├── AWS-specific dependencies          → Terraform only (target)
├── Hardcoded external URLs            → none expected in L2 (no LLM)
├── MQTT broker assumptions            → N/A — HTTP ingest only
├── Secrets management path            → SSM → env/file for local
├── OTA/update mechanism               → migration SQL in releases
└── Existing compose vs prod gap       → docker-compose.l2.yml handoff ref
```

**Gap matrix:**

| Capability | `cloud` | `local` | Change required |
|------------|---------|---------|-----------------|
| HTTP ingest | Designed | Not built | P0 implementation |
| Query API | Designed | Not built | P0 implementation |
| Timescale schema | Documented | Not built | migrations package |
| Compose full stack | Sketch | Not built | `deploy/profiles/local.yml` |
| Zero egress | N/A | Target | No outbound calls in packages |

---

## 2. Target: mode support matrix

| Service | `local` | `local-dashboard` | `cloud` |
|---------|---------|-------------------|---------|
| stamped-l2-ingest | compose :8090 | compose | Fargate |
| stamped-l2-query-api | compose :8091 | compose | Fargate |
| timescaledb | compose | compose | RDS |
| stamped-l6 (reads query-api) | — | compose | Vercel/AWS |
| local-llm | compose (L3 consumer) | compose | — |

---

## 3. Architecture changes

1. **12-factor app tier** — `L2_DATABASE_URL`, `L2_INGEST_SERVICE_KEY` from env only.
2. **Terraform isolation** — `deploy/terraform/aws/` for `cloud`; never import boto3 in `packages/`.
3. **Master compose** — stamped-l2 owns `deploy/profiles/local.yml` orchestrating L1+L2+L3 LLM slot.
4. **Parity with mock-l2** — ingest must match connectors-cloud `mocks/stamped-l2/` responses before cutover.

---

## 4. File-by-file change list

| Path | Action | Detail |
|------|--------|--------|
| `deploy/profiles/local.yml` | **add** | Full stack master compose |
| `deploy/profiles/local-dashboard.yml` | **add** | extends local + stamped-l6 |
| `deploy/profiles/cloud.yml` | **add** | Terraform pointer |
| `deploy/profiles/ARCHITECTURE.md` | **add** | Wiring + env guide |
| `packages/ingest/` | **add** | HTTP ingest (blocked until R-phase merges) |
| `packages/query-api/` | **add** | Read API |
| `packages/migrate/` | **add** | SQL migrations |
| `deploy/terraform/aws/` | **add** | RDS + ECS for `cloud` |
| `.env.example` | **add** | Mode vars |
| `docs/egress-inventory.md` | **add** | Should be empty for L2 |
| `scripts/egress-check.sh` | **add** | CI gate |

---

## 5. New env vars and defaults per profile

| Variable | `local` default | `cloud` default |
|----------|-----------------|-----------------|
| `STAMPED_DEPLOYMENT_MODE` | `local` | `cloud` |
| `L2_DATABASE_URL` | `postgresql://l2:l2@timescaledb:5432/stamped_l2` | RDS via SSM |
| `L2_INGEST_SERVICE_KEY` | dev secret | SSM |
| `L2_INGEST_PORT` | `8090` | `8090` |
| `L2_QUERY_PORT` | `8091` | `8080` (or split P1) |

---

## 6. deploy/profiles/ layout

```text
deploy/profiles/
├── ARCHITECTURE.md
├── local.yml              # mosquitto, L1, L2, minio, local-llm
├── local-dashboard.yml    # local.yml + stamped-l6
└── cloud.yml              # points to deploy/terraform/aws/
```

---

## 7. Egress inventory (repo-specific)

| Call | Package | `local` | Notes |
|------|---------|---------|-------|
| HTTP ingest | ingest | Inbound only | cloud relay POST |
| Query API | query-api | Internal consumers | L3/L6 on compose network |
| External LLM | — | **None** | L2 has no LLM |
| OTel | optional | Local collector or off | P1 |

**Expected:** L2 egress inventory is **empty** in `local` mode.

---

## 8. CI gates

- [ ] Dedupe golden parity with connectors-cloud
- [ ] `scripts/egress-check.sh` — must pass with empty inventory
- [ ] `rg boto3 packages/` — fail if matches
- [ ] Compose E2E: relay POST → inbox → store table → query GET
- [ ] RLS suite on tenant tables

---

## 9. OTA / update bundle process

**`cloud`:** ECS rolling deploy + RDS migration via `packages/migrate`.

**`local`:** Release bundle includes:

```text
stamped-l2-release-{version}.tar.gz
├── images/stamped-l2-ingest-{digest}.tar
├── images/stamped-l2-query-api-{digest}.tar
├── images/timescaledb-pinned.tar
├── sql/migrations/
├── external/contracts/ (pinned)
└── checksums.sha256
```

Run migrations before bringing up new containers.

---

## 10. Testing: E2E per profile

```bash
# local — full stack
export STAMPED_DEPLOYMENT_MODE=local
docker compose -f deploy/profiles/local.yml up -d
# connectors-cloud relay with L2_INGEST_URL=http://stamped-l2-ingest:8090/v1/ingest/records
curl http://localhost:8091/v1/plants/{plant}/bills/{bill}/lines

# local-dashboard
docker compose -f deploy/profiles/local-dashboard.yml up -d
# stamped-l6 loads dashboard reading query-api

# cloud — Terraform apply + existing AWS scripts
```

---

## 11. Phase breakdown

| Phase | Ships |
|-------|-------|
| **R-phase** | Playbooks, profiles sketch, ADR-010 (this doc) |
| **P0-A** | ingest + measurement hypertable + bill_line + query-api stub |
| **P0-B** | RLS, graph stub, joint E2E, real relay cutover |
| **P1** | `pg_dump` backup cron; split ingest/query Fargate |

**Blocked:** `packages/` implementation until R-phase PR merges.

---

## 12. Non-goals

- boto3 in application packages
- MQTT subscriber in L2
- Neo4j, Feast, Redpanda at P0
- Simulating full AWS in local compose (`cloud.yml` is reference only)
