# PHASE_L6_N_HARDENING_COMPLETION.md

> Phase N · 2026-07-21 · L6 architecture + UI handoff

## Validation evidence

| Gate | Result |
|------|--------|
| `./scripts/contract-check.sh` | OK (14 schemas, 12 fixtures) |
| `consumers/stamped-l6` `npm test` | 6/6 pass |
| `npm run typecheck` | pass |
| `npm run build` | pass (9 routes) |

## Ponytail-review (diff)

- `ContextualAnalyst` chip remove: **shrink** — reverse-lookup by string → keyed `ContextChip` (fixed in this phase).
- `PlantMap3D` / Recharts / fake LIVE: **delete** from seed (never imported). Lean already for remaining surface.

`net: - ~25 lines` on chip removal path.

## Security checklist (route-aware analyst)

- [x] Context is structured envelope fields only (no DOM scrape)
- [x] Chips user-visible and removable
- [x] `assertTenantMatch` unit-tested for cross-plant focus
- [x] No service keys / secrets in fixtures
- [x] Irreversible actions remain explicit buttons (agent proposes only)
- [ ] Consumer must re-enforce envelope validation on BFF (documented in ADR-023 + TRANSFER)

## Accessibility smoke (manual against charter)

- Mode A: `role="dialog"` + `aria-modal` + Esc + labelled close
- Status chips include text labels (not colour-only)
- Tables on Reports use `scope="col"`
- Gauge/LoadDial expose `role="img"` + `aria-label`
- `prefers-reduced-motion` honored in tokens.css

Remaining consumer work: full keyboard j/k triage, focus return to Ask Analyst opener, Playwright visual suite.

## Files in this phase

- `consumers/stamped-l6/src/lib/analyst-context.ts` (keyed chips)
- `consumers/stamped-l6/src/components/analyst/ContextualAnalyst.tsx`
- `consumers/stamped-l6/tests/format-and-context.test.ts`
- This report

## Task exit criteria

- [x] Architecture/UI handoffs complete
- [x] Ops-first + EMS ownership explicit
- [x] Contextual analyst contract defined
- [x] Reference shell Today/Alarms/Prescriptions/Mode A–B pass gates
- [x] New L6 agent can start from handoff without opening the Vite demo

## What you learned

- Keyed context chips are both a UX and a security simplification.
- Contract-check needs `jsonschema` in the environment; document for agents.
- Handoff + seed transfer is enough for L6 P0 planning; live HTTP remains the consumer’s first real risk.
