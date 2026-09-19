from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .contracts import (
    BASES,
    MeasurementRound,
    VerificationContext,
    derive_auth_fingerprint,
    sha256_hex,
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
    def __init__(self, config: BaselineConfig | None = None, seed: int = 0):
        self.config = config or BaselineConfig()
        self._rng = np.random.default_rng(seed)
        self._counter = 0

    def _hex(self, nbytes: int = 6) -> str:
        return self._rng.bytes(nbytes).hex()

    def make_legitimate(self) -> VerificationContext:
        cfg = self.config
        rng = self._rng
        signer = str(rng.choice(cfg.signers))
        verifier = str(rng.choice(cfg.authorized_verifiers))
        message_id = f"msg_{self._hex()}"
        digest = sha256_hex(message_id)

        bases = rng.choice(BASES, size=cfg.rounds)
        expected = rng.integers(0, 2, size=cfg.rounds)
        noise = rng.random(cfg.rounds) < cfg.natural_error_rate
        observed = np.where(noise, 1 - expected, expected)
        rounds = tuple(
            MeasurementRound(i, str(bases[i]), int(expected[i]), int(observed[i]))
            for i in range(cfg.rounds)
        )

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
