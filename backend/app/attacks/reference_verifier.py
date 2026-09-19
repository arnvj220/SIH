from __future__ import annotations

import threading
from dataclasses import dataclass

from .contracts import (
    DEFAULT_AUTH_SECRET,
    Decision,
    DetectionOutcome,
    ThreatType,
    VerificationContext,
    derive_auth_fingerprint,
)


@dataclass
class ReferenceVerifierConfig:
    authorized_verifiers: tuple[str, ...] = ("ver_alice", "ver_bob")
    ttl_seconds: float = 300.0
    suspicious_error_rate: float = 0.05
    reject_error_rate: float = 0.11
    auth_secret: str = DEFAULT_AUTH_SECRET


class ReferenceVerifier:
    def __init__(self, config: ReferenceVerifierConfig | None = None):
        self.config = config or ReferenceVerifierConfig()
        self._lock = threading.Lock()
        self._consumed_sessions: set[str] = set()
        self._seen_nonces: set[str] = set()

    def reset(self) -> None:
        with self._lock:
            self._consumed_sessions.clear()
            self._seen_nonces.clear()

    def verify(self, ctx: VerificationContext) -> DetectionOutcome:
        cfg = self.config
        threats: list[ThreatType] = []
        evidence: list[dict] = []

        # --- authorization
        if ctx.verifier_id not in cfg.authorized_verifiers:
            threats.append(ThreatType.UNAUTHORIZED_VERIFICATION)
            evidence.append(
                {"rule_id": "UNAUTH_01", "metric": "verifier_id", "observed": ctx.verifier_id,
                 "expected": "one of authorized verifiers"}
            )

        # --- identity
        expected_fp = derive_auth_fingerprint(ctx.signer_id, cfg.auth_secret)
        if ctx.signer_id != ctx.expected_signer_id or ctx.auth_fingerprint != expected_fp:
            threats.append(ThreatType.IMPERSONATION)
            evidence.append(
                {"rule_id": "IMPERS_01", "metric": "identity_binding",
                 "observed": {"signer": ctx.signer_id, "credential_ok": ctx.auth_fingerprint == expected_fp},
                 "expected": {"signer": ctx.expected_signer_id, "credential_ok": True}}
            )

        # --- replay (atomic check; consumption happens below on ACCEPT)
        age = ctx.received_at - ctx.issued_at
        with self._lock:
            replay_reasons = []
            if ctx.session_id in self._consumed_sessions:
                replay_reasons.append("session_already_consumed")
            if ctx.nonce in self._seen_nonces:
                replay_reasons.append("nonce_already_seen")
            if age > cfg.ttl_seconds or age < 0:
                replay_reasons.append("outside_validity_window")
            if replay_reasons:
                threats.append(ThreatType.REPLAY)
                evidence.append(
                    {"rule_id": "REPLAY_01", "metric": "session_freshness",
                     "observed": {"reasons": replay_reasons, "age_s": round(age, 3)},
                     "threshold": {"ttl_s": cfg.ttl_seconds}}
                )

            # --- signed-message integrity
            if ctx.message_digest != ctx.signed_digest:
                threats.append(ThreatType.FORGERY)
                evidence.append(
                    {"rule_id": "FORGERY_01", "metric": "digest_match", "observed": False,
                     "expected": True}
                )

            # --- measurement statistics
            qber = ctx.error_rate
            measurement_reject = qber >= cfg.reject_error_rate
            measurement_suspicious = qber >= cfg.suspicious_error_rate
            if measurement_suspicious:
                for t in (ThreatType.FORGERY, ThreatType.CHANNEL_MANIPULATION):
                    if t not in threats:
                        threats.append(t)
                evidence.append(
                    {
                        "rule_id": "QBER_REJECT_01" if measurement_reject else "QBER_SUSPICIOUS_01",
                        "metric": "measurement_error_rate",
                        "observed": round(qber, 4),
                        "threshold": cfg.reject_error_rate if measurement_reject
                        else cfg.suspicious_error_rate,
                        "per_basis": {k: round(v, 4) for k, v in ctx.per_basis_error_rates().items()},
                        "ambiguous": "forgery vs channel manipulation",
                    }
                )

            # --- decision
            hard_fail = any(
                t in threats
                for t in (
                    ThreatType.UNAUTHORIZED_VERIFICATION,
                    ThreatType.IMPERSONATION,
                    ThreatType.REPLAY,
                )
            ) or ctx.message_digest != ctx.signed_digest
            if hard_fail or measurement_reject:
                decision = Decision.REJECT
            elif measurement_suspicious:
                decision = Decision.SUSPICIOUS
            else:
                decision = Decision.ACCEPT
                self._consumed_sessions.add(ctx.session_id)
                self._seen_nonces.add(ctx.nonce)

        return DetectionOutcome(decision, threats, evidence)
