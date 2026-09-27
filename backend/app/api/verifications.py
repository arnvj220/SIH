"""GET /api/verifications - list verification events."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pymongo.database import Database

from ..db.session import get_db

router = APIRouter(prefix="/verifications", tags=["verifications"])


@router.get("")
def list_verifications(db: Database = Depends(get_db)) -> list[dict]:
    rows = db["verifications"].find().sort("created_at", -1).limit(500)
    return [
        {
            "verification_id": row.get("verification_id"),
            "signature_id": row.get("signature_id"),
            "verifier_id": row.get("verifier_id"),
            "decision": row.get("decision"),
            "detected": row.get("detected"),
            "error_rate": row.get("error_rate"),
            "created_at": row.get("created_at"),
        }
        for row in rows
    ]
