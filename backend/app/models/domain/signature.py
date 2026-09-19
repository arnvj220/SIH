"""
Domain model for QDS signatures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Signature:
    """Application-level representation of a QDS signature."""

    signature_id: str
    signer_id: str
    message_id: str
    message_digest: str
    protocol_version: str
    session_id: str

    quantum_evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = {
            "signature_id": self.signature_id,
            "signer_id": self.signer_id,
            "message_id": self.message_id,
            "message_digest": self.message_digest,
            "protocol_version": self.protocol_version,
            "session_id": self.session_id,
        }

        for name, value in required.items():
            if not value:
                raise ValueError(f"{name} cannot be empty.")