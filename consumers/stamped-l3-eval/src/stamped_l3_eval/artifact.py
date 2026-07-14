"""Load and validate RunArtifact v1 JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "run-artifact.v1.json"
GOLDEN_DIR = ROOT / "artifacts" / "golden"


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_artifact(path: Path | str) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_artifact(data)
    return data


def validate_artifact(data: dict[str, Any]) -> None:
    if jsonschema is None:
        raise RuntimeError("jsonschema required: pip install jsonschema")
    jsonschema.validate(data, load_schema())


def list_golden_artifacts() -> list[Path]:
    return sorted(GOLDEN_DIR.glob("run_*.json"))


def artifact_for_window(window_id: str) -> Path | None:
    candidate = GOLDEN_DIR / f"run_{window_id}.json"
    return candidate if candidate.is_file() else None
