"""
API schemas for QDS signatures.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class QuantumEvidenceSchema(BaseModel):
    """
    Serializable representation of quantum evidence.

    Complex amplitudes are represented as JSON-friendly values:
    [real, imaginary]
    """

    input_state: list[list[float]]
    measurement_bits: str = Field(pattern=r"^[01]{2}$")
    correction_bits: str = Field(pattern=r"^[01]{2}$")
    correction_operator: str
    bob_state_before_correction: list[list[float]]
    bob_state_after_correction: list[list[float]]
    seed: int | None = None


class SignatureCreate(BaseModel):
    """Request body for creating a QDS signature."""

    signature_id: str = Field(min_length=1, max_length=128)
    signer_id: str = Field(min_length=1, max_length=128)
    message_id: str = Field(min_length=1, max_length=128)
    session_id: str = Field(min_length=1, max_length=128)

    message: str = Field(min_length=1)

    # ComplexVector is converted to a JSON-friendly representation
    # before reaching the API layer.
    input_state: list[list[float]]

    seed: int | None = None


class SignatureResponse(BaseModel):
    """API representation of a generated QDS signature."""

    model_config = ConfigDict(from_attributes=True)

    signature_id: str
    signer_id: str
    message_id: str
    protocol_version: str
    session_id: str
    message_digest: str
    quantum_evidence: QuantumEvidenceSchema

    created_at: datetime | None = None