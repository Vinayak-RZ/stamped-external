# stamped-l6 — Agent onboarding

Paste into **`AGENTS.md`** in the new `stamped-l6` repository.

---

## Identity

You are building **stamped-l6** — Experience & Integration (ops-first control room).

Mount platform pack:

```bash
git submodule add https://github.com/vinayak-rz/stamped-external.git external
cd external && git checkout <release-tag> && cd ..
```

## Read first (in order)

1. `external/technical/layers/L6-experience-and-integration.md`
2. `external/handoff/stamped-l6-architecture-handoff.md`
3. `external/handoff/stamped-l6-ui-ux-charter.md`
4. `external/handoff/stamped-l6-build-plan.md`
5. `external/decisions/ADR-022-l6-bff-runtime-boundary.md`
6. `external/decisions/ADR-023-l6-ems-and-analyst-context.md`
7. `external/decisions/ADR-020-l5-mv-claim-governance.md`
8. `external/design/forge-industrial-design-system.md`
9. `external/consumers/stamped-l6/TRANSFER.md` (+ seed under `external/consumers/stamped-l6/`)
10. `external/consumers/readmes/closure-verification.md` (Connect L6)
11. `external/handoff/l6-counterfactual-display-stub.md`
12. `external/handoff/consumer-platform-prompt.md`

## Hard rules

- **Ponytail** before every code edit (`external/.cursor/skills/ponytail/SKILL.md`).
- HTTP only to L2/L4/L5 — **never** `L2_DATABASE_URL` or OT writes.
- `ops_confirmed` ≠ bill `verified`. Never imply DISCOM verification from ops.
- Workflow/alarm truth is **L5**; L6 renders and forwards actions with Idempotency-Key.
- Analyst RAG is **L4**; send explicit removable context envelopes only ([ADR-023](../decisions/ADR-023-l6-ems-and-analyst-context.md)).
- English only through P2 ([ADR-018](../decisions/ADR-018-l4-pilot-execution-knowledge-reasoning.md)).
- Schema changes → PR in stamped-external + semver; run `./external/scripts/contract-check.sh`.
- **Never** copy `external/contracts` into packages; use submodule.

## NOT in scope

MQTT ingest · edge agents · bill OCR · L3 engines · L4 LangGraph implementation · 3D digital twin · named SAP connectors (P3 paid).

## Definition of done (P0 slice)

- [ ] Commit matrix row tested and conventional-committed
- [ ] Claim badges + modeled disclaimer correct
- [ ] Mobile alarm ack + Rx defer-with-reason work
- [ ] Mode A focus trap + Esc + removable chips
- [ ] No secrets in repo
