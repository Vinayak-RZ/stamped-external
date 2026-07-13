"""Transactional outbox — in-memory store for Finding dicts."""

from __future__ import annotations

from typing import Any


class TransactionalOutbox:
    """Stage findings atomically, then publish to downstream consumers."""

    def __init__(self) -> None:
        self._pending: list[dict[str, Any]] = []
        self._published: list[dict[str, Any]] = []

    def stage(self, finding: dict[str, Any]) -> None:
        self._pending.append(finding)

    def publish(self) -> list[dict[str, Any]]:
        batch = list(self._pending)
        self._published.extend(batch)
        self._pending.clear()
        return batch

    @property
    def pending(self) -> list[dict[str, Any]]:
        return list(self._pending)

    @property
    def published(self) -> list[dict[str, Any]]:
        return list(self._published)
