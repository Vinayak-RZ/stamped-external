#!/usr/bin/env python3
"""E2E fixture replay: Finding → Prescription → WorkflowEvent → LedgerEntry (contract validation)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("pip install jsonschema", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "contracts" / "schemas"
FIXTURES = ROOT / "contracts" / "fixtures"
L4 = ROOT / "consumers" / "stamped-l4" / "src"

sys.path.insert(0, str(L4))
from stamped_l4.template_renderer import render_prescription  # noqa: E402
from stamped_l4.verifier import verify  # noqa: E402


def load_schema(name: str) -> dict:
    with open(SCHEMAS / name) as f:
        return json.load(f)


def main() -> None:
    with open(FIXTURES / "finding.valid.json") as f:
        finding = json.load(f)
    jsonschema.validate(finding, load_schema("finding.json"))

    rx = render_prescription(finding)
    ok, errors = verify(rx, finding)
    if not ok:
        raise ValueError(f"verifier failed: {errors}")
    jsonschema.validate(rx, load_schema("prescription.json"))

    with open(FIXTURES / "workflow_event.valid.json") as f:
        workflow_event = json.load(f)
    workflow_event["prescription_id"] = rx["id"]
    jsonschema.validate(workflow_event, load_schema("workflow-event.json"))

    with open(FIXTURES / "ledger_entry.valid.json") as f:
        ledger = json.load(f)
    ledger["prescription_id"] = rx["id"]
    jsonschema.validate(ledger, load_schema("ledger-entry.json"))

    assert rx["finding_refs"] == [finding["finding_id"]]
    assert workflow_event["to_status"] in {
        "blocked",
        "open",
        "in_progress",
        "done",
        "verified",
        "deferred",
        "rejected",
        "disputed",
    }
    print("e2e_finding_to_ledger: OK")


if __name__ == "__main__":
    main()
