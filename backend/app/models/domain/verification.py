"""
Domain models for signature verification.

Verification decisions are produced by the verification/detection
engine. These classes only represent the input and output contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class VerificationDecision(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    SUSPICIOUS = "SUSPICIOUS"


class ThreatType(str, Enum):
    FORGERY = "FORGERY"
    IMPERSONATION = "IMPERSONATION"
    REPLAY = "REPLAY"
    UNAUTHORIZED_VERIFICATION = "UNAUTHORIZED_VERIFICATION"
    CHANNEL_MANIPULATION = "CHANNEL_MANIPULATION"


class Severity(str, Enum):
    INFO = "INFO"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class VerificationRequest:
    """Input required to verify a signature."""

    signature_id: str
    message_id: str
    message: str
    verifier_id: str
    nonce: str | None = None


@dataclass(frozen=True)
class Evidence:
    """A single measured metric supporting a security decision."""

    metric: str
    observed: float
    expected: float
    threshold: float
    rule_id: str
    explanation: str

    def __post_init__(self) -> None:
        if not self.rule_id:
            raise ValueError("Evidence must reference a rule_id.")


@dataclass(frozen=True)
class ThreatResult:
    """Outcome of one threat detector for one verification event."""

    type: ThreatType
    detected: bool
    severity: Severity
    evidence: tuple[Evidence, ...] = ()


@dataclass(frozen=True)
class VerificationResult:
    """Result produced by the verification pipeline."""

    verification_id: str
    signature_id: str
    decision: VerificationDecision

    threats: tuple[str, ...] = ()
    evidence: tuple[dict[str, Any], ...] = ()

    error_rate: float | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def accepted(self) -> bool:
        return self.decision == VerificationDecision.ACCEPT

    @property
    def detected(self) -> bool:
        return self.decision != VerificationDecision.ACCEPT