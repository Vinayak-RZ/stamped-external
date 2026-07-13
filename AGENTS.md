# Stamped Platform — Agent Mode

> **Repo role:** Shared platform pack (contracts, ADRs, handoff, technical specs) — **not application code**.  
> **Cursor config source:** [cursor-config-coding](https://github.com/Vinayak-RZ/cursor-config-coding) (vendored under `.cursor/`).

Engineering workflow: **ponytail → (spec-kit for features) → research → plan → approve → implement → validate → commit → learn**.

## Repo-specific guidance

| Area | Guidance |
|------|----------|
| **Contracts** (`contracts/`) | Schema changes require `contracts/CHANGELOG.md` semver bump + `scripts/contract-check.sh` pass |
| **ADRs** (`decisions/`) | New decisions as ADR-NNN; update `decisions/README.md` index |
| **Handoff** (`handoff/`) | Cross-repo integration docs; keep in sync with consumer repos |
| **Consumer repos** | See [REPOS.md](REPOS.md) and [SUBMODULE.md](SUBMODULE.md) |
| **Release** | Tag `vYYYY.MM.DD`; bump [VERSION](VERSION) and [CHANGELOG.md](CHANGELOG.md) |

**Reading order for new agents:** [README.md](README.md) → [technical/00-stamped-master-document.md](technical/00-stamped-master-document.md) → [decisions/README.md](decisions/README.md).

## Ponytail — mandatory gate for all coding

**Before writing or modifying any code**, read and apply the `ponytail` skill (`.cursor/skills/ponytail/SKILL.md`). Always-on rule: `ponytail.mdc`.

From [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) — lazy senior dev ladder for minimal, production-grade diffs. **Skills + MDC only** (no Ponytail MCP).

| Layer | What | When |
|-------|------|------|
| Rule | `ponytail.mdc` | Always on — requires reading the `ponytail` skill before code |
| Skill | `ponytail` | **Read first** on every coding task (write, fix, refactor, add deps) |
| Review | `ponytail-review`, `ponytail-audit` | After implementation or on request — hunt over-engineering |

Climb the ladder after you understand the problem: YAGNI → reuse codebase → stdlib → native → installed dep → one line → minimum that works. Never cut validation, security, accessibility, or error handling that prevents data loss.

Intensity: `full` (default). User can say `/ponytail ultra` for stricter YAGNI or `stop ponytail` to disable.

## Spec Kit — Spec-Driven Development (features / greenfield)

From [github/spec-kit](https://github.com/github/spec-kit). Pre-installed skills: `speckit-*`. Rule: `speckit.mdc`.

Use for **new features / greenfield**, not one-line fixes or contract typo fixes.

Order: `constitution` → `specify` → (`clarify`) → `plan` → (`checklist`) → `tasks` → (`analyze`) → `implement` → (`converge`).

During implement, still apply **ponytail** on every code change.

## Before any task

1. Read this file and all `.cursor/rules/` (start with `rule-awareness`, `ponytail`, `core-engineering`, `learn-and-research`).
2. **Coding tasks:** read `ponytail` skill and climb the ladder before proposing or writing code.
3. **Feature / greenfield:** follow `speckit.mdc` and Spec Kit skills when the user wants specs-first or the change is multi-phase.
4. Follow `planning.mdc` — analyze, plan, **get user approval** before non-trivial coding.
5. Follow `communication.mdc` — surface risks and tradeoffs explicitly.
6. Unfamiliar tech → research brief for the user before architectural choices.

## Architecture (when designing or refactoring)

| Domain | Skill | Rule |
|--------|-------|------|
| Frontend / UI / Next.js | `frontend-architecture` | `frontend-architecture.mdc` |
| Backend / API / data | `backend-architecture` | `backend-architecture.mdc` |
| AI agents / LLM / tools | `agentic-system-design` | `agentic-systems.mdc` |
| Any major trade-off | `system-design-tradeoffs` | `trade-offs.mdc` |

Before large refactors, consider `graphify` on the affected directory.

## Learning & documentation

| Need | Skill / doc |
|------|-------------|
| Learn while building | `learn-while-building` |
| Exhaustive README | `extensive-readme` |

End each phase with a short **What you learned** summary.

## Git commits and pushes

After each validated phase or meaningful feature:

- **Conventional commit** per `git-commit-discipline.mdc`
- **Push check** after every commit — auto-push when **≥ 10 unpushed** commits, or when user asks

## MCP (live architecture patterns)

Default server: **agent-patterns** → [Agent Patterns Catalog](https://www.agentpatternscatalog.org/)  
Config: `.cursor/mcp.json`

For agentic design, **query MCP first** (`find_pattern`, `recommend_recipe`, `pattern_for_symptom`) then apply `agentic-system-design` + `system-design-tradeoffs`.

## During implementation

7. Apply `execution.mdc` — phase-based work only; minimal scope; **read `ponytail` skill** on every edit.
8. UI polish: `impeccable`. Animation: `gsap-*` skills.
9. Before marking done on non-trivial changes: consider `ponytail-review` on the diff.

## Before completion

10. Apply `quality-gates.mdc` — validate, report, update progress docs, **commit**.
11. Contract changes: run `./scripts/contract-check.sh` before marking done.

## Pre-installed skills (36)

See [skills-manifest.json](skills-manifest.json) for the full list.

## Upstream config

To refresh from [cursor-config-coding](https://github.com/Vinayak-RZ/cursor-config-coding):

```bash
git clone --depth 1 https://github.com/Vinayak-RZ/cursor-config-coding.git /tmp/cursor-config-coding
cp -a /tmp/cursor-config-coding/.cursor /workspace/
cp /tmp/cursor-config-coding/skills-manifest.json /workspace/
# Re-apply repo-specific AGENTS.md overrides as needed
```
