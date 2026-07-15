"""Map detection status → delivery lane (ADR-015).

ponytail: pure functions; invariant lives in one place.
"""

from __future__ import annotations

from typing import Literal

Status = Literal["emitted", "suppressed", "shadow_only", "hypothesis"]
Delivery = Literal["l4", "lab_only"]

# Cap lab_only rows per window to avoid Lab melt (ADR-015).
LAB_ONLY_CAP = 50


def delivery_for(status: Status | str) -> Delivery:
    """l4 iff emitted; everything else lab_only."""
    return "l4" if status == "emitted" else "lab_only"


def assert_lane_invariant(status: str, delivery: str) -> None:
    expected = delivery_for(status)
    if delivery != expected:
        raise ValueError(f"lane invariant: status={status} requires delivery={expected}, got {delivery}")


def truncate_lab_only(
    detections: list[dict],
    *,
    cap: int = LAB_ONLY_CAP,
) -> list[dict]:
    """Keep all l4 rows; cap lab_only (prefer lower rank / keep order, drop overflow)."""
    l4 = [d for d in detections if d.get("delivery") == "l4"]
    lab = [d for d in detections if d.get("delivery") != "l4"]
    if len(lab) <= cap:
        return detections
    kept = lab[:cap]
    overflow = len(lab) - cap
    if kept:
        logs = list(kept[-1].get("logs") or [])
        logs.append(f"lab_only overflow truncated: dropped {overflow} rows (cap={cap})")
        kept[-1] = {**kept[-1], "logs": logs}
    return l4 + kept
