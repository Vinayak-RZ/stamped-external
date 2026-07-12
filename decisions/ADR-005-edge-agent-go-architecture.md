# ADR-005: Go edge-agent architecture

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-09 |
| **Related** | [ADR-001](ADR-001-l1-repo-split-and-boundaries.md) · [ADR-002](ADR-002-build-all-aws-networking.md) · [ADR-003](ADR-003-connectors-edge-monorepo.md) · [ADR-004](ADR-004-compliance-driven-architecture.md) |

---

## Context

ADR-001–004 define repo boundaries, build-all strategy, monorepo layout, and compliance. This ADR records **implementation architecture** for `packages/edge-agent` (Go).

Full detail: `docs/architecture/edge-agent-architecture.md` (human) · `docs/architecture/edge-agent-architecture.agents.md` (agents) · `docs/plans/edge-agent-architecture-plan.md` (build plan) — in **connectors-edge** consumer repo.

---

## Decision summary

| # | Topic | Decision |
| --- | --- | --- |
| 1 | Buffer | SQLite WAL at `/var/lib/stamped-edge/buffer.db`, ≥72h retention |
| 2 | Config OTA | HTTPS pull of signed manifest; MQTT `cmd/config` wake-up only |
| 3 | MQTT topics | `stamped/v1/{org_id}/{plant_id}/...` — prod-eng `v1/{plant}/live` deprecated |
| 4 | Plugins | Go interfaces + build tags (`p0`/`p1`/`full`); no dynamic loading |
| 5 | Modbus | `github.com/goburrow/modbus`; profiles in `profiles/modbus/*.yaml` |
| 6 | Fleet OTA P0 | Manual docker pull + restart until ~20 devices |
| 7 | Payloads | JSON + `schema_version`; QoS 1 |
| 8 | Mapping | Read-only `MappingConfig` snapshot; no templates on edge |
| 9 | Testing | Test-as-you-go; Phase 9 certification gate before P0 release |

---

## Internal layout

Single Go process: `connectors` → `mapping` → `pipeline` (normaliser + quality) → `buffer` → `uplink`, with side paths for `health` and `harvest`.

Image flavours: `stamped-edge:p0` (modbus, mqtt, sparkplug, filewatch), `:p1` (+opcua, dlms), `:full`.

---

## Consequences

- JSON Schemas in `external/contracts/schemas/` are source of truth for Go types.
- tag-mapping-api publishes mapping snapshots; edge never runs LLM/template match.
- Cloud ingest repo subscribes to same MQTT topics (deferred).

---

## Supersedes

- L1 open question #7 (fleet mgmt) for P0: manual OTA documented in runbook.
