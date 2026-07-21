# stamped-l6 (platform reference UI seed)

> **Non-canonical.** Adapt into the live consumer repo `Vinayak-RZ/stamped-l6` (planned).  
> **Authority:** [handoff/stamped-l6-ui-ux-charter.md](../../handoff/stamped-l6-ui-ux-charter.md) · [ADR-022](../../decisions/ADR-022-l6-bff-runtime-boundary.md) · [ADR-023](../../decisions/ADR-023-l6-ems-and-analyst-context.md) · [Forge](../../design/forge-industrial-design-system.md)

Typed Next.js App Router seed for the ops-first L6 control room: Today, EMS alarms, prescription queue, dual-mode analyst chrome, progressive **More tools** reveal, and Forge tokens.

## Layout

```text
src/
  app/                 # Today, alarms, prescriptions, evidence, analyst, reports
  components/
    shell/             # AppShell + reveal nav + SSE banner
    alarms/            # EMS console
    prescriptions/     # Triage queue
    analyst/           # Mode A contextual + Mode B workspace
    today/             # ≤7 signal board
    charts/            # Gauge + LoadDial (demo-adapted SVG)
    ui/                # StatusChip, Panel, buttons
  fixtures/demo.ts     # Contract-shaped mock data
  lib/                 # types, formatters, analyst context helpers
  styles/tokens.css    # Forge Industrial CSS variables
tests/                 # node:test unit checks
TRANSFER.md            # What to copy into the consumer repo
```

## Setup

```bash
cd consumers/stamped-l6
npm install
npm run typecheck
npm test
npm run build
```

## Demo → seed map

| Taken from demo | How |
|-----------------|-----|
| Forge-aligned tokens | `styles/tokens.css` |
| Gauge / LoadDial | `components/charts/*` |
| KPI strip idea | `TodayBoard` (≤7, linked) |
| Alert / Rx patterns | `AlarmConsole`, `PrescriptionQueue` |
| AiDrawer | Replaced by `ContextualAnalyst` (focus, Esc, removable chips) |

**Not ported:** PlantMap3D, fake LIVE counters, state-key routing, Recharts monolith pages.

## Exit criteria (seed)

- [x] Typed components + fixtures
- [x] Progressive reveal nav
- [x] EMS console + prescription defer reason
- [x] Ops-confirmed / modeled claim labels
- [x] Mode A + Mode B shells
- [x] Unit tests for formatters + analyst context tenancy
- [ ] Live L4/L5/L2 HTTP — consumer build plan
