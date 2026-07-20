# ADR-021: L5 notification and evidence policy

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-20 |
| **Deciders** | Engineering (L5 architecture overhaul) |
| **Related** | [L5 SSOT](../technical/layers/L5-closure-and-verification.md) · [ADR-004](ADR-004-compliance-driven-architecture.md) · [ADR-019](ADR-019-l5-runtime-and-consistency.md) · [compliance register](../compliance/india-compliance-register.md) |

---

## Context

Closure rate depends on WhatsApp-first delivery to named owners. Message spend at Stamped volumes is negligible (~₹7/plant/month `[~]`), so BSP markups buy little. Evidence bundles must remain India-resident and auditable. Prior open questions covered number strategy, SMS timing, and retention.

---

## Decision summary

| # | Topic | Decision |
| --- | --- | --- |
| 1 | WhatsApp route | **Meta Cloud API direct** |
| 2 | SMS | **MSG91 + TRAI DLT** — register in **P0**; send live in **P1** |
| 3 | Number strategy | **One shared Stamped WA Business number** initially |
| 4 | Template set (P0) | issue / reminder / escalation / verified — **utility** + quick-reply buttons |
| 5 | Fatigue budget | ≤ **3** business-initiated pushes per role per day `[~]` |
| 6 | High-urgency SLO | Meta accept ≤ **5 minutes** after L5 intake |
| 7 | Webhook security | Verify Meta signatures; dedupe on `wamid`; button-ID allowlist only |
| 8 | Evidence storage | Object store in **ap-south-1**; content-addressed hashes in L5 DB |
| 9 | Evidence export | Basic refs P0; one-click ZIP/PDF **P2** |
| 10 | Retention | Classes: operational / audit / legal-hold — year counts require legal confirmation |

---

## Number strategy rationale

Shared number minimises ops and Meta verification surface. Revisit **per-account numbers** only if:

- template quality rating pauses threaten multi-tenant blast radius, or
- an enterprise contract requires dedicated sender identity.

---

## Compliance gates (blocking)

| Gate | When |
| --- | --- |
| Contractual WhatsApp opt-in | Before first business-initiated message to a user |
| Meta Business verification | Before scaling beyond Tier-0 limits |
| DPDP DPIA for staff phones | Before production WA (ADR-004) |
| DLT PE/header/templates | Before SMS fallback goes live |

---

## Evidence bundle minimum contents

- Prescription snapshot + WorkflowEvent history excerpt
- Locked baseline id + fit stats hash
- Bill line refs + parsed amounts used in decomposition
- Modelled worksheet inputs (rates, volumes, FSU)
- Analyst decision record (P0)

Commercially sensitive — never ship to non-India regions; redact phone numbers in exports by default.

---

## Consequences

- L5 worker owns template send + quality metric scrape.
- CS playbooks must handle Meta reclassification (utility→marketing).
- L6 counterfactual and verified badges must not confuse channels.

---

## Alternatives considered

| Option | Rejected because |
| --- | --- |
| Gupshup/Twilio/Wati primary | Markup / USD billing / wrong product shape at our volumes |
| Per-plant numbers from day one | Ops overhead without proven quality need |
| SMS as primary channel | Lower engagement; DLT friction; keep as fallback |
| US-region evidence bucket | Residency / enterprise posture failure |
