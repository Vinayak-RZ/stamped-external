# ADR-001: L1 connectors — repo split, edge packaging, schemas, transport, tag mapping

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-09 |
| **Deciders** | Vinayak (product), engineering (Connectors repo) |
| **Context** | [L1 spec](../technical/layers/L1-connect-and-normalise.md) · [Technical architecture §5, §7](../technical/02-technical-architecture.md) |

---

## Context

Stamped L1 (Connect & normalise) is built as **multiple deployable repos** under a microservices-style product. This ADR captures decisions made for the **edge/connectors** program and the **bill ingest** program, plus shared contracts that bind them to L2+.

**In scope for this ADR:** repo boundaries, edge container strategy, schema ownership, MQTT topic contract, tag-mapping placement, deferred items (cloud ingest HTTP API).

**Out of scope (deferred):** cloud ingest service repo layout, L2 repository internals, Redpanda upgrade trigger.

---

## Decision summary

| # | Topic | Decision |
| --- | --- | --- |
| 1 | Repo split | **Two L1 repos:** `connectors-edge` (OT/IT streaming) and `connectors-bill` (PDF/tariff). Cloud ingest HTTP API = **third repo, later**. |
| 2 | Edge packaging | **One base container image** + **build flavours** via Dockerfile `ARG`/targets; **runtime config** selects enabled connector plugins and protocol/profile versions — no per-plant image rebuild. |
| 3 | Schema registry | **Single shared contract package** (`stamped-l1-contracts`): JSON Schema + generated types; versioned semver; consumed by edge, bill, and (later) cloud ingest. |
| 4 | Event transport (edge → cloud) | **MQTT topics** carrying canonical JSON payloads from day one. **Postgres transactional outbox** is owned by the **cloud ingest consumer** (not edge); topic names and payload schemas are fixed now so outbox → broker swap is transport-only later. |
| 5 | Tag mapping UI | **Separate package** in the **edge program** (same GitHub org; can be monorepo with edge agent or sibling repo). Includes onboarding API + web UI; mapping config is **versioned and OTA-pushed** to edge agents. |
| 6 | Bill service boundary | Bill repo owns PDF ingest, DISCOM templates, tariff parser, human review queue; emits **`BillLine`** (and bill lifecycle **`Event`s**) on the **same MQTT topic family** as measurements. |
| 7 | Normalisation & quality gates | **Edge applies** tag mapping + data-quality gates before uplink. Bill repo applies bill-specific recompute gates before publish. Neither repo silently repairs bad data. |
| 8 | `external/` folder | **`stamped-platform`** git submodule at `external/` in each repo ([ADR-011](ADR-011-stamped-platform-submodule-distribution.md)). Contains: `technical/` (reference), `decisions/` (ADRs), `contracts/` (canonical schemas). **Deprecated:** manual copy/sync. |

---

## 1. Repo split

### Decision

| Repo | Owns | Does not own |
| --- | --- | --- |
| **connectors-edge** | Edge agent runtime, protocol connector plugins, edge buffer/uplink, edge-side normaliser + quality gates, register/profile library, tag harvest, tag-mapping UI + onboarding API, fleet/site config OTA | Bill PDF/OCR, DISCOM templates, long-term TSDB, intelligence |
| **connectors-bill** | Bill PDF ingest, layout/LLM extraction, recompute gate, DISCOM/tariff templates, bill human-review UI, tariff-order parser | Modbus/OPC UA, edge buffer, plant OT credentials |
| **connectors-ingest** *(deferred)* | MQTT subscriber, idempotent writers, Postgres outbox, HTTP ingest for Topology F | Protocol drivers |

### Rationale

- **Different failure domains:** OT connectors vs messy DISCOM PDFs.
- **Different release cadence:** meter profiles vs annual tariff orders.
- **Different deployment:** edge runs on plant hardware; bill service is cloud-only batch + review UI.
- **Same contract:** both publish L1 canonical records on agreed MQTT topics.

### Consequences

- Two CI pipelines, two Docker publish paths.
- Shared `stamped-l1-contracts` package must be published (git submodule, private PyPI, or npm) before either repo tags a release.
- Tag-mapping onboarding API may call LLM APIs in cloud even though harvest runs on edge.

---

## 2. Edge container — single image, easy customization

### Decision

**Pattern: core runtime + connector plugins + site config.**

```
stamped-edge-agent (single Dockerfile)
├── core/           # buffer, uplink MQTT, health, OTA, clock, seq numbers
├── normaliser/     # → Measurement, Event (canonical)
├── quality/        # L1 gates (stale, range, counter, clock, gap)
├── connectors/     # plugins (build-tagged or optional layers)
│   ├── modbus/
│   ├── mqtt/
│   ├── sparkplug/
│   ├── opcua/      # P1 flavour
│   └── filewatch/
└── config/         # declarative site YAML (pushed OTA, not baked in image)
```

