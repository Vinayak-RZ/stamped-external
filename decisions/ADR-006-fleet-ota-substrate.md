# ADR-006: Fleet OTA substrate (P1 decision)

| Field | Value |
| --- | --- |
| **Status** | Accepted |
| **Date** | 2026-07-09 |
| **Related** | [ADR-005](ADR-005-edge-agent-go-architecture.md) |

---

## Context

L1 open question #7: balena-class managed OTA vs self-run k3s+GitOps vs enhanced manual. Fleet size at P1 is &lt;20 devices.

---

## Decision

**P1 default: enhanced manual OTA** — signed config manifests, Docker image version pins, documented rollback runbook. No managed fleet platform until ~20 devices or first multi-state ops hire.

| Option | P1 verdict | Trigger to adopt |
|--------|------------|------------------|
| Enhanced manual (`docker pull` + restart) | **Selected** | Now — &lt;20 devices |
| balenaCloud / managed edge | Defer | ≥20 devices OR &gt;4h/week manual OTA ops |
| k3s + GitOps (Flux/Argo) | Defer | Customer mandates K8s OR ≥50 Path A plants |

---

## Consequences

- `docs/runbooks/edge-manual-ota.md` is the fleet SOP for P1.
- Image tags: `stamped-edge:p0`, `stamped-edge:p1`, `stamped-edge:full`.
- Config OTA (mapping/site) remains HTTPS manifest + MQTT wake-up — independent of container OTA substrate.
- Revisit ADR-006 when unpushed manual OTA toil exceeds 4h/week sustained.
