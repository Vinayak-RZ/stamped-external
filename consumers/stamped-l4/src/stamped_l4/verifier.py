"""Schema gate + numeric drift check for template-fast-path prescriptions."""

from __future__ import annotations

from typing import Any

REQUIRED_FIELDS: tuple[str, ...] = (
    "schema_version",
    "id",
    "org_id",
    "plant_id",
    "status",
    "priority",
    "what",
    "why",
    "who",
    "effort",
    "when",
    "impact",
    "waste_category",
    "finding_refs",
    "evidence_refs",
    "mv_plan",
    "dedupe_key",
)

IMPACT_FIELDS: tuple[str, ...] = (
    "inr_monthly",
    "kwh_monthly",
    "tco2e_monthly",
    "confidence_interval",
)

MV_PLAN_FIELDS: tuple[str, ...] = ("method", "baseline_id", "verification_window")

VALID_STATUS = {"open", "in_progress", "done", "deferred", "rejected", "blocked_incomplete"}


def _within_pct(actual: float, expected: float, tolerance_pct: float) -> bool:
    if expected == 0:
        return actual == 0
    return abs(actual - expected) / abs(expected) <= tolerance_pct


def check_required_fields(prescription: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in prescription:
            errors.append(f"missing required field: {field}")

    impact = prescription.get("impact")
    if isinstance(impact, dict):
        for field in IMPACT_FIELDS:
            if field not in impact:
                errors.append(f"missing impact.{field}")
    elif "impact" in prescription:
        errors.append("impact must be an object")

    mv_plan = prescription.get("mv_plan")
    if isinstance(mv_plan, dict):
        for field in MV_PLAN_FIELDS:
            if field not in mv_plan:
                errors.append(f"missing mv_plan.{field}")
    elif "mv_plan" in prescription:
        errors.append("mv_plan must be an object")

    status = prescription.get("status")
    if status is not None and status not in VALID_STATUS:
        errors.append(f"invalid status: {status}")

    finding_refs = prescription.get("finding_refs")
    if finding_refs is not None and (not isinstance(finding_refs, list) or not finding_refs):
        errors.append("finding_refs must be a non-empty list")

    evidence_refs = prescription.get("evidence_refs")
    if evidence_refs is not None and (not isinstance(evidence_refs, list) or not evidence_refs):
        errors.append("evidence_refs must be a non-empty list")

    dedupe_key = prescription.get("dedupe_key")
    if isinstance(dedupe_key, str) and not dedupe_key.startswith("sha256:"):
        errors.append("dedupe_key must start with sha256:")

    return errors


def check_numeric_alignment(
    prescription: dict[str, Any],
    finding: dict[str, Any],
    *,
    tolerance_pct: float = 0.01,
) -> list[str]:
    errors: list[str] = []
    impact = prescription.get("impact")
    if not isinstance(impact, dict):
        return ["impact must be an object for numeric verification"]

    pairs = (
        ("inr_monthly", "estimated_monthly_inr"),
        ("kwh_monthly", "estimated_monthly_kwh"),
    )
    for impact_field, finding_field in pairs:
        if impact_field not in impact or finding_field not in finding:
            continue
        actual = float(impact[impact_field])
        expected = float(finding[finding_field])
        if not _within_pct(actual, expected, tolerance_pct):
            errors.append(
                f"impact.{impact_field} {actual} not within {tolerance_pct:.0%} of "
                f"finding.{finding_field} {expected}"
            )

    return errors


def verify(
    prescription: dict[str, Any],
    finding: dict[str, Any],
    *,
    tolerance_pct: float = 0.01,
) -> tuple[bool, list[str]]:
    errors = check_required_fields(prescription) + check_numeric_alignment(
        prescription, finding, tolerance_pct=tolerance_pct
    )
    return (not errors, errors)
