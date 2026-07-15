"""Lab export RunArtifact shape for eval Lab UI."""

from __future__ import annotations

from stamped_l3_core.lab_export import export_run_artifact, seed_demo_lab


def test_seed_export_has_all_statuses() -> None:
    seed_demo_lab()
    art = export_run_artifact()
    assert art["schema_version"] == "1.1.0"
    assert art["window_id"] == "live-demo"
    statuses = {d["status"] for d in art["detections"]}
    assert statuses >= {"emitted", "suppressed", "shadow_only", "hypothesis"}
    kinds = {d["detector_kind"] for d in art["detections"]}
    assert kinds >= {"engine", "rule", "ml_shadow"}
    for d in art["detections"]:
        if d["status"] == "emitted":
            assert d["delivery"] == "l4"
        else:
            assert d["delivery"] == "lab_only"
    assert art["timeline"]
