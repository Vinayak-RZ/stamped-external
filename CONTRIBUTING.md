# Contributing to stamped-external

## Who changes this repo?

| Change type | Who | Review |
|-------------|-----|--------|
| JSON schema / fixture | Contract owner + affected L1/L2 engineers | BACKWARD compatibility required |
| ADR (new decision) | Architecture / product | ADR template in `decisions/` |
| Handoff / playbook | Layer repo owner | Cross-repo impact noted in PR |
| Technical reference | Research / architecture | Low frequency |

## PR workflow

1. Branch from `main` in **stamped-external** (not in consumer repos)
2. If schema change: update `contracts/CHANGELOG.md` semver
3. Run locally: `./scripts/contract-check.sh`
4. PR description must list **consumer repos** that need submodule bump
5. After merge: tag release (see below)
6. Open submodule bump PRs in each listed consumer

## Release tagging

| Change | Tag bump |
|--------|----------|
| Schema breaking (major) | `contracts` major + platform tag `vYYYY.MM.DD` |
| Schema additive (minor) | `contracts` minor + platform tag |
| ADR / docs only | Platform tag `vYYYY.MM.DD` (patch-level) |

```bash
# After merge to main
echo "2026.07.12" > VERSION
git add VERSION CHANGELOG.md
git commit -m "chore(release): v2026.07.12"
git tag v2026.07.12
git push origin main --tags
```

## Contract compatibility rules

Per [ADR-008](decisions/ADR-008-layer-repo-topology-and-interfaces.md):

- **BACKWARD** mode on JSON Schema changes
- Dedupe golden in `contracts/fixtures/dedupe_golden.json` is authoritative — all repos must match
- Never change `dedupe_key` algorithm without ADR + coordinated major bump

## What not to put here

- Application code (`packages/`, service implementations)
- Repo-specific `deploy/` compose (consumer repos own deploy)
- Secrets, `.env` with real values, customer data
