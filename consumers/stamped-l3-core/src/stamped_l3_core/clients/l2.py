"""L2 query client protocol and fixture-backed implementation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol


class L2QueryClient(Protocol):
    def get_measurements(
        self,
        org_id: str,
        plant_id: str,
        asset_id: str,
        metric: str,
        from_ts: str,
        to_ts: str,
    ) -> dict[str, Any]:
        """Return L2 measurements response (see handoff/stamped-l2-query-api-sketch.md)."""
        ...


class FixtureL2Client:
    """Read-only L2 client backed by JSON fixture files."""

    def __init__(self, fixtures_dir: Path | str) -> None:
        self._fixtures: dict[str, dict[str, Any]] = {}
        for path in Path(fixtures_dir).glob("*.json"):
            data = json.loads(path.read_text())
            if "asset_id" in data and "points" in data:
                self._fixtures[data["asset_id"]] = data

    def get_measurements(
        self,
        org_id: str,
        plant_id: str,
        asset_id: str,
        metric: str,
        from_ts: str,
        to_ts: str,
    ) -> dict[str, Any]:
        if asset_id not in self._fixtures:
            raise KeyError(f"No fixture for asset_id={asset_id!r}")
        resp = dict(self._fixtures[asset_id])
        resp["org_id"] = org_id
        resp["plant_id"] = plant_id
        resp["metric"] = metric
        resp["points"] = [
            p for p in resp["points"] if from_ts <= p["ts"] <= to_ts
        ]
        return resp
