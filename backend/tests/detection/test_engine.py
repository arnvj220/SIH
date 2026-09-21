from app.attacks.contracts import (
    Decision,
    MeasurementRound,
    ThreatType,
    VerificationContext,
)
from app.detection.engine import DetectionEngine


def _context(**overrides) -> VerificationContext:
    values = dict(
        context_id="ctx_1",
        signature_id="sig_1",
        signer_id="alice",
        expected_signer_id="alice",
        verifier_id="bob",
        message_id="msg_1",
        message_digest="abc",
        signed_digest="abc",
        session_id="sess_1",
        nonce="n1",
        issued_at=0.0,
        received_at=1.0,
        auth_fingerprint="fp_alice",
        measurements=(
            MeasurementRound(index=0, basis="Z", expected=0, observed=0),
            MeasurementRound(index=1, basis="Z", expected=1, observed=1),
        ),
    )
    values.update(overrides)
    return VerificationContext(**values)


class TestDetectionEngine:
    def test_clean_context_accepts(self):
        engine = DetectionEngine()
        outcome = engine.verify(_context())
        assert outcome.decision == Decision.ACCEPT
        assert outcome.threats == []

    def test_signer_mismatch_flagged_as_impersonation(self):
        engine = DetectionEngine()
        outcome = engine.verify(_context(signer_id="mallory"))
        assert outcome.decision == Decision.REJECT
        assert ThreatType.IMPERSONATION in outcome.threats

    def test_digest_mismatch_flagged_as_forgery(self):
        engine = DetectionEngine()
        outcome = engine.verify(_context(message_digest="tampered"))
        assert outcome.decision == Decision.REJECT
        assert ThreatType.FORGERY in outcome.threats

    def test_full_round_mismatch_flagged_as_forgery(self):
        engine = DetectionEngine()
        ctx = _context(measurements=tuple(
            MeasurementRound(index=i, basis="Z", expected=0, observed=1)
            for i in range(20)
        ))
        outcome = engine.verify(ctx)
        assert outcome.decision == Decision.REJECT
        assert ThreatType.FORGERY in outcome.threats

    def test_evidence_present_on_reject(self):
        engine = DetectionEngine()
        outcome = engine.verify(_context(signer_id="mallory"))
        assert len(outcome.evidence) >= 1
        assert all("rule_id" in e for e in outcome.evidence)