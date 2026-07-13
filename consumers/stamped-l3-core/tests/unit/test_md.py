from stamped_l3_core.engines.md import detect_md_overlap
from stamped_l3_core.models.finding import compute_dedupe_key


def test_detect_md_overlap_finds_peak_above_band():
    measurements = {
        "org_id": "org_acme",
        "plant_id": "plant_ghaziabad_1",
        "asset_id": "incomer_1",
        "points": [
            {"ts": "2026-06-15T06:00:00Z", "value": 810.0},
            {"ts": "2026-06-15T06:30:00Z", "value": 945.0},
        ],
    }
    findings = detect_md_overlap(
        measurements,
        cmd_kva=900.0,
        baseline_band=(800.0, 850.0),
    )
    assert len(findings) == 1
    f = findings[0]
    assert f.category == "md_overlap"
    assert f.evidence["actual_value"] == 945.0
    assert f.assets == ["incomer_1"]


def test_detect_md_overlap_empty_when_within_band():
    measurements = {
        "org_id": "org_acme",
        "plant_id": "plant_1",
        "asset_id": "incomer_1",
        "points": [{"ts": "2026-06-15T06:00:00Z", "value": 820.0}],
    }
    assert detect_md_overlap(measurements, cmd_kva=900.0, baseline_band=(800.0, 850.0)) == []


def test_dedupe_key_is_stable():
    key = compute_dedupe_key(
        "md_overlap",
        ["incomer_1"],
        "2026-06-15T06:00:00Z/2026-06-15T07:00:00Z",
    )
    assert key.startswith("sha256:")
    assert len(key) == 71
