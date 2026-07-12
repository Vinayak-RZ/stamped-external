# ADR-011: stamped-platform — submodule distribution as single source of truth

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-12 |
| **Deciders** | Vinayak (product), engineering |
| **Related** | [ADR-001](ADR-001-l1-repo-split-and-boundaries.md) · [ADR-008](ADR-008-layer-repo-topology-and-interfaces.md) · [ADR-010](ADR-010-deployment-profiles-and-portability.md) · [SUBMODULE.md](../SUBMODULE.md) |

---

## Context

Stamped uses **one repo per layer** (ADR-008): connectors-edge, connectors-cloud, connectors-bill, stamped-l2 … stamped-l6. Each repo needs identical:

- JSON schemas and dedupe fixtures (`contracts/`)
- Architecture decisions (`decisions/`)
- Cross-repo handoff and deployment docs (`handoff/`)

**Previous pattern:** Copy entire `external/` folder when bootstrapping a repo (ADR-009). This causes **drift** — edge on ADR-009, L2 on ADR-010, mismatched dedupe golden.

ADR-001 already anticipated a published **`stamped-l1-contracts`** package and "sync across repos." This ADR chooses **git submodule** as the P0 distribution mechanism for the full platform pack.

---

## Decision summary

| # | Topic | Decision |
| --- | --- | --- |
| 1 | Platform repo | **`stamped-platform`** — contents = current `external/` tree at repo root |
| 2 | Consumer mount | Git submodule at path **`external/`** in every product repo |
| 3 | Versioning | **Semver tags** on platform repo (`v2026.07.12`); consumers pin explicit tag |
| 4 | Contracts authority | **`stamped-platform/contracts/`** is canonical — not a fork in connectors-edge |
| 5 | Change workflow | PR in platform repo → tag → submodule bump PRs in consumers |
| 6 | CI | Each consumer runs `external/scripts/contract-check.sh` on PR |
| 7 | Copy pattern | **Deprecated** — replace with submodule (see migration in SUBMODULE.md) |

---

## Repository layout

```text
stamped-platform/                 # GitHub: vinayak-rz/stamped-external
├── README.md
├── VERSION
├── CHANGELOG.md
├── SUBMODULE.md
├── contracts/                    # stamped-l1-contracts
├── decisions/                    # ADRs
├── handoff/
├── technical/
├── architecture/
├── compliance/
├── design/
└── scripts/contract-check.sh

connectors-edge/
└── external/  → submodule @ v2026.07.12
```

---

## Consumer matrix

| Repo | Submodule path | Required CI |
|------|----------------|-------------|
| connectors-edge | `external/` | contract-check + edge E2E |
| connectors-cloud | `external/` | contract-check + dedupe golden |
| connectors-bill | `external/` | contract-check + bill dedupe |
| stamped-l2 | `external/` | contract-check + ingest parity |
| stamped-l3–l6 | `external/` | contract-check |

---

## Communication flow

1. **Platform change** merged to `stamped-platform/main`
2. **Tag** released with notes in `CHANGELOG.md`
3. **Submodule bump PRs** in affected consumers (can be parallel)
4. **Release notes** reference ADR number or schema version

No silent schema changes in consumer repos.

---

## Relationship to ADR-001 and ADR-008

| Prior decision | Update |
|----------------|--------|
| ADR-001 §3 schema registry | `stamped-platform/contracts/` replaces per-repo copy; package publish (PyPI/npm) remains **P1** optional |
| ADR-001 §8 `external/` sync | Submodule replaces manual sync |
| ADR-008 §3 contract store | Canonical store is **platform repo**, not connectors-edge fork |
| ADR-007 §7 L1 contracts source | connectors-edge **consumes** platform submodule like other repos |

---

## Alternatives considered

| Option | Rejected because |
|--------|------------------|
| Continue copy-on-bootstrap | Proven drift risk |
| Monorepo for all layers | Violates layer-per-repo topology (ADR-008) |
| npm/PyPI only (no submodule) | Does not distribute ADRs, handoff, technical specs |
| Float submodule on `main` | Unreproducible builds; breaks air-gap bundle pinning |

---

## Consequences

- One-time migration in each consumer repo (SUBMODULE.md)
- Agents must run `git submodule update --init` after clone
- Air-gap bundles vendor pinned platform SHA
- Future ADRs and deployment mode changes propagate via platform tag + bump PRs
- **ADR-011 recorded in platform repo** — consumers inherit on submodule bump

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-12 | Initial ADR — stamped-platform submodule as SSOT |
