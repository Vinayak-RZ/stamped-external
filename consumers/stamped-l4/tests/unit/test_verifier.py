import json
from datetime import datetime, timezone
from pathlib import Path

from stamped_l4.template_renderer import render_prescription
from stamped_l4.verifier import check_numeric_alignment, check_required_fields, verify

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_verify_accepts_renderer_output() -> None:
    finding = _load("finding_md_overlap.json")
    rx = render_prescription(
        finding,
        now=datetime(2026, 7, 13, 12, 0, tzinfo=timezone.utc),
    )
    ok, errors = verify(rx, finding)
    assert ok is True
    assert errors == []


def test_check_required_fields_flags_missing_top_level() -> None:
    errors = check_required_fields({"id": "rx-1"})
    assert any("missing required field: schema_version" in e for e in errors)
    assert any("missing required field: impact" in e for e in errors)


def test_check_required_fields_flags_empty_finding_refs() -> None:
    rx = _load("finding_md_overlap.json")
    prescription = {"finding_refs": [], "evidence_refs": ["x"], "status": "open", "dedupe_key": "sha256:abc"}
    errors = check_required_fields(prescription)
    assert "finding_refs must be a non-empty list" in errors


def test_check_numeric_alignment_rejects_drift() -> None:
    finding = _load("finding_md_overlap.json")
    rx = render_prescription(finding)
    rx["impact"]["inr_monthly"] = finding["estimated_monthly_inr"] * 1.05

    errors = check_numeric_alignment(rx, finding, tolerance_pct=0.01)
    assert any("inr_monthly" in e for e in errors)


def test_verify_combines_schema_and_numeric_errors() -> None:
    finding = _load("finding_tod_exposure.json")
    rx = render_prescription(finding)
    del rx["what"]
    rx["impact"]["kwh_monthly"] = 0

    ok, errors = verify(rx, finding)
    assert ok is False
    assert any("missing required field: what" in e for e in errors)
    assert any("kwh_monthly" in e for e in errors)
