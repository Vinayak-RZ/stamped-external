# ADR-007: connectors-cloud repo charter — L1 cloud ingest only

| Field | Value |
| --- | --- |
| **Status** | Accepted (amended 2026-07-10) |
| **Date** | 2026-07-10 |
| **Deciders** | Vinayak (product), engineering |
| **Related** | [ADR-001](ADR-001-l1-repo-split-and-boundaries.md) · [ADR-003](ADR-003-connectors-edge-monorepo.md) · [ADR-008](ADR-008-layer-repo-topology-and-interfaces.md) · [Handoff spec](../handoff/connectors-cloud-downstream-context.md) |

---

## Context

ADR-001 defined L1 as multiple deployables: `connectors-edge` (OT streaming), `connectors-bill` (PDF/tariff), and a deferred cloud ingest consumer. ADR-003 placed an MVP `packages/connectors-ingest` inside the edge monorepo for lab E2E.

An initial draft of ADR-007 incorrectly placed L2–L6 inside `connectors-cloud`. **That is superseded.** Per product direction and [L1 spec §2.2](../technical/layers/L1-connect-and-normalise.md), L1's job ends at publishing four canonical record types onto the event bus. L2–L6 are **separate repositories**, each a deployable service that communicates only through versioned interface contracts ([ADR-008](ADR-008-layer-repo-topology-and-interfaces.md)).

---

## Decision summary

| # | Topic | Decision |
| --- | --- | --- |
| 1 | Repo identity | **`connectors-cloud`** — L1 cloud portion only |
| 2 | Scope | MQTT/HTTP ingest, schema validation, dedupe, quality flags, **L1→L2 boundary publish** |
| 3 | Out of scope | L2 Timescale schema, L3–L6 intelligence, dashboards, prescriptions |
| 4 | Monorepo layout | `packages/ingest` (primary) · optional `packages/relay` (outbox→bus) |
| 5 | L2–L6 repos | **Separate repos:** `stamped-l2` … `stamped-l6` (one layer per repo) |
| 6 | MVP in edge | `packages/connectors-ingest` retained for lab; **valid in `local` mode** ([ADR-010](ADR-010-deployment-profiles-and-portability.md)); deprecated for **`cloud` mode** once L2 E2E green |
| 7 | L1 contracts source | **`stamped-platform/contracts/`** via submodule ([ADR-011](ADR-011-stamped-platform-submodule-distribution.md)) |
| 8 | L1→L2 contract | Owned in `external/contracts/` as envelope + schemas; enforced in CI ([ADR-008](ADR-008-layer-repo-topology-and-interfaces.md)) |
| 9 | tag-mapping-api | **Stays in connectors-edge** per ADR-001 §5 |
| 10 | connectors-bill | **Separate repo** — publishes `BillLine` on same MQTT family; cloud ingest consumes |

---

## 1. Repo ecosystem (corrected)

| Repo | Layer | Owns | Does not own |
| --- | --- | --- | --- |
| **connectors-edge** | L1 plant | `edge-agent`, `tag-mapping-api`, `tag-mapping-ui`, L1 contract source, templates | Cloud ingest production, L2+ |
| **connectors-cloud** | L1 cloud | MQTT/HTTP ingest, validation, dedupe, outbox/boundary publish | Protocol drivers, L2 DB schema, L3–L6 |
| **connectors-bill** | L1 bill | PDF ingest, DISCOM templates, `BillLine` publish | Modbus, edge buffer |
| **stamped-l2** | L2 | Universal Repository — six stores, internal query APIs | Ingest, intelligence |
| **stamped-l3** | L3 | Intelligence engines, `Finding` emit | Ingest, prescriptions |
| **stamped-l4** | L4 | Prescription agent, `Prescription` emit | Workflow, dashboard |
| **stamped-l5** | L5 | Workflow, M&V, ledger append | UI, ingest |
| **stamped-l6** | L6 | Dashboard, public API, exports | OT connectors, TSDB writes |

---

## 2. connectors-cloud packages

| Package | Deploy | Responsibility |
| --- | --- | --- |
| `packages/ingest` | ECS Fargate satellite | Subscribe MQTT topics; HTTP Topology F backfill; validate JSON Schema; transport + business dedupe; write `l1_outbox` |
| `packages/relay` | Same task or sidecar (P1) | Drain outbox (`SKIP LOCKED`); publish to L2 ingress (bus or HTTP); at-least-once |

