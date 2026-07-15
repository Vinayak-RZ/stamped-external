"""Lane invariant unit tests (ADR-015)."""

from __future__ import annotations

import pytest

from stamped_l3_core.detection_lane import (
    LAB_ONLY_CAP,
    assert_lane_invariant,
    delivery_for,
    truncate_lab_only,
)


def test_delivery_for_mapping() -> None:
    assert delivery_for("emitted") == "l4"
    assert delivery_for("suppressed") == "lab_only"
    assert delivery_for("shadow_only") == "lab_only"
    assert delivery_for("hypothesis") == "lab_only"


def test_assert_lane_invariant() -> None:
    assert_lane_invariant("emitted", "l4")
    assert_lane_invariant("hypothesis", "lab_only")
    with pytest.raises(ValueError):
        assert_lane_invariant("emitted", "lab_only")


def test_truncate_lab_only() -> None:
    dets = [{"delivery": "l4", "logs": []}] + [
        {"delivery": "lab_only", "logs": []} for _ in range(LAB_ONLY_CAP + 5)
    ]
    out = truncate_lab_only(dets, cap=LAB_ONLY_CAP)
    assert sum(1 for d in out if d["delivery"] == "l4") == 1
    assert sum(1 for d in out if d["delivery"] == "lab_only") == LAB_ONLY_CAP
    assert any("overflow" in (d.get("logs") or [""])[-1] for d in out if d["delivery"] == "lab_only")
