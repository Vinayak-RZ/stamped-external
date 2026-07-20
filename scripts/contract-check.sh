#!/usr/bin/env bash
# contract-check.sh — validate JSON schemas and fixtures (stamped-platform)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCHEMAS="${ROOT}/contracts/schemas"
FIXTURES="${ROOT}/contracts/fixtures"

fail() { echo "contract-check: $*" >&2; exit 1; }

test -d "${SCHEMAS}" || fail "missing ${SCHEMAS} — initialize external/ submodule first"

python3 - "${ROOT}" <<'PY'
import json, sys
from pathlib import Path

root = Path(sys.argv[1])
schemas = root / "contracts" / "schemas"
fixtures = root / "contracts" / "fixtures"

try:
    import jsonschema
except ImportError:
    print("contract-check: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

schema_files = sorted(schemas.glob("*.json"))
if not schema_files:
    print("contract-check: no schemas found", file=sys.stderr)
    sys.exit(1)

for sf in schema_files:
    with open(sf) as f:
        json.load(f)

for ff in sorted(fixtures.glob("*.json")):
    with open(ff) as f:
        json.load(f)

pairs = {
    "bill_line.valid.json": "bill-line.json",
    "finding.valid.json": "finding.json",
    "prescription.valid.json": "prescription.json",
    "ledger_entry.valid.json": "ledger-entry.json",
    "ledger_entry_opportunity_cost.valid.json": "ledger-entry.json",
    "workflow_event.valid.json": "workflow-event.json",
}
for fixture, schema_name in pairs.items():
    fp, sp = fixtures / fixture, schemas / schema_name
    if fp.exists() and sp.exists():
        with open(sp) as f:
            schema = json.load(f)
        with open(fp) as f:
            data = json.load(f)
        jsonschema.validate(instance=data, schema=schema)

print(f"contract-check: OK ({len(schema_files)} schemas, {len(list(fixtures.glob('*.json')))} fixtures)")
PY

test -f "${FIXTURES}/dedupe_golden.json" || fail "missing dedupe_golden.json"
echo "contract-check: dedupe golden present"
