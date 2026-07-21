# stamped-l3 — P0 build order

> **Aligned with:** [ADR-012](../decisions/ADR-012-l3-artifact-repo-topology.md) · [ADR-008](../decisions/ADR-008-layer-repo-topology-and-interfaces.md) · [L3 spec](../technical/layers/L3-intelligence-core.md) · [ADR-020](../decisions/ADR-020-l5-mv-claim-governance.md)  
> **Repos:** `stamped-l3-core` · `stamped-l3-rulepacks` · `stamped-l3-eval`  
> **Ops-clearance enablement:** [stamped-l3-ops-clearance-consumer-prompt.md](./stamped-l3-ops-clearance-consumer-prompt.md)

---

## Exit criterion (P0 complete)

- MD engine emits `Finding` **1.1.0** (with `ops_clearance` + optional `alarm_hint`) from L2 fixture client via transactional outbox
- incomer rulepack v0.1.0 golden CI green
- `./scripts/contract-check.sh` green on pinned `external/contracts` SHA
- Hot path scheduler runs MD + PF without blocking cold refit
- Every emitted Finding validates against `finding.json` const `1.1.0`

---

## Phase B — Core scaffold

| Step | Repo | Deliverable | Exit test |
| --- | --- | --- | --- |
| B1 | l3-core | Repo scaffold + pyproject | `pytest --collect-only` |
| B2 | l3-core | L2 query client protocol + fixture | Unit mock returns measurements |
| B3 | l3-core | Finding model + dedupe_key + **ops_clearance** | Schema round-trip **1.1.0** |
| B4 | l3-core | MD engine deterministic core | Golden window → finding with clearance |
| B5 | l3-core | Suppression service | Startup window suppresses emit (≠ reopen) |
| B6 | l3-core | Transactional outbox | Finding envelope persisted |
| B7 | l3-core | Hot path scheduler | APScheduler tick fires engines |
| B8 | l3-core | Tariff/PF engine v0 | PF slab finding + clearance |
| B9 | l3-core | Rulepack loader interface | Loads semver manifest |
| B10 | l3-core | Clearance helpers per category | `related_tag_ids` are real L2 tag ids |

**L2 workaround:** Use fixture JSON until `stamped-l2` query API live ([handoff/stamped-l2-query-api-sketch.md](stamped-l2-query-api-sketch.md)).

**Do not implement in l3-core:** alarm ack/route/escalate, ops clearance poller, ledger append — those are L5.

---

## Phase C — Rulepacks + eval

| Step | Repo | Deliverable | Exit test |
| --- | --- | --- | --- |
| C1 | rulepacks | Manifest schema + incomer v0.1.0 | Golden replay pytest |
| C2 | rulepacks | TOD exposure rules v0.1.0 | Golden replay |
| C3 | eval | Synthetic corpus v0 | CLI lists windows |
| C4 | eval | Rolling backtest skeleton | CLI runs without error |
| C5 | eval | False-clear / regress labels from L5 fixtures | Calibration harness stub |

**P0 vertical:** incomer-only (MD/PF/TOD). Forging/auto packs deferred P1.

---

## Submodule pin

```bash
git submodule add https://github.com/Vinayak-RZ/stamped-external.git external
cd external && git checkout <platform-tag>
```

Pin SHA in l3-core README on every release. After ops-clearance merge, pin a tag that includes contracts **0.8.0** / Finding **1.1.0**.

---

## Consumer relay

```
stamped-l2 (query API) ← stamped-l3-core (read-only)
stamped-l3-core (outbox Finding 1.1.0) → stamped-l4 (Finding inbox)
stamped-l4 (Prescription) → stamped-l5 (ops_clearance eval + alarm router)
```

No `L2_DATABASE_URL` in l3-core — ADR-008 non-negotiable.
