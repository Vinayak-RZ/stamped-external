#!/usr/bin/env python3
"""Contract adversarial fixtures — RT-01 through RT-06 patterns."""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "contracts" / "schemas"
FIXTURES = ROOT / "contracts" / "fixtures"
L4 = ROOT / "consumers" / "stamped-l4" / "src"
sys.path.insert(0, str(L4))
from stamped_l4.verifier import verify  # noqa: E402


def load(name: str) -> dict:
    with open(FIXTURES / name) as f:
        return json.load(f)


def test_rt06_forged_finding_rejected_at_l4() -> None:
    """RT-06: inflated INR on finding must fail numeric gate when copied to Rx."""
    finding = load("finding_forged_inr.json")
    rx = load("prescription.valid.json")
    rx["impact"]["inr_monthly"] = finding["estimated_monthly_inr"]
    try:
        ok, errors = verify(rx, finding)
        if ok:
            raise AssertionError("expected numeric gate failure for forged INR")
    except ValueError:
        return


def test_valid_fixtures_pass_schema() -> None:
    for fixture, schema in [
        ("finding.valid.json", "finding.json"),
        ("prescription.valid.json", "prescription.json"),
        ("ledger_entry.valid.json", "ledger-entry.json"),
    ]:
        with open(SCHEMAS / schema) as f:
            sch = json.load(f)
        with open(FIXTURES / fixture) as f:
            jsonschema.validate(json.load(f), sch)


if __name__ == "__main__":
    test_valid_fixtures_pass_schema()
    test_rt06_forged_finding_rejected_at_l4()
    print("adversarial contract fixtures: OK")
