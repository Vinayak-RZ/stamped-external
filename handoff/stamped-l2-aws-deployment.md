# stamped-l2 — AWS deployment (cost-first P0)

> **Audience:** Engineers and agents deploying `stamped-l2` on AWS.  
> **Scope:** **`cloud` deployment mode only** — see [ADR-010](../decisions/ADR-010-deployment-profiles-and-portability.md) for `local` / `local-dashboard` compose profiles.  
> **Budget context:** [ADR-002](../decisions/ADR-002-build-all-aws-networking.md) targets **≤ ₹15–25k/month** total AWS at ≤10 pilot plants. L2 is one slice (~₹3–4.5k).  
> **Charter:** [ADR-009](../decisions/ADR-009-stamped-l2-repo-charter.md)

---

## 1. P0 footprint summary

| Component | AWS service | Sizing | Est. monthly (ap-south-1) |
| --- | --- | --- | --- |
| Database | **RDS PostgreSQL 16** + Timescale extension | **`db.t4g.small` Single-AZ**, gp3 50 GB | ~₹1.5–2.5k (L2 share of shared instance) |
| L2 compute | **ECS Fargate** | 1 task, **0.25 vCPU / 512 MB**, colocated ingest + query-api | ~₹1–1.5k |
| Storage | gp3 (allocated on shared RDS) | 50 GB prorated | ~₹300–500 |
| Backups | RDS automated | 7-day retention, within free window | ₹0 |
| Secrets | SSM Parameter Store | Free tier | ₹0 |
| **L2 total** | | | **~₹3–4.5k (~$35–55)** |

At 1–3 plants and <100 rows/s ingest, this is within the L2 research envelope. **Do not** provision P2 sizing (4 vCPU + read replica ≈ ₹1.3–1.9L/mo) until upgrade triggers fire.

---

## 2. Shared RDS pattern

connectors-cloud and stamped-l2 share **one RDS instance** but **separate databases** — ADR-008 table isolation preserved.

```
RDS instance: stamped-pilot-db (db.t4g.small, Single-AZ, ap-south-1)
├── database: connectors_cloud   ← L1 outbox (connectors-cloud packages/ingest, relay)
└── database: stamped_l2         ← L2 six schemas (stamped-l2 packages/ingest, query-api)
```

| Property | connectors_cloud | stamped_l2 |
| --- | --- | --- |
| Owner repo | connectors-cloud | stamped-l2 |
| Extensions | None required | `timescaledb` |
| Connection env | `DATABASE_URL` in cloud ingest/relay | `L2_DATABASE_URL` in L2 services |
| Blast radius | Outbox lag if L2 slow | Query load if cloud hammers same CPU |

**When to split:** CPU >70% sustained for 7 days, storage >80%, or enterprise contract requires dedicated PITR/isolation.

---

## 3. RDS configuration

| Setting | P0 value | Notes |
| --- | --- | --- |
| Engine | PostgreSQL **16** | Avoid EOL versions (Extended Support surcharges) |
| Instance | **db.t4g.small** (Graviton, 2 vCPU, 2 GiB RAM) | Upgrade path: db.t4g.medium |
| AZ | **Single-AZ** | Multi-AZ when pilot SLA requires |
| Storage | **gp3**, 50 GB, autoscaling off initially | Monitor; enable at 70% |
| Extension | `CREATE EXTENSION timescaledb;` on `stamped_l2` only | Verify version supports P0 caggs before prod |
| Backups | Automated, 7 days | PITR enabled (default on RDS) |
| Encryption | At rest (AES-256), TLS in transit | CMK when enterprise asks |
| Region | **ap-south-1** (Mumbai) | [ADR-004](../decisions/ADR-004-compliance-driven-architecture.md) residency |

### Parameter group hints

- `shared_preload_libraries = 'timescaledb'`
- `max_connections` — default OK for pilot; pool via PgBouncer only if connection count grows (P1)

---

## 4. ECS Fargate (L2 services)

**P0 cost mode:** One task definition runs both processes (supervisor or combined FastAPI app with ingest + query routers).

| Setting | P0 value |
| --- | --- |
| CPU | 256 (0.25 vCPU) |
| Memory | 512 MB |
| Launch type | Fargate |
| Networking | Same VPC as connectors-cloud; **public subnet + strict SG** (no NAT Gateway) |
| Health check | `GET /health` on port 8080 |
| Logs | CloudWatch Logs, ap-south-1 |

