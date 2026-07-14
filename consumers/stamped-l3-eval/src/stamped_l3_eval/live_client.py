"""Poll stamped-l3-core lab export for live detections."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def fetch_live_snapshot(
    url: str | None = None,
    token: str | None = None,
    timeout: float = 5.0,
) -> dict[str, Any]:
    """GET RunArtifact or {detections, timeline} snapshot from CORE_LAB_URL."""
    base = url or os.environ.get("CORE_LAB_URL")
    if not base:
        raise RuntimeError("CORE_LAB_URL not set")
    secret = token if token is not None else os.environ.get("CORE_LAB_TOKEN", "")
    endpoint = base.rstrip("/") + "/lab/export"
    req = urllib.request.Request(endpoint, headers={"Accept": "application/json"})
    if secret:
        req.add_header("Authorization", f"Bearer {secret}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"live attach failed: {exc}") from exc
