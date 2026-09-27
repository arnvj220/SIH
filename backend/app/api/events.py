from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from pymongo.database import Database

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
def create_event(request: EventCreate, db: Database = Depends(get_db)) -> EventResponse:
    row = {
        "event_id": f"evt_{uuid.uuid4().hex[:12]}",
        "event_type": request.event_type,
        "entity_type": "manual",
        "entity_id": request.context_id,
        "severity": "INFO",
        "payload": request.details,
        "created_at": datetime.now(timezone.utc),
    }
    db["events"].insert_one(row)
    return EventResponse(
        event_id=row["event_id"],
        event_type=row["event_type"],
        context_id=row["entity_id"],
        details=row["payload"],
        created_at=row["created_at"],
    )


@router.get("", response_model=list[EventResponse])
def list_events(db: Database = Depends(get_db)) -> list[EventResponse]:
    rows = db["events"].find().sort("created_at", -1).limit(500)
    return [
        EventResponse(
            event_id=row["event_id"],
            event_type=row["event_type"],
            context_id=row.get("entity_id"),
            details=row.get("payload", {}),
            created_at=row["created_at"],
        )
        for row in rows
    ]


@router.delete("", status_code=204)
def clear_events(db: Database = Depends(get_db)) -> None:
    db["events"].delete_many({})