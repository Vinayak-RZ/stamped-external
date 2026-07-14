"""JSON Schema validation for every rulepack on disk."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
MANIFEST_SCHEMA = json.loads((SCHEMA_DIR / "rulepack-manifest.schema.json").read_text())
RULE_SCHEMA = json.loads((SCHEMA_DIR / "rule-file.schema.json").read_text())


def _manifests() -> list[Path]:
    return sorted(ROOT.glob("domain/*/1.0.0/manifest.yaml")) + sorted(
        ROOT.glob("tariffs/*/1.0.0/manifest.yaml")
    )


def _rule_files() -> list[Path]:
    return sorted(ROOT.glob("domain/*/1.0.0/rules/*.yaml")) + sorted(
        ROOT.glob("tariffs/*/1.0.0/rules/*.yaml")
    )


@pytest.mark.skipif(jsonschema is None, reason="jsonschema not installed")
@pytest.mark.parametrize("path", _manifests(), ids=lambda p: str(p.relative_to(ROOT)))
def test_manifest_valid(path: Path) -> None:
    data = yaml.safe_load(path.read_text())
    jsonschema.validate(data, MANIFEST_SCHEMA)


@pytest.mark.skipif(jsonschema is None, reason="jsonschema not installed")
@pytest.mark.parametrize("path", _rule_files(), ids=lambda p: str(p.relative_to(ROOT)))
def test_rule_file_valid(path: Path) -> None:
    data = yaml.safe_load(path.read_text())
    jsonschema.validate(data, RULE_SCHEMA)


@pytest.mark.skipif(jsonschema is None, reason="jsonschema not installed")
def test_at_least_nine_packs() -> None:
    assert len(_manifests()) >= 9
