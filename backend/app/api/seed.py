"""
Demo seeding.

POST /api/seed/demo  - creates signatures, verifications (legit + malicious),
                        and events so the frontend has data to show.
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pymongo.database import Database

from ..db.session import get_db

router = APIRouter(prefix="/seed", tags=["seed"])

def _serialize_evidence(ev) -> dict:
    """Convert QuantumEvidence to a JSON-safe dict."""
    if ev is None:
        return {}

    def convert(v):
        # numpy array -> list, recursively convert elements
        if hasattr(v, "tolist"):
            return convert(v.tolist())
        # complex -> [real, imag]
        if isinstance(v, complex):
            return [v.real, v.imag]
        # containers -> recurse
        if isinstance(v, dict):
            return {str(k): convert(x) for k, x in v.items()}
        if isinstance(v, (list, tuple)):
            return [convert(x) for x in v]
        # primitives -> as-is
        if isinstance(v, (str, int, float, bool)) or v is None:
            return v
        # numpy scalars (np.float64, np.int64, etc.) -> Python scalars
        if hasattr(v, "item"):
            return convert(v.item())
        # anything else -> stringify
        return str(v)

    if hasattr(ev, "__dict__"):
        return {k: convert(v) for k, v in vars(ev).items()}

    # Frozen dataclass without __dict__ (slots) — use dataclasses.fields
    import dataclasses
    if dataclasses.is_dataclass(ev):
        return {f.name: convert(getattr(ev, f.name)) for f in dataclasses.fields(ev)}

    return {"repr": str(ev)}

def _insert_signature(db: Database, sig) -> None:
    """Persist a signature document."""
    db["signatures"].insert_one(
        {
            "signature_id": sig.signature_id,
            "signer_id": sig.signer_id,
            "message_id": sig.message_id,
            "message_digest": sig.message_digest,
            "protocol_version": sig.protocol_version,
            "session_id": sig.session_id,
            "quantum_evidence": _serialize_evidence(sig.quantum_evidence),
            "metadata_json": {},
            "created_at": datetime.now(timezone.utc),
        }
    )
    


def _short(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _digest(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


@router.post("/demo")
def seed_demo(db: Database = Depends(get_db)) -> dict:
    """
    Populate signatures table + verification events + alerts via
    the real endpoints' persistence code paths.

    Idempotent-ish: adds new rows each call.
    """
    from ..services.signature_service import SignatureRequest, SignatureService
    from ..services.verification_service import VerificationService
    from ..services.detection_service import DetectionService
    from ..services.alert_service import persist_verification_and_alerts
    from ..quantum.states.pauli_states import plus_state

    sig_svc = SignatureService()
    ver_svc = VerificationService()
    det_svc = DetectionService()

    created_signatures: list[str] = []
    created_alerts: list[str] = []
    verification_count = 0

    # 3 legit signatures + verifications
    for i in range(3):
        sid = _short("sig")
        try:
            sig = sig_svc.create_signature(
                SignatureRequest(
                    signature_id=sid,
                    signer_id="usr_alice",
                    message_id=_short("msg"),
                    session_id=_short("sess"),
                    message=f"demo message {i}",
                    input_state=plus_state(),
                    seed=1000 + i,
                )
            )
            created_signatures.append(sid)
            _insert_signature(db, sig)
            

            ctx = ver_svc.build_context(
                sig,
                verifier_id="ver_bob",
                message=f"demo message {i}",
                nonce=_short("nonce"),
            )
            outcome = det_svc.detect(ctx)
            verification_count += 1
            created_alerts += persist_verification_and_alerts(db, ctx, outcome)
        except Exception as exc:
            print(f"[seed] legit {i} failed: {exc}")

    # 2 malicious verifications (forgery + impersonation)
    malicious = [
        {"signer_id": "usr_mallory", "expected": "usr_alice"},
        {"signer_id": "usr_alice", "expected": "usr_alice", "tamper_digest": True},
    ]
    for i, spec in enumerate(malicious):
        sid = _short("sig")
        try:
            sig = sig_svc.create_signature(
                SignatureRequest(
                    signature_id=sid,
                    signer_id=spec["signer_id"],
                    message_id=_short("msg"),
                    session_id=_short("sess"),
                    message=f"malicious {i}",
                    input_state=plus_state(),
                    seed=2000 + i,
                )
            )
            created_signatures.append(sid)
            _insert_signature(db, sig)
            

            ctx = ver_svc.build_context(
                sig,
                verifier_id="ver_bob",
                message=f"malicious {i}",
                expected_signer_id=spec["expected"],
                nonce=_short("nonce"),
            )
            if spec.get("tamper_digest"):
                ctx = ctx.clone(message_digest="deadbeef" * 8)
            outcome = det_svc.detect(ctx)
            verification_count += 1
            created_alerts += persist_verification_and_alerts(db, ctx, outcome)
        except Exception as exc:
            print(f"[seed] malicious {i} failed: {exc}")

    return {
        "signatures_created": len(created_signatures),
        "verifications_created": verification_count,
        "alerts_created": len(created_alerts),
    }