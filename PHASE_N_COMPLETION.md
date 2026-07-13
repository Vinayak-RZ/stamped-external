# Phase N completion — L3/L4 intelligence P0

> Branch: `cursor/l3-l4-intelligence-272a` · Date: 2026-07-13

## Completed

- Phase A: L1–L5 spec updates, ADR-012/013/014, contracts 0.6.0
- Phase B: `consumers/stamped-l3-core` — MD engine, suppression, outbox (9 tests)
- Phase C: `consumers/stamped-l3-rulepacks` + `stamped-l3-eval` scaffolds
- Phase D: `consumers/stamped-l4` template-fast-path + 22-task eval manifest
- Phase P2: TimesFM shadow stub; ADR-014 promotion = do not promote
- Phase N: `scripts/validate.sh` green; E2E finding→ledger; adversarial RT-06

## Validation

```
./scripts/validate.sh  # ALL GREEN
```

## What you learned

- Contract-first unblocked consumer scaffolds: Finding/Prescription/Ledger schemas before any engine handler.
- Template-fast-path covers P0 without LLM — LangGraph deferred P1 with eval baseline already in place.
- ADR-012 three-repo split mirrors L1 edge/cloud/bill without breaking ADR-008 single-Finding-outbox rule.

## Remaining (P1)

- Wire stamped-l3-core to live L2 query API
- LangGraph agent lane + forging rulepacks
- TimesFM eval with real pilot windows
