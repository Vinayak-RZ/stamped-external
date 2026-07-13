"""L3 Finding domain model aligned with contracts/schemas/finding.json."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any


def compute_dedupe_key(category: str, assets: list[str], window: str) -> str:
    """Stable dedupe key: sha256(category + sorted assets + window)."""
    payload = f"{category}|{'|'.join(sorted(assets))}|{window}"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return f"sha256:{digest}"


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
    dedupe_key: str = field(default="")
    inr_decomposition: dict[str, str] | None = None
    suppressions_checked: list[str] | None = None

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
        return data
