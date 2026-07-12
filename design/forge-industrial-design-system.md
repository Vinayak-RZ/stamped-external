# Forge Industrial v2.0 — Stamped Energy design system

> **Use in:** connectors-bill customer UI, stamped-l6 dashboard, marketing-adjacent product surfaces.  
> **Live references:** [stamped.work/how-it-works](https://stamped.work/how-it-works) · [stamped-energy.vercel.app](https://stamped-energy.vercel.app/)  
> **Machine-readable tokens:** [forge-industrial-v2.tokens.yaml](./forge-industrial-v2.tokens.yaml)

---

## 1. Brand & personality

The design system is built for **manufacturing decision-makers** who need immediate clarity and professional rigor. The personality is **industrial, high-contrast, and authoritative** — factory-floor energy balanced with analytics precision.

**Aesthetic:** Modern Industrial Minimalism — heavy visual weights, crisp intersections, structural integrity. Every element serves a functional purpose in high-stakes operational environments.

**Product voice (from marketing):**

- Lead with **rupees on the bill**, not abstract kWh.
- Five-step loop: **Connect → Observe → Decide → Execute → Verify**.
- Prescriptions show **What · Why · Who · Impact · Due** — bill upload UI should feel like step **01 Connect** ("Start with meter + bill").

---

## 2. Color system

High-contrast palette for legibility in office and plant-floor lighting.

### 2.1 Semantic roles

| Token | Hex | Role |
|-------|-----|------|
| **Primary** | `#F75440` | CTAs, critical actions, alerts, energy/urgency |
| **Secondary** | `#051F13` | Nav, footers, anchor sections, stable states |
| **Tertiary** | `#00666b` / `#008287` | Informational accents, links, data highlights |
| **Surface** | `#f7faf5` | App background (warm grey — reduces eye strain) |
| **Surface container** | `#ecefea` → `#ffffff` | Cards sit on white over warm surface |
| **On-surface** | `#191c1a` | Primary text |
| **On-surface variant** | `#5a403c` | Secondary text |
| **Outline** | `#8f706b` | Borders |
| **Outline variant** | `#e3beb8` | Subtle dividers |
| **Error** | `#ba1a1a` | Validation failures, publish blocked |

### 2.2 Status mapping (product UI)

Align with dashboard demo at [stamped-energy.vercel.app](https://stamped-energy.vercel.app/):

| Status | Color treatment | Example |
|--------|-----------------|---------|
| Critical / Over limit | Primary coral fill or strong border | Kiln overload, recompute fail |
| Warning | Tertiary or amber-adjacent chip | Review required, low confidence field |
| Good / Normal / Validated | Secondary green tint or neutral chip | Bill published, recompute pass |
| Optimized / AI | Tertiary accent | Auto-extracted high confidence |
| Info / Offline | Muted outline chip | Processing, draft |

**connectors-bill:** Use **Primary** for "Publish" and blocking errors; **Secondary** for nav/header; **Good** state when `extraction.validated=true`.

---

## 3. Typography

Two-font strategy: **executive headlines** vs **operational data**.

| Role | Family | Usage |
|------|--------|--------|
| **Display / Headlines** | **Plus Jakarta Sans** 700–800 | Page titles, KPI hero numbers, section headers |
| **Body / UI / Data** | **Inter** 400–600 | Paragraphs, forms, tables, labels |

### 3.1 Scale

| Token | Font | Size / Weight | Use |
|-------|------|---------------|-----|
| `display-lg` | Plus Jakarta Sans | 48px / 800, LH 56 | Desktop hero KPI (e.g. bill total ₹) |
| `display-lg-mobile` | Plus Jakarta Sans | 32px / 800, LH 40 | Mobile hero |
| `headline-lg` | Plus Jakarta Sans | 32px / 700 | Page title |
| `headline-md` | Plus Jakarta Sans | 24px / 700 | Card title |
| `body-lg` | Inter | 18px / 400 | Intro copy |
| `body-md` | Inter | 16px / 400 | Default body |
| `data-tabular` | Inter | 14px / 500, tabular nums | **All ₹ amounts, kWh, line tables** |
| `label-sm` | Inter | 12px / 600 | Field labels, chips |

**Rules:**

- Use `font-variant-numeric: tabular-nums` for bill line tables and totals.
- Headlines: letter-spacing `-0.02em` (display) / `-0.01em` (mobile).
- Hindi labels: same scale; test line-height +2px if needed.

### 3.2 Google Fonts import

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@700;800&display=swap" rel="stylesheet">
```

---

## 4. Layout & grid

**Fixed-fluid hybrid grid** — max content width **1440px**, centered.

| Breakpoint | Columns | Gutter | Side margin |
|------------|---------|--------|-------------|
| Desktop | 12 | 24px | 40px |
| Tablet | 8 | 16px | 24px |
| Mobile | 4 | 16px | 16px |

**Vertical rhythm:** 4px baseline grid.

| Spacing token | Value | Use |
|---------------|-------|-----|
| `sm` | 8px | Tight groups |
| `md` | 16px | Form fields, list items |
| `lg` | 24px | Card padding |
| `xl` | 48px | Section breaks |

---

## 5. Elevation & depth

**Tonal layering + low-contrast outlines** — not soft Material shadows.

| Level | Treatment |
|-------|-----------|
| **0 Base** | Surface `#f7faf5` |
| **1 Cards** | White `#ffffff`, 1px border `#e0e3df` or outline-variant, **no shadow** |
| **2 Dropdowns / modals** | White + 4px hard shadow (10% black) |
| **3 Active** | Primary coral accent — elevation via **color**, not blur |

---

## 6. Border radius

| Token | Value | Components |
|-------|-------|------------|
| `sm` | 4px | Small tags |
| `md` | 8px | **Buttons, inputs** |
| `lg` | 16px | **Cards, modals** |
| `xl` | 24px | Section wrappers |
| `full` | 9999px | Avatars only — avoid pill-overuse |

---

## 7. Components

### 7.1 Buttons

| Variant | Background | Text | Height |
|---------|------------|------|--------|
| Primary | `#F75440` | `#ffffff` | **48px** min (touch-friendly) |
| Secondary | `#051F13` | `#ffffff` | 48px |
| Ghost | transparent | `#051F13` | 48px, 1px border |

Mobile: full-width primary CTAs on upload/publish screens.

### 7.2 Inputs & upload

- White background, 1px outline border.
- Focus: 2px border `#051F13`.
- Label above field (`label-sm`).
- **Upload zone:** dashed border, coral on drag-over; camera + file icons 2px stroke.

### 7.3 Cards

- White bg, 16px radius, 24px padding.
- Header with subtle bottom border separator.
- Bill summary card: large ₹ total in `display-lg-mobile` + `data-tabular`.

### 7.4 Chips / status

- 12px bold text, high-contrast fill.
- Examples: `Published` (secondary green tint), `Review` (primary), `Processing` (tertiary).

### 7.5 Data tables (bill lines)

- Inter for all cells; zebra optional at 2% secondary tint.
- Right-align ₹ and qty columns.
- Row actions: ghost buttons, 44px tap targets on mobile.

### 7.6 KPI / summary widgets

From dashboard demo pattern:

- Large number top, delta chip below (e.g. "18.4% vs last month").
- Subtle label: "Verified via M&V Protocol" style footnote for `extraction.validated`.

---

## 8. Patterns from live product surfaces

### 8.1 Marketing — [how-it-works](https://stamped.work/how-it-works)

Reuse for **empty states & onboarding** in bill upload:

- **Five-step loop** visual — bill upload is **Step 1: Connect**.
- **Utility bill** icon in unified ingestion diagram (alongside SCADA, meters).
- Copy tone: "Start with meter + bill", "Check the next bill".
- Section structure: eyebrow label → headline → supporting body → CTA.

### 8.2 Dashboard demo — [stamped-energy.vercel.app](https://stamped-energy.vercel.app/)

Reuse for **dense operational UI** (review screen, history):

- **Top KPI strip** — 2–4 metrics max on mobile (bill total, line count, status).
- **Status chips:** CRITICAL / WARNING / GOOD / INFO color system.
- **Prescription card pattern** — adapt for "Review field" cards:
  - WHAT = field name
  - WHY = confidence / recompute note
  - IMPACT = ₹ delta if wrong
- **Tables:** sortable columns, benchmark column, status pill last column.
- **Live feed pattern** — use for upload/processing timeline ("Now: extracting page 2…").

**Do not clone** full dashboard in connectors-bill — only borrow components listed above.

---

## 9. connectors-bill UI mapping

| Screen | Design patterns |
|--------|-----------------|
| Login / plant picker | Secondary nav bar, surface background, primary CTA |
| Upload hub | How-it-works "Connect" iconography; large upload card Level 1 |
| Camera capture | Full-bleed mobile, primary shutter CTA, 48px buttons |
| Processing | Dashboard "Live feed" timeline; tertiary progress |
| Review | Prescription card layout; PDF viewer left / fields right (desktop); stacked mobile |
| Bill summary | KPI widget + data table; primary "Publish to Stamped" |
| History | Dashboard table pattern; status chips |

---

## 10. Tailwind / CSS variables (implementation)

See [forge-industrial-v2.tokens.yaml](./forge-industrial-v2.tokens.yaml) for copy-paste into:

```js
// tailwind.config.ts excerpt
theme: {
  extend: {
    colors: {
      primary: '#F75440',
      secondary: '#051F13',
      surface: '#f7faf5',
      // ... full set in tokens file
    },
    fontFamily: {
      display: ['"Plus Jakarta Sans"', 'sans-serif'],
      sans: ['Inter', 'sans-serif'],
    },
    borderRadius: {
      md: '0.5rem',
      lg: '1rem',
      xl: '1.5rem',
    },
  },
},
```

**PWA meta:** `theme-color: #051F13`, `background-color: #f7faf5`.

---

## 11. Accessibility

- WCAG AA contrast on text vs surface (on-surface on surface passes).
- Focus rings: 2px secondary outline, offset 2px.
- Touch targets ≥44×44px on mobile (buttons already 48px).
- Do not rely on color alone for status — include text label (Critical, Validated, etc.).

---

## 12. Assets & logos

- Marketing site: [stamped.work](https://stamped.work/)
- Request brand assets from product team if SVG logo not in repo `[!]`.
- Favicon / app icon: use Secondary `#051F13` background + Primary accent mark.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-11 | Initial Forge Industrial v2.0 doc for connectors-bill handoff |