**Anti-pattern rejected:** ingest writing directly to L2 Timescale tables in production. The lab MVP (`measurements_raw`) is a **dev shortcut** until `stamped-l2` ships its consumer.

---

## 3. Integration contracts

| Contract | Document |
| --- | --- |
| MQTT plant ingress | [TOPICS.md](../contracts/TOPICS.md) |
| L1→L2 boundary envelope | [layer-interfaces-l2.md](../architecture/layer-interfaces-l2.md) §2 |
| L2–L6 inter-layer | [layer-interfaces-l2.md](../architecture/layer-interfaces-l2.md) §3–6 |
| OTA / mapping | tag-mapping-api in edge repo — unchanged |

---

## 4. Migration path

| Step | Owner |
| --- | --- |
| Bootstrap `connectors-cloud` from handoff spec | cloud |
| Copy `connectors-ingest` → `packages/ingest`; add validation + outbox | cloud |
| Bootstrap `stamped-l2` with L1 consumer + inbox dedupe | l2 |
| Edge lab compose: cloud ingest + l2 consumer (replace direct Timescale write) | edge + cloud + l2 |
| Remove `packages/connectors-ingest` from edge after 3 green E2E passes | edge |

---

## 5. Trade-off: L1→L2 transport (P0)

## Trade-off: L1→L2 event transport at pilot scale

**Decision:** Postgres transactional outbox in `connectors-cloud`; `stamped-l2` consumer with inbox dedupe.

**Option A — Outbox + polling/LISTEN:** Zero new infra; same PITR as data; `SKIP LOCKED` workers; at-least-once with idempotent L2 consumer. Pros: simple, matches [production engineering §3.1.2](../technical/cross-cutting/03-production-engineering.md). Cons: not a replayable log; ~10k msg/s ceiling.

**Option B — Redpanda/Kafka at day one:** Replayable log; fan-out ready. Pros: scale headroom. Cons: ops cost for 1–3 pilots; premature per L2 §3.1 P0 simplification.

**Default:** Option A until sustained >5k msg/s or second independent consumer of raw streams ([production engineering triggers](../technical/cross-cutting/03-production-engineering.md)).

**Override:** Set PRIORITY = SIMPLICITY (pilot) | AVAILABILITY (fleet fan-out).

---

## 6. Consequences

- Eight repo CI pipelines at full stack (edge, cloud, bill, l2–l6).
- Every cross-repo change requires contract compatibility CI (BACKWARD mode on JSON schemas).
- New workspace for cloud starts with handoff spec + ADR-007 + ADR-008 — not edge implementation archaeology.

---

## 7. Alternatives considered

| Option | Rejected because |
| --- | --- |
| connectors-cloud owns L2–L6 | Violates user's layer-per-repo microservice topology; blurs L1 completion boundary |
| Single monolith for L2–L6 | User explicitly chose separate operators/repos per layer |
| Ingest writes L2 tables directly | Couples L1 release to L2 schema; breaks repo boundary (distributed monolith) |

---

## 8. ADR-010 addendum — deployment modes (2026-07-12)

connectors-cloud must run in all three modes per [ADR-010](ADR-010-deployment-profiles-and-portability.md).

| Mode | Compute | MQTT broker | Postgres | Secrets | L2 relay |
| --- | --- | --- | --- | --- | --- |
| **`cloud`** | ECS Fargate | EC2 Mosquitto (ADR-002) | RDS `connectors_cloud` | SSM Parameter Store | `L2_INGEST_URL` → Fargate L2 |
| **`local`** | Compose `ingest` + `relay` | Compose `mosquitto` | Compose Postgres | `.env` / file mount | `L2_INGEST_URL` on Docker network |
| **`local-dashboard`** | Same as `local` | Same | Same | Same | Same |

**P0 orchestration:** Docker Compose only — no K3s. Playbook: [connectors-cloud-portability-playbook.md](../handoff/connectors-cloud-portability-playbook.md).

**Compose-first:** `deploy/profiles/local.yml` is the production path for `local*` modes; `deploy/docker-compose.cloud.yml` remains the `cloud` dev reference until AWS Terraform ships.
