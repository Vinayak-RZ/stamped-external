from pathlib import Path

from stamped_l3_core.clients.l2 import FixtureL2Client
from stamped_l3_core.outbox import TransactionalOutbox
from stamped_l3_core.rulepack_loader import load_rulepack
from stamped_l3_core.scheduler import run_hot_path
from stamped_l3_core.suppression import SuppressionService

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def test_md_golden_fixture_emits_finding():
    rulepack = load_rulepack(FIXTURES / "incomer_rulepack.json")
    md_cfg = rulepack["engines"]["md_overlap"]
    md_cfg["rulepack_version"] = rulepack["version"]

    client = FixtureL2Client(FIXTURES)
    outbox = TransactionalOutbox()
    suppression = SuppressionService()

    published = run_hot_path(
        client,
        outbox,
        suppression,
        org_id="org_acme",
        plant_id="plant_ghaziabad_1",
        asset_id="incomer_1",
        from_ts="2026-06-15T00:00:00Z",
        to_ts="2026-06-15T23:59:59Z",
        md_config=md_cfg,
    )

    assert len(published) == 1
    finding = published[0]
    assert finding["category"] == "md_overlap"
    assert finding["assets"] == ["incomer_1"]
    assert finding["evidence"]["actual_value"] == 945.0
    assert finding["dedupe_key"].startswith("sha256:")
    assert finding["engine"] == "rules.md_overlap"
