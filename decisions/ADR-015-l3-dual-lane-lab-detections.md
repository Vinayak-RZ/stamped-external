# ADR-015: L3 dual-lane lab detections

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-15 |
| **Deciders** | Engineering (L3 dual-lane / Lab retention) |
| **Related** | [ADR-012](ADR-012-l3-artifact-repo-topology.md) · [ADR-008](ADR-008-layer-repo-topology-and-interfaces.md) · [ADR-016](ADR-016-attribution-shadow-challengers.md) · [L3 spec](../technical/layers/L3-intelligence-core.md) |

---

## Context

Strict L3→L4 gates (suppression, confidence floors, M&V-eligible evidence) intentionally drop many structured candidates. Those candidates may still indicate savings opportunity or ranking ambiguity. Silently discarding them prevents forensic learning. They must **not** enter the L4 Finding outbox.

RunArtifact already had `emitted` / `suppressed` / `shadow_only`, but the hot path used silent `continue` on suppress — Lab never saw them.

---

## Decision

1. **Dual delivery lanes** on every Lab detection:
   - `delivery: l4` — may stage to Finding outbox; `status` must be `emitted`
   - `delivery: lab_only` — RunArtifact / Lab UI only; never outbox
2. **Status enum** extends with `hypothesis` (weak/near-miss/unbacked structured signal). Existing: `emitted`, `suppressed`, `shadow_only`.
3. **Invariant:** `delivery == l4` ⇔ `status == emitted` ⇔ outbox staged. All other statuses ⇒ `lab_only`.
4. **Observation-only:** no per-finding “promote to L4” UI. Coverage improvements ship via rulepack / threshold / calibration changes.
5. Emitted detections are **mirrored** into Lab with `delivery=l4` for forensic parity.
6. RunArtifact schema version **1.1.0** (required `delivery` field).

---

## Consequences

- `stamped-l3-core` scheduler logs every candidate to `LabLog` before outbox decisions.
- Lab UI primary filter is lane (L4 vs Lab-only); status is secondary.
- Precision / M&V floors for L4 unchanged.
- Attribution runner-ups and shadows follow ADR-016 into `lab_only`.

---

## Alternatives considered

| Option | Rejected because |
| --- | --- |
| Status-only separation (no `delivery`) | UI language unclear; hypothesis conflates with suppress |
| Manual promote-to-L4 from Lab | Bypasses golden CI / semver; risk of unverified ₹ to L4 |
| Widen L4 emit gates | Destroys precision-first closure product |
