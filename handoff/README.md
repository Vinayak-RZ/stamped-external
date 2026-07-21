# Handoff package — Stamped L1 + L2 bootstrap

> **Audience:** AI agents and engineers starting **`connectors-bill`**, **`stamped-l2`**, or sibling layer repos.  
> **Master product context:** [../technical/00-stamped-master-document.md](../technical/00-stamped-master-document.md)  
> **Distribution:** This folder is part of **[stamped-external](../README.md)** — mount as git submodule at `external/` ([ADR-011](../decisions/ADR-011-stamped-platform-submodule-distribution.md), [SUBMODULE.md](../SUBMODULE.md))

**Agent prompt for any consumer repo:** [consumer-platform-prompt.md](./consumer-platform-prompt.md) — paste into `AGENTS.md` in connectors-edge, stamped-l2, and future repos.

---

## Setup (do not copy — use submodule)

```bash
git submodule add https://github.com/vinayak-rz/stamped-external.git external
cd external && git checkout v2026.07.12 && cd ..
git submodule update --init --recursive
```

---

## stamped-l2 — read first (new workspace)

| # | Document | Purpose |
|---|----------|---------|
| 1 | [stamped-l2-spec.md](./stamped-l2-spec.md) | **Repo charter** — scope, packages, P0/P1 phases, exit criteria |
| 2 | [stamped-l2-ecosystem-integration.md](./stamped-l2-ecosystem-integration.md) | **How all eight repos connect** |
| 3 | [stamped-l2-l1-consumer-contract.md](./stamped-l2-l1-consumer-contract.md) | `POST /v1/ingest/records`, dedupe, demux routing |
| 4 | [stamped-l2-database-schema.md](./stamped-l2-database-schema.md) | Six Postgres schemas, P0 DDL, RLS, retention |
| 5 | [stamped-l2-build-order.md](./stamped-l2-build-order.md) | Phased P0 tasks + E2E with connectors-cloud |
| 6 | [stamped-l2-aws-deployment.md](./stamped-l2-aws-deployment.md) | **Cost-first AWS** — RDS, Fargate, upgrade triggers |
| 7 | [stamped-l2-upstream-context.md](./stamped-l2-upstream-context.md) | What L1 (edge/cloud/bill) already guarantees |
| 8 | [stamped-l2-query-api-sketch.md](./stamped-l2-query-api-sketch.md) | L3/L4 read contracts |
| 9 | [stamped-l2-agent-onboarding.md](./stamped-l2-agent-onboarding.md) | Paste into new repo `AGENTS.md` |
| 10 | [../architecture/layer-interfaces-l2.md](../architecture/layer-interfaces-l2.md) | **Boundary authority** L1↔L2↔L3 |
| 11 | [deployment-profiles.md](./deployment-profiles.md) | Three deployment modes + playbooks |
| 12 | [stamped-l2-portability-playbook.md](./stamped-l2-portability-playbook.md) | Air-gap / cloud portability |

Also read ADRs: [ADR-008](../decisions/ADR-008-layer-repo-topology-and-interfaces.md), [ADR-009](../decisions/ADR-009-stamped-l2-repo-charter.md), [ADR-010](../decisions/ADR-010-deployment-profiles-and-portability.md), [ADR-011](../decisions/ADR-011-stamped-platform-submodule-distribution.md).

### stamped-l2 one-line mission

**stamped-l2** is the **Universal Repository** — six data stores in one Postgres+TimescaleDB database, consuming `StampedRecordEnvelope` from **connectors-cloud** and serving read APIs to **stamped-l3…l6**.

### stamped-l2 bootstrap checklist

1. Add **stamped-platform** submodule at `external/` ([SUBMODULE.md](../SUBMODULE.md))
2. Clone **connectors-cloud** for E2E compose + `mocks/stamped-l2` reference
3. Run `external/scripts/contract-check.sh` before first HTTP ingest handler
4. Run L2 ingest on **port 8090** for drop-in replacement of mock-l2
5. Point cloud `L2_INGEST_URL` at real L2 when POST parity proven
6. Copy [layer-interfaces-l2.md](../architecture/layer-interfaces-l2.md) → `docs/architecture/layer-interfaces.md` (repo-local)

**Suggested repo name:** `stamped-l2` (GitHub: `Vinayak-RZ/universal-repositary`)

---

## connectors-bill — read first

