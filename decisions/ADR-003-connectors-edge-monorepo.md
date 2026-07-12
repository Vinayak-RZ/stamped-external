# ADR-003: connectors-edge monorepo — Go/Python packages, asset IDs, templates

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-09 |
| **Deciders** | Vinayak (product), engineering |
| **Related** | [ADR-001](ADR-001-l1-repo-split-and-boundaries.md) · [ADR-002](ADR-002-build-all-aws-networking.md) |

---

## Context

ADR-001 left open: edge language, monorepo layout, repo naming, `asset_id` before L2 exists, and where vertical mapping templates live. This ADR closes those items.

**Repo identity:** This GitHub repository (`Connectors` / `Vinayak-RZ/Connectors`) **is** the **`connectors-edge`** monorepo. Bill ingest remains a **separate future repo** (`connectors-bill`).

---

## Decision summary

| # | Topic | Decision |
| --- | --- | --- |
| 1 | Edge runtime language | **Go** — edge agent, connectors, buffer, uplink, on-device quality gates |
| 2 | Cloud onboarding language | **Python** — tag-mapping-api (FastAPI), LLM suggestion jobs |
| 3 | Package separation | **Go and Python are separate packages** in one monorepo — no mixed runtime in one deployable |
| 4 | Monorepo | **Yes** — edge agent + tag-mapping-api + tag-mapping-ui + contracts in this repo |
| 5 | Bill repo | **Separate** `connectors-bill` GitHub repo (not in this monorepo) |
| 6 | `asset_id` before L2 | **Temporary IDs** with `stamped.local/` prefix; migration path when L2 graph exists |
| 7 | Vertical templates | **Git YAML** in repo at P0; move to DB when fleet &gt;50 plants |

---

## 1. Monorepo layout (`connectors-edge`)

This repository structure:

```text
connectors-edge/                    # this repo (Connectors on GitHub)
├── external/
│   ├── technical/                # reference specs (synced)
│   ├── decisions/                # ADRs
│   └── contracts/                # stamped-l1-contracts (JSON Schema)
├── packages/
│   ├── edge-agent/               # Go — plant runtime (see §2)
│   ├── tag-mapping-api/          # Python — FastAPI onboarding backend
│   ├── tag-mapping-ui/           # TypeScript — web UI (Vite/React or Next)
│   └── contracts-gen/            # optional: codegen scripts (Go + TS from schemas)
├── templates/
│   └── verticals/                # Git YAML mapping templates (see §5)
│       ├── forging.yaml
│       ├── auto-components.yaml
│       └── ...
├── AGENTS.md
└── README.md
```

**Not in this repo:** `connectors-bill`, L2+ services.

**In this repo (implemented):** `packages/connectors-ingest` — MQTT subscriber → Timescale dedupe + outbox publisher + optional HTTP ingest.

### Rationale

- One PR can ship connector change + mapping API + UI fix + schema bump.
- `external/` travels via **stamped-platform submodule** in each repo ([ADR-011](../decisions/ADR-011-stamped-platform-submodule-distribution.md)).
- Go and Python stay isolated — different Docker images, different CI jobs.

---

## 2. Go vs Python — separate packages

| Package | Language | Deploy target | Responsibility |
| --- | --- | --- | --- |
| **`packages/edge-agent`** | **Go** | Edge gateway / industrial PC (arm64 + amd64) | Modbus, MQTT, Sparkplug, filewatch; buffer; normaliser; quality gates; MQTT uplink; harvest export; drift watch; OTA config apply |
| **`packages/tag-mapping-api`** | **Python** (FastAPI) | AWS Fargate / Lambda | Ingest harvest; template match; LLM suggestions; mapping CRUD; publish `MappingConfig` to fleet; serves UI API |
| **`packages/tag-mapping-ui`** | **TypeScript** | S3 + CloudFront | Onboarding screens (ADR-001 §5) |
| **`packages/connectors-ingest`** | **Python** | AWS Fargate / sidecar | MQTT → Timescale dedupe, outbox publisher, optional HTTP backfill |
| **`external/contracts`** | JSON Schema | — | Source of truth; generate Go structs + Pydantic models in CI |

