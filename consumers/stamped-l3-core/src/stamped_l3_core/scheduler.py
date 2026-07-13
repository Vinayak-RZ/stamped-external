"""Hot-path scheduler — runs MD engine on each tick."""

from __future__ import annotations

from typing import Any

from stamped_l3_core.clients.l2 import L2QueryClient
from stamped_l3_core.engines.md import detect_md_overlap
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
    """Fetch incomer kVA, run MD overlap engine, stage non-suppressed findings."""
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
        if suppressed:
            continue
        payload = finding.to_dict()
        payload["suppressions_checked"] = checked
        outbox.stage(payload)

    return outbox.publish()