| # | Document | Purpose |
|---|----------|---------|
| 1 | [connectors-bill-spec.md](./connectors-bill-spec.md) | **Repo charter** — scope, packages, build order, exit criteria |
| 2 | [connectors-bill-ecosystem-integration.md](./connectors-bill-ecosystem-integration.md) | **How all Stamped repos connect** |
| 3 | [connectors-cloud-downstream-context.md](./connectors-cloud-downstream-context.md) | What **connectors-cloud already accepts** (MQTT, dedupe, E2E) |
| 4 | [connectors-bill-ui-ux-charter.md](./connectors-bill-ui-ux-charter.md) | **Customer-facing UI** — mobile-first, multi-doc upload |
| 5 | [../design/forge-industrial-design-system.md](../design/forge-industrial-design-system.md) | **Forge Industrial v2.0** |
| 6 | [connectors-bill-agent-onboarding.md](./connectors-bill-agent-onboarding.md) | Paste into new repo `AGENTS.md` |
| 7 | [connectors-bill-portability-playbook.md](./connectors-bill-portability-playbook.md) | Air-gap / cloud portability |
| 8 | [../architecture/layer-interfaces-l2.md](../architecture/layer-interfaces-l2.md) | Boundary authority |

Also read ADRs: [ADR-001](../decisions/ADR-001-l1-repo-split-and-boundaries.md), [ADR-007](../decisions/ADR-007-connectors-cloud-repo-charter.md), [ADR-008](../decisions/ADR-008-layer-repo-topology-and-interfaces.md).

### connectors-bill one-line mission

**connectors-bill** turns **uploaded documents and photos** into validated **`BillLine`** records and publishes them on MQTT for **connectors-cloud** → **stamped-l2** — with a **customer-facing review UI**.

---

## connectors-edge / connectors-cloud

| Repo | Playbook |
|------|----------|
| connectors-edge | [connectors-edge-portability-playbook.md](./connectors-edge-portability-playbook.md) |
| connectors-cloud | [connectors-cloud-portability-playbook.md](./connectors-cloud-portability-playbook.md) |

---

## stamped-l3 (core / rulepacks / eval)

| # | Document | Purpose |
|---|----------|---------|
| 1 | [stamped-l3-build-order.md](./stamped-l3-build-order.md) | P0 build order across three L3 repos |
| 2 | [stamped-l3-dual-lane-consumer-prompt.md](./stamped-l3-dual-lane-consumer-prompt.md) | **Paste to core & rulepacks agents** after ADR-015/016 — submodule pin + dual-lane + attribution shadows |
| 3 | [stamped-l3-ops-clearance-consumer-prompt.md](./stamped-l3-ops-clearance-consumer-prompt.md) | **Paste to L3 agents** — Finding 1.1.0 `ops_clearance` + `alarm_hint` for L5 ops-first verification |

Authority ADRs: [ADR-012](../decisions/ADR-012-l3-artifact-repo-topology.md) · [ADR-015](../decisions/ADR-015-l3-dual-lane-lab-detections.md) · [ADR-016](../decisions/ADR-016-attribution-shadow-challengers.md) · [ADR-020](../decisions/ADR-020-l5-mv-claim-governance.md).

---

## stamped-l4 — read first

| # | Document | Purpose |
|---|----------|---------|
| 1 | [stamped-l4-architecture-handoff.md](./stamped-l4-architecture-handoff.md) | **Primary handoff** — dual-lane agent, adaptive RAG, T4 web, eval stack, L3 prompt |
| 2 | [../technical/layers/L4-knowledge-and-reasoning.md](../technical/layers/L4-knowledge-and-reasoning.md) | Architecture SSOT |
| 3 | [../decisions/ADR-017-l4-adaptive-retrieval-and-web-trust.md](../decisions/ADR-017-l4-adaptive-retrieval-and-web-trust.md) | Adaptive hybrid RAG + web trust tiers |
| 4 | [stamped-l4-build-order.md](./stamped-l4-build-order.md) | Superseded stub (redirects here) |
| 5 | [../consumers/stamped-l4/README.md](../consumers/stamped-l4/README.md) | Platform Lane A scaffold reference |

### stamped-l4 one-line mission

**stamped-l4** is the **Knowledge & Reasoning** layer — Finding → Prescription with template fast path + bounded LangGraph, adaptive RAG over industrial practice corpus, and OSS-first RAG/agent eval (Langfuse + Phoenix + DeepEval).

---

## stamped-l5 — consumer live (`closure-verification`)

