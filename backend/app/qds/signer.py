"""
QDS signer.

Generates a QDS signature by combining message context,
signer/session metadata, and the quantum teleportation
simulation.
"""

from __future__ import annotations

from ..quantum.states.state_utils import ComplexVector
from .protocol import PROTOCOL_VERSION, execute_protocol
from .signature import QDSSignature


def sign(
    *,
    signature_id: str,
    signer_id: str,
    message_id: str,
    session_id: str,
    message: str,
    input_state: ComplexVector,
    seed: int | None = None,
) -> QDSSignature:
    """
    Generate a QDS signature.

    This function is responsible only for signature generation.
    Verification and security decisions are handled elsewhere.
    """

    message_digest, quantum_evidence = execute_protocol(
        message=message,
        input_state=input_state,
        seed=seed,
    )

    return QDSSignature(
        signature_id=signature_id,
        signer_id=signer_id,
        message_id=message_id,
        protocol_version=PROTOCOL_VERSION,
        session_id=session_id,
        message_digest=message_digest,
        quantum_evidence=quantum_evidence,
    )