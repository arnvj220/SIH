import unittest

from app.attacks import AttackConfigError, AttackExperimentConfig, Decision, DetectionOutcome, run_attack_experiment
from app.attacks.reference_verifier import ReferenceVerifier


def run(attack, params=None, n=100, seed=7, **kw):
    """These tests target the STUB verifier; engine tests live in test_engine.py."""
    cfg = AttackExperimentConfig(attack, params or {}, n_targets=n, seed=seed, **kw)
    return run_attack_experiment(cfg, ReferenceVerifier)


class DetectionTests(unittest.TestCase):
    """Acceptance criteria AC-002..AC-005 against the reference verifier."""

    def test_each_default_attack_is_fully_detected(self):
        for name in ("forgery", "impersonation", "replay", "unauthorized_verification", "channel_manipulation"):
            with self.subTest(attack=name):
                m = run(name).metrics
                self.assertEqual(m["detection_rate"], 1.0)
                self.assertEqual(m["false_negative_rate"], 0.0)
                self.assertEqual(m["classification_rate"], 1.0)

    def test_no_false_positives_on_legitimate_traffic(self):
        m = run("forgery", n=300).metrics
        self.assertEqual(m["false_positives"], 0)
        self.assertGreater(m["benign_total"], 0)

    def test_replay_setup_is_accepted_and_replays_rejected(self):
        rep = run("replay", {"replay_count": 3}, n=20)
        setups = [r for r in rep.records if r.role == "setup"]
        replays = [r for r in rep.records if r.is_attack]
        self.assertTrue(all(r.decision == Decision.ACCEPT for r in setups))
        self.assertTrue(all(r.decision == Decision.REJECT for r in replays))
        self.assertEqual(len(replays), 60)

    def test_expired_replay_is_rejected(self):
        m = run("replay", {"delay_seconds": 10_000, "replay_count": 1}).metrics
        self.assertEqual(m["detection_rate"], 1.0)

    def test_weak_attacks_can_be_missed(self):
        """Honest evaluation: a tiny perturbation should evade the thresholds."""
        m = run("channel_manipulation", {"perturbation": 0.01}, n=200).metrics
        self.assertGreater(m["false_negative_rate"], 0.5)

    def test_detection_rate_grows_with_strength(self):
        rates = [
            run("channel_manipulation", {"perturbation": p}, n=200).metrics["detection_rate"]
            for p in (0.02, 0.08, 0.3)
        ]
        self.assertEqual(rates, sorted(rates))
        self.assertLess(rates[0], rates[-1])

    def test_measurement_only_threats_are_ambiguous_in_stub(self):
        m = run("channel_manipulation").metrics
        self.assertEqual(m["exact_classification_rate"], 0.0)  # documents the stub's limitation


class ReproducibilityTests(unittest.TestCase):
    def test_same_config_same_fingerprint(self):
        a = run("channel_manipulation", {"perturbation": 0.1}, n=50, seed=99)
        b = run("channel_manipulation", {"perturbation": 0.1}, n=50, seed=99)
        self.assertEqual(a.metrics["result_fingerprint"], b.metrics["result_fingerprint"])
        self.assertEqual(a.config.experiment_id, b.config.experiment_id)

    def test_different_seed_different_fingerprint(self):
        a = run("forgery", n=50, seed=1)
        b = run("forgery", n=50, seed=2)
        self.assertNotEqual(a.metrics["result_fingerprint"], b.metrics["result_fingerprint"])


class RobustnessTests(unittest.TestCase):
    def test_verifier_crash_fails_closed_and_is_visible(self):
        class Broken:
            def verify(self, ctx):
                raise RuntimeError("boom")

        rep = run_attack_experiment(AttackExperimentConfig("forgery", n_targets=5), lambda: Broken())
        self.assertEqual(rep.metrics["verifier_errors"], 10)  # 5 attack + 5 control
        self.assertTrue(all(r.decision == Decision.REJECT for r in rep.records))
        self.assertEqual(rep.metrics["false_positives"], 5)  # visible, not hidden

    def test_custom_verifier_plugs_in(self):
        class AcceptAll:
            def verify(self, ctx):
                return DetectionOutcome(Decision.ACCEPT)

        rep = run_attack_experiment(AttackExperimentConfig("forgery", n_targets=10), lambda: AcceptAll())
        self.assertEqual(rep.metrics["detection_rate"], 0.0)  # a blind verifier is exposed

    def test_invalid_experiment_config(self):
        for kw in ({"n_targets": 0}, {"rounds": 0}, {"natural_error_rate": 0.7}):
            with self.subTest(kw=kw), self.assertRaises(AttackConfigError):
                run_attack_experiment(AttackExperimentConfig("forgery", **kw))


class ReferenceVerifierTests(unittest.TestCase):
    def test_reset_clears_replay_state(self):
        from app.attacks.baseline import BaselineFactory

        v, ctx = ReferenceVerifier(), BaselineFactory(seed=1).make_legitimate()
        self.assertEqual(v.verify(ctx).decision, Decision.ACCEPT)
        self.assertEqual(v.verify(ctx).decision, Decision.REJECT)
        v.reset()
        self.assertEqual(v.verify(ctx).decision, Decision.ACCEPT)

    def test_every_alert_carries_evidence(self):
        """SR-003 / AC-006: no detection without rule id + numbers."""
        from app.attacks import ATTACK_REGISTRY, create_attack
        from app.attacks.baseline import BaselineFactory

        factory = BaselineFactory(seed=4)
        for name in ATTACK_REGISTRY:
            attack = create_attack(name, seed=4)
            v = ReferenceVerifier()
            for sample in attack.execute(factory.make_legitimate()):
                out = v.verify(sample.context)
                if sample.is_attack:
                    with self.subTest(attack=name):
                        self.assertTrue(out.detected)
                        self.assertTrue(out.evidence)
                        self.assertTrue(all("rule_id" in e and "metric" in e for e in out.evidence))


if __name__ == "__main__":
    unittest.main()