| # | Document | Purpose |
|---|----------|---------|
| 1 | [../consumers/readmes/closure-verification.md](../consumers/readmes/closure-verification.md) | **Consumer README snapshot** — shipped L5 API/worker surface |
| 2 | [stamped-l5-architecture-handoff.md](./stamped-l5-architecture-handoff.md) | Platform handoff — runtime, modules, consistency |
| 3 | [stamped-l5-build-plan.md](./stamped-l5-build-plan.md) | Starter commit matrix (historical P0–P2) |
| 4 | [../technical/layers/L5-closure-and-verification.md](../technical/layers/L5-closure-and-verification.md) | Architecture SSOT |
| 5 | [../decisions/ADR-019-l5-runtime-and-consistency.md](../decisions/ADR-019-l5-runtime-and-consistency.md) | Runtime + L2 append protocol |
| 6 | [../decisions/ADR-020-l5-mv-claim-governance.md](../decisions/ADR-020-l5-mv-claim-governance.md) | Ops-first claim gates (`ops_confirmed`; bill deferred) |
| 7 | [../decisions/ADR-021-l5-notification-and-evidence.md](../decisions/ADR-021-l5-notification-and-evidence.md) | WhatsApp + evidence |
| 8 | [l6-counterfactual-display-stub.md](./l6-counterfactual-display-stub.md) | Modeled delay-cost display |

### stamped-l5 one-line mission

**stamped-l5** (`closure-verification`) is **Closure & Verification** — EMS alarm routing, ops-clearance verification, WhatsApp-first notification, calculated savings ledger (bill path deferred), and L2 append policy.

L6 consumer handoff remains empty until `stamped-l6` is planned beyond display stubs.

---

## Consumer README snapshots (L1–L4)

Mirrored root READMEs from live consumer repos (context only — canonical docs stay in each repo):

| Layer | Snapshot index |
|-------|----------------|
| L1–L4 | [../consumers/readmes/README.md](../consumers/readmes/README.md) |

L5 consumer README snapshot: [../consumers/readmes/closure-verification.md](../consumers/readmes/closure-verification.md) (architecture SSOT remains the L5 layer doc + ADRs).

---

## Contracts & fixtures (shared)

| Path | Use |
|------|-----|
| [../contracts/schemas/stamped-record-envelope.json](../contracts/schemas/stamped-record-envelope.json) | L1→L2 envelope |
| [../contracts/schemas/bill-line.json](../contracts/schemas/bill-line.json) | Canonical `BillLine` |
| [../contracts/schemas/measurement.json](../contracts/schemas/measurement.json) | Telemetry ingest |
| [../contracts/TOPICS.md](../contracts/TOPICS.md) | MQTT topic layout |
| [../contracts/fixtures/dedupe_golden.json](../contracts/fixtures/dedupe_golden.json) | Expected `sha256:` dedupe keys (cloud + L2 CI) |
| [../contracts/fixtures/bill_line.valid.json](../contracts/fixtures/bill_line.valid.json) | Golden valid BillLine |

---

## Research authority

| Layer | Document |
|-------|----------|
| L5 depth | [../technical/layers/L5-closure-and-verification.md](../technical/layers/L5-closure-and-verification.md) |
| L4 depth | [../technical/layers/L4-knowledge-and-reasoning.md](../technical/layers/L4-knowledge-and-reasoning.md) |
| L3 depth | [../technical/layers/L3-intelligence-core.md](../technical/layers/L3-intelligence-core.md) |
| L2 depth | [../technical/layers/L2-universal-repository.md](../technical/layers/L2-universal-repository.md) |
| L1 depth | [../technical/layers/L1-connect-and-normalise.md](../technical/layers/L1-connect-and-normalise.md) |
| Eval spine | [../technical/cross-cutting/04-evaluation-and-quality.md](../technical/cross-cutting/04-evaluation-and-quality.md) |
| Master | [../technical/00-stamped-master-document.md](../technical/00-stamped-master-document.md) |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-11 | Initial handoff for connectors-bill bootstrap |
| 2026-07-12 | Added stamped-l2 handoff section, ADR-009, layer-interfaces-l2 |
| 2026-07-12 | Submodule distribution (ADR-011); playbooks + deployment-profiles |
| 2026-07-17 | L4 architecture handoff + ADR-017; build-order superseded |
| 2026-07-19 | Link consumer README snapshots under `consumers/readmes/` |
| 2026-07-20 | L5 architecture handoff + build plan; ADR-019/020/021; contracts 0.7.0 |
| 2026-07-21 | Ops-first L5 + Finding 1.1.0 `ops_clearance`; contracts 0.8.0; L3 ops-clearance consumer prompt |
| 2026-07-21 | Mirrored completed L5 README → `consumers/readmes/closure-verification.md` |
