# IA: Alarms vs Prescriptions vs Evidence

> **Status:** Proposed recommendation (awaiting product approval)  
> **Consumer:** [Vinayak-RZ/experience-integration](https://github.com/Vinayak-RZ/experience-integration) (L6 UI) · live `https://trying.stamped.work/`  
> **Source audit:** [audits/2026-07-24-trying-stamped-work.md](./audits/2026-07-24-trying-stamped-work.md) · screenshots in `artifacts/ui-audit/`  
> **Authority conflict:** Platform [ADR-023](../decisions/ADR-023-l6-ems-and-analyst-context.md) puts Evidence in primary nav; L6 consumer `DESIGN.md` / DEC-012 treat Evidence as deep-link / Reports-tier. This doc proposes how to resolve that for UX.

---

## 1. One-line definitions (memorize these)

| Concept | Plain meaning | User job | Owned by |
|--------|---------------|----------|----------|
| **Alarm** | “Something abnormal is happening *now* — notice it.” | Acknowledge / escalate / silence / clear attention | L5 alarm router → L6 EMS console |
| **Prescription (Rx)** | “Here is the *recommended action* and ₹ at stake.” | Assign / act / defer / reject / mark done | L4 language + L5 workflow → L6 queue |
| **Evidence** | “Here is the *proof* for that alarm or Rx.” | Trust before acting; defend after closing | L5 EvidenceBundle → L6 scoped viewer |

They are **not** three equal dashboards. They are three **roles in one decision chain**:

```text
Finding (L3) ──raises──► Alarm (attention)
        │
        └──compiles──► Prescription (action + ₹)
                │
                └──cites──► Evidence (proof pack)
```

An alarm without a prescription is a **watch**.  
A prescription without evidence is a **guess**.  
Evidence without an alarm or Rx is a **chart gallery** (anti-goal).

---

## 2. What should feel different in the UI

| Dimension | Alarms | Prescriptions | Evidence |
|-----------|--------|---------------|----------|
| Time feeling | Urgent / ageing | Due date + ₹ delay cost | Frozen window (pre-scoped) |
| Sort | Severity → age | Addressable ₹ × confidence → age | By linked entity / time |
| Primary verbs | Ack, Escalate, Silence | Assign, Done, Defer, Reject | Open, Export (later) |
| Success | Cleared / calm plant | Ops-confirmed ₹ | User understood *why* |
| Density | List + detail (triage) | Lane queue (closure) | One pack at a time |
| Badge language | Critical / Warning / Info + lifecycle | Needs review · Active · Verifying · Closed + claim badges | Proof pack · missing slices honesty |

**Rename cue:** drop “AI Prescriptions” in chrome if it fights “Alarms” as peers — prefer **Prescriptions**. “AI” is implementation detail; the job is closure.

---

## 3. How both connect to Evidence

```text
                    ┌─────────────────────┐
   Alarm.detail ───►│  EvidencePack       │◄─── Rx.expand / Full case
   “Open evidence”  │  (scoped chart +    │     “Show proof”
                    │   baseline + rule + │
                    │   tariff + lineage) │
                    └──────────┬──────────┘
                               │
                    /evidence/[id]?from=alarm|rx
                               │
                    Never a generic explorer as the default entry
```

**Rules that keep this simple:**

1. **Evidence is a *view of a parent*, not a third workflow.** Default entry = deep link from Alarm or Rx with `alarmId` / `rxId` already resolved (already implemented in `/evidence` redirect).
2. **Inline snapshot ≠ Evidence screen.** Alarm “Evidence snapshot” table and Rx “data evidence” table are *teasers*. Always offer one explicit **Show proof** CTA that opens the same EvidencePack route.
3. **One pack, two parents allowed.** Same Finding can back both an open Alarm and its related Prescription (`relatedPrescriptionId`). UI should show chips: `Alarm alm_…` · `Rx rx_…` · `Finding fnd_…`.
4. **Index page is secondary.** `/evidence` grid is for auditors / energy managers — park it under Reports (current) or keep deep-link-only. Do **not** make operators browse packs to start work.

---

## 4. Why it feels jumbled today (Playwright findings)

Live audit (2026-07-24) against `trying.stamped.work`:

| Finding | Evidence |
|---------|----------|
| Evidence absent from primary sidebar | Sidebar shows Overview · Live · Ask Analyst · Alarms · AI Prescriptions; Evidence only under **Reports** when that group is open |
| Concepts mixed on Alarm detail | Same panel: lifecycle actions + “Open prescription” + “Evidence snapshot” + “Open evidence” |
| Prescriptions lack Show proof | Expand shows text “Case description & data evidence” table but **zero** `/evidence` links (unlike Alarms) |
| Nav denser than ops charter | Live / Energy / Machine Health / Plant Map / Sustainability compete with Alarms+Rx for attention |
| Vocabulary drift | Platform ADR-023 primary = Today · Alarms · Prescriptions · Evidence · Analyst · Reports; shipped UI + DESIGN.md diverge |

Screenshots: `artifacts/ui-audit/desktop_{alarms,prescriptions,evidence,evidence_detail}.png` (this pack) and mirrored under the L6 consumer when synced.

---

## 5. Recommended IA (default)

### Trade-off: Where does Evidence live?

**Decision:** Evidence placement in navigation

**Option A — Primary nav peer (ADR-023):** Today · Alarms · Prescriptions · Evidence · Analyst · Reports  
— Pros: discoverable; matches platform SSOT. Cons: invites chart browsing; three ops nouns compete.

**Option B — Deep-link only + Reports shelf (DESIGN.md today):** Evidence opened from Alarm/Rx; index under Reports  
— Pros: operators stay on attention/action; proof stays attached to a job. Cons: harder for auditors to start from proof; Evidence feels “hidden.”

**Default:** **Option B with stronger in-context CTAs** (PRIORITY = SIMPLICITY for operators).  
Promote Evidence to primary only if plant heads report they cannot find proof after two weeks of use.

**Override:** Set PRIORITY = CONSISTENCY → Option A and shrink Insights into More/Reveal.

### Concrete structure

```text
Sidebar (ops-first)
  Overview
  Operations ▾
    Alarms          ← attention
    Prescriptions   ← action + ₹
  Ask Analyst
  More / Insights ▾   (Energy, Machine Health, Plant Map, …)
  Reports ▾
    Ledger / exports
    Evidence index    ← audit shelf, not triage
```

### In-context pattern (this is the real separation)

| Screen | Owns | May show | Must not own |
|--------|------|----------|--------------|
| `/alarms` | Lifecycle + severity | 3-row snapshot + **Show proof** + **Open Rx** | ₹ triage lanes, chart gallery |
| `/prescriptions` | Lanes + ₹ + assign/done | Why blurb + **Show proof** + linked alarm chip | Ack/escalate/silence |
| `/evidence/[id]` | Pre-scoped chart + lineage + missing honesty | Back to alarm / Back to Rx | Workflow state mutation (except future export) |

### Relationship chip strip (shared component)

On Alarm detail, Rx expand, and Evidence pack header:

`[Alarm · raised] → [Rx · needs review · ₹84k/mo] → [Proof pack]`

Clicking a chip navigates; never duplicates the other entity’s full UI inline.

---

## 6. Smallest UX fixes (if approved)

1. Add **Show proof** on every Rx expand → `/evidence?rxId=…` (mirror Alarms).
2. Rename nav **AI Prescriptions → Prescriptions**.
3. Relabel Alarm “Evidence snapshot” → **Signal snapshot** (reserve “Evidence” for the pack route).
4. On Evidence pack, always show parent chips + back link (partially done).
5. Keep Evidence index under Reports; do not add a third primary ops item unless Option A wins.

Non-goals for first pass: merging Alarm+Rx into one “Cases” list; SCADA-style alarm flood; generic evidence explorer landing.

---

## 7. Acceptance checks

- Operator can ack critical alarm without opening Evidence.
- Supervisor can sort Rx by ₹ and open proof in ≤2 clicks.
- Same EvidencePack id resolves from both `alarmId` and related `rxId`.
- No page titled both “alarm” and “prescription” as peer columns without an explicit relationship strip.
- Today still ≤7 signals; no third equal “Evidence” KPI competing with Alarms/Rx.

---

## 8. Open question for product

Approve **Default (Option B + Show proof CTAs)** or override to **Option A (Evidence primary)**?

After approval, implement as a short UI phase in `packages/web` (nav copy + Rx Show proof + snapshot rename + relationship chips).
