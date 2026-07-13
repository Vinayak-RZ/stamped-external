from stamped_l3_core.suppression import SuppressionService


def test_startup_window_suppresses_overlapping_finding():
    svc = SuppressionService(
        startup_windows={
            "incomer_1": [("2026-06-15T06:00:00Z", "2026-06-15T06:45:00Z")]
        }
    )
    suppressed, checked = svc.should_suppress(
        "2026-06-15T06:30:00Z/2026-06-15T07:00:00Z",
        ["incomer_1"],
    )
    assert suppressed is True
    assert "startup_window" in checked


def test_maintenance_calendar_suppresses():
    svc = SuppressionService(
        maintenance_windows=[("2026-06-15T00:00:00Z", "2026-06-15T23:59:59Z")]
    )
    suppressed, checked = svc.should_suppress(
        "2026-06-15T06:30:00Z/2026-06-15T07:00:00Z",
        ["incomer_1"],
    )
    assert suppressed is True
    assert "maintenance_calendar" in checked


def test_no_suppression_outside_windows():
    svc = SuppressionService()
    suppressed, checked = svc.should_suppress(
        "2026-06-15T06:30:00Z/2026-06-15T07:00:00Z",
        ["incomer_1"],
    )
    assert suppressed is False
    assert checked == []
