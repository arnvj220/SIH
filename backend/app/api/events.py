from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..services.audit_service import AuditService


router = APIRouter(
    prefix="/events",
    tags=["events"],
)


service = AuditService()


class EventCreate(BaseModel):
    event_type: str = Field(
        min_length=1,
        max_length=128,
    )

    context_id: str | None = Field(
        default=None,
        max_length=128,
    )

    details: dict[str, Any] = Field(
        default_factory=dict,
    )


class EventResponse(BaseModel):
    event_type: str
    context_id: str | None
    details: dict[str, Any]


@router.post(
    "",
    response_model=EventResponse,
    status_code=201,
)
def create_event(request: EventCreate) -> EventResponse:
    event = service.record(
        request.event_type,
        context_id=request.context_id,
        details=request.details,
    )

    return EventResponse(**event)


@router.get(
    "",
    response_model=list[EventResponse],
)
def list_events() -> list[EventResponse]:
    return [
        EventResponse(**event)
        for event in service.list_events()
    ]


@router.delete(
    "",
    status_code=204,
)
def clear_events() -> None:
    service.clear()