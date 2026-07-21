# stamped-l6 — UI/UX charter

> **Audience:** Engineers / agents building the L6 product UI or adapting `consumers/stamped-l6`.  
> **Authority:** [L6 SSOT](../technical/layers/L6-experience-and-integration.md) · [ADR-022](../decisions/ADR-022-l6-bff-runtime-boundary.md) · [ADR-023](../decisions/ADR-023-l6-ems-and-analyst-context.md) · [ADR-020](../decisions/ADR-020-l5-mv-claim-governance.md)  
> **Design system:** [Forge Industrial v2.0](../design/forge-industrial-design-system.md) · [tokens YAML](../design/forge-industrial-v2.tokens.yaml)  
> **Demo inspiration:** stamped-energy-dashboard (tokens, Gauge/LoadDial, KPI strip, prescription cards, alert feed) — **adapt, do not clone** mock routing / fake LIVE / inaccessible drawer.  
> **Register:** Product (task UI). Color strategy: **Restrained**. Theme scene: *Supervisor at a bright plant office desk at 10am, glancing between phone WhatsApp nudges and a laptop to clear alarms and prescriptions before lunch.* → **light** Forge surface `#f7faf5`.

---

## 1. Feature summary

L6 is the ops-first control room for Indian manufacturing energy teams. Users triage EMS alarms, close prescriptions with evidence, read ops-confirmed ₹ savings, and ask a route-aware analyst — without drowning in every EMS/analytics skill at once.

## 2. Primary user action

**Clear the next high-value operational decision** (ack alarm or act on ₹-sorted Rx) with proof one tap away.

## 3. Design direction

| Axis | Choice |
|------|--------|
| Color | Restrained — tinted neutrals + Primary `#F75440` ≤10% for critical CTAs/alerts |
| Theme | Light industrial office (Forge); dark chrome only for topbar/secondary anchors |
| Typography | Plus Jakarta Sans display · Inter body/data (tabular nums for ₹) |
| Anchors | Linear triage · ISA-101 HMI calm · stamped-energy demo KPI/status DNA |
| Density | Today ≤7 signals; More/Reveal for advanced modules |

**Anti-goals:** purple SaaS gradients, card-grid overload, hero-metric clichés, glassmorphism, fake “LIVE” pulses, drawer-only AI, bill-verified badges from ops-only data.

---

## 4. Personas and landings

| Role | Default route | Must see | Reveal-only |
|------|---------------|----------|-------------|
| Operator | `/alarms` | Open critical alarms, assigned Rx | Ledger, Admin |
| Supervisor | `/prescriptions` | Triage lanes, Alarms badge | Multi-plant, API keys |
| Plant head | `/` (Today) | Ops-confirmed ₹, closure, queue rollup | Admin |
| Energy manager | `/` → Reveal Energy | Trends, TOD, top consumers | Webhook admin |
| Sustainability | `/reports` | Exports, SEC, CO₂ | Alarm write actions |
| CFO | `/reports/ledger` | Ledger read-only | Telemetry, ack |
| Admin | `/settings` | Users, keys, webhooks | — |

---

## 5. Screen inventory (routes)

### Primary (P0)

| Screen | Route | Purpose |
|--------|-------|---------|
| Today | `/` | ≤7 decision signals + deep links |
| Alarms (EMS) | `/alarms` | Lifecycle console |
| Alarm detail | `/alarms/[id]` | Evidence + actions |
| Prescriptions | `/prescriptions` | Triage lanes |
| Rx detail | `/prescriptions/[id]` | What/Why/Impact/Owner + evidence |
| Evidence explorer | `/evidence` | Pre-scoped charts from alarm/Rx |
| Analyst (Mode B shell) | `/analyst` | Full workspace layout (fixture P0; live P1) |
| Reports hub | `/reports` | Exports entry |
| Ledger | `/reports/ledger` | Potential vs ops_confirmed |
| Settings | `/settings` | Profile, reveal prefs, plant |

### Reveal-tier (P1 UI; routes reserved P0)

| Screen | Route |
|--------|-------|
| Energy analytics | `/energy` |
| Equipment health | `/equipment` |
| TOD / MD | `/energy/tod` |
| Intensity / CO₂ | `/intensity` |
| Integrations | `/settings/integrations` |
| Admin users/keys | `/settings/admin` |

### Shell chrome (always)

| Surface | Behaviour |
|---------|-----------|
| Topbar | Plant switcher, connection/SSE status (truthful), Ask Analyst |
| Sidebar | Primary nav + **More** disclosure |
| Contextual analyst (Mode A) | Side panel with context chips; Esc closes; focus trap |
| Toast | Action confirmations; not the only error channel |

---

## 6. Layout strategy

```text
┌─────────────────────────────────────────────────────────────┐
│ Topbar (secondary #051F13)  plant · SSE · Ask Analyst       │
├──────────┬──────────────────────────────────────┬───────────┤
│ Sidebar  │ Main (surface #f7faf5)               │ Mode A    │
│ Today    │ PageHead + ≤7 KPI strip              │ analyst   │
│ Alarms   │ Primary work surface                 │ (optional)│
│ Rx       │ Evidence / tables without card soup  │ chips +   │
│ Evidence │                                      │ chat      │
│ Analyst  │                                      │           │
│ Reports  │                                      │           │
│ More ▾   │                                      │           │
└──────────┴──────────────────────────────────────┴───────────┘
```

- Mobile: single column; bottom primary actions for ack/done; sidebar → sheet.
- No nested cards. Cards only when they bound an interactive unit (Rx row, alarm row).

---

## 7. Progressive reveal

