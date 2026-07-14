# stamped-l3-eval — Corpus, gates, and Internal Lab UI

> **What it is:** Golden corpus, rolling backtest CLI, and an **internal Lab UI** for engineers to inspect every L3 engine / rule / ML-shadow detection.  
> **What it is not:** Plant operator dashboard (L6), rule authoring (rulepacks), prescription approval (L4/L5), or the engine runtime (core).  
> **Authority:** [ADR-012](../../decisions/ADR-012-l3-artifact-repo-topology.md) · [finding.json](../../contracts/schemas/finding.json)

---

## What evals do

| Capability | Role |
| --- | --- |
| Corpus | Gold windows for CI |
| CLI backtest | Batch metrics / gates |
| **Lab UI** | Human forensic: all engines, rules, ML shadow, suppressions |
| Champion gates | Promote/demote via metrics (P1+) |
| Live attach | Debug running core without L6 |

---

## Quickstart — CLI

```bash
cd consumers/stamped-l3-eval
pip install -e ".[dev]"
stamped-l3-eval corpus list
stamped-l3-eval backtest run
stamped-l3-eval artifact show --path artifacts/golden/run_w-md-001.json
stamped-l3-eval lab-run --window w-md-001
```

## Quickstart — Lab UI

```bash
export LAB_SHARED_SECRET=dev-secret
cd consumers/stamped-l3-eval/ui
pnpm install && pnpm dev
# open http://localhost:3000 — Authorization: Bearer / cookie via LAB_SHARED_SECRET
```

Live attach (optional):

```bash
export CORE_LAB_URL=http://127.0.0.1:8090
export CORE_LAB_TOKEN=dev-token
```

---

## Layout

```text
corpus/                 # windows
artifacts/golden/       # RunArtifact v1 fixtures
schemas/run-artifact.v1.json
src/stamped_l3_eval/    # CLI + artifact + live_client
ui/                     # Next.js Lab
PRODUCT.md · DESIGN.md  # Impeccable context
```

## Design

Impeccable product register — light laboratory theme (see `DESIGN.md`). Dense tables; emit/suppress/shadow status chips; no customer dashboard chrome.

## Related

- [stamped-l3-core](../stamped-l3-core/) — engines + lab export  
- [stamped-l3-rulepacks](../stamped-l3-rulepacks/) — rules cited as `rulepack://…`  
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
