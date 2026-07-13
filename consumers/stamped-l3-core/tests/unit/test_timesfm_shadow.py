"""TimesFM shadow stub tests."""

from stamped_l3_core.challenger.timesfm_shadow import PROMOTION_ALLOWED, SHADOW_ONLY, is_available


def test_shadow_only_flags():
    assert SHADOW_ONLY is True
    assert PROMOTION_ALLOWED is False


def test_timesfm_not_installed_by_default():
    assert is_available() is False
