---
type: Product Architecture
title: "L6 — Experience & Integration"
description: "Deep research and build spec for Stamped's L6 layer: web dashboard, prescription queue UX, PDF/CSV sustainability exports, and the outbound REST/webhook/ERP integration surface."
tags: [stamped-energy, technical, layer-spec]
timestamp: "2026-07-09T00:00:00Z"
---

# L6 — Experience & Integration

*Layer research document · July 2026 · Status: pre-build research, feeds engineering scoping*

> **Honesty convention:** `[~]` approximate / benchmark-derived · `[!]` evolving — verify before customer-facing claims.
>
> **Siblings:** [L5 — Closure & verification](L5-closure-and-verification.md) · [L2 — Universal repository](L2-universal-repository.md) · [Technical architecture](../02-technical-architecture.md)

L6 is everything the customer *sees and connects to*: the web dashboard, the prescription queue, PDF/CSV report generation (including the monthly sustainability pack), and the outbound integration surface — REST API, signed webhooks, ERP/ESG connectors, and the "connect to any custom system" promise. Every other layer produces intelligence; L6 is where that intelligence gets acted on, renewed, and defended in front of a CFO or an auditor.

---

## 1. Role in the 15–20% target

L6 does not detect a single kWh of waste. It still directly controls two of the three variables the savings equation depends on:

```
verified savings = (waste detected by L3/L4) × (closure rate driven by L5+L6 UX) × (M&V defensibility from L5, presented by L6)
```

### 1.1 Experience drives closure

The architecture target is ≥60% of high-priority prescriptions acted within one billing cycle `[!]`. WhatsApp (L5) reaches the floor, but the dashboard is where the *supervisor triages* and where the *plant head holds people accountable*. Concretely:

| L6 mechanism | Closure effect |
| --- | --- |
| Prescription queue with total addressable ₹ visible | Plant head sees the cost of inaction weekly — social pressure on owners |
| Evidence drill-down (Rx card → underlying telemetry chart) | Kills the "prove it" objection that stalls actions; supervisor trusts the ask |
| Ageing / overdue indicators on open Rx | Deferred prescriptions don't silently die; they escalate |
| One-tap acknowledge synced with WhatsApp state | Floor action and dashboard state never diverge → no double-asking, no lost credit |
| Role-scoped views (operator vs CFO) | Each persona sees only decisions they can make → less noise, faster action |

A prescription that is *seen, understood, and trivially actionable* closes; one buried in a generic dashboard does not. This is the core lesson from every competitor synthesis in this bundle: dashboards are table stakes, willingness-to-pay sits on assigned action + verification.

### 1.2 Exports drive renewal

The renewal conversation is: "Stamped saved us ₹X verified this year, here is the bill-reconciled evidence, and here is the sustainability pack our ESG team forwarded to corporate." Both artifacts are L6 outputs:

- **CFO renewal artifact:** savings ledger export — potential vs realised ₹, per prescription, reconciled against DISCOM bill lines (data from L5).
- **Sustainability renewal artifact:** the monthly pack — verified kWh, tCO₂e with factor disclosure, SEC trends, methodology note, BRSR/PAT adjunct tables. This is what makes Stamped sticky with a *second* buyer persona inside the account.
- **Integration stickiness:** once a customer's ESG tool, ERP dashboard, or group-level reporting consumes Stamped webhooks/API, ripping Stamped out breaks their own reporting pipeline. Integration depth is churn insurance `[~]`.

### 1.3 What L6 must NOT become

The architecture rule from the [technical architecture](../02-technical-architecture.md) applies hardest here: *layers that only add charts are rejected*. L6 is not a BI tool, not an ESG platform, not a SCADA HMI replacement. Every screen must serve detection→prescription→closure→verification→evidence, or it is cut.

---

## 2. Requirements from the architecture

### 2.1 Inputs L6 consumes

| Input | Producing layer | Consumed by |
| --- | --- | --- |
| Savings ledger entries (potential/verified ₹, kWh, tCO₂e) | L5 ledger | Savings ledger module, exports, `ledger.entry.added` webhook |
| Prescription workflow state (Open → In Progress → Done/Deferred/Rejected) | L5 workflow | Prescription queue, WhatsApp sync, `prescription.*` webhooks |
| M&V verification results + bill reconciliation flags | L5 M&V | Evidence drill-down, methodology note, dispute view |
| Time-series telemetry + baseline bands | L2 TS store + baseline store | 30-day trend, TOD profile, evidence charts |
| Anomaly scores / findings stream | L3 | Live anomaly feed, equipment health map, `anomaly.raised` webhook |
| SEC / intensity series | L3 SEC engine + L2 | Intensity chart, sustainability pack |
| Feature store aggregates (top consumers, benchmarks) | L2 feature store | Top consumers module, multi-plant benchmark |
| Narrative text (methodology, pack prose) | L4 narrative engine | PDF pack generation |
| Emission factor (value + source + vintage) | L4 impact calculator | Every tCO₂e figure rendered or exported |
| Audit trail (issued/viewed/acted/verified) | L5 audit log | Prescription audit trail export, compliance view |

### 2.2 Dashboard module list (from §10.1 of the architecture, mapped to demo)

