# stamped-external changelog

All notable changes to the shared platform pack. Consumer repos pin via git submodule tags.

Format: [Keep a Changelog](https://keepachangelog.com/). Platform tags: `vYYYY.MM.DD` (aligned with [VERSION](VERSION)).

## [2026.07.12] - 2026-07-12

### Added

- Platform pack structure for `stamped-platform` repository distribution
- [ADR-010](decisions/ADR-010-deployment-profiles-and-portability.md) — three deployment modes (`local`, `local-dashboard`, `cloud`)
- [ADR-011](decisions/ADR-011-stamped-platform-submodule-distribution.md) — submodule single source of truth
- Four portability playbooks (edge, cloud, bill, stamped-l2)
- [deployment-profiles.md](handoff/deployment-profiles.md) cross-repo mode matrix
- [SUBMODULE.md](SUBMODULE.md) migration guide
- [scripts/contract-check.sh](scripts/contract-check.sh) shared CI helper
- Research brief mirrored in consumer repos at `docs/research/` (not in platform pack)

### Changed

- ADR-002, ADR-007, ADR-009 — ADR-010 addenda for deployment modes
- `stamped-l2-ecosystem-integration.md` — three-mode section; `connectors-ingest` reclassified for `local` mode
- `02-technical-architecture.md` §16.4 — deployment mode table
- Contract authority moved to platform repo per ADR-011 (supersedes connectors-edge fork)

### Deprecated

- Manual copy of `external/` folder into new repos — use submodule (ADR-011)

## [Unreleased]

### Added

- Extensive README — architecture (L0–L6), tech stack, ADR catalog, contracts reference, deployment modes, Cursor config
- **L5 architecture overhaul** — authoritative [L5 SSOT](technical/layers/L5-closure-and-verification.md); [ADR-019](decisions/ADR-019-l5-runtime-and-consistency.md) / [ADR-020](decisions/ADR-020-l5-mv-claim-governance.md) / [ADR-021](decisions/ADR-021-l5-notification-and-evidence.md); handoffs [stamped-l5-architecture-handoff.md](handoff/stamped-l5-architecture-handoff.md) + [build plan](handoff/stamped-l5-build-plan.md)
- Contracts **0.7.0** — `workflow-event.json`, envelope `workflow_event`, ledger `supersedes_entry_id` / `emission_factor_ref`
- **Ops-first L5 + L3 enablement** — Finding **1.1.0** `ops_clearance` / `alarm_hint`; ledger `ops_confirmed`; workflow `alarm_*` / `ops_verified` / `ops_regressed`; [L3 ops-clearance consumer prompt](handoff/stamped-l3-ops-clearance-consumer-prompt.md)
- Contracts **0.8.0** — see [contracts/CHANGELOG.md](contracts/CHANGELOG.md)

### Changed

- L2 `ledger.mv_ledger` DDL sketch aligned to contract `verification_status` (`modeled`, not mutable `superseded`); later **`ops_confirmed`**
- Production-engineering Temporal default superseded by ADR-019 for L5
- Arch §5.2 / §5.4 — Finding 1.1.0 + ops_confirmed / alarm events
- ADR-020 reframed: ops-cleared verification; bill path deferred
- L5 SSOT / handoffs: EMS alarm router; calculated savings; vertical catalog map

### Planned

- Submodule migration in connectors-edge, connectors-cloud, connectors-bill, universal-repositary
- `stamped-l1-contracts` PyPI/npm publish (optional P1)
- Create `stamped-l5` consumer repo per build plan
- Bill reconcile / IPMVP Option C as optional add-on (not P0 gate)
