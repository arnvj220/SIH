from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from typing import Any, Protocol

BASES = ("X", "Y", "Z")  # Pauli measurement bases
DEFAULT_AUTH_SECRET = "sih-26141-demo-secret"  # demo only, never a real secret


class ThreatType(str, Enum):
    NONE = "NONE"
    FORGERY = "FORGERY"
    IMPERSONATION = "IMPERSONATION"
    REPLAY = "REPLAY"
    UNAUTHORIZED_VERIFICATION = "UNAUTHORIZED_VERIFICATION"
    CHANNEL_MANIPULATION = "CHANNEL_MANIPULATION"


class Decision(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    SUSPICIOUS = "SUSPICIOUS"


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def derive_auth_fingerprint(signer_id: str, secret: str = DEFAULT_AUTH_SECRET) -> str:
    """Stand-in for a signer's authentication credential."""
    return sha256_hex(f"{signer_id}:{secret}")[:16]


@dataclass(frozen=True)
class MeasurementRound:
    """One projective measurement round.

    `expected` is the outcome a legitimate run should give; `observed` is what
    the verifier actually saw. Rishi's engine will fill these from Qiskit.
    """

    index: int
    basis: str  # "X" | "Y" | "Z"
    expected: int  # 0 or 1
    observed: int  # 0 or 1

    @property
    def is_error(self) -> bool:
        return self.expected != self.observed


@dataclass
class VerificationContext:
    """Everything a verifier sees for one verification attempt."""

    context_id: str
    signature_id: str
    signer_id: str  # who the presenter CLAIMS signed
    expected_signer_id: str  # who the session says should have signed
    verifier_id: str  # who is asking to verify
    message_id: str
    message_digest: str  # digest of the message being presented now
    signed_digest: str  # digest the signature was originally created over
    session_id: str
    nonce: str
    issued_at: float  # epoch seconds, signature creation
    received_at: float  # epoch seconds, verification request arrival
    auth_fingerprint: str  # credential presented with the request
    measurements: tuple[MeasurementRound, ...]
    protocol_version: str = "qds-v1"
    metadata: dict[str, Any] = field(default_factory=dict)

    def clone(self, **changes: Any) -> "VerificationContext":
        """Copy with modifications. Attacks MUST use this, never mutate the
        target (SR-005 attack isolation)."""
        changes.setdefault("metadata", dict(self.metadata))
        return replace(self, **changes)

    @property
    def error_rate(self) -> float:
        if not self.measurements:
            return 0.0
        return sum(m.is_error for m in self.measurements) / len(self.measurements)

    def per_basis_error_rates(self) -> dict[str, float]:
        rates: dict[str, float] = {}
        for basis in BASES:
            rounds = [m for m in self.measurements if m.basis == basis]
            rates[basis] = (
                sum(m.is_error for m in rounds) / len(rounds) if rounds else 0.0
            )
        return rates

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DetectionOutcome:
    """What a verifier/detector returns. Shubh's engine must return this."""

    decision: Decision
    threats: list[ThreatType] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)

    @property
    def detected(self) -> bool:
        return self.decision != Decision.ACCEPT


class Verifier(Protocol):
    """Interface the attack runner needs from Shubh's verification/detection engine."""

    def verify(self, context: VerificationContext) -> DetectionOutcome: ...


@dataclass
class AttackedSample:
    """One context to submit to the system under test, with ground truth."""

    context: VerificationContext
    is_attack: bool
    expected_threat: ThreatType
    role: str = "attack"  # "setup" | "attack" | "control"
    evidence: dict[str, Any] = field(default_factory=dict)
