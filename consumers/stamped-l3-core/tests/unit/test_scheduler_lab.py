"""Hot path logs suppressed + never silent-drops (ADR-015)."""

from __future__ import annotations

from pathlib import Path

from stamped_l3_core.clients.l2 import FixtureL2Client
from stamped_l3_core.lab_export import get_lab_log
from stamped_l3_core.outbox import TransactionalOutbox
from stamped_l3_core.rulepack_loader import load_rulepack
from stamped_l3_core.scheduler import run_hot_path
from stamped_l3_core.suppression import SuppressionService

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def test_hot_path_logs_emit_and_never_lab_only_in_outbox() -> None:
    rulepack = load_rulepack(FIXTURES / "incomer_rulepack.json")
    md_cfg = dict(rulepack["engines"]["md_overlap"])
    md_cfg["rulepack_version"] = rulepack["version"]
    md_cfg["attribution_candidates"] = [
        {"asset": "furnace-a", "ramp_kw": 220, "hops": 1, "proximity": 0.5, "score": 110, "corr_abs": 0.7},
        {"asset": "comp-2", "ramp_kw": 40, "hops": 2, "proximity": 0.33, "score": 13, "corr_abs": 0.9},
    ]

    published = run_hot_path(
        FixtureL2Client(FIXTURES),
        TransactionalOutbox(),
        SuppressionService(),
        org_id="org_acme",
        plant_id="plant_ghaziabad_1",
        asset_id="incomer_1",
        from_ts="2026-06-15T00:00:00Z",
        to_ts="2026-06-15T23:59:59Z",
        md_config=md_cfg,
    )
    assert len(published) >= 1
    lab = get_lab_log().to_run_artifact()
    assert lab["schema_version"] == "1.1.0"
    assert any(d["delivery"] == "l4" for d in lab["detections"])
    assert any(d["status"] == "hypothesis" for d in lab["detections"])
    assert any(d.get("scores", {}) and d["scores"].get("shadow_method") for d in lab["detections"])
    # outbox payloads are findings only — no delivery=lab_only concept on Finding
    for p in published:
        assert "category" in p


def test_suppressed_candidate_logged_not_outbox() -> None:
    rulepack = load_rulepack(FIXTURES / "incomer_rulepack.json")
    md_cfg = dict(rulepack["engines"]["md_overlap"])
    md_cfg["rulepack_version"] = rulepack["version"]
    # Suppression window covering whole day
    suppression = SuppressionService(
        startup_windows={"incomer_1": [("2026-06-15T00:00:00Z", "2026-06-16T00:00:00Z")]},
    )
    published = run_hot_path(
        FixtureL2Client(FIXTURES),
        TransactionalOutbox(),
        suppression,
        org_id="org_acme",
        plant_id="plant_ghaziabad_1",
        asset_id="incomer_1",
        from_ts="2026-06-15T00:00:00Z",
        to_ts="2026-06-15T23:59:59Z",
        md_config=md_cfg,
    )
    assert published == []
    lab = get_lab_log().to_run_artifact()
    assert any(d["status"] == "suppressed" and d["delivery"] == "lab_only" for d in lab["detections"])
