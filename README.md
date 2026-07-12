# Stamped Platform — shared architecture, contracts, and handoff

> **Repo:** `stamped-external` (`vinayak-rz/stamped-external`)  
> **Role:** Single source of truth for all Stamped product repositories  
> **Distribution:** Git submodule mounted at `external/` in each consumer repo  
> **Authority:** [ADR-011](decisions/ADR-011-stamped-platform-submodule-distribution.md)

---

## What this repository is

This pack is **not application code**. It is the shared platform layer every Stamped repo consumes:

| Directory | Purpose | Change frequency |
|-----------|---------|------------------|
| [`contracts/`](contracts/) | JSON schemas, MQTT topics, dedupe golden fixtures (`stamped-l1-contracts`) | **High** — CI-enforced |
| [`decisions/`](decisions/) | Architecture Decision Records (ADRs) | **High** — living |
| [`handoff/`](handoff/) | Cross-repo integration docs, playbooks, per-repo bootstrap guides | Medium |
| [`technical/`](technical/) | Product + engineering reference specs (L0–L6) | Low |
| [`architecture/`](architecture/) | Layer interface contracts (implementation authority) | Medium |
| [`compliance/`](compliance/) | India regulatory register | Low |
| [`design/`](design/) | Forge Industrial design system tokens | Low |
| [`scripts/`](scripts/) | Shared CI helpers (`contract-check.sh`) | Medium |

**Invariant:** Contracts and ADRs apply to **all** deployment modes (`local`, `local-dashboard`, `cloud`) per [ADR-010](decisions/ADR-010-deployment-profiles-and-portability.md).

---

## Consumer repositories

| Repo | GitHub | Mount path |
|------|--------|------------|
| connectors-edge | `Vinayak-RZ/connectors-edge` | `external/` |
| connectors-cloud | `Vinayak-RZ/connectors-cloud` | `external/` |
| connectors-bill | `Vinayak-RZ/connectors-bill` | `external/` |
| stamped-l2 | `Vinayak-RZ/universal-repositary` | `external/` |
| stamped-l3 … stamped-l6 | (future) | `external/` |

Pin each consumer to a **semver tag** of this repo (see [VERSION](VERSION)). Do not float on `main` in production branches.

---

## Quick start — new consumer repo

```bash
# From consumer repo root (e.g. stamped-l2)
git submodule add https://github.com/vinayak-rz/stamped-external.git external
git submodule update --init --recursive
cd external && git checkout v2026.07.12   # pin to release tag
cd .. && git add .gitmodules external && git commit -m "chore: add stamped-external submodule"
```

Full migration guide: [SUBMODULE.md](SUBMODULE.md).

---

## Quick start — platform maintainers

1. **Contract or ADR change** → PR in `stamped-external` only  
2. Merge → tag release (`vYYYY.MM.DD` or semver bump on `contracts/CHANGELOG.md`)  
3. Open PR in each affected consumer repo bumping `external` submodule pointer  
4. Consumer CI must pass `scripts/contract-check.sh` and repo-specific E2E  

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Reading order (new engineer or agent)

| # | Document |
|---|----------|
| 1 | [technical/00-stamped-master-document.md](technical/00-stamped-master-document.md) |
| 2 | [decisions/README.md](decisions/README.md) — ADRs |
| 3 | [handoff/deployment-profiles.md](handoff/deployment-profiles.md) — three deployment modes |
| 4 | [handoff/README.md](handoff/README.md) — repo-specific bootstrap index |
| 5 | Your repo's handoff doc (e.g. `handoff/stamped-l2-spec.md`) |

---

## Release versioning

| File | Purpose |
|------|---------|
| [VERSION](VERSION) | Current platform release identifier |
| [CHANGELOG.md](CHANGELOG.md) | Cross-pack release notes |
| [contracts/CHANGELOG.md](contracts/CHANGELOG.md) | Schema semver (BACKWARD compatibility) |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-12 | Platform pack prepared for `stamped-external` repo + submodule distribution (ADR-011) |
