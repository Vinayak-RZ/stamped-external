#!/usr/bin/env bash
# validate.sh — orchestrator for L3/L4 intelligence platform + consumer scaffolds
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

echo "== validate: contract-check =="
./scripts/contract-check.sh

echo "== validate: stamped-l3-core =="
(cd consumers/stamped-l3-core && pip install -e ".[dev]" -q && pytest -q)

echo "== validate: stamped-l3-rulepacks =="
(cd consumers/stamped-l3-rulepacks && pip install -e ".[dev]" -q && pytest -q)

echo "== validate: stamped-l3-eval =="
(cd consumers/stamped-l3-eval && pip install -e ".[dev]" -q && pytest -q)

echo "== validate: stamped-l3-eval Lab UI =="
(cd consumers/stamped-l3-eval/ui && pnpm install --frozen-lockfile 2>/dev/null || pnpm install && pnpm test && pnpm build)

echo "== validate: stamped-l4 =="
(cd consumers/stamped-l4 && pip install -e ".[dev]" -q && pytest -q)

echo "== validate: E2E fixture chain =="
python3 "${ROOT}/scripts/e2e_finding_to_ledger.py"

echo "== validate: adversarial contract fixtures =="
python3 "${ROOT}/scripts/test_adversarial_contracts.py"

echo "validate.sh: ALL GREEN"
