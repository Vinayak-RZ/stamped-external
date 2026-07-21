"""L3 Finding domain model aligned with contracts/schemas/finding.json v1.1.0."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any


def compute_dedupe_key(category: str, assets: list[str], window: str) -> str:
    """Stable dedupe key: sha256(category + sorted assets + window)."""
    payload = f"{category}|{'|'.join(sorted(assets))}|{window}"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return f"sha256:{digest}"


_REOPEN_INVERT = {
    "lt": "gte",
    "lte": "gt",
    "gt": "lte",
    "gte": "lt",
    "eq": "eq",
    "in_band": "out_of_band",
    "out_of_band": "in_band",
}


def default_ops_clearance(
    *,
    asset_id: str,
    metric: str,
    tag_id: str,
    band: list[float] | None = None,
    threshold: float | None = None,
    comparator: str = "in_band",
    stabilize_window: str = "PT30M",
    expected: str = "Metric within clearance band after corrective action",
) -> dict[str, Any]:
    """Minimal ops_clearance block so L5 can poll L2 tags (Finding 1.1.0)."""
    predicate: dict[str, Any] = {
        "metric": metric,
        "comparator": comparator,
        "relative_to": "absolute",
    }
    if band is not None:
        predicate["band_ref"] = band
    if threshold is not None:
        predicate["threshold"] = threshold
    reopen: dict[str, Any] = {
        "metric": metric,
        "comparator": _REOPEN_INVERT.get(comparator, "gt"),
        "relative_to": "absolute",
    }
    if band is not None:
        reopen["band_ref"] = band
    elif threshold is not None:
        reopen["threshold"] = threshold
    return {
        "measurement_boundary": asset_id,
        "related_tag_ids": [tag_id],
        "clearance_predicate": predicate,
        "expected_post_fix_signal": expected,
        "stabilize_window": stabilize_window,
        "reopen_if_regresses": {
            "enabled": True,
            "predicate": reopen,
            "grace_window": "PT10M",
        },
    }


@dataclass
class Finding:
    schema_version: str
    finding_id: str
    org_id: str
    plant_id: str
    category: str
    waste_category: int
    assets: list[str]
    evidence: dict[str, Any]
    confidence: float
    estimated_monthly_kwh: float
    estimated_monthly_inr: float
    urgency: str
    engine: str
    engine_version: str
    rule_or_model_ref: str
    ops_clearance: dict[str, Any]
    dedupe_key: str = field(default="")
    inr_decomposition: dict[str, str] | None = None
    suppressions_checked: list[str] | None = None
    alarm_hint: dict[str, str] | None = None

    def __post_init__(self) -> None:
        if not self.dedupe_key:
            self.dedupe_key = compute_dedupe_key(
                self.category, self.assets, self.evidence["window"]
            )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if data["inr_decomposition"] is None:
            del data["inr_decomposition"]
        if data["suppressions_checked"] is None:
            del data["suppressions_checked"]
        if data["alarm_hint"] is None:
            del data["alarm_hint"]
        return data