1. Default collapsed **More** for operator/supervisor.
2. User can pin Energy/Equipment into primary (persisted preference).
3. Unread critical alarm count badge remains on Alarms even if Energy is pinned.
4. Reveal never removes Alarms or Prescriptions from primary for ops roles.

---

## 8. EMS console interaction

| State | User sees | Actions |
|-------|-----------|---------|
| raised | Severity chip, age, asset, summary | Ack, Escalate, Silence, Open evidence, Link Rx |
| acked | Owner + ack time | Escalate, Silence, Clear (if policy), Evidence |
| escalated | Escalation target | Ack, Silence |
| silenced | Silence until | Unsilence, Evidence |
| cleared | Read-only history | Open related Rx |

**Keyboard (desktop):** `j/k` move · `a` ack · `e` evidence · `Enter` open.  
**Stale SSE:** banner “Live updates paused — reconnecting”; dim list confidence.  
**Empty:** “No open alarms — plant looks calm” + link to Today.  
**Error:** plain-language retry; never blank.

---

## 9. Prescription queue

Lanes: **Needs review · Active · Verifying · Closed**.  
Default sort: addressable ₹/month × confidence with ageing boost.  
Header: total addressable ₹ for open queue.  
Expand: pre-scoped evidence chart + rule id + tariff math + lineage tags.  
Defer/Reject: **reason required**.  
Done → Verifying → **Ops-confirmed ₹X** (badge) or Disputed.  
Opportunity cost: **Modeled — not bill-verified** disclaimer.

---

## 10. Dual-mode analyst

### Mode A — Contextual side (P0)

- Opens from Ask Analyst or `?analyst=1`.
- Shows chips from `AnalystContextEnvelope` (route, focus entity, time range).
- User removes chips before send.
- Suggestions are screen-aware (“Why is this alarm critical?”, “Summarise open ₹ on this feeder”).
- Focus trap, `aria-modal`, Esc, return focus to opener.

### Mode B — Full workspace (P1 live)

```text
┌──────────────┬────────────────────┬─────────────────┐
│ Conversations│ Transcript         │ Sources / canvas│
│ + saved      │ + composer         │ citations       │
│ investigations│ handoff-to-action │ evidence chart  │
└──────────────┴────────────────────┴─────────────────┘
```

Handoff-to-action always confirms before L5 write.

---

## 11. Claim & status vocabulary

| Badge | When |
|-------|------|
| Ops-confirmed | `verification_status=ops_confirmed` |
| Pending | clearance in flight |
| Modeled | opportunity_cost / non-ops estimate |
| Disputed | challenge open |
| Bill-verified | **hidden until** bill path enabled — never show from ops alone |
| Critical / Warning / Good / Offline | alarm & asset status (text + colour) |

---

## 12. Key states (every primary screen)

| State | Requirement |
|-------|-------------|
| Default | Calm grayscale + action colour |
| Loading | Skeletons, not centered spinner-only |
| Empty | Teach next action |
| Error | Recoverable copy + retry |
| Stale / offline | Dim + timestamp + reconnect |
| Forbidden | Role explanation + request access CTA |
| Partial data | Label missing series; do not invent |

---

## 13. Motion

- 150–250ms ease-out for panel open/close.
- No decorative pulse on healthy KPIs.
- `prefers-reduced-motion: reduce` disables non-essential animation.
- Motion conveys state only (drawer, toast, reconnect).

---

## 14. Accessibility

- WCAG AA contrast on Forge tokens.
- Focus rings 2px secondary outline.
- Touch targets ≥44×44 (buttons 48px).
- Tables: `scope` headers; sort announcements.
- Charts: `role="img"` + text alternative or data table toggle.
- Status never colour-only.

---

## 15. Content / microcopy

- Lead with ₹ and operational verbs (“Ack alarm”, “Mark done”).
- Evidence CTA: “Show proof”.
- Analyst empty: “Ask about this screen — or open full Analyst”.
- Modeled delay: required disclaimer from [l6-counterfactual-display-stub.md](./l6-counterfactual-display-stub.md).

---

## 16. Demo → product port map

| Demo asset | L6 fate |
|------------|---------|
| `index.css` tokens | Map → Forge tokens / CSS variables |
| `ui.jsx` Card/Pill/StatusDot | Adapt → typed primitives |
| `Gauge.jsx` / `LoadDial.jsx` | Direct port (SVG) with a11y text |
| `KpiStrip`, `AlertFeed`, `Prescriptions` | Prop-ify + loading/empty/error |
| `EnergyChart` / analytics page | Rebuild on ECharts; keep baseline-band idea |
| `AiDrawer` | Replace with Mode A (focus trap + context chips) |
| `App.jsx` state routing | Discard → App Router |
| `PlantMap3D` | Inspiration only — out of scope |
| Fake LIVE / sync counter | Discard — use real SSE status |

---

## 17. Acceptance criteria (P0 UI)

- [ ] Today shows ≤7 signals; More reveal works and persists.
- [ ] Operator can ack an alarm on mobile viewport.
- [ ] Supervisor can defer Rx only with reason.
- [ ] Ops-confirmed vs Modeled badges never confuse with bill-verified.
- [ ] Mode A shows removable context chips; Esc returns focus.
- [ ] SSE stale banner appears when stream drops (fixture-simulated OK).
- [ ] Keyboard triage on Alarms desktop.
- [ ] Lighthouse / manual a11y: no critical contrast or focus traps missing.

---

## 18. Recommended impeccable refs at implement

`reference/product.md`, spatial-design, interaction-design, motion-design (state-only), harden (errors/empty).

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-21 | Initial L6 UI/UX charter — ops-first, EMS, progressive reveal, dual-mode analyst |
