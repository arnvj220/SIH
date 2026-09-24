import unittest

from app.attacks.baseline import BaselineFactory
from app.attacks.contracts import Decision, DetectionOutcome, ThreatType
from app.attacks.reference_verifier import ReferenceVerifier
from app.attacks.verifier_adapter import real_verifier_factory, validate_verifier


class GoodVerifier:
    """Accepts legit traffic, rejects anything already seen (minimal but correct)."""

    def __init__(self):
        self._seen = set()

    def verify(self, ctx):
        if ctx.context_id in self._seen:
            return DetectionOutcome(Decision.REJECT, [ThreatType.REPLAY], [{"rule": "seen"}])
        self._seen.add(ctx.context_id)
        return DetectionOutcome(Decision.ACCEPT, [], [])


class ValidatorTests(unittest.TestCase):
    def test_reference_verifier_passes(self):
        self.assertTrue(validate_verifier(ReferenceVerifier)["ok"])

    def test_good_custom_verifier_passes(self):
        self.assertTrue(validate_verifier(GoodVerifier)["ok"])

    def test_real_verifier_factory_returns_working_engine(self):
        """
        Replaces the previous 'unwired template fails loudly' test.

        The template is now wired to Shubh's DetectionEngine. This test proves
        the factory returns a contract-compliant verifier that:
          - returns DetectionOutcome on legitimate input
          - does not flag fresh legitimate traffic (0 false positives)
          - rejects a replayed context (replay protection active)
        """
        result = validate_verifier(real_verifier_factory)
        self.assertTrue(result["ok"])
        self.assertEqual(result["false_positives_on_fresh_legit"], 0)

    def test_real_verifier_factory_instances_are_isolated(self):
        """
        Two factories must not share replay state. If they did, a context
        consumed by instance A would be flagged as REPLAY by instance B.
        """
        src = BaselineFactory(seed=7)
        ctx = src.make_legitimate()

        a = real_verifier_factory()
        b = real_verifier_factory()

        first = a.verify(ctx)
        # b has never seen this context; must NOT fire REPLAY.
        second = b.verify(ctx)

        self.assertNotIn(ThreatType.REPLAY, second.threats)
        self.assertNotIn(ThreatType.REPLAY, first.threats)

    def assert_fails(self, factory, fragment):
        with self.assertRaises(AssertionError) as cm:
            validate_verifier(factory)
        self.assertIn(fragment, str(cm.exception))

    def test_wrong_return_type(self):
        class Bad:
            def verify(self, ctx):
                return {"decision": "ACCEPT"}  # plain dict, not DetectionOutcome

        self.assert_fails(Bad, "must return a DetectionOutcome")

    def test_missing_verify_method(self):
        class NoVerify:
            pass

        self.assert_fails(NoVerify, "no callable .verify")

    def test_constructor_raises(self):
        class Explodes:
            def __init__(self):
                raise RuntimeError("db not configured")

        self.assert_fails(Explodes, "raised")

    def test_verify_raises_on_legitimate_input(self):
        class Crashes:
            def verify(self, ctx):
                raise KeyError("some_field")

        self.assert_fails(Crashes, "raised on a legitimate context")

    def test_flags_fresh_legitimate_traffic(self):
        class TooStrict:
            def verify(self, ctx):
                return DetectionOutcome(Decision.REJECT, [ThreatType.FORGERY], [{"rule": "always"}])

        self.assert_fails(TooStrict, "flagged as attacks")

    def test_flags_inactive_replay_protection(self):
        class NoReplayProtection:
            def verify(self, ctx):
                return DetectionOutcome(Decision.ACCEPT, [], [])

        self.assert_fails(NoReplayProtection, "replay protection")

    def test_bad_decision_type(self):
        class WrongEnum:
            def verify(self, ctx):
                return DetectionOutcome(decision="ACCEPT", threats=[])  # string, not Decision

        self.assert_fails(WrongEnum, "must be a Decision enum")

    def test_bad_threats_type(self):
        class WrongThreats:
            def verify(self, ctx):
                return DetectionOutcome(decision=Decision.ACCEPT, threats=["FORGERY"])  # strings, not enums

        self.assert_fails(WrongThreats, "must be a list[ThreatType]")


if __name__ == "__main__":
    unittest.main()