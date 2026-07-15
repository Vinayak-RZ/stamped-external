"""RunArtifact v1 schema + golden fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stamped_l3_eval.artifact import (
    GOLDEN_DIR,
    list_golden_artifacts,
    load_artifact,
    validate_artifact,
)

ROOT = Path(__file__).resolve().parents[1]


def test_schema_exists() -> None:
    assert (ROOT / "schemas" / "run-artifact.v1.json").is_file()


def test_at_least_three_goldens() -> None:
    assert len(list_golden_artifacts()) >= 3


@pytest.mark.parametrize("path", list(GOLDEN_DIR.glob("run_*.json")), ids=lambda p: p.name)
def test_golden_valid(path: Path) -> None:
    load_artifact(path)


def test_md_artifact_has_all_statuses() -> None:
    data = load_artifact(GOLDEN_DIR / "run_w-md-001.json")
    assert data["schema_version"] == "1.1.0"
    statuses = {d["status"] for d in data["detections"]}
    assert statuses >= {"emitted", "suppressed", "shadow_only", "hypothesis"}
    deliveries = {d["delivery"] for d in data["detections"]}
    assert deliveries == {"l4", "lab_only"}
    for d in data["detections"]:
        if d["status"] == "emitted":
            assert d["delivery"] == "l4"
        else:
            assert d["delivery"] == "lab_only"


def test_md_attribution_scores_and_shadow() -> None:
    data = load_artifact(GOLDEN_DIR / "run_w-md-001.json")
    by_id = {d["detection_id"]: d for d in data["detections"]}
    top = by_id["d-md-attr-top1"]
    assert top["scores"]["rank"] == 1
    assert top["delivery"] == "l4"
    runner = by_id["d-md-attr-runner"]
    assert runner["status"] == "hypothesis"
    assert runner["delivery"] == "lab_only"
    shadow = by_id["d-md-attr-shadow-ablation"]
    assert shadow["scores"]["shadow_method"] == "rank_ablation_corr_primary"


def test_invalid_rejected() -> None:
    with pytest.raises(Exception):
        validate_artifact({"schema_version": "1.1.0"})