**Image flavours** (same Dockerfile, different build targets):

| Image tag | Connectors compiled in | Typical use |
| --- | --- | --- |
| `edge:p0` | modbus, mqtt, sparkplug, filewatch | Path B pilots |
| `edge:p1` | p0 + opcua + dlms | Path A |
| `edge:full` | all open-source connectors | Field standard |

**Per-site customization** = **config only**:

- `connectors.enabled[]` — which plugins start
- `profiles.modbus[]` — register map + byte order + scaling + **profile version**
- `profiles.mqtt[]` — JSON-path decoder id + version
- `mapping.version` — tag map snapshot id deployed to this agent
- `uplink.broker`, `plant_id`, `credentials`

**Protocol versions** are **profile versions** in config/registry, not separate images. Example: `schneider-pm5560@v3` vs `@v2` register map.

### Rationale

Matches L1 spec §4.2–4.3: one fleet-managed container, plugins per site, OTA config. Avoids combinatorial explosion of images per meter model.

### Alternatives considered

| Option | Rejected because |
| --- | --- |
| One image per protocol | Ops nightmare at 50+ plants |
| Fat image always | RAM/attack surface on 4G gateways |
| Node-RED per site | L1 spec: prototyping only, not fleet standard |

---

## 3. Schema registry — single contract package

### Decision

Create **`external/contracts/`** (and publish as **`stamped-l1-contracts`**):

| Artifact | Purpose |
| --- | --- |
| `schemas/measurement.json` | L1→L2 time-series |
| `schemas/event.json` | state, alarms, connector health, gaps |
| `schemas/production-record.json` | shift/batch quantities |
| `schemas/bill-line.json` | validated bill economics |
| `schemas/tag-inventory.json` | harvest output (onboarding) |
| `schemas/mapping-config.json` | approved tag map snapshot for edge |
| `TOPICS.md` | MQTT topic layout + QoS + retention |
| `CHANGELOG.md` | semver breaking changes |

**Versioning:** package semver + `schema_version` field inside each payload. Edge and bill pin a **minimum contract version** in releases.

**Generation:** JSON Schema → Python (Pydantic) + TypeScript types in CI for edge, bill, and UI repos.

### Rationale

Layer contract in [02-technical-architecture §5](../technical/02-technical-architecture.md) is the integration API across microservices. One registry prevents edge and bill drifting.

---

## 4. Event transport

### Decision

**Edge & bill (publishers):**

- MQTT 3.1.1 or 5.0, TLS, QoS **1** for measurements, outbound-only from plant (edge) or cloud (bill).
- Payload = canonical JSON validated against `stamped-l1-contracts` before publish.

**Topic layout (v1):**

```
stamped/v1/{org_id}/{plant_id}/measurements     # stream
stamped/v1/{org_id}/{plant_id}/events           # stream
stamped/v1/{org_id}/{plant_id}/production       # stream
stamped/v1/{org_id}/{plant_id}/bills            # bill repo publishes BillLine batches
stamped/v1/{org_id}/{plant_id}/health           # connector birth/death/heartbeat
```

Partition key for ordering: `{plant_id}/{source_tag}` implied by payload; broker does not need Kafka-style keys at pilot scale.

**Cloud ingest (deferred repo):**

- Subscribes to topics → idempotent write Timescale + **Postgres transactional outbox** for domain events.
- Outbox pattern per [02-technical-architecture §4](../technical/02-technical-architecture.md) decision #8.
- HTTP ingest API only for Topology F (file drop) — **not in scope until ingest repo**.

### Rationale

User decision: MQTT from day one; outbox on cloud side. Fixing topic names and schemas now avoids rewrite when ingest service appears.

---

## 5. Tag mapping — deep design

### Problem

Raw OT tags (`COMP_2_KW`, `40001`) must become semantic IDs (`asset:compressor-2/metric:active_power`) before L2/L3 can reason. Target: **≤2 engineer-days per Path A plant (500–1,500 tags)** per L1 spec §4.5.

### Decision — five-stage pipeline

| Stage | Where it runs | Owner repo |
| --- | --- | --- |
| **1. Harvest** | Edge connector browse/poll | connectors-edge |
| **2. Template match** | Cloud (deterministic rules) | connectors-edge (`tag-mapping-api`) |
| **3. LLM suggest** | Cloud (optional, suggestion only) | connectors-edge |
| **4. Human confirm** | Web UI | connectors-edge (`tag-mapping-ui` package) |
| **5. Drift watch** | Edge runtime (stats fingerprint) | connectors-edge |

