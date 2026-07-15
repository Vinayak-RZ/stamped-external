# Prompt — L3 dual-lane + attribution shadows (for core & rulepacks agents)

> **Audience:** Agents / engineers working in **`stamped-l3-core`** and **`stamped-l3-rulepacks`** (standalone GitHub repos or `consumers/` scaffolds).  
> **Platform source:** [stamped-external](https://github.com/Vinayak-RZ/stamped-external) — pin `external/` after the dual-lane PR merges (or pin this branch SHA meanwhile).  
> **Authority:** [ADR-015](../decisions/ADR-015-l3-dual-lane-lab-detections.md) · [ADR-016](../decisions/ADR-016-attribution-shadow-challengers.md) · [L3-attribution-explainability.md](../technical/layers/L3-attribution-explainability.md) · [L3-decision-defense-brief.md](../technical/layers/L3-decision-defense-brief.md)

---

## Copy-paste prompt (start here)

```text
PLATFORM UPDATE — stamped-external has decided and documented L3 dual-lane Lab
retention + attribution explainability/shadows. Your repo must sync the
submodule and implement against those decisions. Do not invent a different
trust model.

### 1) Update the platform submodule

In this consumer repo:
  git submodule update --init --recursive
  cd external
  git fetch origin
  # After merge to main, prefer a release tag (e.g. vYYYY.MM.DD).
  # Until then, pin the dual-lane branch tip or merge SHA from:
  #   https://github.com/Vinayak-RZ/stamped-external/pull/9
  git checkout <pin-sha-or-tag>
  cd ..
  git add external && git commit -m "chore(external): pin stamped-external for ADR-015/016 dual-lane"

Read (mandatory, in order):
  1. external/decisions/ADR-015-l3-dual-lane-lab-detections.md
  2. external/decisions/ADR-016-attribution-shadow-challengers.md
  3. external/technical/layers/L3-attribution-explainability.md
  4. external/technical/layers/L3-intelligence-core.md §3.4 + §9 Lab retention note
  5. external/handoff/stamped-l3-build-order.md
  6. If scaffold still lives under stamped-external consumers/, also compare:
     external/consumers/stamped-l3-core/ and external/consumers/stamped-l3-rulepacks/
     (reference implementation — port, do not blindly overwrite product code)

Rules:
  - Ponytail first (.cursor/skills/ponytail or external AGENTS.md).
  - Never edit finding.json to widen L4 trust; dual-lane keeps weak signals in Lab only.
  - Observation-only: no “promote this Lab row to L4” feature.

### 2) Shared contract (both repos)

Every structured detection candidate gets:
  - status ∈ {emitted, suppressed, shadow_only, hypothesis}
  - delivery ∈ {l4, lab_only}
Invariant: delivery == l4  ⇔  status == emitted  ⇔  Finding outbox stage.
Everything else stays lab_only forever until a rulepack/threshold/calibration
change makes a future emit legitimate.

RunArtifact schema is 1.1.0 — see:
  external/consumers/stamped-l3-eval/schemas/run-artifact.v1.json
Lab UI (eval) already separates L4 vs Lab-only lanes; core must export the fields.

### 3) stamped-l3-core — required work

A. Sync submodule (step 1).
B. Ensure LabLog / lab export emits schema_version "1.1.0" with delivery on every
   detection (mirror of external/consumers/stamped-l3-core/src/stamped_l3_core/).
C. Hot / warm paths: NEVER silent-drop suppressed candidates. Log them to LabLog
   with status=suppressed, delivery=lab_only. Emit+outbox only when emitted/l4.
D. detection_lane helper: delivery_for(status) — one source of truth.
E. Attribution of-record remains graph co-start:
     score = ramp_kw × proximity, proximity = 1/(1+hops)
   Top-1 gated → emitted/l4 (+ outbox Finding citing rulepack://attribution/…#costart_window).
   Runner-ups → hypothesis/lab_only with full scores (ramp_kw, hops, proximity, score, rank, …).
F. Attribution shadows (ADR-016) — Lab-only only:
     - ranking ablations (corr_primary, flat_proximity, wider_window)
     - STUMPY/motif concordance stub
     - NOT SHAP, NOT full deep NILM
     scores.shadow_method + scores.agree_with_primary required
G. Tests: (1) suppress → lab_only and empty outbox for that candidate
           (2) emit → outbox + lab l4 mirror
           (3) shadows never outbox
H. Commit conventionally; update README pointing at ADR-015/016.

Exit criteria (core):
  - pytest green
  - /lab/export (or LabLog.to_run_artifact) validates against RunArtifact 1.1.0
  - grep proves no “if suppressed: continue” without LabLog.add_detection

### 4) stamped-l3-rulepacks — required work

A. Sync submodule (step 1).
B. Keep domain/attribution costart_window params as of-record defaults
   (costart_minutes, max_hops) — document that Lab runner-ups/shadows are
   engine-side, not new Finding categories.
C. Do NOT invent Finding categories for shadows or hypotheses.
D. AUTHORING.md must link to:
     external/technical/layers/L3-attribution-explainability.md
E. Goldens may assert expected_rule_id for of-record emits only; lab_only rows
   are not rulepack golden expectations unless you add optional lab fixtures
   under fixtures/ (engine owns LabLog).
F. Vertical overlays remain thresholds/priors only — no delivery overrides that
   force L4 for weak signals.
G. Commit conventionally; DECISIONS.md note “ADR-015/016 synced via external pin”.

Exit criteria (rulepacks):
  - pytest / golden CI green
  - AUTHORING + attribution pack README mention dual-lane + explainability doc
  - No new enum categories for shadow methods

### 5) Non-goals (reject if asked)

- Manual promote Lab row → L4 outbox
- SHAP as attribution shadow
- Full industrial NILM as of-record or default shadow
- Changing L4 Finding contract for “maybe” savings
- Customer/L6 visibility of Lab-only lane

### 6) Done report back

Report: external pin SHA/tag, files changed, tests run, confirmation of lane
invariant, and any gaps vs external/consumers reference scaffolds.
```

---

## Short variants

### Core-only one-liner block

```text
Update external/ to stamped-external ADR-015/016 (PR #9 / post-merge tag). Implement dual-lane: log all candidates to LabLog with delivery l4|lab_only; only emitted→outbox; attribution top-1 of-record, runners hypothesis/lab_only; shadows = ranking ablations + motif stub (not SHAP/NILM). Mirror external/consumers/stamped-l3-core reference. Tests for no silent suppress drop + shadows ∉ outbox. Ponytail.
```

### Rulepacks-only one-liner block

```text
Update external/ to stamped-external ADR-015/016. Attribution of-record stays costart_window (ramp_kw×1/(1+hops)); do not add shadow Finding categories; link AUTHORING to L3-attribution-explainability.md; verticals cannot force weak signals to L4. Goldens cover of-record emits only. Ponytail.
```

---

## Pin reminder

| When | Pin |
| --- | --- |
| PR #9 open | Branch `cursor/l3-dual-lane-lab-detections-c33b` tip SHA |
| After merge | `main` then next `vYYYY.MM.DD` tag — prefer tag in production |
| Eval | `stamped-l3-eval` Lab UI already consumed 1.1.0 in the platform PR; pin the same external SHA |

---

## What changed in external (for orientation)

| Artifact | Role |
| --- | --- |
| ADR-015 | Dual delivery lanes; observation-only |
| ADR-016 | Attribution shadows (ablations + STUMPY; reject SHAP/full NILM) |
| `L3-attribution-explainability.md` | Engineer-facing explainability + quality grade |
| RunArtifact 1.1.0 | `delivery` + `hypothesis` |
| `consumers/stamped-l3-core` | Reference: detection_lane, scheduler LabLog, attribution_shadow |
| `consumers/stamped-l3-eval` | Lab UI lanes + inspector (eval agent / same pin) |
