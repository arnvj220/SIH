from __future__ import annotations

from dataclasses import dataclass

from ..qds.signer import sign
from ..qds.signature import QDSSignature
from ..quantum.states.state_utils import ComplexVector


@dataclass(frozen=True)
class SignatureRequest:
    signature_id: str
    signer_id: str
    message_id: str
    session_id: str
    message: str
    input_state: ComplexVector
    seed: int | None = None


class SignatureService:
    """Application service responsible for QDS signature generation."""

    def create_signature(
        self,
        request: SignatureRequest,
    ) -> QDSSignature:
        return sign(
            signature_id=request.signature_id,
            signer_id=request.signer_id,
            message_id=request.message_id,
            session_id=request.session_id,
            message=request.message,
            input_state=request.input_state,
            seed=request.seed,
        )