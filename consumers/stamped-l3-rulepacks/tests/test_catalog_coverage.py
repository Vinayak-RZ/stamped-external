"""Catalog completeness vs Finding.category + catalog_index."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INDEX = json.loads((ROOT / "schemas" / "catalog_index.json").read_text())
FINDING_SCHEMA = Path("/workspace/contracts/schemas/finding.json")


def test_every_finding_category_mapped() -> None:
    finding = json.loads(FINDING_SCHEMA.read_text())
    cats = set(finding["properties"]["category"]["enum"])
    covered = set(INDEX["finding_category_coverage"].keys())
    assert cats <= covered, f"missing categories: {cats - covered}"
    for cat in cats:
        assert INDEX["finding_category_coverage"][cat], f"no rules for {cat}"


def test_every_index_rule_on_disk() -> None:
    for category, refs in INDEX["finding_category_coverage"].items():
        for ref in refs:
            assert ref.startswith("rulepack://"), ref
            body = ref.removeprefix("rulepack://")
            loc, rule_id = body.rsplit("#", 1)
            pack, ver = loc.split("/", 1)
            path = ROOT / "domain" / pack / ver / "rules" / f"{rule_id}.yaml"
            assert path.is_file(), f"missing {path} for {category}"


def test_every_vertical_overlay_exists() -> None:
    for name in INDEX["verticals"]:
        path = ROOT / "verticals" / name / "params.yaml"
        assert path.is_file(), path


def test_rule_count_matches_disk() -> None:
    on_disk = len(list(ROOT.glob("domain/*/1.0.0/rules/*.yaml")))
    assert on_disk == INDEX["rule_count"]


def test_manifest_rules_exist() -> None:
    for man in ROOT.glob("domain/*/1.0.0/manifest.yaml"):
        data = yaml.safe_load(man.read_text())
        for entry in data["rules"]:
            path = man.parent / entry["file"]
            assert path.is_file(), f"{man}: missing {entry['file']}"
