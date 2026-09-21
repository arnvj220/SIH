"""
Benchmark the real end-to-end pipeline.

Unlike benchmark.py (which fabricates VerificationContexts directly),
this module drives the full stack:

    SignatureService.create_signature
        → VerificationService.build_context
        → DetectionService.detect

Attacks are injected at the signature level (before verification),
matching how they would occur in the deployed system.

Channel-manipulation attacks are excluded because they require
corruption of the quantum state, which belongs to the quantum engine
(see docs/architecture.md §9).
"""

from __future__ import annotations

import statistics
import time
from dataclasses import dataclass, field, replace

from app.attacks.contracts import Decision, ThreatType
from app.detection.stores import AuthorizationStore, ReplayStore
from app.quantum.states.pauli_states import plus_state
from app.services.detection_service import DetectionService
from app.services.signature_service import SignatureRequest, SignatureService
from app.services.verification_service import VerificationService
from app.detection.engine import DetectionEngine


@dataclass
class RealBenchmarkMetrics:
    total: int = 0
    correct: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    true_positives: int = 0
    true_negatives: int = 0
    classified_correctly: int = 0
    classified_wrongly: int = 0
    latencies_ms: list[float] = field(default_factory=list)
    per_attack: dict[str, dict] = field(default_factory=dict)

    @property
    def detection_rate(self) -> float:
        denom = self.true_positives + self.false_negatives
        return self.true_positives / denom if denom else 0.0

    @property
    def false_positive_rate(self) -> float:
        denom = self.false_positives + self.true_negatives
        return self.false_positives / denom if denom else 0.0

    @property
    def false_negative_rate(self) -> float:
        denom = self.false_negatives + self.true_positives
        return self.false_negatives / denom if denom else 0.0

    @property
    def classification_accuracy(self) -> float:
        denom = self.classified_correctly + self.classified_wrongly
        return self.classified_correctly / denom if denom else 0.0

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def mean_latency_ms(self) -> float:
        return statistics.mean(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def p95_latency_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        sl = sorted(self.latencies_ms)
        return sl[int(0.95 * (len(sl) - 1))]


def _fresh_services(shots_per_basis: int = 100):
    """Isolated service graph per benchmark run."""
    replay_store = ReplayStore()
    auth_store = AuthorizationStore()
    auth_store.allow("alice", "bob")  # restrict for unauthorized scenarios
    engine = DetectionEngine(
        replay_store=replay_store,
        authorization_store=auth_store,
    )
    return (
        SignatureService(),
        VerificationService(shots_per_basis=shots_per_basis),
        DetectionService(engine=engine),
    )


def _record(
    metrics: RealBenchmarkMetrics,
    *,
    name: str,
    is_attack: bool,
    expected_threat: ThreatType,
    decision: Decision,
    threats: list[ThreatType],
    latency_ms: float,
) -> None:
    flagged = decision != Decision.ACCEPT
    correct_threat = expected_threat in threats

    metrics.total += 1
    metrics.latencies_ms.append(latency_ms)

    if is_attack and flagged and correct_threat:
        metrics.true_positives += 1
        metrics.correct += 1
        metrics.classified_correctly += 1
    elif is_attack and flagged:
        metrics.true_positives += 1
        metrics.classified_wrongly += 1
    elif is_attack and not flagged:
        metrics.false_negatives += 1
        metrics.classified_wrongly += 1
    elif not is_attack and flagged:
        metrics.false_positives += 1
    else:
        metrics.true_negatives += 1
        metrics.correct += 1
        metrics.classified_correctly += 1

    metrics.per_attack.setdefault(name, {"total": 0, "detected": 0, "missed": 0})
    metrics.per_attack[name]["total"] += 1
    if is_attack:
        if correct_threat:
            metrics.per_attack[name]["detected"] += 1
        else:
            metrics.per_attack[name]["missed"] += 1


def run_real_benchmark(
    *,
    iterations: int = 50,
    seed: int = 12345,
    shots_per_basis: int = 100,
) -> RealBenchmarkMetrics:
    """Run the real pipeline across legit + injectable attacks."""
    metrics = RealBenchmarkMetrics()

    for i in range(iterations):
        sig_svc, ver_svc, det_svc = _fresh_services(shots_per_basis)

        # ---------- Legit ----------
        sig = sig_svc.create_signature(SignatureRequest(
            signature_id=f"legit_{i}",
            signer_id="alice", message_id=f"m_legit_{i}",
            session_id=f"s_legit_{i}", message=f"hello {i}",
            input_state=plus_state(), seed=seed + i,
        ))
        t0 = time.perf_counter()
        ctx = ver_svc.build_context(
            sig, verifier_id="bob", message=f"hello {i}",
            nonce=f"n_legit_{i}",
        )
        outcome = det_svc.detect(ctx)
        dt = (time.perf_counter() - t0) * 1000.0
        _record(
            metrics, name="legit", is_attack=False,
            expected_threat=ThreatType.NONE,
            decision=outcome.decision, threats=list(outcome.threats),
            latency_ms=dt,
        )

        # ---------- Forgery: alter signed_digest ----------
        sig = sig_svc.create_signature(SignatureRequest(
            signature_id=f"forge_{i}",
            signer_id="alice", message_id=f"m_forge_{i}",
            session_id=f"s_forge_{i}", message=f"hello {i}",
            input_state=plus_state(), seed=seed + i,
        ))
        tampered = replace(sig, message_digest="deadbeef" * 8)
        t0 = time.perf_counter()
        ctx = ver_svc.build_context(
            tampered, verifier_id="bob", message=f"hello {i}",
            nonce=f"n_forge_{i}",
        )
        outcome = det_svc.detect(ctx)
        dt = (time.perf_counter() - t0) * 1000.0
        _record(
            metrics, name="forgery", is_attack=True,
            expected_threat=ThreatType.FORGERY,
            decision=outcome.decision, threats=list(outcome.threats),
            latency_ms=dt,
        )

        # ---------- Impersonation: expected signer mismatch ----------
        sig = sig_svc.create_signature(SignatureRequest(
            signature_id=f"imp_{i}",
            signer_id="mallory", message_id=f"m_imp_{i}",
            session_id=f"s_imp_{i}", message=f"hello {i}",
            input_state=plus_state(), seed=seed + i,
        ))
        t0 = time.perf_counter()
        ctx = ver_svc.build_context(
            sig, verifier_id="bob", message=f"hello {i}",
            expected_signer_id="alice",  # claimed signer ≠ expected
            nonce=f"n_imp_{i}",
        )
        outcome = det_svc.detect(ctx)
        dt = (time.perf_counter() - t0) * 1000.0
        _record(
            metrics, name="impersonation", is_attack=True,
            expected_threat=ThreatType.IMPERSONATION,
            decision=outcome.decision, threats=list(outcome.threats),
            latency_ms=dt,
        )

        # ---------- Replay: submit same context twice ----------
        sig = sig_svc.create_signature(SignatureRequest(
            signature_id=f"replay_{i}",
            signer_id="alice", message_id=f"m_replay_{i}",
            session_id=f"s_replay_{i}", message=f"hello {i}",
            input_state=plus_state(), seed=seed + i,
        ))
        ctx = ver_svc.build_context(
            sig, verifier_id="bob", message=f"hello {i}",
            nonce=f"n_replay_{i}",
        )
        det_svc.detect(ctx)  # first — consumes (session, nonce)
        t0 = time.perf_counter()
        outcome = det_svc.detect(ctx)  # second — replay
        dt = (time.perf_counter() - t0) * 1000.0
        _record(
            metrics, name="replay", is_attack=True,
            expected_threat=ThreatType.REPLAY,
            decision=outcome.decision, threats=list(outcome.threats),
            latency_ms=dt,
        )

        # ---------- Unauthorized ----------
        sig = sig_svc.create_signature(SignatureRequest(
            signature_id=f"unauth_{i}",
            signer_id="alice", message_id=f"m_unauth_{i}",
            session_id=f"s_unauth_{i}", message=f"hello {i}",
            input_state=plus_state(), seed=seed + i,
        ))
        t0 = time.perf_counter()
        ctx = ver_svc.build_context(
            sig, verifier_id="mallory", message=f"hello {i}",
            nonce=f"n_unauth_{i}",
        )
        outcome = det_svc.detect(ctx)
        dt = (time.perf_counter() - t0) * 1000.0
        _record(
            metrics, name="unauthorized", is_attack=True,
            expected_threat=ThreatType.UNAUTHORIZED_VERIFICATION,
            decision=outcome.decision, threats=list(outcome.threats),
            latency_ms=dt,
        )

    return metrics