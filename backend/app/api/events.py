from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db.models.event import EventModel
from ..db.session import get_db


router = APIRouter(prefix="/events", tags=["events"])


class EventCreate(BaseModel):
    event_type: str = Field(min_length=1, max_length=128)
    context_id: str | None = Field(default=None, max_length=128)
    details: dict[str, Any] = Field(default_factory=dict)


class EventResponse(BaseModel):
    event_id: str
    event_type: str
    context_id: str | None
    details: dict[str, Any]
    created_at: datetime


@router.post("", response_model=EventResponse, status_code=201)
def create_event(request: EventCreate, db: Session = Depends(get_db)) -> EventResponse:
    row = EventModel(
        event_id=f"evt_{uuid.uuid4().hex[:12]}",
        event_type=request.event_type,
        entity_type="manual",
        entity_id=request.context_id,
        severity="INFO",
        payload=request.details,
        created_at=datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return EventResponse(
        event_id=row.event_id,
        event_type=row.event_type,
        context_id=row.entity_id,
        details=row.payload,
        created_at=row.created_at,
    )


@router.get("", response_model=list[EventResponse])
def list_events(db: Session = Depends(get_db)) -> list[EventResponse]:
    rows = db.query(EventModel).order_by(EventModel.created_at.desc()).limit(500).all()
    return [
        EventResponse(
            event_id=r.event_id,
            event_type=r.event_type,
            context_id=r.entity_id,
            details=r.payload,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.delete("", status_code=204)
def clear_events(db: Session = Depends(get_db)) -> None:
    db.query(EventModel).delete()
    db.commit()