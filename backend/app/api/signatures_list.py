"""GET /api/signatures - list signatures."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from ..db.session import get_db

router = APIRouter(prefix="/signatures", tags=["signatures"])


@router.get("")
def list_signatures(db: Database = Depends(get_db)) -> list[dict]:
    rows = db["signatures"].find().sort("created_at", -1).limit(500)
    return [
        {
            "signature_id": row.get("signature_id"),
            "signer_id": row.get("signer_id"),
            "message_id": row.get("message_id"),
            "session_id": row.get("session_id"),
            "protocol_version": row.get("protocol_version"),
            "created_at": row.get("created_at"),
        }
        for row in rows
    ]


@router.get("/{signature_id}")
def get_signature(signature_id: str, db: Database = Depends(get_db)) -> dict:
    row = db["signatures"].find_one(
        {"signature_id": signature_id},
        {"_id": 0},
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Signature not found.")
    return {
        "signature_id": row.get("signature_id"),
        "signer_id": row.get("signer_id"),
        "message_id": row.get("message_id"),
        "message_digest": row.get("message_digest"),
        "session_id": row.get("session_id"),
        "protocol_version": row.get("protocol_version"),
        "created_at": row.get("created_at"),
        "quantum_evidence": row.get("quantum_evidence", {}),
    }
