"""Shared suppression service — startup windows and maintenance calendar."""

from __future__ import annotations


def _parse_window(window: str) -> tuple[str, str]:
    start, _, end = window.partition("/")
    return start, end


class SuppressionService:
    """Check contextual suppressions before finding emission."""

    def __init__(
        self,
        startup_windows: dict[str, list[tuple[str, str]]] | None = None,
        maintenance_windows: list[tuple[str, str]] | None = None,
    ) -> None:
        self.startup_windows = startup_windows or {}
        self.maintenance_windows = maintenance_windows or []

    def should_suppress(self, window: str, assets: list[str]) -> tuple[bool, list[str]]:
        checked: list[str] = []
        win_start, win_end = _parse_window(window)

        for asset in assets:
            for start, end in self.startup_windows.get(asset, []):
                checked.append("startup_window")
                if start <= win_end and end >= win_start:
                    return True, checked

        for start, end in self.maintenance_windows:
            checked.append("maintenance_calendar")
            if start <= win_end and end >= win_start:
                return True, checked

        return False, checked