**Hard rule (from L1 spec):** LLM suggestions are **never auto-applied** — always human confirm or template rule with explicit confidence threshold.

### Data model (contract additions)

```
TagInventoryItem {
  plant_id, source_system, source_tag,
  native_unit?, sample_stats?, harvested_at,
  connector_id, profile_version?
}

MappingSuggestion {
  inventory_item_id, asset_id?, metric_type?, unit?,
  confidence, method: "template|llm|manual",
  status: "pending|accepted|rejected"
}

MappingConfig (versioned, immutable snapshot) {
  mapping_version, plant_id, published_at,
  rules: [{ source_system, source_tag, asset_id, metric_type, unit, transform? }]
}
```

Edge stores **only the active `MappingConfig` snapshot** locally; cloud holds history and draft suggestions.

### UI package (`tag-mapping-ui`)

**Location:** package in edge program (monorepo recommended: `packages/tag-mapping-ui` + `packages/tag-mapping-api` + `packages/edge-agent`).

**Core screens:**

1. **Plant onboarding** — plant metadata, timezone, vertical template (forging, cement, …)
2. **Harvest import** — pull latest inventory from edge or upload JSON export
3. **Mapping grid** — filter pending/low-confidence; bulk accept; inline edit asset/metric
4. **Preview** — sample raw → normalised `Measurement` for selected tags
5. **Publish** — create `mapping_version` N, push to edge OTA channel
6. **Drift inbox** — `tag_remapped?` events from edge

**API (`tag-mapping-api`):** REST for UI; auth per org/plant; publishes `MappingConfig` to edge fleet config service (part of edge repo initially).

### Edge runtime behaviour

1. Connector reads raw value.
2. Lookup `(source_system, source_tag)` in active `MappingConfig`.
3. If unmapped: emit `Event` type `unmapped_tag` (sampled, not every point) + optionally buffer with `asset_id: null` per L1 schema §4.4.
4. If mapped: normalise → quality gates → MQTT publish.

### Open tag-mapping choices (see § Open questions)

- Whether `asset_id` namespace is owned by L2 graph service (recommended) or duplicated in L1.
- Where vertical templates live (git in edge repo vs DB).

---

## 6. What lives in this repo

**This repository is `connectors-edge`** — the L1 edge monorepo per [ADR-003](ADR-003-connectors-edge-monorepo.md).

| Path | Role |
| --- | --- |
| `external/technical/` | Reference specs (from Stamped-Energy) |
| `external/decisions/` | ADRs (living) |
| `external/contracts/` | Canonical schemas (`stamped-l1-contracts`) |
| `packages/edge-agent/` | **Go** — plant runtime, connectors, uplink |
| `packages/tag-mapping-api/` | **Python** — onboarding API, template/LLM match |
| `packages/tag-mapping-ui/` | **TypeScript** — mapping UI |
| `templates/verticals/` | Git YAML vertical mapping templates (P0) |

**Separate repo (not here):** `connectors-bill`. **Deferred:** `connectors-ingest`.

---

## 7. Deferred / not decided yet

| Item | Notes |
| --- | --- |
| Cloud ingest repo name & layout | After edge publishes stable MQTT contract |
| ~~`asset_id` authority~~ | **Decided:** `stamped.local/*` until L2 — [ADR-003](ADR-003-connectors-edge-monorepo.md), [asset-id-migration.md](asset-id-migration.md) |
| ~~Edge language / monorepo~~ | **Decided:** Go `edge-agent` + Python `tag-mapping-api` — [ADR-003](ADR-003-connectors-edge-monorepo.md) |
| MQTT broker hosting | **Self-hosted Mosquitto on AWS EC2** (P0) — [ADR-002](ADR-002-build-all-aws-networking.md) |
| Kepware/NeuronEX | **Build OSS drivers** — [ADR-002](ADR-002-build-all-aws-networking.md) |

---

## 8. Consequences for downstream layers (L2+)

- L2 ingest consumers **must** treat MQTT payloads as at-least-once; dedupe keys `(plant_id, source_tag, ts_utc, granularity)` per L1 spec.
- L2 should expose **asset graph API** for tag-mapping UI to pick canonical `asset_id`s when live. Until then: `stamped.local/*` per [ADR-003](ADR-003-connectors-edge-monorepo.md).
- Bill `BillLine` with `validated=false` must be quarantined in L2 — never feed M&V.

---

## References

- [L1 — Connect & normalise](../technical/layers/L1-connect-and-normalise.md) §4.1, §4.4–4.6
- [Technical architecture](../technical/02-technical-architecture.md) §5, §7, §16.2
- [Production engineering](../technical/cross-cutting/03-production-engineering.md)
