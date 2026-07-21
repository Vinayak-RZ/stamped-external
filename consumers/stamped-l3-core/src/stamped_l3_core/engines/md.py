"""Deterministic MD overlap detection from kVA measurements."""

from __future__ import annotations

from typing import Any

from stamped_l3_core.models.finding import Finding, default_ops_clearance


def detect_md_overlap(
    measurements: dict[str, Any],
    *,
    cmd_kva: float,
    baseline_band: tuple[float, float],
    md_rate_inr_per_kva: float = 350.0,
    engine_version: str = "1.0.0",
    rulepack_version: str = "1.0.0",
) -> list[Finding]:
    """Flag windows where apparent_power_kva exceeds the baseline upper band."""
    points = measurements.get("points", [])
    if not points:
        return []

    upper = baseline_band[1]
    org_id = measurements["org_id"]
    plant_id = measurements["plant_id"]
    asset_id = measurements["asset_id"]

    exceedances = [(p["ts"], float(p["value"])) for p in points if float(p["value"]) > upper]
    if not exceedances:
        return []

    peak_ts, peak_kva = max(exceedances, key=lambda item: item[1])
    window_start = exceedances[0][0]
    window_end = exceedances[-1][0]
    window = f"{window_start}/{window_end}"
    excess_kva = peak_kva - cmd_kva
    monthly_inr = max(0.0, excess_kva * md_rate_inr_per_kva)

    return [
        Finding(
            schema_version="1.1.0",
            finding_id=f"f-md-{peak_ts.replace(':', '').replace('-', '')[:15]}",
            org_id=org_id,
            plant_id=plant_id,
            category="md_overlap",
            waste_category=1,
            assets=[asset_id],
            evidence={
                "metric": "apparent_power_kva",
                "baseline_value": baseline_band[0],
                "actual_value": peak_kva,
                "window": window,
                "baseline_id": f"bl-{asset_id}-cmd",
                "baseline_band": list(baseline_band),
                "supporting_tags": [f"{asset_id}/apparent_power_kva"],
                "rule_version": rulepack_version,
            },
            confidence=0.88,
            estimated_monthly_kwh=0.0,
            estimated_monthly_inr=monthly_inr,
            inr_decomposition={
                "bill_line": "demand_charge",
                "rate_ref": f"cmd-{int(cmd_kva)}kva",
            },
            urgency="high" if peak_kva > cmd_kva else "medium",
            engine="rules.md_overlap",
            engine_version=engine_version,
            rule_or_model_ref=f"rulepack://incomer/{rulepack_version}#md_overlap",
            ops_clearance=default_ops_clearance(
                asset_id=asset_id,
                metric="apparent_power_kva",
                tag_id=f"{asset_id}/apparent_power_kva",
                band=list(baseline_band),
                comparator="in_band",
                expected="Incomer kVA within baseline band; no co-start spike",
            ),
            alarm_hint={"severity": "error", "category_code": "md.coincidence"},
        )
    ]