### Boundaries

- **No Python on the edge** — keeps RAM and image size low on 4G gateways.
- **No Go in tag-mapping-api** — faster iteration for LLM/template logic.
- Shared types flow **only through `external/contracts`** — not copy-paste between Go and Python.

### Docker images (from ADR-001 flavours)

| Image | Built from |
| --- | --- |
| `stamped-edge:p0` / `:p1` / `:full` | `packages/edge-agent` Dockerfile |
| `stamped-tag-mapping-api` | `packages/tag-mapping-api` Dockerfile |
| UI | static build → S3 (no container required P0) |

---

## 3. `asset_id` before L2 exists

### Decision

Until L2 exposes an energy-graph API, tag mapping uses **temporary plant-local asset IDs**:

```
stamped.local/{plant_slug}/{asset_slug}
```

Example: `stamped.local/pilot-forge-01/incomer-main`

### Rules

| Rule | Detail |
| --- | --- |
| Prefix | Must start with `stamped.local/` — clearly non-production graph |
| Uniqueness | Unique per `plant_id` |
| UI | Tag-mapping UI may create assets inline; list stored in plant config until L2 exists |
| Mapping config | `MappingConfig` references these IDs opaquely — L1 does not model graph edges |
| Migration | When L2 graph is live: **one-time remap** `stamped.local/*` → canonical `asset:*` IDs; publish new `mapping_version`; document in `external/decisions/ADR-004-migration-stamped-local-assets.md` when executed |

### L2 handoff (future)

L2 **owns canonical `asset_id`** namespace. Tag-mapping-api calls `GET /plants/{id}/assets` when available; `stamped.local/*` creation disabled for new plants.

---

## 4. Vertical templates — Git YAML (P0)

### Location

```text
templates/verticals/{vertical}.yaml
```

Committed to this repo; reviewed in PR like code.

### Template shape (sketch)

```yaml
vertical: forging
version: 1
rules:
  - match: { source_tag_pattern: "(?i)incomer.*kw" }
    asset_slug: incomer-main
    metric_type: active_power_kw
  - match: { source_tag_pattern: "(?i)comp.*_kw" }
    asset_slug: compressor-{n}
    metric_type: active_power_kw
```

Template match runs in **tag-mapping-api** (Python). Edge agent does **not** embed templates — only the published `MappingConfig` snapshot.

### Upgrade trigger

When fleet **&gt;50 plants** or template change velocity hurts ops → move templates to DB with Git export/sync. Until then, **Git YAML only**.

---

## 5. Repo naming

| GitHub repo (current) | Canonical name | Scope |
| --- | --- | --- |
| `Vinayak-RZ/Connectors` | **`connectors-edge`** | This monorepo (edge-agent, tag-mapping-api/ui, connectors-ingest, contracts) |
| *(future)* | **`connectors-bill`** | Bill PDF, tariff, BillLine publish |

Rename GitHub repo when convenient; docs use **`connectors-edge`** as the logical name from now on.

---

## 6. Consequences

- CI: separate workflows `edge-agent` (Go test + cross-compile), `tag-mapping-api` (pytest), `tag-mapping-ui` (lint/build).
- First implementation sprint starts with `packages/edge-agent` (Modbus P0) + `external/contracts` schemas.
- Bill work must not land in this repo — `external/contracts` comes from **stamped-platform** submodule like all repos.

---

## 7. Supersedes

- ADR-001 §6 "program home until split" → **this repo is connectors-edge**
- ADR-001 §7 open items: edge language, monorepo, asset_id → **closed**
- ADR-002 §7 item 3 (S7comm) — unchanged; implement in Go `edge-agent`
