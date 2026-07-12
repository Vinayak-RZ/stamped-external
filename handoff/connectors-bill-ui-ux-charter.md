# connectors-bill — UI/UX charter (customer-facing)

> **Product anchor:** [Master document](../technical/00-stamped-master-document.md) — customers trust **rupees on the DISCOM bill**, not dashboards alone.  
> **L1 spec:** [§3.4](../technical/layers/L1-connect-and-normalise.md) — portal PDFs **and WhatsApp-quality phone photos** are P0 inputs.  
> **L6 reference:** [L6 experience layer](../technical/layers/L6-experience-and-integration.md) — stack defaults (Next.js, ECharts, next-intl); bill UI is a **focused module**, not full L6.

---

## 1. Who uses this UI

| Persona | Context | Primary device |
|---------|---------|----------------|
| **Plant energy manager** | Uploads monthly HT bill, reviews extracted lines | Desktop + phone |
| **Accountant / admin** | Checks totals vs printed bill, approves for M&V | Desktop |
| **Floor supervisor** | Photographs bill received in mailroom | **Phone** |
| **Stamped CS / analyst** | Fixes template misses (internal role, P1) | Desktop |

**Not in scope for this UI:** prescription queue, live meter charts, sustainability pack — those live in **stamped-l6**.

---

## 2. Design principles

| Principle | Implementation |
|-----------|----------------|
| **Mobile-first** | Design breakpoints phone → tablet → desktop; touch targets ≥44px |
| **Trust through arithmetic** | Always show recompute: extracted total vs recomputed total vs printed total |
| **Never hide uncertainty** | Low-confidence fields highlighted; `validated=false` blocks publish |
| **Minimal typing on mobile** | Camera capture, pre-filled org/plant, swipe approve/reject |
| **Progressive disclosure** | Upload → processing spinner → summary → detail drill-down |
| **Offline-tolerant upload (P1)** | Queue photo locally if network poor; retry when online |
| **Accessibility** | WCAG AA contrast, Hindi screen reader labels, keyboard nav on desktop |
| **Data residency messaging** | "Stored in India region" badge for enterprise trust `[!]` |

---

## 3. Core user journeys

### 3.1 Happy path — portal PDF (desktop)

```text
Login → select plant → Upload PDF → Processing (15–60s)
  → "Bill validated ✓" summary (MD, total ₹, month)
  → Auto-published to Stamped (if all lines pass recompute)
  → Confirmation + link to "View in dashboard" (L6, P1)
```

### 3.2 Happy path — phone photo (mobile)

```text
Login → select plant → [📷 Capture bill] or gallery pick
  → Crop / rotate assist → Upload
  → Processing → If OCR weak: "Review 2 fields" card
  → Tap field → edit → Approve
  → Published confirmation
```

### 3.3 Review path — recompute failure

```text
Upload → Processing → ⚠ "Total mismatch ₹847"
  → Side-by-side: PDF crop | extracted table | editable fields
  → User fixes TOD slot kVAh → Recompute → Pass → Publish
```

### 3.4 History path

```text
Bills list by month → status chips: Draft | Review | Published | Failed
  → Tap row → lines detail → re-download original PDF
```

---

## 4. Screen inventory (P0)

| Screen | Route (suggested) | Purpose |
|--------|-------------------|---------|
| Login / plant picker | `/` | Auth + `plant_id` context |
| Upload hub | `/upload` | PDF + camera entry |
| Processing | `/documents/{id}` | Poll status; skeleton UI |
| Review | `/documents/{id}/review` | Field editor + PDF viewer |
| Bill summary | `/bills/{bill_id}` | Lines table, publish button |
| History | `/bills` | Past bills filterable by month |
| Settings | `/settings` | Language, notifications |

**PWA:** `manifest.json`, service worker for shell cache, add-to-home-screen prompt on mobile.

---

## Design system (mandatory for UI)

**Forge Industrial v2.0** — [../design/forge-industrial-design-system.md](../design/forge-industrial-design-system.md)

| Reference | Use |
|-----------|-----|
| [stamped.work/how-it-works](https://stamped.work/how-it-works) | Onboarding copy, five-step loop, "Connect" = bill upload |
| [stamped-energy.vercel.app](https://stamped-energy.vercel.app/) | KPI strips, status chips, prescription-style review cards, tables |
| [forge-industrial-v2.tokens.yaml](../design/forge-industrial-v2.tokens.yaml) | Tailwind / CSS token import |

- **Primary `#F75440`** — Publish, critical actions  
- **Secondary `#051F13`** — Nav, headers  
- **Plus Jakarta Sans** — headlines; **Inter** — body + tabular ₹ data  
- **48px button height** on mobile; cards white on warm grey surface `#f7faf5`

---

## 5. Visual & component guidance

| Area | Recommendation |
|------|----------------|
| Framework | Next.js App Router + TypeScript |
| Styling | **Tailwind CSS** mapped to Forge Industrial tokens ([design doc](../design/forge-industrial-design-system.md)) |
| Components | shadcn/ui or Radix — **themed with Stamped colors**, not default shadcn palette |
| PDF viewer | `react-pdf` or PDF.js; highlight bbox overlays from extract |
| Camera | `<input capture="environment">` + Capacitor optional P1 |
| Charts (minimal) | Sparkline for monthly bill total trend only — not full L6 |
| Loading | Skeleton states; never blank screen >300ms |
| Errors | Plain language: "We couldn't read the demand charge row" + support CTA |

**Brand tone:** Professional, industrial, rupee-first — not consumer fintech flashy.

---

## 6. Internationalization

Per L6 research — **next-intl**:

| Locale | Priority |
|--------|----------|
| `en-IN` | P0 |
| `hi-IN` | P0 (field labels mirror DISCOM Hindi headers) |

Date format: `bill_month` as `YYYY-MM`; display as "June 2026" / "जून 2026".

---

## 7. Document types UX (beyond DISCOM)

UI copy and flows should say **"Upload bill or utility document"** — not DISCOM-only.

| doc_type (internal) | User label | P0 |
|---------------------|------------|-----|
| `discom_ht_bill` | Electricity bill (HT) | Yes |
| `discom_lt_bill` | Electricity bill (LT) | P2 |
| `tariff_order` | Tariff / rate order | P1 |
| `other` | Other document | P1 (manual review) |

Template picker: "Which DISCOM?" dropdown (MSEDCL, UPPCL, …) improves extract accuracy.

---

## 8. Security & privacy (UI layer)

- No bill PDFs in browser localStorage long-term
- Presigned S3 URLs expire ≤15 min
- Session timeout on shared plant kiosks
- Mask account numbers in UI except last 4 digits
- Audit log: who approved publish (feeds L5 later)

See [compliance register](../compliance/india-compliance-register.md) for DPDP context.

---

## 9. Success metrics (UX)

| Metric | Target `[~]` |
|--------|--------------|
| Mobile upload completion rate | ≥85% |
| Time upload → published (auto-pass) | <2 min |
| Review queue completion | <24h median |
| User-reported "wrong field" after publish | <1% |

---

## 10. Explicit non-goals (UI)

- Not a general document management system (DMS)
- Not email inbox replacement
- Not WhatsApp bot (L5 may notify via WhatsApp; upload stays in web PWA P0)
- Not admin console for edge agents

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-11 | Initial UI/UX charter — mobile-first, multi-doc scope |