The demo at [stamped-energy.vercel.app](https://stamped-energy.vercel.app/) is the visual reference `[!]` (site was intermittently unreachable during this research — treat the module list below, which comes from the architecture doc, as authoritative):

| # | Module | Data source | Primary user |
| --- | --- | --- | --- |
| M1 | Savings ledger | L5 ledger | Plant head, CFO |
| M2 | 30-day trend vs baseline | L2 TS + baseline store | Energy manager |
| M3 | Equipment health map | L3 anomaly scores | Operations |
| M4 | Live anomaly feed | L3 findings stream | All |
| M5 | Prescription queue | L4 + L5 workflow | Supervisors |
| M6 | Top consumers vs benchmark | L2 feature store | Energy manager |
| M7 | TOD / 24h demand profile | L3 MD engine | Utilities |
| M8 | Intensity (SEC) chart | SEC engine + production | Sustainability |
| M9 | CO₂ equivalent card | Impact calculator | Sustainability |

### 2.3 Non-functional requirements inherited from §14

- **Tenancy:** `org_id` → `plant_id` isolation enforced at the API layer; no cross-tenant queries. Every L6 query is tenant-scoped by construction.
- **RBAC:** operator / supervisor / plant head / sustainability / admin — role determines both module visibility and action rights (e.g. only supervisors+ can mark Rx done).
- **Audit:** every prescription view/acknowledge from the dashboard writes to the immutable L5 audit log.
- **Data residency:** India region default for enterprise — constrains hosting choices (see §4.1).
- **Read-only principle:** L6 never writes to plant systems. The only "writes" are workflow state, comments, and configuration.

### 2.4 Sustainability export pack requirements (from §10.2, §11)

| Artifact | Contents | L6 responsibility |
| --- | --- | --- |
| Verified savings summary | Realised ₹, kWh, tCO₂e by period | Aggregate + render, factor disclosure on every tCO₂e |
| SEC / intensity report | By line, shift, product where data exists | Chart + table rendering |
| Prescription audit trail | Action, owner, date, outcome | Tabular export from L5 audit log |
| Methodology note | IPMVP option, emission factor source, limitations | Render L4 narrative + fixed template |
| BRSR/PAT adjunct tables `[!]` | Pre-formatted CSV matching the SEBI table shape (see §3.4) | Format mapping only — Stamped supplies *inputs*, never files |

---

## 3. Researched landscape

### 3.1 Dashboard stack

#### Framework & rendering

Next.js (App Router) + React remains the default for data-dense SaaS dashboards in 2026 — server components keep the initial payload small, and the ecosystem (auth, i18n, charts, testing) is deepest there. The interesting decisions are below the framework.

#### Charting — the load-bearing choice

2026 comparisons converge on a clear picture ([LogRocket [1]](https://blog.logrocket.com/best-react-chart-libraries-2026/), [DataBrain [2]](https://www.usedatabrain.com/blog/react-chart-libraries), [Chen [3]](https://chenguangliang.com/en/posts/blog152_react-chart-libraries-comparison/), [Youngju deep dive [4]](https://www.youngju.dev/blog/culture/2026-05-14-data-visualization-libraries-2026-d3-plot-visx-recharts-echarts-vega-comparison-deep-dive-2026.en)):

| Library | Renderer | Sweet spot | Failure mode for Stamped |
| --- | --- | --- | --- |
| **Recharts** | SVG | <5k points, standard charts, fastest React DX | Janks past ~1k points; 15-min telemetry over 30 days per feeder ≈ 2,880 points × multiple series → borderline |
| **Apache ECharts 6** (via `echarts-for-react`) | Canvas/SVG/WebGL | 50k–1M points, LTTB downsampling built in, heatmaps/calendar charts native, tree-shakeable to ~100 kB gz | Option-object API is less "React-ish"; theming discipline needed |
| **TradingView lightweight-charts** | Canvas | Purpose-built for high-density financial time series, tiny bundle | No bar/heatmap variety; time-series-only |
| **visx** | SVG | Bespoke visual systems, full control | You build everything yourself — wrong trade for a 2–4 person team |
| **Highcharts** | SVG | Mature, accessible, commercial support | Commercial licence cost; capability now matched by ECharts free |
| **Observable Plot** | SVG | Exploratory/report notebooks | Not built for interactive product dashboards |

Key performance facts: SVG libraries stutter past ~5 updates/sec on charts above 1,000 points; Canvas handles orders of magnitude more [2]. ECharts ships LTTB sampling, progressive rendering, and `large` mode natively [2][4] — exactly what a month of 1-minute incomer data (43,200 points) needs.

#### Realtime updates: SSE beats WebSocket for this shape

The 2026 consensus is unambiguous for dashboard-shaped products ([getstream [5]](https://getstream.io/blog/websocket-sse/), [Boyko [6]](https://www.nazarboyko.com/articles/sse-vs-websockets-for-live-ui-updates), [FlowVerify [7]](https://www.flowverify.co/blog/sse-websockets-polling-when-each-wins-2026)):

- Stamped's realtime traffic is strictly one-way: anomaly feed items, Rx state changes, ledger updates flow server→client. Client actions (acknowledge, comment) are ordinary REST POSTs.
- SSE gives automatic reconnection with `Last-Event-ID` resume, plain HTTP semantics (works through corporate proxies — relevant for factory IT networks), and no sticky-session requirement [5][6].
- Enterprise/managed-network environments specifically favour SSE because WebSocket upgrades get blocked by middleboxes [7].
- Production checklist: `text/event-stream` + `X-Accel-Buffering: no`, heartbeat comments every ~25s, Redis pub/sub fan-out across app instances [5].

WebSocket is justified only if a future collaborative feature (shared live annotation) appears — not speculative infrastructure now.

#### Time-series UX for energy data

ISA-101 high-performance HMI principles apply directly even though Stamped is not an HMI ([Industriant ISA-101 cheat sheet [8]](https://industriant.com/Industriant_ISA-101_Cheat_Sheet.pdf), [FuseLab manufacturing dashboard guide [9]](https://fuselabcreative.com/manufacturing-dashboard-ux-design/), [iFactory monitoring guide [10]](https://ifactoryapp.com/industries/infrastructure-management/smart-infrastructure-monitoring-dashboard-good-looks)):

| Principle | Application to Stamped |
| --- | --- |
| Deviation-first: show value *against* a visible tolerance band, not a raw number | Every trend renders the L2 baseline band as a shaded region; the line's job is "how far off and which way" [8] |
| Grayscale normal, colour = abnormal only | Calm dashboard when the plant is fine; red/amber reserved for anomalies and overdue Rx [8] |
| Trends adjacent to point of use | Rx card embeds its evidence sparkline; no navigation to "prove it" [8] |
| Stale data must *look* stale | Dim + timestamp when telemetry lags (gateway offline); never render stale data at full confidence [9] |
| 5–7 KPIs per view, three-tier hierarchy (North Star → supporting → diagnostic) | Overview = ledger + closure rate + live feed; drill = per-module detail [10] |
| Progressive update rules | Numbers refresh on threshold crossing, not every tick — reduces flicker and cognitive load [9] |

Energy-specific idioms (from EMS/tariff domain practice, `[~]` synthesised):

- **TOD shading:** background bands on the 24h demand profile coloured by tariff period (peak/normal/off-peak from the L3 tariff engine) so "shift this load" is visually self-evident.
- **MD visualisation:** monthly peak-kVA histogram with contract demand (CMD) as a hard reference line; billing-period reset markers.
- **Baseline bands:** shaded expected-consumption envelope (P10–P90) with actuals overlaid — confidence bands must be visually distinct (transparency) from the actual line to avoid clutter [8].
- **Bill overlay:** vertical markers for billing period boundaries on all long-range trends, since the bill is the trust anchor.

#### Role-based views

RBAC roles from §14 map to view compositions, not separate apps:

| Role | Landing view | Hidden |
| --- | --- | --- |
| Operator | Live anomaly feed + own assigned Rx (mobile-first) | ₹ ledger, tariff detail |
| Supervisor | Prescription queue (triage view) + equipment health | Multi-plant, API keys |
| Plant head | Savings ledger + closure rate + queue rollup | Admin config |
| Sustainability | Intensity chart + CO₂ card + export centre | Workflow actions |
| CFO / group exec | Ledger + multi-plant rollup + benchmark (read-only) | Telemetry detail |
| Admin | Everything + user/API/webhook management | — |

#### Mobile responsiveness

Plant heads and supervisors live on phones. The demo's module grid must collapse to a single-column card stack; the prescription queue and acknowledge flow are the two surfaces that must be *genuinely excellent* on mobile, because WhatsApp deep-links land there (see §3.2). A separate native app is not justified at this stage `[~]`.

#### i18n (Hindi)

For Next.js App Router, `next-intl` is the 2026 standard: RSC-native, ICU MessageFormat (handles Hindi's two grammatical genders and plural rules properly), type-safe keys, middleware locale routing ([Nair — Indian language guide [11]](https://rajeshrnair.com/blog/web-development/frontend/nextjs-i18n-indian-languages-hindi-malayalam-tamil-2026.html), [next-intl guide [12]](https://noqta.tn/en/tutorials/nextjs-next-intl-i18n-app-router-guide-2026)). Specifics for Hindi:

- **Font:** self-host Noto Sans Devanagari via `next/font/google` — Devanagari font files are several hundred kB and naive loading causes layout shift [11].
- **Scope discipline `[!]`:** translate the *operator/supervisor surfaces* (Rx cards, acknowledge flow, anomaly labels) first; keep CFO/sustainability/export surfaces English-only in P0–P1. Prescription text itself is generated by L4 — Hindi Rx generation is an L4 concern L6 must merely render (Devanagari-safe layout, no truncation assumptions).
- Numbers stay Latin numerals with Indian digit grouping (₹12,34,567) via `Intl.NumberFormat('en-IN')`.

### 3.2 Prescription queue UX

The best-researched pattern is Linear's Triage ([Linear docs [13]](https://linear.app/docs/triage), [Linear unplanned-work guide [14]](https://linear.app/docs/triage-manage-unplanned-work)):

| Linear pattern | Stamped translation |
| --- | --- |
| Dedicated inbox separate from active work | New Rx land in a "Needs review" state distinct from accepted/in-progress — supervisors trust that the active list is real work |
| Triage captain / responsibility rotation | Plant-level "energy champion" owns the queue; configurable notification target |
| Quick actions: accept / merge / decline / snooze with keyboard shortcuts | Accept (assign + due date) / Defer (reason required) / Reject (reason required — feeds L3 calibration) / Snooze to next shift |
| Decline prompts a reason comment | Rejection reasons are *first-class data* — they train the L4 ranker and L3 calibrator (defer/reject learning loop from §3.3 of the architecture) |
| Triage rules for auto-routing | Category → default owner role mapping from the L2 energy graph (electrical / production / utilities) |

Stamped-specific additions beyond the Linear pattern:

- **₹-sorted, not recency-sorted.** Default ordering is addressable ₹/month × confidence, with an ageing boost. Total addressable ₹ for the open queue is the header number.
- **Evidence drill-down as a first-class interaction.** Every Rx card expands to: the telemetry chart slice that triggered it (with baseline band and the anomalous window highlighted), the rule/engine that fired (from L3), the tariff math for the ₹ figure (from L4 impact calculator), and source tag IDs (lineage). This is the "What/Why/Impact/Owner/Due/Priority" card from the product definition, backed by proof. Design rule: the chart is *pre-scoped* to the event window — never dump the user into a generic explorer.
- **WhatsApp ↔ dashboard state sync (with L5).** WhatsApp button replies ("Done", "Defer") update L5 workflow state; the dashboard queue reflects it in seconds via SSE. Conversely, dashboard state changes suppress redundant WhatsApp nudges. Every WhatsApp message carries a deep link `stamped.app/rx/{id}` that opens the mobile-responsive Rx detail with a one-tap acknowledge — no login wall for a signed, expiring link `[!]` (magic-link with short TTL; security review needed on link forwarding risk).
- **Verification visibility.** After "Done", the card doesn't disappear — it moves to a "Verifying" lane showing the M&V window countdown, then lands in "Verified ₹X" or "Disputed". Closure feels rewarding; this is the loop that builds trust.

### 3.3 Report & export generation

#### Engine comparison

2026 benchmarks and comparisons ([pdf4.dev react-pdf vs Playwright [15]](https://pdf4.dev/blog/react-pdf-vs-playwright-pdf-generation), [Typcraft browser-vs-native [16]](https://typcraft.com/blog/pdf-engines-browser-vs-native), [pdf4.dev benchmark [17]](https://pdf4.dev/blog/html-to-pdf-benchmark-2026), [Nutrient overview [18]](https://www.nutrient.io/blog/generate-pdfs-from-javascript/)):

| Engine | Layout | Charts | Speed/memory | Verdict for Stamped |
| --- | --- | --- | --- | --- |
| **Playwright print-CSS** (headless Chromium) | Full CSS3, `@page`, `break-inside` | Renders the *same ECharts components as the dashboard* | 3–13 ms warm, ~250 MB browser pool [17] | **Winner** — one design system for screen and paper |
| Puppeteer | Same Chromium engine | Same | Similar | Fine, but Playwright has better tooling and we'll use it for E2E anyway [18] |
| @react-pdf/renderer | Yoga flexbox subset, no Grid, no `@media print` | No DOM → no chart libs | Light, serverless-friendly | Rejected: can't reuse dashboard charts; fights every table-heavy layout [15] |
| Typst | Own DSL, excellent typography | Would require re-plotting | 15–50 ms, 30 MB [16] | Attractive at high volume `[!]` — revisit if pack generation exceeds ~10k docs/month; wrong first choice (duplicate template system) |
| LaTeX | — | — | Slow toolchain, heavyweight | Rejected — maintenance burden without benefit |

The decisive argument: the monthly pack is *the dashboard's charts, printed*. Playwright renders the actual React/ECharts report route with print CSS, so chart parity between screen and PDF is automatic, and report templates are just React components [15]. Cost: run a warm browser pool on a worker node, never in the request path.

#### Scheduled jobs

Month-end pack generation, weekly digests, and export jobs are queue work, not cron scripts. BullMQ (Redis) vs pg-boss (Postgres) is the standard 2026 fork ([Rogulia comparison [19]](https://iurii.rogulia.fi/blog/background-jobs-nodejs), [BuildPilot [20]](https://trybuildpilot.com/641-trigger-dev-vs-bullmq-vs-pgboss-2026)): the decision reduces to "is Redis already in the stack?" Since Redis is already required for SSE fan-out and caching, **BullMQ** with `upsertJobScheduler` (idempotent cron registration across deploys) is the pick; Bull Board behind admin auth for observability [19].

#### CSV/Excel

CSV is the universal answer for Indian plant IT — Excel is where energy managers actually live. Every dashboard table gets a CSV export; the sustainability pack ships adjunct tables as CSV; ledger export offers `.xlsx` (ExcelJS — streaming write, formats, no licensing issues) `[~]`. Design rules: ISO-8601 timestamps + explicit timezone column (IST), units in headers (`energy_kwh`, `md_kva`), emission factor + vintage columns on every tCO₂e row, stable column order (documented as part of the API contract — customers build macros against these files).

#### BRSR Principle 6 — what the export must actually match

SEBI's BRSR format, Principle 6, Essential Indicator 1 requires ([SEBI Annexure II [21]](https://www.sebi.gov.in/sebi_data/commondocs/jul-2023/Annexure_II-Updated-BRSR_p.PDF), [SEBI BRSR Core circular [22]](https://ca2013.com/wp-content/uploads/2023/07/SEBI-Circular_12.07.2023.pdf), [Batchwise P6 methodology [23]](https://batchwise.ai/methodology/principle-6-environment/)):

| BRSR EI-1 line item | Stamped can supply |
| --- | --- |
| Total electricity consumption — renewable (A) | Yes, where source meters exist (solar/WHR sub-metering) `[!]` |
| Total fuel consumption — renewable (B) | No (fuel out of scope) — leave blank, flag in methodology note |
| Other sources — renewable (C) | No |
| Total electricity consumption — non-renewable (D) | Yes — grid kWh from incomer + bill (highest confidence) |
| Total fuel consumption — non-renewable (E) | No |
| Energy intensity per rupee of turnover | Inputs only — Stamped has kWh, customer supplies revenue |
| Energy intensity per rupee of turnover, PPP-adjusted | Inputs only (PPP adjustment is the filer's job) |
| Energy intensity in terms of physical output | **Yes — this is Stamped's SEC engine output** (kWh/ton, kWh/part), the strongest line |
| PAT designated-consumer question (EI-2) | Adjunct: SEC trend evidence for PAT target narrative |

Context that shapes positioning: BRSR Core assurance applies to the top 500 listed entities in FY 2025–26 and top 1,000 in FY 2026–27 ([KPMG [24]](https://assets.kpmg.com/content/dam/kpmgsites/in/pdf/2026/02/chapter-1-emerging-trends-in-brsr-reporting-by-listed-companies.pdf.coredownload.pdf)), energy consumption intensity is one of the four Principle 6 BRSR Core attributes subject to *reasonable assurance* under SAE 3000, and the filing is an XBRL instance against the MCA taxonomy [23]. Implications:

1. Stamped's export is an **evidence adjunct feeding the filer's process**, never the filing itself (consistent with §16 boundaries). The CSV mirrors the EI-1 table shape with electricity rows populated and everything else explicitly `not_measured_by_stamped`.
2. Because assured numbers need workpapers, the pack's audit-trail + methodology note (meter lineage, factor source/vintage, M&V approach) is *more valuable* than the numbers — it's what the assurance partner asks for.
3. BRSR Core value-chain disclosures (top 250 companies, voluntary from FY 2025–26 [24]) mean Stamped's *unlisted* mid-size customers will increasingly be asked for energy/intensity data by their listed OEM buyers — the OEM supplier-questionnaire export is the same artifact repackaged `[~]`.

#### ESG platform ingestion

Enterprise carbon/ESG tools (Persefoni, Sweep, Novisto) ingest via pre-built API connectors, bulk CSV, and utility-bill integrations ([Persefoni Integration Hub [25]](https://www.persefoni.com/en-gb/product/integration-hub), [Novisto Collect [26]](https://novisto.com/product/collect)). None of them have a "Stamped connector," and building per-platform connectors is premature. The realistic P1 answer: a documented **activity-data CSV** (period, site, grid kWh, renewable kWh, verified reduction kWh, tCO₂e + factor metadata) matching the generic bulk-import shape these tools accept, plus the REST endpoint so a customer's ESG consultant can automate the pull. Named ESG connectors are a paid-engagement tier item (§4.5).

### 3.4 Outbound integration surface

#### REST API design

2026 best-practice consensus ([Cadence [27]](https://cadence.withremote.ai/blog/api-design-best-practices), [bytepane [28]](https://bytepane.com/blog/rest-api-best-practices/), [APIScout versioning [29]](https://apiscout.dev/guides/api-versioning-strategies-2026)):

- **Contract-first OpenAPI 3.1** — spec is the artifact; SDKs, docs, and contract tests generate from it [27].
- **URL path versioning (`/v1/`)** — simplest and most debuggable for a young public API; Stripe-style date-header versioning is overkill before dozens of consumers [29].
- **Auth:** API keys (per-plant or per-org, scoped, hashed at rest) for the 80% case; OAuth2 client credentials for enterprise machine-to-machine where security teams demand token rotation [28]. Least-privilege scopes from day one (`read:ledger`, `read:prescriptions`, `write:acknowledgements`) — a single all-powerful key is the anti-pattern [27].
- **Rate limiting at the gateway**, not app code: `X-RateLimit-*` headers, 429 + `Retry-After` [28]. Limits generous for read (this is a read-mostly API), tight for write.
- **Idempotency-Key** header on the few POST endpoints (acknowledgement, export trigger) [27].
- **Deprecation:** RFC 8594 `Sunset` header + 12-month support window as public policy [29].

#### Outbound webhooks — adopt Standard Webhooks

The [Standard Webhooks spec [30]](https://github.com/standard-webhooks/standard-webhooks/) (Svix-initiated, adopted by OpenAI, Supabase, Twilio, PagerDuty et al.) is the obvious convention to follow rather than inventing one:

| Concern | Standard Webhooks / best practice | 
| --- | --- |
| Signing | HMAC-SHA256 over `msg_id.timestamp.payload`, `webhook-signature` header; constant-time verification [30][31] |
| Replay protection | `webhook-timestamp` header, receivers reject >5 min skew [30] |
| Idempotency | `webhook-id` is the consumer's dedup key [30] |
| Retries | Exponential backoff + jitter over multiple days; Svix's reference schedule is ~8 attempts over ~1 day ([Hookdeck [31]](https://hookdeck.com/blog/building-reliable-outbound-webhooks), [digitalapplied [32]](https://www.digitalapplied.com/blog/webhook-reliability-idempotency-retries-engineering-reference-2026)) |
| Dead-lettering | After exhausted retries → DLQ with ~30-day retention, customer-visible failed-delivery log + manual replay [31][32] |
| Secret rotation | Per-endpoint secrets, rotation API with dual-accept window [31] |
| Endpoint verification | Require HTTPS; SSRF guard on customer-supplied URLs (no private IP ranges) [30] |

Build vs buy `[!]`: Svix's hosted service outsources all of the above for ~$0–500/month at Stamped's early volumes; a BullMQ-based sender is a bounded 1–2 week build. Recommendation: build thin on BullMQ (the queue exists anyway) but wire the payload/header format to the Standard Webhooks spec so migrating to Svix later is a transport swap, not a contract break.

#### Event catalogue

| Event | Payload core | Trigger layer |
| --- | --- | --- |
| `prescription.created` | rx_id, plant_id, category tag, what/why summary, impact ₹/kWh/tCO₂e, owner role, due | L4→L5 |
| `prescription.acknowledged` | rx_id, actor, channel (whatsapp/dashboard/api) | L5 |
| `prescription.status_changed` | rx_id, from→to, reason (for defer/reject) | L5 |
| `prescription.verified` | rx_id, verified ₹/kWh/tCO₂e, M&V window, method | L5 M&V |
| `ledger.entry.added` | entry_id, type (potential/verified/disputed), amounts, factor metadata | L5 ledger |
| `anomaly.raised` | finding_id, asset, severity, score, category | L3 |
| `anomaly.cleared` | finding_id, duration | L3 |
| `report.generated` | report_id, type (monthly_pack/ledger_export), download URL (signed, expiring) | L6 |
| `bill.reconciled` | period, modelled vs actual deltas, flags | L5 |

Thin payloads + a `data.links.self` API URL for full detail — keeps webhooks fast and avoids leaking data through third-party webhook consumers' logs `[~]`.

#### Polling vs push

Both, explicitly: webhooks for latency-sensitive consumers, and a `GET /v1/events?since=cursor` polling endpoint over the same event log for customers whose IT will not open an inbound endpoint (common in Indian plant IT `[~]`). The event log is the single source; webhooks and polling are two delivery modes over it.

#### ERP integration reality in India

| System | Integration surface | Reality check |
| --- | --- | --- |
| **SAP S/4HANA** (on-prem/private cloud — the common Indian large-manufacturer install) | OData/REST APIs (800+ published), IDocs still supported and officially Clean Core Level B ([SAP Press [33]](https://blog.sap-press.com/apis-vs-idocs-in-sap-s4hana-and-sap-cloud-erp), [SAP community [34]](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-members/idocs-are-still-safe-for-sap-s-4hana-sap-clean-core-extensibility-level-b/ba-p/14225439)) | Every SAP integration is a *project*: Basis team approval, transport requests, months of lead time. IDocs are gone from S/4HANA Public Cloud as of release 2508 [33] — APIs are the only forward path there |
| **SAP ECC** (still widespread) | IDoc/RFC/file export | Even slower change cycles; CSV drop from a scheduled ABAP report is the honest v1 |
| **Tally Prime** (mid-market default) | Built-in HTTP server (port 9000) accepting XML/JSON envelopes; ODBC for pulls ([TallyHelp [35]](https://help.tallysolutions.com/getting-started-with-tally-integrations/)) | Tally runs on a desktop inside the plant LAN — reaching it requires an on-prem agent or the customer's Tally operator doing manual exports. Direction of value is mostly *Stamped ← Tally* (production quantities for SEC), not outbound |
| **Oracle (Fusion/EBS)** | REST APIs (Fusion), varies wildly (EBS) | Rare enough in the ICP to be strictly bespoke `[~]` |

The key insight: for L6 *outbound*, no Indian ERP has a natural "receive energy prescriptions" inbox. What customers actually want is (a) verified savings entries for cost-centre accounting and (b) maintenance work orders. Both are better served by **webhook → their middleware/iPaaS** or **scheduled CSV to SFTP** than by Stamped writing into SAP directly. Direct ERP *writes* (e.g. creating SAP PM work orders from prescriptions) is a P3 named-connector engagement, never self-serve.

#### Embedded analytics `[!]`

If enterprise customers demand "your charts inside our portal": Metabase's paid tiers own the turnkey multi-tenant embed (data sandboxing, React SDK), Superset is the self-host-and-engineer path, and Cube is the headless semantic-layer option for fully custom frontends ([modern-datatools [36]](https://www.modern-datatools.com/compare/metabase-vs-superset), [Cube [37]](https://cube.dev/articles/best-embedded-analytics-platforms-2026)). Recommendation: **do not build this now**. The nearer-term equivalent is a signed, read-only *share link* per module (iframe-able savings ledger card) — 5% of the effort, covers the actual ask (showing the group CFO a live number) `[~]`.

### 3.5 Multi-plant / enterprise

- **Group rollup:** org → plants hierarchy already exists in tenancy. Rollup view = aggregated ledger, closure rate, and intensity per plant, with plant drill-down. The interesting design problem is *normalisation* — cross-plant comparison is only honest within a vertical (forging vs forging) using SEC, not absolute kWh; the fleet-benchmark data comes from L3/ML-06.
- **SSO expectations:** enterprise Indian manufacturers run Azure AD (Entra ID) overwhelmingly, some Google Workspace `[~]`. 2026 B2B guidance: support both SAML 2.0 and OIDC per-organisation (deals split roughly 55/45 [39]), model organisations first-class from day one, JIT provisioning for mid-size, SCIM only when 500+ seat accounts demand it ([WorkOS checklist [38]](https://workos.com/blog/enterprise-readiness-checklist-2026), [Zulbera guide [39]](https://www.zulbera.com/insights/enterprise-authentication-sso-saas-guide/)). Buying (WorkOS or similar, ~$149/month first connection [39]) beats building — SSO is a deal-closing checkbox, not a differentiator.
- **Audit-log export and data-residency answers** are the other two recurring security-questionnaire items [38]; both are already architecture commitments (§14).

---

## 4. Recommended approach

### 4.1 Stack picks

| Concern | Pick | Rationale |
| --- | --- | --- |
| Framework | **Next.js (App Router) + TypeScript** | RSC for data-dense first paint; team/ecosystem default; matches demo |
| UI kit | **Tailwind + shadcn/ui** | Fast, ownable components; no design-system licence |
| Charts | **Apache ECharts 6** (tree-shaken) for all time-series/heatmap/TOD modules; Recharts acceptable for small static cards `[~]` | Canvas + LTTB handles 15-min×30-day×multi-series without jank [2][4]; calendar/heatmap native |
| Data fetching | TanStack Query + REST (the same `/v1` public API where possible) | Dogfooding the public API keeps it honest |
| Realtime | **SSE** (Redis pub/sub fan-out), heartbeats, `Last-Event-ID` resume | One-way traffic shape; proxy-friendly for factory IT [5][6][7] |
| i18n | **next-intl** + self-hosted Noto Sans Devanagari | RSC-native, ICU for Hindi grammar [11][12] |
| Auth (users) | Session auth + org-scoped RBAC; **WorkOS (or equivalent) for SAML/OIDC** when first enterprise deal demands it | Buy the protocol zoo [38][39] |
| PDF | **Playwright print-CSS** over dedicated report routes, warm browser pool on worker | Screen/paper chart parity; templates are React [15][17] |
| Jobs | **BullMQ** (`upsertJobScheduler`) + Bull Board | Redis already present; idempotent cron [19] |
| Excel/CSV | ExcelJS (xlsx), streaming CSV | No licensing; handles large ledger exports |
| Hosting `[!]` | India region (AWS Mumbai / GCP Delhi-Mumbai); self-hosted Next.js (not Vercel) for data-residency and SSE control | §14 residency default |

### 4.2 Dashboard module specs (delta over demo)

| Module | Spec highlights |
| --- | --- |
| M1 Savings ledger | Dual-audience card: ₹ (CFO) and kWh/tCO₂e (sustainability) toggled, never mixed on one axis. Potential vs realised as paired bars; every tCO₂e hover discloses factor value+source+vintage |
| M2 Trend vs baseline | ECharts line + shaded P10–P90 baseline band; bill-period markers; anomaly windows highlighted; LTTB downsampling above 5k points |
| M3 Equipment health | Grid of asset tiles: load %, anomaly score as border state (grayscale normal, amber/red abnormal — ISA-101 colour discipline) |
| M4 Anomaly feed | SSE-driven; severity-grouped, not strictly chronological; each item links to pre-scoped evidence chart |
| M5 Prescription queue | Triage pattern per §3.2: Needs-review / Active / Verifying / Closed lanes; ₹-sorted; keyboard quick actions; reason-required defer/reject; ageing badges |
| M6 Top consumers | Horizontal bars (long asset labels) with benchmark deviation markers |
| M7 TOD profile | 24h area chart with tariff-period background shading; CMD reference line; MD histogram sub-view |
| M8 Intensity | SEC line per production line/product; production-volume context band; PAT target reference line where configured |
| M9 CO₂ card | Single number + factor disclosure footnote; links to methodology |
| Export centre (new) | All downloads in one place: monthly packs (archive), ledger CSV/xlsx, BRSR adjunct CSV, audit trail; per-file generation timestamp and data-window disclosure |

Performance budgets (enforced in CI, see §5): overview route LCP < 2.5 s on mid-range Android over 4G `[~]`, INP < 200 ms, chart interaction (zoom/pan on 30-day 15-min series) at 60 fps target / 30 fps floor, JS bundle for the overview route < 350 kB gz `[!]`.

### 4.3 API design (v1 surface)

```
GET  /v1/plants                                  # scoped by API key
GET  /v1/plants/{id}/prescriptions?status=&category=&since=
GET  /v1/plants/{id}/prescriptions/{rx_id}       # incl. evidence refs
POST /v1/plants/{id}/prescriptions/{rx_id}/acknowledge   # Idempotency-Key
GET  /v1/plants/{id}/ledger?period=&status=verified
GET  /v1/plants/{id}/timeseries?metric=&asset=&from=&to=&granularity=15min
GET  /v1/plants/{id}/intensity?line=&from=&to=
GET  /v1/plants/{id}/reports?type=monthly_pack   # signed download URLs
GET  /v1/events?since={cursor}                   # polling twin of webhooks
GET  /v1/openapi.json
```

Conventions: OpenAPI 3.1 contract-first; cursor pagination everywhere; RFC 9457 problem+json errors with `request_id`; scoped API keys + optional OAuth2 client-credentials; gateway rate limiting with `X-RateLimit-*`; `Sunset` header policy published. Time-series responses cap granularity by range (raw only ≤7 days) to protect the L2 store `[~]`.

### 4.4 Webhook design

Standard Webhooks-compliant sender on BullMQ: per-endpoint HMAC secrets with rotation, `webhook-id`/`webhook-timestamp`/`webhook-signature` headers, exponential backoff + jitter across ~24h (8 attempts `[~]`), DLQ with 30-day retention, customer-visible delivery log with manual replay in the admin UI, HTTPS-only endpoints with SSRF guards, event-type subscription filters per endpoint. Event catalogue per §3.4.

### 4.5 Integration tier menu — how "connects to your systems" stays bounded

This is the commercial answer to unbounded integration engineering:

| Tier | What | Who does the work | Pricing posture `[!]` |
| --- | --- | --- | --- |
| **T0 — Files (self-serve)** | CSV/xlsx exports, scheduled email delivery, SFTP drop | Customer | Included |
| **T1 — Webhooks (self-serve)** | Standard Webhooks endpoints, event filters, delivery log, docs + verification snippets | Customer IT (hours) | Included |
| **T2 — REST API (self-serve)** | Scoped keys, OpenAPI, polling events endpoint | Customer IT / their SI | Included; rate-limited |
| **T3 — Guided generic** | Stamped engineer maps T0–T2 onto customer middleware (iPaaS, SAP PI/PO, custom) in a timeboxed engagement | Joint, 1–2 weeks | One-time fee |
| **T4 — Named connectors** | SAP (OData/IDoc), Tally agent, specific ESG platforms; built once, productised only after ≥3 paying requests for the same target | Stamped | Paid engagement → product roadmap |

Sales rule: the phrase "connects to any custom system" is *true at T1/T2* — anything that can receive an HTTPS POST or call a REST API connects. Anything requiring Stamped to speak a proprietary protocol is T3/T4 and priced. This mirrors how the ESG platforms themselves scope ingestion (API + bulk CSV first, named connectors as catalogue items [25][26]).

---

## 5. How this layer is tested and evaluated

| Test class | Tooling | What it covers |
| --- | --- | --- |
| **E2E flows** | Playwright (same dependency as PDF) | Golden paths per role: supervisor triages Rx → acknowledges → state syncs; plant head views ledger; sustainability downloads pack. Run against seeded demo tenant in CI |
| **Visual regression** | Playwright screenshot diffs (or Chromatic if Storybook adopted `[~]`) | Chart modules with fixed seed data — catches ECharts option regressions, baseline-band rendering, TOD shading; mobile + desktop viewports; `hi` locale snapshots for Devanagari overflow |
| **API contract tests** | Schemathesis (property-based, driven from OpenAPI 3.1) + per-version contract suite in CI | Responses match spec; pagination, error envelope, auth scopes; breaking-change detection blocks merge |
| **Webhook conformance** | standard-webhooks verification libraries as test consumers | Signature validity, timestamp skew rejection, retry schedule, DLQ behaviour under a deliberately failing endpoint |
| **Report snapshot tests** | Byte-stable PDF render of golden dataset → rasterise → image diff; CSV golden-file diffs | Monthly pack layout, BRSR adjunct column contract (customers script against these), factor-disclosure presence on every tCO₂e |
| **Performance budgets** | Lighthouse CI on overview + queue routes; ECharts frame profiling on 43k-point fixture | LCP < 2.5 s / INP < 200 ms / bundle < 350 kB gz budgets fail the build `[!]` |
| **Tenancy/RBAC tests** | Integration suite: every endpoint × every role × cross-tenant attempt | No cross-tenant read is the single highest-severity test class; runs on every merge |
| **SSE resilience** | Test harness: kill connection mid-stream, verify `Last-Event-ID` resume with no missed events | Reconnect correctness |

Evaluation metrics (product-level, reviewed monthly):

- **Rx closure rate via dashboard vs WhatsApp** — is the queue pulling its weight toward the ≥60% target?
- **Time-to-acknowledge** (Rx created → first acknowledge, by channel).
- **Evidence drill-down rate** — % of Rx views that expand evidence; low rate = trusted-by-default or ignored (pair with closure to tell which).
- **Export usage** — packs downloaded/forwarded per account per quarter (renewal-risk leading indicator `[~]`).
- **Webhook delivery success rate** and DLQ depth per endpoint.
- **API adoption** — % of accounts with ≥1 active API key or webhook endpoint (integration stickiness).

---

## 6. Build phasing

Aligned to the master phases (§15 of the technical architecture):

| Phase | L6 scope | Exit criterion |
| --- | --- | --- |
| **P0** (weeks 1–8) | Dashboard core: M1 savings ledger, M2 trend vs baseline, M4 anomaly feed, M5 prescription queue (triage lanes, evidence drill-down, WhatsApp deep-link acknowledge); SSE updates; mobile-responsive queue; CSV export on ledger + queue; role-gated views (operator/supervisor/plant head); English UI | A pilot supervisor closes an Rx end-to-end from phone; plant head reads verified ₹ without asking anyone |
| **P1** (months 3–6) | M3 health map, M6 top consumers, M7 TOD profile, M8 intensity; Playwright PDF pipeline + first monthly pack (savings summary, SEC report, methodology note); BullMQ scheduled packs; Hindi UI for operator/supervisor surfaces; Export centre | Month-end pack generates unattended and survives a customer's sustainability-lead review |
| **P2** (months 6–12) | Public REST API v1 (OpenAPI, scoped keys, rate limits) + docs; Standard Webhooks sender + event catalogue + delivery log; polling events endpoint; BRSR/PAT adjunct CSVs; multi-plant rollup + benchmark view; SSO (SAML/OIDC via provider) for first enterprise account; T3 guided-integration playbook | One customer system consumes Stamped events in production without Stamped hand-holding |
| **P3** | T4 named connectors as demand proves (SAP OData export, Tally production-pull agent, first ESG connector); OAuth2 client credentials; embedded/share-link analytics `[!]`; conversational analyst surface (L4-driven); SCIM if a 500+ seat account requires it | Decided per paid engagement, not roadmap faith |

Deliberately late: embedded analytics, named connectors, SCIM, native mobile app — each waits for a paying pull signal.

---

## 7. Open questions

1. **WhatsApp deep-link auth `[!]`** — signed magic links with short TTL vs forcing login: forwarding a link must not leak plant data. Needs a security decision with L5 (who owns link issuance) before P0 ships.
2. **Time-series API granularity economics** — raw-resolution API pulls could hammer the L2 TSDB; where do we cap granularity/range per tier, and do heavy consumers get a pre-aggregated export instead?
3. **Hindi prescription text** — L4 generates Rx text; does it generate Hindi natively or does L6 machine-translate `[!]`? Rendering is L6's job, generation ownership is unresolved.
4. **Pack sign-off workflow** — does the monthly pack auto-send, or does a customer sustainability lead approve before distribution? Auto-send risks a wrong number reaching corporate ESG; approval adds friction. Leaning approval-first for the first year `[~]`.
5. **Svix buy trigger** — at what webhook volume/endpoint count does operating our own sender cost more than Svix's fee? Revisit at 50 active endpoints `[~]`.
6. **Demo dashboard → product parity** — the Vercel demo's visual language must be audited against ISA-101 colour discipline (§3.1) before it hardens into the product; deviation-first charts may require redesigning some demo modules.
7. **BRSR XBRL ambitions `[!]`** — customers may ask Stamped to emit MCA-taxonomy XBRL fragments rather than CSV. Explicitly out of scope for now (filing-adjacent liability); revisit only with legal review.
8. **On-prem dashboard variant** — will any enterprise demand a plant-LAN-hosted read-only mirror (OT-security posture)? Would fork the hosting story; no current evidence of demand `[~]`.

---

# Citations

1. https://blog.logrocket.com/best-react-chart-libraries-2026/
2. https://www.usedatabrain.com/blog/react-chart-libraries
3. https://chenguangliang.com/en/posts/blog152_react-chart-libraries-comparison/
4. https://www.youngju.dev/blog/culture/2026-05-14-data-visualization-libraries-2026-d3-plot-visx-recharts-echarts-vega-comparison-deep-dive-2026.en
5. https://getstream.io/blog/websocket-sse/
6. https://www.nazarboyko.com/articles/sse-vs-websockets-for-live-ui-updates
7. https://www.flowverify.co/blog/sse-websockets-polling-when-each-wins-2026
8. https://industriant.com/Industriant_ISA-101_Cheat_Sheet.pdf
9. https://fuselabcreative.com/manufacturing-dashboard-ux-design/
10. https://ifactoryapp.com/industries/infrastructure-management/smart-infrastructure-monitoring-dashboard-good-looks
11. https://rajeshrnair.com/blog/web-development/frontend/nextjs-i18n-indian-languages-hindi-malayalam-tamil-2026.html
12. https://noqta.tn/en/tutorials/nextjs-next-intl-i18n-app-router-guide-2026
13. https://linear.app/docs/triage
14. https://linear.app/docs/triage-manage-unplanned-work
15. https://pdf4.dev/blog/react-pdf-vs-playwright-pdf-generation
16. https://typcraft.com/blog/pdf-engines-browser-vs-native
17. https://pdf4.dev/blog/html-to-pdf-benchmark-2026
18. https://www.nutrient.io/blog/generate-pdfs-from-javascript/
19. https://iurii.rogulia.fi/blog/background-jobs-nodejs
20. https://trybuildpilot.com/641-trigger-dev-vs-bullmq-vs-pgboss-2026
21. https://www.sebi.gov.in/sebi_data/commondocs/jul-2023/Annexure_II-Updated-BRSR_p.PDF
22. https://ca2013.com/wp-content/uploads/2023/07/SEBI-Circular_12.07.2023.pdf
23. https://batchwise.ai/methodology/principle-6-environment/
24. https://assets.kpmg.com/content/dam/kpmgsites/in/pdf/2026/02/chapter-1-emerging-trends-in-brsr-reporting-by-listed-companies.pdf.coredownload.pdf
25. https://www.persefoni.com/en-gb/product/integration-hub
26. https://novisto.com/product/collect
27. https://cadence.withremote.ai/blog/api-design-best-practices
28. https://bytepane.com/blog/rest-api-best-practices/
29. https://apiscout.dev/guides/api-versioning-strategies-2026
30. https://github.com/standard-webhooks/standard-webhooks/
31. https://hookdeck.com/blog/building-reliable-outbound-webhooks
32. https://www.digitalapplied.com/blog/webhook-reliability-idempotency-retries-engineering-reference-2026
33. https://blog.sap-press.com/apis-vs-idocs-in-sap-s4hana-and-sap-cloud-erp
34. https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-members/idocs-are-still-safe-for-sap-s-4hana-sap-clean-core-extensibility-level-b/ba-p/14225439
35. https://help.tallysolutions.com/getting-started-with-tally-integrations/
36. https://www.modern-datatools.com/compare/metabase-vs-superset
37. https://cube.dev/articles/best-embedded-analytics-platforms-2026
38. https://workos.com/blog/enterprise-readiness-checklist-2026
39. https://www.zulbera.com/insights/enterprise-authentication-sso-saas-guide/
40. https://stamped-energy.vercel.app/ (demo dashboard — intermittently unreachable during research)
