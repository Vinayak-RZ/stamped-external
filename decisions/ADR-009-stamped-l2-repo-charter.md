# ADR-009: stamped-l2 repo charter — Universal Repository, cost-first AWS

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-12 |
| **Deciders** | Vinayak (product), engineering |
| **Related** | [ADR-008](ADR-008-layer-repo-topology-and-interfaces.md) · [ADR-002](ADR-002-build-all-aws-networking.md) · [L2 spec](../technical/layers/L2-universal-repository.md) · [Handoff spec](../handoff/stamped-l2-spec.md) |

---

## Context

Stamped L2 (Universal Repository) holds six data stores — time-series, energy graph, commercial context, features, baselines, and M&V ledger — that every downstream intelligence layer depends on. ADR-008 places L2 in its own repo (`stamped-l2`). L1 cloud ingest (`connectors-cloud`) is complete for pilot prep and relays `StampedRecordEnvelope` records over HTTP.

This ADR records **repo topology**, **database technology**, **AWS cost posture**, and **P0 transport** so the `stamped-l2` workspace can bootstrap without re-deciding architecture.

---

## Decision summary

| # | Topic | Decision |
| --- | --- | --- |
| 1 | Repo count | **One repo:** `stamped-l2` — all six stores as Postgres **schemas**, not separate repos |
| 2 | Database | **RDS PostgreSQL 16 + TimescaleDB extension**, database `stamped_l2`, **ap-south-1** |
| 3 | RDS sizing (P0) | **`db.t4g.small` Single-AZ**, gp3 50 GB — **shared RDS instance** with connectors-cloud (separate DB `connectors_cloud`) |
| 4 | L1 transport (P0) | **HTTP POST** `/v1/ingest/records` — no Redpanda/MSK at pilot |
| 5 | Compute (P0) | **1× ECS Fargate** 0.25 vCPU / 512 MB — ingest + query-api **colocated** |
| 6 | Monorepo layout | `packages/ingest`, `packages/query-api`, `packages/migrate`, `packages/jobs` (P1) |
| 7 | Tenancy | Shared schema + `org_id` + **RLS** on all tenant tables |
| 8 | Graph / features | Postgres adjacency + caggs — **no** Neo4j, **no** Feast in v1 |
| 9 | Cost ceiling | L2 slice **~₹3–4.5k/month** at P0 — see [AWS deployment handoff](../handoff/stamped-l2-aws-deployment.md) |

---

## 1. One repo, six schemas

```
stamped_l2 (database)
├── ingest      — l1_processed_inbox, l1_ingest_audit
├── telemetry   — measurement hypertable, event hypertable, caggs
├── graph       — asset, asset_edge
├── commercial  — tariff_version, bill, bill_line, shift_calendar, emission_factor
├── features    — derived metric tables (P1 jobs)
├── baselines   — baseline (versioned, lock-on-cite)
└── ledger      — mv_ledger (append-only)
```

**Rationale:** Stamped's constraint is breadth of context (tariffs, topology, baselines, audit), not point volume. One engine enables FK joins between `ledger.mv_ledger.bill_line_refs` and `commercial.bill_line` in a single transaction.

**Rejected:** Six micro-repos (telemetry-repo, graph-repo, …) — cross-store consistency glue and 6× backup stories for zero benefit at ≤100k series.

---

## 2. Technology choices

| Store | Technology | Rejected alternative |
| --- | --- | --- |
| Time-series | TimescaleDB hypertables + continuous aggregates | InfluxDB (licensing risk), ClickHouse (premature second engine) |
| Graph | Postgres adjacency + recursive CTEs; in-memory mirror in L3 | Neo4j at ≤500 nodes/plant |
| Features | Caggs + SQL jobs with PIT discipline | Feast/Tecton at <10 models |
| Ledger | Append-only Postgres + REVOKE + trigger | Event-sourcing framework |

Research authority: [L2-universal-repository.md](../technical/layers/L2-universal-repository.md).

---

## 3. Cost-first AWS (P0)

Align with [ADR-002](ADR-002-build-all-aws-networking.md) total AWS budget **≤ ₹15–25k/month** at ≤10 pilot plants.

| Service | P0 choice | Explicitly excluded |
| --- | --- | --- |
| Database | Shared RDS `db.t4g.small` Single-AZ | Aurora, Tiger Cloud, Multi-AZ, read replica |
| Compute | 1 Fargate task (colocated) | Second task until ingest lag >2 min |
| Messaging | HTTP ingest only | MSK, Redpanda, IoT Core |
| Cache | None | ElastiCache |
| NAT | None (public subnet + SG) | NAT Gateway per AZ |
| Object storage | Defer S3 artefacts | — |

