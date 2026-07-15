"""ADR-016 attribution shadows never imply L4."""

from __future__ import annotations

from stamped_l3_core.challenger.attribution_shadow import emit_attribution_shadows
from stamped_l3_core.detection_lane import delivery_for


def test_shadows_are_shadow_only_lab_lane() -> None:
    cands = [
        {"asset": "furnace-a", "ramp_kw": 220, "hops": 1, "score": 110, "corr_abs": 0.8},
        {"asset": "comp-2", "ramp_kw": 40, "hops": 2, "score": 13, "corr_abs": 0.9},
    ]
    rows = emit_attribution_shadows(cands)
    assert len(rows) >= 4  # 3 ablations + motif
    for r in rows:
        assert r["status"] == "shadow_only"
        assert delivery_for(r["status"]) == "lab_only"
        assert r["scores"]["shadow_method"]
    # corr-primary should prefer comp-2
    corr = next(r for r in rows if r["scores"]["shadow_method"] == "rank_ablation_corr_primary")
    assert corr["scores"]["agree_with_primary"] is False
