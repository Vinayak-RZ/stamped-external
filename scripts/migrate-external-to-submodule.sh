#!/usr/bin/env bash
# migrate-external-to-submodule.sh — replace copied external/ with stamped-external submodule
# Usage: ./migrate-external-to-submodule.sh [TAG]
# Run from consumer repo root (e.g. universal-repositary, connectors-edge).
set -euo pipefail

PLATFORM_REPO="${PLATFORM_REPO:-https://github.com/vinayak-rz/stamped-external.git}"
TAG="${1:-v2026.07.12}"
MOUNT="${MOUNT:-external}"

if [[ ! -d .git ]]; then
  echo "migrate: run from consumer repo root" >&2
  exit 1
fi

if [[ -f .gitmodules ]] && grep -q "stamped-external" .gitmodules 2>/dev/null; then
  echo "migrate: submodule already configured — bump with: cd ${MOUNT} && git fetch && git checkout ${TAG}"
  exit 0
fi

if [[ -d "${MOUNT}" ]]; then
  echo "migrate: backing up existing ${MOUNT}/ to ${MOUNT}.bak"
  mv "${MOUNT}" "${MOUNT}.bak"
fi

git submodule add "${PLATFORM_REPO}" "${MOUNT}"
git -C "${MOUNT}" checkout "${TAG}"

if [[ -d "${MOUNT}.bak" ]]; then
  git rm -r --cached "${MOUNT}.bak" 2>/dev/null || true
  rm -rf "${MOUNT}.bak"
fi

git add .gitmodules "${MOUNT}"
echo "migrate: staged submodule at ${TAG}. Commit with:"
echo "  git commit -m \"refactor: replace copied external/ with stamped-external submodule @ ${TAG}\""
echo "migrate: verify with ./${MOUNT}/scripts/contract-check.sh"
