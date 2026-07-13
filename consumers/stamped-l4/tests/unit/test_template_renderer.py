import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from stamped_l4.template_renderer import CATEGORY_TEMPLATE_ID, render_prescription
from stamped_l4.verifier import verify

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


@pytest.mark.parametrize(
    ("fixture_name", "category"),
    [
        ("finding_md_overlap.json", "md_overlap"),
        ("finding_pf_slab_breach.json", "pf_slab_breach"),
        ("finding_tod_exposure.json", "tod_exposure"),
    ],
)
def test_render_prescription_maps_category_to_template(fixture_name: str, category: str) -> None:
    finding = _load(fixture_name)
    rx = render_prescription(
        finding,
        prescription_id="rx-test-001",
        now=datetime(2026, 7, 13, 12, 0, tzinfo=timezone.utc),
    )

    assert rx["template_id"] == CATEGORY_TEMPLATE_ID[category]
    assert rx["finding_refs"] == [finding["finding_id"]]
    assert rx["provenance"]["lane"] == "template_fast_path"
    assert rx["impact"]["inr_monthly"] == finding["estimated_monthly_inr"]
    assert rx["impact"]["kwh_monthly"] == finding["estimated_monthly_kwh"]

    ok, errors = verify(rx, finding)
    assert ok, errors


def test_render_prescription_rejects_unknown_category() -> None:
    finding = _load("finding_md_overlap.json")
    finding["category"] = "idle_load"
    with pytest.raises(ValueError, match="unsupported"):
        render_prescription(finding)
