"""Golden fixture smoke checks (structure only — engines live in core)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "fixtures" / "golden"


def test_golden_fixtures_present() -> None:
    files = sorted(GOLDEN.glob("*.json"))
    assert len(files) >= 11


def test_golden_have_expected_findings() -> None:
    for path in GOLDEN.glob("*.json"):
        data = json.loads(path.read_text())
        assert "expected_finding" in data, path.name
        finding = data["expected_finding"]
        assert "category" in finding
        assert "expected_rule_id" in data