**Upgrade triggers:** CPU >70% sustained → `db.t4g.medium`; ingest lag >2 min → split Fargate; enterprise isolation → dedicated RDS for L2.

Full sizing table: [stamped-l2-aws-deployment.md](../handoff/stamped-l2-aws-deployment.md).

---

## 4. L1 boundary

| Rule | Detail |
| --- | --- |
| Sole L2 writer | Only `stamped-l2` `packages/ingest` writes L2 tables |
| Upstream | `connectors-cloud` relay POSTs `StampedRecordEnvelope` |
| Idempotency | `ingest.l1_processed_inbox` PRIMARY KEY on `dedupe_key` |
| No cross-repo SQL | L3+ use `stamped-l2` query API — never direct DB access |
| Lab shortcut | Edge `connectors-ingest` → Timescale is **deprecated for `cloud` mode** once L2 E2E green; **valid in `local` mode** per [ADR-010](ADR-010-deployment-profiles-and-portability.md) |

Contract: [stamped-l2-l1-consumer-contract.md](../handoff/stamped-l2-l1-consumer-contract.md).

---

## 5. P0 scope (staged bootstrap)

**Phase A (weeks 1–4):** inbox + measurement hypertable + bill_line + minimal query API + docker-compose local stack.

**Phase B (weeks 5–8):** minimal graph, JVVNL tariff seed, baselines stub, ledger immutability, RLS suite, joint E2E with connectors-cloud.

**P0 exit:** First evidence pointer resolves (tag window → bill line); connectors-cloud relay targets real L2 instead of mock-l2; ADR-008 step-2 criterion met.

Build order: [stamped-l2-build-order.md](../handoff/stamped-l2-build-order.md).

---

## 6. Alternatives considered

| Option | Rejected because |
| --- | --- |
| L2–L6 monolith | User chose layer-per-repo (ADR-008) |
| Postgres 17 + Tiger Cloud | Cost (~₹8k+/mo) vs shared RDS (~₹3–4.5k L2 slice) |
| Redpanda P0 | No L3 stream consumer yet; HTTP matches cloud relay today |
| EC2 self-hosted Timescale | Cheapest $ but ops burden (patching, PITR) unacceptable for prod pilot |
| Dedicated RDS for L2 P0 | ~2× DB cost; shared instance preserves ADR-008 table isolation |

---

## 7. Consequences

- Next workspace adds **stamped-platform** submodule at `external/` and bootstraps `stamped-l2` repo ([ADR-011](ADR-011-stamped-platform-submodule-distribution.md)).
- connectors-cloud `mocks/stamped-l2` remains reference until real L2 passes parity tests.
- Timescale extension version on RDS must be verified before Terraform apply.
- Single-AZ acceptable for pilot; document downtime window for enterprise FAQ.

---

## Changelog

| Date | Change |
| --- | --- |
| 2026-07-12 | Initial ADR — repo charter, cost-first AWS, HTTP P0 ingest |
| 2026-07-12 | ADR-010 addendum — portability NFR, compose profiles, no AWS SDK in packages/ |

---

## 8. ADR-010 addendum — portability NFR (2026-07-12)

stamped-l2 must support all three deployment modes per [ADR-010](ADR-010-deployment-profiles-and-portability.md).

| Mode | Database | Compute | Backup |
| --- | --- | --- | --- |
| **`cloud`** | RDS `stamped_l2` + Timescale (this ADR §3) | ECS Fargate colocated ingest + query-api | RDS PITR |
| **`local`** | `timescale/timescaledb` container | Compose `stamped-l2-ingest` + `stamped-l2-query-api` | `pg_dump` cron + volume snapshots |
| **`local-dashboard`** | Same as `local` | Same + stamped-l6 reads query-api | Same |

**Portability rules:**

1. **Zero `boto3` / AWS SDK in `packages/`** — Terraform under `deploy/terraform/aws/` only; app tier uses env vars.
2. **`deploy/profiles/`** — `local.yml`, `local-dashboard.yml`; `cloud.yml` references Terraform.
3. **Egress inventory** — CI blocks undeclared external calls on `local` paths (see `docs/architecture/egress-inventory-template.md` in consumer repos).
4. **Contracts invariant** — `external/contracts/`, HTTP ingest, query API unchanged across modes.

Playbook: [stamped-l2-portability-playbook.md](../handoff/stamped-l2-portability-playbook.md).
