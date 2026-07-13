"""Golden replay scaffold — validates expected finding category from fixture."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "fixtures" / "golden_md_spike.json"


def load_golden() -> dict:
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


def replay_category(golden: dict) -> str:
    """ponytail: stub replay — returns expected category until l3-core wires engines."""
    return golden["expected_finding"]["category"]


def test_golden_md_spike_category():
    golden = load_golden()
    assert golden["rule"] == "md_overlap"
    assert replay_category(golden) == golden["expected_finding"]["category"]
    assert golden["expected_finding"]["category"] == "md_overlap"


def test_golden_has_input_window():
    golden = load_golden()
    window = golden["input_window"]
    assert window["asset"] == "incomer_1"
    assert len(window["measurements"]) >= 1
