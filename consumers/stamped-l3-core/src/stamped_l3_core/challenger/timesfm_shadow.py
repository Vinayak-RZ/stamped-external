"""TimesFM shadow challenger — optional P2 extra. Import-only stub until eval gates pass."""

SHADOW_ONLY = True
PROMOTION_ALLOWED = False


def is_available() -> bool:
    """ponytail: optional dep timesfm>=2.0.2 — not installed in P0."""
    try:
        import timesfm  # noqa: F401
        return True
    except ImportError:
        return False
