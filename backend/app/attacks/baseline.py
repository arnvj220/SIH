from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

import numpy as np

from .contracts import (
    BASES,
    MeasurementRound,
    VerificationContext,
    derive_auth_fingerprint,
    sha256_hex,
)


# THE integration seam with Rishi's quantum engine.
# A provider returns the measurement rounds of ONE legitimate signature:
#     provider(rng, n_rounds, natural_error_rate) -> sequence of MeasurementRound
# where for each round: basis in {"X","Y","Z"}, expected = the ideal outcome (0/1),
# observed = what was actually measured (equals expected except for honest noise).
RoundsProvider = Callable[[np.random.Generator, int, float], Sequence[MeasurementRound]]

# Anything with make_legitimate() -> VerificationContext, built per (seed, rounds, noise).
SourceFactory = Callable[[int, int, float], Any]


def synthetic_rounds(
    rng: np.random.Generator, n_rounds: int, natural_error_rate: float
) -> tuple[MeasurementRound, ...]:
    """Fake-but-plausible rounds. Stand-in until Rishi's engine is wired in."""
    bases = rng.choice(BASES, size=n_rounds)
    expected = rng.integers(0, 2, size=n_rounds)
    noise = rng.random(n_rounds) < natural_error_rate
    observed = np.where(noise, 1 - expected, expected)
    return tuple(
        MeasurementRound(i, str(bases[i]), int(expected[i]), int(observed[i]))
        for i in range(n_rounds)
    )


@dataclass
class BaselineConfig:
    rounds: int = 200
    natural_error_rate: float = 0.01  # honest channel noise
    authorized_verifiers: tuple[str, ...] = ("ver_alice", "ver_bob")
    signers: tuple[str, ...] = ("usr_alice", "usr_bob", "usr_carol", "usr_dave")
    protocol_version: str = "qds-v1"
    start_time: float = 1_700_000_000.0
    network_delay_s: float = 1.0

    def __post_init__(self) -> None:
        if self.rounds < 1:
            raise ValueError("rounds must be >= 1")
        if not 0.0 <= self.natural_error_rate < 0.5:
            raise ValueError("natural_error_rate must be in [0, 0.5)")


class BaselineFactory:
    def __init__(
        self,
        config: BaselineConfig | None = None,
        seed: int = 0,
        rounds_provider: RoundsProvider | None = None,
    ):
        self.config = config or BaselineConfig()
        self._rng = np.random.default_rng(seed)
        self._counter = 0
        self._provider: RoundsProvider = rounds_provider or synthetic_rounds

    def _hex(self, nbytes: int = 6) -> str:
        return self._rng.bytes(nbytes).hex()

    def make_legitimate(self) -> VerificationContext:
        cfg = self.config
        rng = self._rng
        signer = str(rng.choice(cfg.signers))
        verifier = str(rng.choice(cfg.authorized_verifiers))
        message_id = f"msg_{self._hex()}"
        digest = sha256_hex(message_id)

        rounds = tuple(self._provider(rng, cfg.rounds, cfg.natural_error_rate))
        if not rounds or not all(isinstance(m, MeasurementRound) for m in rounds):
            raise TypeError("rounds_provider must return a non-empty sequence of MeasurementRound")

        issued = cfg.start_time + self._counter
        self._counter += 1
        return VerificationContext(
            context_id=f"ctx_{self._hex()}",
            signature_id=f"sig_{self._hex()}",
            signer_id=signer,
            expected_signer_id=signer,
            verifier_id=verifier,
            message_id=message_id,
            message_digest=digest,
            signed_digest=digest,
            session_id=f"sess_{self._hex()}",
            nonce=f"nonce_{self._hex(8)}",
            issued_at=issued,
            received_at=issued + cfg.network_delay_s,
            auth_fingerprint=derive_auth_fingerprint(signer),
            measurements=rounds,
            protocol_version=cfg.protocol_version,
            metadata={"origin": "baseline"},
        )


def default_source_factory(seed: int, rounds: int, natural_error_rate: float) -> BaselineFactory:
    return BaselineFactory(BaselineConfig(rounds=rounds, natural_error_rate=natural_error_rate), seed)
