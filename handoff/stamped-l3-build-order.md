# stamped-l3 — P0 build order

> **Aligned with:** [ADR-012](../decisions/ADR-012-l3-artifact-repo-topology.md) · [ADR-008](../decisions/ADR-008-layer-repo-topology-and-interfaces.md) · [L3 spec](../technical/layers/L3-intelligence-core.md)  
> **Repos:** `stamped-l3-core` · `stamped-l3-rulepacks` · `stamped-l3-eval`

---

## Exit criterion (P0 complete)

- MD engine emits `Finding` from L2 fixture client via transactional outbox
- incomer rulepack v0.1.0 golden CI green
- `./scripts/contract-check.sh` green on pinned `external/contracts` SHA
- Hot path scheduler runs MD + PF without blocking cold refit

---

## Phase B — Core scaffold

| Step | Repo | Deliverable | Exit test |
| --- | --- | --- | --- |
| B1 | l3-core | Repo scaffold + pyproject | `pytest --collect-only` |
| B2 | l3-core | L2 query client protocol + fixture | Unit mock returns measurements |
| B3 | l3-core | Finding model + dedupe_key | Schema round-trip |
| B4 | l3-core | MD engine deterministic core | Golden window → finding |
| B5 | l3-core | Suppression service | Startup window suppresses emit |
| B6 | l3-core | Transactional outbox | Finding envelope persisted |
| B7 | l3-core | Hot path scheduler | APScheduler tick fires engines |
| B8 | l3-core | Tariff/PF engine v0 | PF slab finding |
| B9 | l3-core | Rulepack loader interface | Loads semver manifest |

**L2 workaround:** Use fixture JSON until `stamped-l2` query API live ([handoff/stamped-l2-query-api-sketch.md](stamped-l2-query-api-sketch.md)).

---

## Phase C — Rulepacks + eval

| Step | Repo | Deliverable | Exit test |
| --- | --- | --- | --- |
| C1 | rulepacks | Manifest schema + incomer v0.1.0 | Golden replay pytest |
| C2 | rulepacks | TOD exposure rules v0.1.0 | Golden replay |
| C3 | eval | Synthetic corpus v0 | CLI lists windows |
| C4 | eval | Rolling backtest skeleton | CLI runs without error |

**P0 vertical:** incomer-only (MD/PF/TOD). Forging/auto packs deferred P1.

---

## Submodule pin

```bash
git submodule add https://github.com/Vinayak-RZ/stamped-external.git external
cd external && git checkout <platform-tag>
```

Pin SHA in l3-core README on every release.

---

## Consumer relay

```
stamped-l2 (query API) ← stamped-l3-core (read-only)
stamped-l3-core (outbox) → stamped-l4 (Finding inbox)
```

No `L2_DATABASE_URL` in l3-core — ADR-008 non-negotiable.