**Environment variables (SSM or task def):**

| Var | Example | Purpose |
| --- | --- | --- |
| `L2_DATABASE_URL` | `postgresql://l2_app:***@stamped-pilot-db.../stamped_l2` | App role, INSERT+SELECT on L2 schemas |
| `L2_INGEST_SERVICE_KEY` | (secret) | Validates `X-Service-Key` from connectors-cloud relay |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | (optional P1) | Traces |

**P1 isolation mode:** Split into `stamped-l2-ingest` and `stamped-l2-query` task definitions when ingest p95 lag >2 min due to query load.

---

## 5. Explicitly excluded (P0)

| Service | Why excluded | Revisit when |
| --- | --- | --- |
| Aurora | ~70% premium vs RDS Postgres | Never at seed stage |
| Tiger Cloud managed | ₹8k+/mo | Fleet >50 plants |
| MSK / Redpanda | HTTP ingest sufficient | L3 stream processors need fan-out |
| ElastiCache / Redis | No measured cache miss problem | Query p95 breach under load |
| Read replica | Pilot read load fits primary | Dashboard CPU >30% of instance |
| NAT Gateway | ~₹2.5k+/mo per AZ | Enterprise requires private-only subnets |
| S3 baseline artefacts | JSONB params sufficient P0 | Pickled models or WORM ledger export (P1) |
| Multi-AZ RDS | 2× instance cost | Signed pilot SLA or >10 plants |

---

## 6. Upgrade triggers (from ADR-002)

| Signal | Action |
| --- | --- |
| RDS CPU >70% sustained (7d) | Scale to `db.t4g.medium` |
| Storage >80% | Increase gp3 allocation or enable autoscaling |
| Ingest lag p95 >2 min | Split Fargate ingest vs query-api |
| >30 plants or Multi-AZ SLA | Multi-AZ RDS + read replica for dashboards |
| Enterprise isolation contract | Clone `stamped_l2` to dedicated RDS instance |
| Fan-out to multiple L3 consumers | Introduce Redpanda; keep HTTP ingest as alternate ingress |
| Query benchmark breach 2 months | Evaluate ClickHouse sidecar or Parquet cold tier (P2+) |

---

## 7. Local / CI parity

**`local` / `local-dashboard` modes:** Use [deploy/profiles/local.yml](../../deploy/profiles/local.yml) — not this AWS doc.

Docker Compose (`deploy/docker-compose.l2.yml` or profiles) must mirror production semantics:

- `timescale/timescaledb:latest-pg16` image
- Database `stamped_l2` with Timescale enabled
- ingest on `:8090` (same port as connectors-cloud mock-l2 for drop-in E2E)

Joint E2E: connectors-cloud compose with `L2_INGEST_URL=http://host.docker.internal:8090/v1/ingest/records`.

---

## 8. Terraform stub layout

```text
deploy/terraform/
├── main.tf           # provider aws ap-south-1
├── rds.tf            # shared instance OR data source if owned by infra repo
├── ecs.tf            # Fargate service + task def
├── ssm.tf            # L2_INGEST_SERVICE_KEY, DATABASE_URL refs
├── security_groups.tf
└── variables.tf      # environment, instance_class default db.t4g.small
```

**Note:** If a central infra repo owns the shared RDS, stamped-l2 Terraform only provisions ECS + IAM + SSM references.

---

## 9. Cost comparison (decision record)

| Option | Est. L2 monthly | Verdict |
| --- | --- | --- |
| **A — Shared RDS db.t4g.small + 1 Fargate** | ~₹3–4.5k | **Selected** |
| B — Dedicated RDS db.t4g.micro | ~₹2–3k | Risky RAM for hypertables |
| C — EC2 t4g.small Docker Timescale | ~₹2k | Reject for prod (ops burden) |
| D — Tiger Cloud / Aurora | ₹8k+ | Over budget |

---

## Changelog

| Date | Change |
| --- | --- |
| 2026-07-12 | Initial cost-first AWS profile for stamped-l2 P0 |
| 2026-07-12 | Scoped to `cloud` mode; local compose in deploy/profiles/ |
