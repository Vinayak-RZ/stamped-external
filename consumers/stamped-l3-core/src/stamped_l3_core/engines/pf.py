"""PF slab breach engine stub — deterministic threshold check."""

from __future__ import annotations

from typing import Any

from stamped_l3_core.models.finding import Finding


def detect_pf_slab_breach(
    measurements: dict[str, Any],
    *,
    pf_threshold: float = 0.90,
    engine_version: str = "1.0.0",
    rulepack_version: str = "1.0.0",
) -> list[Finding]:
    """Emit pf_slab_breach when power factor stays below the tariff slab."""
    points = measurements.get("points", [])
    if not points:
        return []

    org_id = measurements["org_id"]
    plant_id = measurements["plant_id"]
    asset_id = measurements["asset_id"]

    below = [(p["ts"], float(p["value"])) for p in points if float(p["value"]) < pf_threshold]
    if len(below) < 2:
        return []

    worst_ts, worst_pf = min(below, key=lambda item: item[1])
    window = f"{below[0][0]}/{below[-1][0]}"

    return [
        Finding(
            schema_version="1.0.0",
            finding_id=f"f-pf-{worst_ts.replace(':', '').replace('-', '')[:15]}",
            org_id=org_id,
            plant_id=plant_id,
            category="pf_slab_breach",
            waste_category=1,
            assets=[asset_id],
            evidence={
                "metric": "power_factor",
                "baseline_value": pf_threshold,
                "actual_value": worst_pf,
                "window": window,
                "supporting_tags": [f"{asset_id}/power_factor"],
                "rule_version": rulepack_version,
            },
            confidence=0.75,
            estimated_monthly_kwh=0.0,
            estimated_monthly_inr=0.0,
            urgency="medium",
            engine="rules.pf_slab",
            engine_version=engine_version,
            rule_or_model_ref=f"rulepack://incomer/{rulepack_version}#pf_slab_breach",
        )
    ]
