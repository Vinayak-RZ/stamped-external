# stamped-l2 — Agent onboarding

Paste into **`AGENTS.md`** in the new repository.

---

```markdown
# stamped-l2 — Agent Mode

**Layer:** L2 Universal Repository — six data stores, L1 HTTP ingest consumer, internal query API.  
**NOT in scope:** MQTT ingest, edge agents, bill OCR, L3–L6 intelligence, customer dashboard.

## Read first

1. [external/handoff/stamped-l2-spec.md](external/handoff/stamped-l2-spec.md) — repo charter
2. [external/handoff/stamped-l2-ecosystem-integration.md](external/handoff/stamped-l2-ecosystem-integration.md) — how all repos connect
3. [external/handoff/stamped-l2-l1-consumer-contract.md](external/handoff/stamped-l2-l1-consumer-contract.md) — POST /v1/ingest/records
4. [external/handoff/stamped-l2-database-schema.md](external/handoff/stamped-l2-database-schema.md) — six schemas, DDL, RLS
5. [external/handoff/stamped-l2-build-order.md](external/handoff/stamped-l2-build-order.md) — phased P0 tasks
6. [external/handoff/stamped-l2-aws-deployment.md](external/handoff/stamped-l2-aws-deployment.md) — cost-first AWS sizing
7. [external/architecture/layer-interfaces-l2.md](external/architecture/layer-interfaces-l2.md) — boundary authority
8. [external/technical/layers/L2-universal-repository.md](external/technical/layers/L2-universal-repository.md) — research depth
9. [external/decisions/ADR-009-stamped-l2-repo-charter.md](external/decisions/ADR-009-stamped-l2-repo-charter.md)

**Upstream L1 (already built):** connectors-cloud (relay ready) · connectors-edge (MQTT) · connectors-bill (BillLine publish).  
**Downstream:** stamped-l3 … stamped-l6 — consume query API only.

| Package | Role |
| --- | --- |
| `packages/ingest` | L1 consumer — POST /v1/ingest/records, inbox dedupe, store routers |
| `packages/query-api` | Internal read API for L3/L4/L6 |
| `packages/migrate` | SQL migrations, RLS, Timescale hypertables |
| `packages/jobs` | Cagg refresh, feature batch (P1) |

## Rules

- **Sole writer** to L2 tables — only `packages/ingest` inserts store data from L1 path.
- Dedupe keys must match [dedupe_golden.json](external/contracts/fixtures/dedupe_golden.json) — same as connectors-cloud.
- L3+ **never** get `L2_DATABASE_URL` — query API only (ADR-008).
- Reach **mock-l2 parity** before cloud cutover — reference: connectors-cloud `mocks/stamped-l2/`.
- **Cost-first P0:** shared RDS `db.t4g.small`, colocated Fargate task — see ADR-009.
- Schema changes: migrations in `packages/migrate`; RLS policy required for every new tenant table.
- Deprecated: edge lab `connectors-ingest` → Timescale — production path is cloud → L2 only.

## Verification

```bash
# Dedupe golden first
pytest packages/ingest/tests/test_dedupe_golden.py

# Local stack
docker compose -f deploy/docker-compose.l2.yml up --build --wait
cd packages/migrate && ./apply.sh
./scripts/e2e-l1-ingest.sh

# Joint with connectors-cloud
./scripts/e2e-l1-ingest.sh --with-cloud
```

## Upstream contract

connectors-cloud relay POSTs `StampedRecordEnvelope` to `/v1/ingest/records`.  
See [stamped-l2-upstream-context.md](external/handoff/stamped-l2-upstream-context.md).
```

---

## Bootstrap commands

```bash
mkdir stamped-l2 && cd stamped-l2
git init

# Add stamped-platform submodule (do not copy)
git submodule add https://github.com/vinayak-rz/stamped-external.git external
cd external && git checkout v2026.07.12 && cd ..

# AGENTS.md from section above
# README → point to external/handoff/README.md L2 section

# Clone connectors-cloud for E2E reference
git clone https://github.com/Vinayak-RZ/connectors-cloud ../connectors-cloud
```

---

## First implementation milestones

1. **docker-compose + Timescale** — local parity  
2. **Dedupe golden tests** — prove cloud alignment  
3. **POST /v1/ingest/records** — mock-l2 parity  
4. **measurement + bill_line routers** — golden fixtures  
5. **15min cagg + query API** — read path  
6. **RLS probe suite** — tenancy  
7. **Joint E2E** — cloud relay → real L2  

---

## Changelog

| Date | Change |
| --- | --- |
| 2026-07-12 | Initial agent onboarding for stamped-l2 |
