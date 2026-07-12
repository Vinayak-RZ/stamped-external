# connectors-bill — Agent onboarding

Paste into **`AGENTS.md`** in the new repository.

---

```markdown
# connectors-bill — Agent Mode

**Layer:** L1 bill ingest + **customer-facing document UI** (Connect & Normalise).  
**NOT in scope:** cloud MQTT consumer/outbox (connectors-cloud), edge Modbus, L2–L6 intelligence/dashboard core.

## Read first

1. [external/handoff/connectors-bill-spec.md](external/handoff/connectors-bill-spec.md) — repo charter
2. [external/handoff/connectors-bill-ecosystem-integration.md](external/handoff/connectors-bill-ecosystem-integration.md) — how repos connect
3. [external/handoff/connectors-cloud-downstream-context.md](external/handoff/connectors-cloud-downstream-context.md) — MQTT consumer already built
4. [external/handoff/connectors-bill-ui-ux-charter.md](external/handoff/connectors-bill-ui-ux-charter.md) — mobile-first customer UI
5. [external/design/forge-industrial-design-system.md](external/design/forge-industrial-design-system.md) — **Forge Industrial v2.0** (stamped.work + dashboard demo)
6. [docs/architecture/layer-interfaces.md](docs/architecture/layer-interfaces.md) — boundary contracts (copy from connectors-cloud)
7. [external/technical/00-stamped-master-document.md](external/technical/00-stamped-master-document.md) — product master doc
8. [external/technical/layers/L1-connect-and-normalise.md](external/technical/layers/L1-connect-and-normalise.md) — §3.4 bill ingest depth

**Sibling repos:** connectors-edge (plant MQTT) · **connectors-cloud** (L1 cloud consumer — **ready**) · stamped-l2…l6 (downstream).

| Package | Role |
|---------|------|
| `packages/web` | Next.js PWA — upload, review, history (customer-facing) |
| `packages/api` | Upload API, review CRUD, publish trigger |
| `packages/extract` | OCR, template parse, LLM assist |
| `packages/validate` | Recompute gate (₹ arithmetic) |
| `packages/publish` | MQTT BillLine + Event publisher |
| `packages/templates` | Per-DISCOM field maps |

## Rules

- Publish **only** `extraction.validated=true` BillLines to MQTT.
- Dedupe keys: `sha256(plant_id | bill_id | line_type | bill_month)` — match [dedupe_golden.json](external/contracts/fixtures/dedupe_golden.json).
- Never write stamped-l2 tables; MQTT → connectors-cloud → L2 only.
- Schema changes: update `external/contracts/CHANGELOG.md`; BACKWARD compat in CI.
- Customer UI: **mobile-first**; support PDF upload **and** camera capture.
- Scope includes **future doc types** — do not hard-code DISCOM-only in architecture.

## Verification

```bash
# Dedupe unit tests must pass first
pytest packages/publish/tests/test_dedupe.py

# MQTT → cloud inbox (connectors-cloud compose running)
./scripts/e2e-bill-to-cloud.sh
```

## Downstream

connectors-cloud subscribes to `stamped/v1/+/+/bills` — see connectors-cloud-downstream-context.md for exact contract.
```

---

## Bootstrap commands (human or agent)

```bash
mkdir connectors-bill && cd connectors-bill
git init

# Copy handoff package (this external/ folder)
cp -r /path/to/external ./external

# Copy layer interfaces from connectors-cloud
mkdir -p docs/architecture
cp /path/to/connectors-cloud/docs/architecture/layer-interfaces.md docs/architecture/

# Create AGENTS.md from section above
# Create README pointing to external/handoff/README.md
```

---

## First implementation milestones

1. **Dedupe + schema tests** — prove contract alignment with cloud  
2. **MQTT publish CLI** — manual `bill_line.valid.json` → cloud inbox  
3. **Presigned upload API** — single PDF  
4. **Mobile upload UI** — camera + file picker  
5. **One DISCOM template** — MSEDCL or UPPCL  
6. **Recompute gate** — block unvalidated publish  
7. **Review UI** — edit + approve  
8. **E2E script** — full path automated  

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-11 | Initial agent onboarding block |
