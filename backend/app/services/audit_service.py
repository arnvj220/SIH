from __future__ import annotations

from typing import Any


class AuditService:
    """Collects structured audit events for application operations."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def record(
        self,
        event_type: str,
        *,
        context_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        event = {
            "event_type": event_type,
            "context_id": context_id,
            "details": details or {},
        }

        self._events.append(event)
        return event

    def list_events(self) -> list[dict[str, Any]]:
        return list(self._events)

    def clear(self) -> None:
        self._events.clear()