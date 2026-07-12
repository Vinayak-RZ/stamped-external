# Temporary asset IDs (`stamped.local/*`) — migration policy

**Status:** Active until L2 energy graph ships.  
**Authority:** [ADR-003](ADR-003-connectors-edge-monorepo.md)

## Format

```
stamped.local/{plant_slug}/{asset_slug}
```

- Lowercase slugs; `[a-z0-9-]` only.
- Unique per `plant_id`.

## When L2 exists

1. L2 exposes canonical assets (e.g. `asset:incomer-main` or UUID).
2. Run plant migration: map each `stamped.local/*` → L2 `asset_id`.
3. Publish new `mapping_version` to edge fleet.
4. Record execution in `ADR-004-migration-stamped-local-assets.md` (create when first migration runs).

## Do not

- Use `stamped.local/*` in customer-facing reports after L2 cutover.
- Auto-migrate without human sign-off per plant.
