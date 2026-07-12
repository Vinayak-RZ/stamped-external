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

### Planned

- Submodule migration in connectors-edge, connectors-cloud, connectors-bill, universal-repositary
- `stamped-l1-contracts` PyPI/npm publish (optional P1)
