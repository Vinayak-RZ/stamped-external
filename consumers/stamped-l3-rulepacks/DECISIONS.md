# Decisions — stamped-l3-rulepacks

## D001 — Domain × vertical × tariff axes

- **Context:** Need breadth across HT verticals without embedding plant overrides.
- **Alternatives:** Single flat pack per plant; monolith constants in core.
- **Selected:** Domain packs + vertical overlays + DISCOM tariff tables.
- **Rationale:** Matches L3 §3.5 / §3.9; keeps core engine-only (ADR-012).

## D002 — Optimization methods as first-class rule IDs

- **Context:** Furnace hold, idle sleep, stagger/shed/TOD/PF/CMD must not collapse into one vague rule per pack.
- **Alternatives:** One rule file per pack with method enum.
- **Selected:** Separate `rules/<id>.yaml` per method (§E); same Finding category allowed.
- **Rationale:** Findings cite distinct `rule_or_model_ref`; goldens can assert method id.

## D003 — Dual path for incomer layout

- **Context:** Existing `incomer/1.0.0/` consumed before `domain/` tree.
- **Selected:** Canonical `domain/incomer/1.0.0/`; legacy mirror until core cutover.
- **Rationale:** Avoid breaking `RULEPACK_PATH` during catalog expansion.
