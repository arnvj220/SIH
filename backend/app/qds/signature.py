"""
QDS signature representation.

This module contains the data produced by the QDS signing process.
It does not perform verification or threat detection.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..quantum.measurements.evidence import QuantumEvidence


@dataclass(frozen=True)
class QDSSignature:
    """Output of the QDS signature-generation process."""

    signature_id: str
    signer_id: str
    message_id: str
    protocol_version: str
    session_id: str

    # Digest identifies the message associated with this signature.
    message_digest: str

    # Quantum evidence produced during signature generation.
    quantum_evidence: QuantumEvidence