# Progress — L3/L4 Intelligence (Beat Zerowatt)

> Live status for [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) · Nawab v3 · Branch `cursor/l3-l4-intelligence-272a`

## Current phase

**Complete** — P0 platform + consumer scaffolds through Phase N

## Completed phases

| Phase | Status | Notes |
|-------|--------|-------|
| 0 | done | IMPLEMENTATION_PLAN, PROGRESS, DECISIONS |
| A | done | Specs, ADR-012/013/014, contracts 0.6.0 |
| B | done | stamped-l3-core scaffold (9 tests) |
| C | done | rulepacks v0.1 + eval CLI |
| D | done | stamped-l4 template-fast-path (22 eval tasks) |
| P2 | done | TimesFM shadow stub; no promotion |
| N | done | validate.sh green |

## Blockers cleared

| Item | Status |
|------|--------|
| Finding contract frozen | done — contracts 0.6.0 |
| Pilot golden windows | done — synthetic v0 + golden_md_spike |
| L2 query API | workaround — FixtureL2Client in l3-core |

## Validation

```bash
./scripts/validate.sh
```

## Dual-lane Lab retention (2026-07-15)

| Item | Status |
|------|--------|
| ADR-015 / ADR-016 | done |
| RunArtifact 1.1.0 + Lab UI lanes | done |
| Attribution explainability + shadows | done |
| Core hot-path LabLog (no silent drop) | done |

## L4 architecture SSOT (2026-07-17)

| Item | Status |
|------|--------|
| L4 layer spec rewrite | done — adaptive RAG, dual lane, eval stack |
| ADR-017 adaptive retrieval + web T4 | done |
| handoff/stamped-l4-architecture-handoff.md | done (supersedes build-order) |

## Next (P1 — out of P0 scope)

- Live L2 query API integration
- LangGraph full agent lane (per L4 handoff)
- Forging/auto rulepacks
- TimesFM promotion re-eval with pilot data
- Event NILM-lite attribution shadow (gated 1-min + labels)
