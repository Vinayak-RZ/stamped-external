"""Deterministic Finding → Prescription mapping for template-fast-path categories."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

# ponytail: static template table — add categories only when build-order lists them
CATEGORY_TEMPLATE_ID: dict[str, str] = {
    "md_overlap": "md_overlap.stagger_costart.v1",
    "pf_slab_breach": "pf_slab.apfc_health.v1",
    "tod_exposure": "tod_exposure.shift_load.v1",
}

_TEMPLATES: dict[str, dict[str, str]] = {
    "md_overlap.stagger_costart.v1": {
        "what": "Stagger co-start loads on {assets} to reduce MD overlap during {window_label}.",
        "why": "Incomer MD spike {actual} vs {baseline} baseline — co-start pattern detected.",
        "who": "electrical_supervisor",
        "effort": "low_schedule_change",
        "when": "next_shift_start",
    },
    "pf_slab.apfc_health.v1": {
        "what": "Inspect APFC bank and capacitor steps on {assets}; correct PF to stay above slab threshold.",
        "why": "PF {actual} below contract slab — penalty exposure on {assets}.",
        "who": "electrical_supervisor",
        "effort": "medium_maintenance",
        "when": "within_7_days",
    },
    "tod_exposure.shift_load.v1": {
        "what": "Shift flexible loads on {assets} out of peak TOD window {window_label}.",
        "why": "Peak-window energy {actual} kWh vs {baseline} baseline — TOD surcharge exposure.",
        "who": "production_planner",
        "effort": "low_schedule_change",
        "when": "next_billing_cycle",
    },
}

# ponytail: flat grid factor; replace with plant-specific factor when available
_TCO2E_PER_KWH = 0.00074


def _fmt_assets(assets: list[str]) -> str:
    return ", ".join(assets)


def _window_label(window: str) -> str:
    if "/" in window:
        return window.split("/", 1)[0][:16]
    return window[:16]


def _render_fields(template_id: str, finding: dict[str, Any]) -> dict[str, str]:
    tpl = _TEMPLATES[template_id]
    evidence = finding["evidence"]
    ctx = {
        "assets": _fmt_assets(finding["assets"]),
        "baseline": evidence["baseline_value"],
        "actual": evidence["actual_value"],
        "window_label": _window_label(evidence["window"]),
    }
    return {key: value.format(**ctx) for key, value in tpl.items()}


def _impact_from_finding(finding: dict[str, Any]) -> dict[str, Any]:
    inr = float(finding["estimated_monthly_inr"])
    kwh = float(finding["estimated_monthly_kwh"])
    return {
        "inr_monthly": inr,
        "kwh_monthly": kwh,
        "tco2e_monthly": round(kwh * _TCO2E_PER_KWH, 2),
        "confidence_interval": [round(inr * 0.75), round(inr * 1.2)],
    }


def _evidence_refs(finding: dict[str, Any]) -> list[str]:
    evidence = finding["evidence"]
    refs = [
        f"tag:{finding['assets'][0]}/{evidence['metric']}?window={evidence['window']}",
    ]
    if baseline_id := evidence.get("baseline_id"):
        refs.append(f"baseline:{baseline_id}")
    rate_ref = (finding.get("inr_decomposition") or {}).get("rate_ref")
    if rate_ref:
        refs.append(f"tariff:{rate_ref}")
    return refs


def _prescription_dedupe_key(finding: dict[str, Any], template_id: str) -> str:
    payload = json.dumps(
        {
            "finding_id": finding["finding_id"],
            "template_id": template_id,
            "dedupe_key": finding["dedupe_key"],
        },
        sort_keys=True,
    )
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return f"sha256:{digest}"


def render_prescription(
    finding: dict[str, Any],
    *,
    prescription_id: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Map a Finding dict to a Prescription dict via approved templates."""
    category = finding["category"]
    if category not in CATEGORY_TEMPLATE_ID:
        raise ValueError(f"unsupported template-fast-path category: {category}")

    template_id = CATEGORY_TEMPLATE_ID[category]
    fields = _render_fields(template_id, finding)
    ts = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    rx_id = prescription_id or f"rx-{finding['finding_id'].removeprefix('f-')}"

    return {
        "schema_version": "1.0.0",
        "id": rx_id,
        "org_id": finding["org_id"],
        "plant_id": finding["plant_id"],
        "status": "open",
        "priority": 2 if finding.get("urgency") == "high" else 3,
        **fields,
        "template_id": template_id,
        "impact": _impact_from_finding(finding),
        "waste_category": finding["waste_category"],
        "finding_refs": [finding["finding_id"]],
        "evidence_refs": _evidence_refs(finding),
        "mv_plan": {
            "method": "option_c",
            "baseline_id": finding["evidence"].get("baseline_id", "baseline-default"),
            "measurement_boundary": "whole_plant_incomer",
            "verification_window": "2026-08-01/2026-09-01",
        },
        "provenance": {
            "agent_version": "l4-template-1.0.0",
            "lane": "template_fast_path",
            "rule_versions": [finding["rule_or_model_ref"]],
        },
        "first_recommended_at": ts,
        "implemented_at": None,
        "verified_at": None,
        "dedupe_key": _prescription_dedupe_key(finding, template_id),
    }
