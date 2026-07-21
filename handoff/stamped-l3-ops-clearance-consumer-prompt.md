# Prompt — L3 ops_clearance enablement (for L3 workspace agents)

> **Audience:** Agents / engineers in **`stamped-l3-core`** / **`stamped-l3-rulepacks`** (standalone repos or `consumers/` scaffolds).  
> **Platform source:** [stamped-external](https://github.com/Vinayak-RZ/stamped-external) — pin `external/` after contracts **0.8.0** / Finding **1.1.0** merge.  
> **Authority:** [ADR-020](../decisions/ADR-020-l5-mv-claim-governance.md) · [finding.json](../contracts/schemas/finding.json) · [L3 SSOT](../technical/layers/L3-intelligence-core.md) §2.2 · [L5 SSOT](../technical/layers/L5-closure-and-verification.md)

---

## Copy-paste prompt (start here)

```text
PLATFORM UPDATE — stamped-external requires Finding schema 1.1.0 with
ops_clearance (+ optional alarm_hint) so L5 can ops-verify closures and
route EMS-style alarms. You implement L3 emit only. Do NOT implement L5.

### Mission

Every Finding that leaves the L4 outbox must include a machine-evalable
ops_clearance contract. L5 will poll L2 tags, hold stabilize_window, and
emit WorkflowEvent ops_verified / ops_regressed. Your job is correct emit
shape + tag ids + predicates — not ack, routing, or ledger writes.

### 1) Pin the platform submodule

  git submodule update --init --recursive
  cd external
  git fetch origin
  # Prefer release tag after merge; until then pin the PR branch tip:
  #   cursor/l5-architecture-overhaul-b186  (or merge SHA)
  git checkout <pin-sha-or-tag>
  cd ..
  git add external && git commit -m "chore(external): pin stamped-external Finding 1.1.0 / contracts 0.8.0"

Read (mandatory, in order):
  1. external/decisions/ADR-020-l5-mv-claim-governance.md
  2. external/contracts/schemas/finding.json          # const schema_version 1.1.0
  3. external/contracts/fixtures/finding.valid.json
  4. external/technical/layers/L3-intelligence-core.md §1.1 #3, §2.2, §3.9, §10
  5. external/technical/layers/L5-closure-and-verification.md  (ops-first overview only)
  6. external/handoff/stamped-l3-build-order.md
  7. Optional reference scaffold:
     external/consumers/stamped-l3-core/src/stamped_l3_core/models/finding.py
     (default_ops_clearance helper — port, do not invent a second schema)

Rules:
  - Ponytail first.
  - Never widen Finding category enum unless a theme cannot map (prefer map).
  - Never claim bill-verified savings from L3.
  - Do not implement alarm router, clearance poller, or ledger append (L5).

### 2) Binding Finding 1.1.0 shape

schema_version MUST be "1.1.0".

ops_clearance (REQUIRED on every emitted Finding):
{
  measurement_boundary,          // asset / meter / graph node id
  related_tag_ids: string[],     // L2 tag ids L5 polls — NOT free-text
  clearance_predicate: {
    metric, comparator,          // lt|lte|gt|gte|eq|in_band|out_of_band
    threshold? | band_ref?,      // band_ref = [lo, hi]
    relative_to?                 // baseline | actual_at_detect | absolute
  },
  expected_post_fix_signal,   // short human+machine description
  stabilize_window,              // ISO-8601 duration e.g. PT30M
  reopen_if_regresses: {
    enabled,
    predicate?,                  // required when enabled=true in practice
    grace_window?                // e.g. PT10M
  }
}

alarm_hint (OPTIONAL — suggestion only):
{ severity: info|warning|error|critical, category_code: string }

Keep estimated_monthly_kwh / estimated_monthly_inr as calculated-savings SoT.
inr_decomposition still maps to bill lines for the deferred bill path.

### 3) Emit rules

1. No Finding without ops_clearance — bounce at outbox / schema gate.
2. related_tag_ids must resolve in L2 tag inventory for that plant.
3. clearance_predicate must be evaluable from those tags alone
   (no LLM prose, no "looks better").
4. stabilize_window defaults: MD/coincidence PT30M; SP/idle PT1H;
   SEC drift PT24H — override per plant config when needed.
5. reopen_if_regresses.enabled=true for P0 waste categories 1–5 unless
   plant config disables; include a concrete reopen predicate.
6. Suppression (startup / mix / maintenance / data_quality) still blocks
   emit — that is NOT the same as reopen after ops_verified.
7. Optional alarm_hint.severity: map urgency high→error/critical,
   medium→warning, low→info; category_code stable per theme
   (e.g. md.coincidence, ca.sp_drift, pq.pf_slab).
8. Dedupe unchanged: one open Finding per dedupe_key.

### 4) Vertical catalog → existing categories (map, don't invent)

| Theme                         | category              | waste |
|-------------------------------|-----------------------|-------|
| MD coincidence / headroom     | md_overlap, md_exceedance_risk, cmd_oversized | 1 |
| Idle / run-on                 | idle_load             | 3     |
| Furnace holding               | furnace_holding       | 2     |
| Compressor unload / SP drift  | compressor_sp_drift  | 4     |
| HVAC / chiller staging        | cop_degradation       | 5     |
| WHR / TOD mistiming           | tod_exposure, dispatch_gap | 6 |
| SEC / kWh/t drift             | sec_drift             | 2–5   |

### 5) stamped-l3-core — required work

A. Sync submodule (step 1).
B. Finding model schema_version "1.1.0"; require ops_clearance on to_dict/outbox.
C. MD + PF (+ any other emit paths) populate ops_clearance + alarm_hint.
D. Helper (optional): default_ops_clearance(...) matching schema band_ref.
E. Tests: fixture validates against external/contracts/schemas/finding.json;
   missing ops_clearance fails; golden MD window still emits.
F. README: link ADR-020 + this prompt; note L5 owns verification.

### 6) stamped-l3-rulepacks — required work

A. Sync submodule.
B. Golden expected Findings → 1.1.0 with ops_clearance per rule.
C. Manifest docs: each rule documents suggested related_tag_ids pattern
   and default stabilize_window.
D. Do not add L5 logic to rulepacks.

### Exit criteria

- [ ] ./scripts/contract-check.sh green on pinned external (Finding 1.1.0 fixture)
- [ ] Every outbox Finding validates as schema_version 1.1.0 with ops_clearance
- [ ] related_tag_ids are concrete L2-style tag paths (asset/metric)
- [ ] No L5 alarm router / clearance poller / ledger code in l3 repos
- [ ] Conventional commits; README updated

### Explicit non-goals

- Implementing stamped-l5 or L6 EMS console
- Bill-verified ledger status (verified reserved; L5 uses ops_confirmed)
- Expanding Finding.category enum without platform ADR
- Ack / silence / escalate UX
```

---

## After paste — platform pointers for reviewers

| Check | Path |
|-------|------|
| Schema | [`contracts/schemas/finding.json`](../contracts/schemas/finding.json) |
| Golden | [`contracts/fixtures/finding.valid.json`](../contracts/fixtures/finding.valid.json) |
| Scaffold helper | [`consumers/stamped-l3-core/.../models/finding.py`](../consumers/stamped-l3-core/src/stamped_l3_core/models/finding.py) |
| L5 consumes | [`handoff/stamped-l5-architecture-handoff.md`](./stamped-l5-architecture-handoff.md) |
