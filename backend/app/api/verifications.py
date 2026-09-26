"""GET /api/verifications - list verification events."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.models.verification import VerificationModel
from ..db.session import get_db

router = APIRouter(prefix="/verifications", tags=["verifications"])


@router.get("")
def list_verifications(db: Session = Depends(get_db)) -> list[dict]:
    rows = (
        db.query(VerificationModel)
        .order_by(VerificationModel.created_at.desc())
        .limit(500)
        .all()
    )
    return [
        {
            "verification_id": getattr(r, "verification_id", None) or getattr(r, "id", None),
            "signature_id": getattr(r, "signature_id", None),
            "verifier_id": getattr(r, "verifier_id", None),
            "decision": getattr(r, "decision", None),
            "detected": getattr(r, "detected", None),
            "error_rate": getattr(r, "error_rate", None),
            "created_at": getattr(r, "created_at", None),
        }
        for r in rows
    ]
