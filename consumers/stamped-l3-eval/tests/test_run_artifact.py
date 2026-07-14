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
    statuses = {d["status"] for d in data["detections"]}
    assert statuses >= {"emitted", "suppressed", "shadow_only"}


def test_invalid_rejected() -> None:
    with pytest.raises(Exception):
        validate_artifact({"schema_version": "1.0.0"})
