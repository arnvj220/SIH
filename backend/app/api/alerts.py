from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.models.alert import AlertModel
from ..db.session import get_db
from ..models.schemas.alert import AlertCreate, AlertResponse


router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=AlertResponse, status_code=201)
def create_alert(request: AlertCreate, db: Session = Depends(get_db)) -> AlertResponse:
    if db.query(AlertModel).filter_by(alert_id=request.alert_id).first():
        raise HTTPException(status_code=409, detail="Alert already exists.")

    row = AlertModel(
        alert_id=request.alert_id,
        alert_type=request.alert_type,
        severity=request.severity,
        status="OPEN",
        title=request.title,
        description=request.description,
        verification_id=request.verification_id,
        attack_id=request.attack_id,
        evidence=request.evidence,
        created_at=datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return AlertResponse(
        alert_id=row.alert_id,
        alert_type=row.alert_type,
        severity=row.severity,
        title=row.title,
        description=row.description,
        verification_id=row.verification_id,
        attack_id=row.attack_id,
        evidence=row.evidence or [],
        status=row.status,
        created_at=row.created_at,
        resolved_at=row.resolved_at,
    )


@router.get("", response_model=list[AlertResponse])
def list_alerts(db: Session = Depends(get_db)) -> list[AlertResponse]:
    rows = db.query(AlertModel).order_by(AlertModel.created_at.desc()).all()
    return [
        AlertResponse(
            alert_id=r.alert_id,
            alert_type=r.alert_type,
            severity=r.severity,
            title=r.title,
            description=r.description,
            verification_id=r.verification_id,
            attack_id=r.attack_id,
            evidence=r.evidence or [],
            status=r.status,
            created_at=r.created_at,
            resolved_at=r.resolved_at,
        )
        for r in rows
    ]


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: str, db: Session = Depends(get_db)) -> AlertResponse:
    r = db.query(AlertModel).filter_by(alert_id=alert_id).first()
    if r is None:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return AlertResponse(
        alert_id=r.alert_id,
        alert_type=r.alert_type,
        severity=r.severity,
        title=r.title,
        description=r.description,
        verification_id=r.verification_id,
        attack_id=r.attack_id,
        evidence=r.evidence or [],
        status=r.status,
        created_at=r.created_at,
        resolved_at=r.resolved_at,
    )


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: str, db: Session = Depends(get_db)) -> AlertResponse:
    r = db.query(AlertModel).filter_by(alert_id=alert_id).first()
    if r is None:
        raise HTTPException(status_code=404, detail="Alert not found.")
    r.status = "RESOLVED"
    r.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(r)
    return AlertResponse(
        alert_id=r.alert_id,
        alert_type=r.alert_type,
        severity=r.severity,
        title=r.title,
        description=r.description,
        verification_id=r.verification_id,
        attack_id=r.attack_id,
        evidence=r.evidence or [],
        status=r.status,
        created_at=r.created_at,
        resolved_at=r.resolved_at,
    )