"""Load semver rulepack manifest from disk."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def load_rulepack(path: Path | str) -> dict[str, Any]:
    """Load and validate a rulepack manifest (requires semver version field)."""
    manifest = json.loads(Path(path).read_text())
    version = manifest.get("version")
    if not version or not _SEMVER.match(version):
        raise ValueError(f"rulepack manifest missing valid semver version: {version!r}")
    return manifest
