# Stamped platform — agent prompt for all consumer repos

> **Use this in:** `AGENTS.md`, Cursor rules, or the first message to any agent working in a Stamped product repo.  
> **Platform repo:** [vinayak-rz/stamped-external](https://github.com/vinayak-rz/stamped-external) · **ADR:** [ADR-011](../decisions/ADR-011-stamped-platform-submodule-distribution.md)

---

## Copy-paste prompt (full)

Paste the block below into your repo's `AGENTS.md` (prepend or merge with repo-specific sections).

```markdown
# Stamped platform — single source of truth

This repository is a **Stamped product repo** (L1/L2/L3…). It does **not** own platform-wide contracts, ADRs, or cross-repo architecture. Those live in a separate repo mounted here as a git submodule.

## Platform submodule (`external/`)

| Field | Value |
| --- | --- |
| **Canonical repo** | `https://github.com/vinayak-rz/stamped-external` |
| **Mount path** | `external/` (always this path) |
| **Current pin** | Check `external/VERSION` and `git -C external describe --tags` |
| **Authority** | ADR-011 — `external/` is the **single source of truth** |

### What lives in `external/` (read-only from this repo)

| Path | Purpose | You may edit here? |
| --- | --- | --- |
| `external/contracts/` | JSON schemas, MQTT topics, dedupe golden fixtures | **No** — PR in stamped-external only |
| `external/decisions/` | Architecture Decision Records (ADRs) | **No** |
| `external/handoff/` | Cross-repo integration docs, playbooks, bootstrap guides | **No** (except repo-local notes in *this* repo's `docs/`) |
| `external/technical/` | L0–L6 reference architecture | **No** |
| `external/architecture/` | Layer interface contracts | **No** |
| `external/scripts/contract-check.sh` | Shared CI validation | **No** |

### What lives in *this* repo (you edit here)

- `packages/` — application code
- `deploy/` — compose, terraform, profiles for **this** service
- `docs/` — repo-specific runbooks, architecture deep-dives, research
- `.github/workflows/` — CI for **this** repo (must call platform contract-check)

## Setup — clone and init

**Always** initialize the submodule before build, test, or reading platform docs:

```bash
git submodule update --init --recursive
test -f external/VERSION || { echo "Run: git submodule update --init"; exit 1; }
```

Clone with submodules:

```bash
git clone --recurse-submodules <this-repo-url>
```

## New repo — add platform submodule

```bash
git submodule add https://github.com/vinayak-rz/stamped-external.git external
cd external && git checkout v2026.07.12   # pin to release tag, not main
cd .. && git add .gitmodules external
git commit -m "chore: add stamped-external submodule at v2026.07.12"
```

**Never** copy files from stamped-external into this repo. **Never** fork `external/contracts/` into `packages/` or `docs/`.

## Rules for agents and engineers

1. **Single source of truth** — If a schema, ADR, dedupe rule, or cross-repo interface is defined in `external/`, that definition wins. Do not duplicate or override it in this repo without an ADR in stamped-external first.

2. **Contract changes** — Open PR in `vinayak-rz/stamped-external`, merge, tag release, then bump `external/` submodule pointer in this repo. Never change JSON schemas only in this repo.

3. **Dedupe golden** — `external/contracts/fixtures/dedupe_golden.json` is authoritative. All L1/L2 dedupe tests must match it exactly.

4. **Read before implement** — Before touching ingest, MQTT, envelopes, or layer boundaries:
   - `external/contracts/TOPICS.md`
   - `external/contracts/schemas/stamped-record-envelope.json`
   - `external/architecture/layer-interfaces-l2.md`
   - `external/decisions/ADR-008-layer-repo-topology-and-interfaces.md`
   - This repo's handoff doc under `external/handoff/` (e.g. `stamped-l2-spec.md`, `connectors-bill-spec.md`)

5. **Deployment modes** — `local`, `local-dashboard`, and `cloud` share the same contracts. See `external/handoff/deployment-profiles.md` and ADR-010.

6. **CI on every PR** — This repo must run:

   ```bash
   git submodule update --init --recursive
   ./external/scripts/contract-check.sh
   ```

7. **Bump platform version** — When told to upgrade platform docs/contracts:

   ```bash
   cd external && git fetch origin && git checkout v<NEW_TAG> && cd ..
   git add external && git commit -m "chore(platform): bump stamped-external to v<NEW_TAG>"
   ```

8. **Do not float on main** — Production branches pin `external/` to an explicit tag (e.g. `v2026.07.12`), not `main`.

## Reading order (new to Stamped)

| # | Document |
| --- | --- |
| 1 | `external/technical/00-stamped-master-document.md` |
| 2 | `external/decisions/README.md` |
| 3 | `external/handoff/deployment-profiles.md` |
| 4 | `external/handoff/README.md` → find **this repo's** handoff doc |
| 5 | Repo-specific `AGENTS.md` / `docs/` in this repository |

## Ecosystem map

| Repo | Layer | Handoff doc |
| --- | --- | --- |
| connectors-edge | L1 plant | `external/handoff/connectors-edge-portability-playbook.md` |
| connectors-cloud | L1 cloud | `external/handoff/connectors-cloud-downstream-context.md` |
| connectors-bill | L1 bill | `external/handoff/connectors-bill-spec.md` |
| stamped-l2 (universal-repositary) | L2 | `external/handoff/stamped-l2-spec.md` |
| stamped-l3 … l6 | L3–L6 | (future — same `external/` submodule) |

Full matrix: `external/REPOS.md`

## When you need to change platform docs

```text
1. PR in vinayak-rz/stamped-external  (schema / ADR / playbook)
2. Merge + tag vYYYY.MM.DD
3. PR in this repo bumping external/ submodule pointer
4. CI: contract-check.sh + this repo's E2E
```

Do **not** edit `external/` files in this repo's working tree and commit them here — those commits belong in stamped-external.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Empty `external/` | `git submodule update --init --recursive` |
| Agent can't find schemas | Paths are `external/contracts/schemas/*.json`, not `contracts/` at repo root |
| Submodule detached HEAD | Normal when pinned to a tag |
| Schema mismatch with another repo | Bump both repos to same `external/` tag |
```

---

## Short prompt (minimal — for Cursor / chat)

Use when you only need a brief agent instruction:

```markdown
This is a Stamped product repo. Platform contracts, ADRs, and cross-repo docs are **not** in this repo — they are in git submodule `external/` → https://github.com/vinayak-rz/stamped-external (ADR-011, single source of truth).

Before any work: `git submodule update --init --recursive`.

Rules:
- Never copy or fork `external/contracts/` — change schemas only via PR in stamped-external, then bump submodule here.
- Read `external/handoff/<this-repo>-*.md` and `external/decisions/ADR-008` before layer-boundary work.
- CI must run `./external/scripts/contract-check.sh` on every PR.
- Pin `external/` to a release tag (e.g. v2026.07.12), not main.

Dedupe authority: `external/contracts/fixtures/dedupe_golden.json`.
Layer interfaces: `external/architecture/layer-interfaces-l2.md`.
```

---

## One-liner (issue / PR template footer)

```markdown
Platform SSOT: `external/` submodule → [stamped-external](https://github.com/vinayak-rz/stamped-external) @ tag pinned in this PR. Contract/ADR changes require stamped-external PR first. Run `./external/scripts/contract-check.sh`.
```

---

## Changelog

| Date | Change |
| --- | --- |
| 2026-07-12 | Initial consumer agent prompt for stamped-external submodule model |
