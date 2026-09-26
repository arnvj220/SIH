"""GET /api/signatures - list signatures."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.models.signature import SignatureModel
from ..db.session import get_db

router = APIRouter(prefix="/signatures", tags=["signatures"])


@router.get("")
def list_signatures(db: Session = Depends(get_db)) -> list[dict]:
    rows = (
        db.query(SignatureModel)
        .order_by(SignatureModel.created_at.desc())
        .limit(500)
        .all()
    )
    return [
        {
            "signature_id": getattr(r, "signature_id", None) or getattr(r, "id", None),
            "signer_id": getattr(r, "signer_id", None),
            "message_id": getattr(r, "message_id", None),
            "session_id": getattr(r, "session_id", None),
            "protocol_version": getattr(r, "protocol_version", None),
            "created_at": getattr(r, "created_at", None),
        }
        for r in rows
    ]
