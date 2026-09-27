from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pymongo import ReturnDocument
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from ..db.session import get_db
from ..models.schemas.alert import AlertCreate, AlertResponse


router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=AlertResponse, status_code=201)
def create_alert(request: AlertCreate, db: Database = Depends(get_db)) -> AlertResponse:
    row = request.model_dump()
    row.update(
        status="OPEN",
        created_at=datetime.now(timezone.utc),
        resolved_at=None,
    )
    try:
        db["alerts"].insert_one(row)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="Alert already exists.") from exc
    return AlertResponse(**row)


@router.get("", response_model=list[AlertResponse])
def list_alerts(db: Database = Depends(get_db)) -> list[AlertResponse]:
    rows = db["alerts"].find().sort("created_at", -1)
    return [AlertResponse(**row) for row in rows]


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: str, db: Database = Depends(get_db)) -> AlertResponse:
    r = db["alerts"].find_one({"alert_id": alert_id})
    if r is None:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return AlertResponse(**r)


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: str, db: Database = Depends(get_db)) -> AlertResponse:
    r = db["alerts"].find_one_and_update(
        {"alert_id": alert_id},
        {"$set": {"status": "RESOLVED", "resolved_at": datetime.now(timezone.utc)}},
        return_document=ReturnDocument.AFTER,
    )
    if r is None:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return AlertResponse(**r)