"""Hot-path scheduler — runs MD engine on each tick; logs every candidate to Lab (ADR-015)."""

from __future__ import annotations

from typing import Any

from stamped_l3_core.challenger.attribution_shadow import emit_attribution_shadows
from stamped_l3_core.clients.l2 import L2QueryClient
from stamped_l3_core.engines.md import detect_md_overlap
from stamped_l3_core.lab_export import get_lab_log
from stamped_l3_core.outbox import TransactionalOutbox
from stamped_l3_core.suppression import SuppressionService


def run_hot_path(
    l2_client: L2QueryClient,
    outbox: TransactionalOutbox,
    suppression: SuppressionService,
    *,
    org_id: str,
    plant_id: str,
    asset_id: str,
    from_ts: str,
    to_ts: str,
    md_config: dict[str, Any],
) -> list[dict[str, Any]]:
    """Fetch incomer kVA, run MD overlap engine, stage non-suppressed findings.

    Every candidate is logged to LabLog. Only emitted (delivery=l4) stage outbox.
    """
    lab = get_lab_log()
    lab.reset(window_id=f"{plant_id}:{from_ts}", plant_id=plant_id)
    lab.inputs = {
        "source": "hot_path",
        "fixture_ref": f"{org_id}/{plant_id}/{asset_id}",
    }

    measurements = l2_client.get_measurements(
        org_id,
        plant_id,
        asset_id,
        "apparent_power_kva",
        from_ts,
        to_ts,
    )
    findings = detect_md_overlap(
        measurements,
        cmd_kva=md_config["cmd_kva"],
        baseline_band=tuple(md_config["baseline_band"]),
        md_rate_inr_per_kva=md_config.get("md_rate_inr_per_kva", 350.0),
        engine_version=md_config.get("engine_version", "1.0.0"),
        rulepack_version=md_config.get("rulepack_version", "1.0.0"),
    )

    for finding in findings:
        suppressed, checked = suppression.should_suppress(
            finding.evidence["window"], finding.assets
        )
        payload = finding.to_dict()
        payload["suppressions_checked"] = checked
        det_id = f"det-{finding.finding_id}"
        ref = finding.rule_or_model_ref
        if suppressed:
            lab.add_detection(
                detection_id=det_id,
                detector_kind="engine",
                rule_or_model_ref=ref,
                category=finding.category,
                status="suppressed",
                finding=None,
                suppressions_checked=checked,
                scores={"actual_value": finding.evidence.get("actual_value")},
                logs=[f"suppressed: {', '.join(checked) or 'gate'}"],
            )
            continue

        lab.add_detection(
            detection_id=det_id,
            detector_kind="engine",
            rule_or_model_ref=ref,
            category=finding.category,
            status="emitted",
            finding=payload,
            suppressions_checked=checked,
            scores={"actual_value": finding.evidence.get("actual_value")},
            logs=["emit outbox"],
        )
        outbox.stage(payload)

    # Optional attribution scoreboard from config (tests / warm path)
    attr_candidates = md_config.get("attribution_candidates") or []
    if attr_candidates:
        # Of-record list is score-sorted; top-1 may emit + outbox when not suppressed.
        ranked = sorted(attr_candidates, key=lambda c: c.get("score") or 0, reverse=True)
        primary = ranked[0]
        attr_payload = {
            "schema_version": "1.1.0",
            "finding_id": f"f-attr-{primary.get('asset', 'x')}",
            "org_id": org_id,
            "plant_id": plant_id,
            "category": "md_overlap",
            "waste_category": 1,
            "assets": [primary.get("asset")],
            "evidence": {
                "metric": "co_start_score",
                "baseline_value": 0,
                "actual_value": primary.get("score") or 0,
                "window": f"{from_ts}/{to_ts}",
            },
            "confidence": 0.6,
            "estimated_monthly_kwh": 0.0,
            "estimated_monthly_inr": 0.0,
            "urgency": "medium",
            "engine": "rules.costart_window",
            "engine_version": "1.0.0",
            "rule_or_model_ref": "rulepack://attribution/1.0.0#costart_window",
            "ops_clearance": {
                "measurement_boundary": primary.get("asset") or "incomer_1",
                "related_tag_ids": [f"{primary.get('asset', 'incomer_1')}/apparent_power_kva"],
                "clearance_predicate": {
                    "metric": "co_start_score",
                    "comparator": "lt",
                    "threshold": 0.3,
                    "relative_to": "absolute",
                },
                "expected_post_fix_signal": "Co-start score below 0.3 for stabilize window",
                "stabilize_window": "PT30M",
                "reopen_if_regresses": {"enabled": True},
            },
            "alarm_hint": {"severity": "warning", "category_code": "md.coincidence"},
        }
        lab.add_detection(
            detection_id=f"attr-rank-1-{primary.get('asset', 'x')}",
            detector_kind="rule",
            rule_or_model_ref="rulepack://attribution/1.0.0#costart_window",
            category="md_overlap",
            status="emitted",
            finding=attr_payload,
            scores={**primary, "rank": 1},
            logs=["of-record co-start top-1"],
        )
        outbox.stage(attr_payload)
        for i, cand in enumerate(ranked[1:], start=2):
            lab.add_detection(
                detection_id=f"attr-rank-{i}-{cand.get('asset', 'x')}",
                detector_kind="rule",
                rule_or_model_ref="rulepack://attribution/1.0.0#costart_window",
                category="md_overlap",
                status="hypothesis",
                scores={**cand, "rank": i},
                logs=["runner-up lab_only"],
            )
        for shadow in emit_attribution_shadows(ranked):
            lab.add_detection(**shadow)

    return outbox.publish()
