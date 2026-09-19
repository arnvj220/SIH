from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..models.schemas.alert import AlertCreate, AlertResponse


router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
)


_alerts: dict[str, AlertResponse] = {}


@router.post(
    "",
    response_model=AlertResponse,
    status_code=201,
)
def create_alert(request: AlertCreate) -> AlertResponse:
    if request.alert_id in _alerts:
        raise HTTPException(
            status_code=409,
            detail="Alert already exists.",
        )

    alert = AlertResponse(
        **request.model_dump(),
        status="open",
        created_at=datetime.now(timezone.utc),
    )

    _alerts[request.alert_id] = alert

    return alert


@router.get(
    "",
    response_model=list[AlertResponse],
)
def list_alerts() -> list[AlertResponse]:
    return list(_alerts.values())


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
)
def get_alert(alert_id: str) -> AlertResponse:
    alert = _alerts.get(alert_id)

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found.",
        )

    return alert


@router.post(
    "/{alert_id}/resolve",
    response_model=AlertResponse,
)
def resolve_alert(alert_id: str) -> AlertResponse:
    alert = _alerts.get(alert_id)

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found.",
        )

    resolved = alert.model_copy(
        update={
            "status": "resolved",
            "resolved_at": datetime.now(timezone.utc),
        }
    )

    _alerts[alert_id] = resolved

    return resolved