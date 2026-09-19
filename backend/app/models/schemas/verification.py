"""
API schemas for signature verification.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ...attacks.contracts import Decision, ThreatType


class MeasurementRoundSchema(BaseModel):
    """One expected-vs-observed measurement round."""

    index: int = Field(ge=0)
    basis: str = Field(pattern=r"^[XYZ]$")
    expected: int = Field(ge=0, le=1)
    observed: int = Field(ge=0, le=1)


class VerificationRequest(BaseModel):
    """
    Input required to verify a signature.

    This mirrors the important parts of VerificationContext without
    exposing the internal domain object directly through the API.
    """

    verification_id: str = Field(min_length=1, max_length=128)

    signature_id: str = Field(min_length=1, max_length=128)

    signer_id: str = Field(min_length=1, max_length=128)

    expected_signer_id: str = Field(min_length=1, max_length=128)

    verifier_id: str = Field(min_length=1, max_length=128)

    message_id: str = Field(min_length=1, max_length=128)

    message_digest: str = Field(
        min_length=64,
        max_length=64,
    )

    signed_digest: str = Field(
        min_length=64,
        max_length=64,
    )

    session_id: str = Field(min_length=1, max_length=128)

    nonce: str = Field(min_length=1, max_length=128)

    issued_at: float

    received_at: float

    auth_fingerprint: str = Field(
        min_length=1,
        max_length=128,
    )

    measurements: list[MeasurementRoundSchema]

    protocol_version: str = "qds-v1"

    metadata: dict = Field(default_factory=dict)


class VerificationResponse(BaseModel):
    """Result returned by the verification API."""

    verification_id: str

    decision: Decision

    threats: list[ThreatType] = Field(
        default_factory=list,
    )

    evidence: list[dict] = Field(
        default_factory=list,
    )

    detected: bool

    error_rate: float = Field(
        ge=0.0,
        le=1.0,
    )