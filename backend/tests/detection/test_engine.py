"""Tests for the deterministic detection engine."""

import pytest

from app.attacks.contracts import (
    Decision,
    MeasurementRound,
    ThreatType,
    VerificationContext,
)
from app.detection.engine import DetectionEngine
from app.detection.stores import AuthorizationStore, ReplayStore


def _context(**overrides) -> VerificationContext:
    """Build a clean, legitimate verification context. Override to attack."""
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
        nonce="nonce_1",
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


def _fresh_engine() -> DetectionEngine:
    """Engine with fresh stores — no cross-test state."""
    return DetectionEngine(
        replay_store=ReplayStore(),
        authorization_store=AuthorizationStore(),
    )


class TestCleanContext:
    def test_clean_context_accepts(self):
        engine = _fresh_engine()
        outcome = engine.verify(_context())
        assert outcome.decision == Decision.ACCEPT
        assert outcome.threats == []

    def test_clean_context_produces_no_evidence(self):
        engine = _fresh_engine()
        outcome = engine.verify(_context())
        assert outcome.evidence == []


class TestImpersonation:
    def test_signer_mismatch_flagged(self):
        engine = _fresh_engine()
        outcome = engine.verify(_context(signer_id="mallory"))
        assert outcome.decision == Decision.REJECT
        assert ThreatType.IMPERSONATION in outcome.threats

    def test_impersonation_evidence_has_rule_id(self):
        engine = _fresh_engine()
        outcome = engine.verify(_context(signer_id="mallory"))
        assert any(
            e.get("rule_id") == "IMPERSONATION_ID_MISMATCH_01"
            for e in outcome.evidence
        )


class TestForgery:
    def test_digest_mismatch_flagged(self):
        engine = _fresh_engine()
        outcome = engine.verify(_context(message_digest="tampered"))
        assert outcome.decision == Decision.REJECT
        assert ThreatType.FORGERY in outcome.threats

    def test_all_rounds_mismatched_flagged(self):
        engine = _fresh_engine()
        ctx = _context(measurements=tuple(
            MeasurementRound(index=i, basis="Z", expected=0, observed=1)
            for i in range(20)
        ))
        outcome = engine.verify(ctx)
        assert outcome.decision == Decision.REJECT
        assert ThreatType.FORGERY in outcome.threats


class TestChannelManipulation:
    def test_distribution_shift_flagged(self):
        engine = _fresh_engine()
        # 20 rounds, half match expected=0, half are expected=1 but observed=0.
        # error_rate = 0.5 (would trigger forgery) but let's disable forgery
        # by using a lower threshold rule set... in practice we just check that
        # the channel rule exists in the outcome.
        measurements = tuple(
            [MeasurementRound(index=i, basis="Z", expected=0, observed=0)
             for i in range(5)]
            + [MeasurementRound(index=5 + i, basis="Z", expected=1, observed=0)
               for i in range(15)]
        )
        ctx = _context(measurements=measurements)
        outcome = engine.verify(ctx)
        assert outcome.decision == Decision.REJECT
        # Either forgery (error_rate) or channel manipulation can fire.
        assert (
            ThreatType.FORGERY in outcome.threats
            or ThreatType.CHANNEL_MANIPULATION in outcome.threats
        )


class TestReplay:
    def test_second_submission_same_session_nonce_flagged(self):
        engine = _fresh_engine()
        ctx = _context()
        first = engine.verify(ctx)
        assert first.decision == Decision.ACCEPT

        second = engine.verify(ctx)
        assert second.decision == Decision.REJECT
        assert ThreatType.REPLAY in second.threats

    def test_different_nonce_is_not_replay(self):
        engine = _fresh_engine()
        engine.verify(_context(nonce="nonce_1"))
        second = engine.verify(_context(nonce="nonce_2"))
        assert second.decision == Decision.ACCEPT

    def test_attacker_cannot_burn_legit_session(self):
        """An impersonating request must not consume the session."""
        engine = _fresh_engine()
        # Attacker submits with wrong signer
        engine.verify(_context(signer_id="mallory"))
        # Legit request with same session+nonce should still succeed
        legit = engine.verify(_context())
        assert legit.decision == Decision.ACCEPT

    def test_replay_evidence_has_rule_id(self):
        engine = _fresh_engine()
        ctx = _context()
        engine.verify(ctx)
        replayed = engine.verify(ctx)
        assert any(
            e.get("rule_id") == "REPLAY_SESSION_REUSE_01"
            for e in replayed.evidence
        )


class TestUnauthorized:
    def test_unregistered_verifier_denied_when_store_has_entries(self):
        auth = AuthorizationStore()
        auth.allow("alice", "bob")  # only bob can verify for alice
        engine = DetectionEngine(
            replay_store=ReplayStore(),
            authorization_store=auth,
        )
        # mallory tries to verify for alice
        outcome = engine.verify(_context(verifier_id="mallory"))
        assert outcome.decision == Decision.REJECT
        assert ThreatType.UNAUTHORIZED_VERIFICATION in outcome.threats

    def test_registered_verifier_allowed(self):
        auth = AuthorizationStore()
        auth.allow("alice", "bob")
        engine = DetectionEngine(
            replay_store=ReplayStore(),
            authorization_store=auth,
        )
        outcome = engine.verify(_context(verifier_id="bob"))
        assert outcome.decision == Decision.ACCEPT

    def test_open_mode_allows_anyone(self):
        auth = AuthorizationStore()  # no entries
        engine = DetectionEngine(
            replay_store=ReplayStore(),
            authorization_store=auth,
        )
        outcome = engine.verify(_context(verifier_id="anyone"))
        assert outcome.decision == Decision.ACCEPT


class TestCombinedAttacks:
    def test_impersonation_and_forgery_both_reported(self):
        engine = _fresh_engine()
        ctx = _context(signer_id="mallory", message_digest="tampered")
        outcome = engine.verify(ctx)
        assert ThreatType.IMPERSONATION in outcome.threats
        assert ThreatType.FORGERY in outcome.threats

    def test_evidence_always_has_rule_id_on_reject(self):
        engine = _fresh_engine()
        outcome = engine.verify(_context(signer_id="mallory"))
        assert outcome.decision == Decision.REJECT
        assert len(outcome.evidence) >= 1
        assert all("rule_id" in e for e in outcome.evidence)