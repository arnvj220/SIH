import copy
import unittest

from app.attacks import AttackConfigError, ThreatType, UnknownAttackError, create_attack, describe_attacks
from app.attacks.baseline import BaselineConfig, BaselineFactory
from app.attacks.contracts import derive_auth_fingerprint


def legit(seed=1, rounds=400, noise=0.01):
    return BaselineFactory(BaselineConfig(rounds=rounds, natural_error_rate=noise), seed=seed).make_legitimate()


class BaselineTests(unittest.TestCase):
    def test_deterministic_for_same_seed(self):
        self.assertEqual(legit(5).to_dict(), legit(5).to_dict())

    def test_different_seed_differs(self):
        self.assertNotEqual(legit(5).context_id, legit(6).context_id)

    def test_natural_noise_is_low(self):
        self.assertLess(legit(rounds=2000).error_rate, 0.03)

    def test_legit_is_internally_consistent(self):
        c = legit()
        self.assertEqual(c.signer_id, c.expected_signer_id)
        self.assertEqual(c.message_digest, c.signed_digest)
        self.assertEqual(c.auth_fingerprint, derive_auth_fingerprint(c.signer_id))


class IsolationTests(unittest.TestCase):
    """SR-005: attacks must never mutate the target."""

    def test_no_attack_mutates_target(self):
        from app.attacks import ATTACK_REGISTRY

        for name in ATTACK_REGISTRY:
            target = legit()
            before = copy.deepcopy(target.to_dict())
            create_attack(name, seed=3).execute(target)
            self.assertEqual(before, target.to_dict(), f"{name} mutated its target")


class ForgeryTests(unittest.TestCase):
    def test_message_tamper_changes_digest_only(self):
        t = legit()
        s = create_attack("forgery", 1, {"mode": "message_tamper"}).execute(t)[0]
        self.assertNotEqual(s.context.message_digest, s.context.signed_digest)
        self.assertEqual(s.context.measurements, t.measurements)
        self.assertTrue(s.is_attack)
        self.assertEqual(s.expected_threat, ThreatType.FORGERY)

    def test_blind_guess_error_near_half(self):
        s = create_attack("forgery", 1, {"mode": "blind_guess"}).execute(legit(rounds=4000))[0]
        self.assertAlmostEqual(s.context.error_rate, 0.5, delta=0.05)

    def test_signature_alter_scales_with_fraction(self):
        t = legit(rounds=4000, noise=0.0)
        low = create_attack("forgery", 1, {"modified_fraction": 0.2}).execute(t)[0].context.error_rate
        high = create_attack("forgery", 1, {"modified_fraction": 0.8}).execute(t)[0].context.error_rate
        self.assertLess(low, high)
        self.assertAlmostEqual(high, 0.4, delta=0.04)


class ReplayTests(unittest.TestCase):
    def test_setup_first_then_replays(self):
        t = legit()
        samples = create_attack("replay", 1, {"replay_count": 4}).execute(t)
        self.assertEqual(len(samples), 5)
        self.assertEqual(samples[0].role, "setup")
        self.assertFalse(samples[0].is_attack)
        self.assertTrue(all(s.is_attack for s in samples[1:]))

    def test_exact_reuses_session_and_nonce(self):
        t = legit()
        replays = create_attack("replay", 1, {"mode": "exact"}).execute(t)[1:]
        for s in replays:
            self.assertEqual(s.context.session_id, t.session_id)
            self.assertEqual(s.context.nonce, t.nonce)
            self.assertNotEqual(s.context.context_id, t.context_id)

    def test_session_reuse_changes_nonce_only(self):
        t = legit()
        replays = create_attack("replay", 1, {"mode": "session_reuse"}).execute(t)[1:]
        for s in replays:
            self.assertEqual(s.context.session_id, t.session_id)
            self.assertNotEqual(s.context.nonce, t.nonce)

    def test_delay_shifts_arrival_time(self):
        t = legit()
        replays = create_attack("replay", 1, {"delay_seconds": 100, "replay_count": 2}).execute(t)[1:]
        self.assertEqual([s.context.received_at - t.received_at for s in replays], [100, 200])


class ImpersonationTests(unittest.TestCase):
    def test_identity_swap(self):
        t = legit()
        c = create_attack("impersonation", 1, {"mode": "identity_swap"}).execute(t)[0].context
        self.assertEqual(c.signer_id, "usr_mallory")
        self.assertNotEqual(c.signer_id, c.expected_signer_id)

    def test_stolen_identity_keeps_claim_but_wrong_credential(self):
        t = legit()
        c = create_attack("impersonation", 1, {"mode": "stolen_identity"}).execute(t)[0].context
        self.assertEqual(c.signer_id, t.signer_id)
        self.assertNotEqual(c.auth_fingerprint, derive_auth_fingerprint(t.signer_id))

    def test_attacker_cannot_be_victim(self):
        t = legit()
        atk = create_attack("impersonation", 1, {"attacker_id": t.expected_signer_id})
        with self.assertRaises(AttackConfigError):
            atk.execute(t)


class UnauthorizedTests(unittest.TestCase):
    def test_unregistered_and_revoked(self):
        t = legit()
        a = create_attack("unauthorized_verification", 1, {"mode": "unregistered"}).execute(t)[0].context
        self.assertTrue(a.verifier_id.startswith("ver_rogue_"))
        b = create_attack(
            "unauthorized_verification", 1, {"mode": "revoked", "revoked_verifiers": ["ver_x"]}
        ).execute(t)[0].context
        self.assertEqual(b.verifier_id, "ver_x")


class ChannelTests(unittest.TestCase):
    N = 6000

    def rate(self, params):
        t = legit(rounds=self.N, noise=0.0)
        return create_attack("channel_manipulation", 2, params).execute(t)[0]

    def test_depolarizing_rate_matches_perturbation(self):
        s = self.rate({"mode": "depolarizing", "perturbation": 0.2})
        self.assertAlmostEqual(s.context.error_rate, 0.2, delta=0.03)

    def test_intercept_resend_rate_is_p_over_3(self):
        s = self.rate({"mode": "intercept_resend", "perturbation": 0.6})
        self.assertAlmostEqual(s.context.error_rate, 0.6 / 3, delta=0.03)

    def test_dephasing_only_hits_x_and_y(self):
        s = self.rate({"mode": "basis_dephasing", "perturbation": 0.5})
        pb = s.evidence["per_basis"]
        self.assertEqual(pb["Z"]["errors"], 0)
        self.assertGreater(pb["X"]["error_rate"], 0.4)
        self.assertGreater(pb["Y"]["error_rate"], 0.4)

    def test_message_identity_session_untouched(self):
        t = legit()
        c = create_attack("channel_manipulation", 1).execute(t)[0].context
        for f in ("signer_id", "message_digest", "session_id", "nonce", "verifier_id"):
            self.assertEqual(getattr(c, f), getattr(t, f))


class ConfigValidationTests(unittest.TestCase):
    def test_unknown_parameter_rejected(self):
        with self.assertRaises(AttackConfigError):
            create_attack("forgery", 1, {"bogus": 1})

    def test_bad_values_rejected(self):
        bad = [
            ("forgery", {"mode": "nope"}),
            ("forgery", {"modified_fraction": 0}),
            ("forgery", {"modified_fraction": 1.5}),
            ("replay", {"replay_count": 0}),
            ("replay", {"replay_count": 2.5}),
            ("replay", {"delay_seconds": -1}),
            ("channel_manipulation", {"perturbation": 0}),
            ("channel_manipulation", {"perturbation": True}),
            ("unauthorized_verification", {"revoked_verifiers": []}),
        ]
        for name, params in bad:
            with self.subTest(name=name, params=params), self.assertRaises(AttackConfigError):
                create_attack(name, 1, params)

    def test_unknown_attack(self):
        with self.assertRaises(UnknownAttackError):
            create_attack("does_not_exist")

    def test_reset_reproduces_output(self):
        t = legit()
        atk = create_attack("channel_manipulation", 9, {"perturbation": 0.3})
        first = atk.execute(t)[0].context.to_dict()
        atk.reset()
        self.assertEqual(atk.parameters["perturbation"], 0.3)  # params survive reset
        self.assertEqual(first, atk.execute(t)[0].context.to_dict())

    def test_describe_attacks_covers_all_five(self):
        names = {d["name"] for d in describe_attacks()}
        self.assertEqual(
            names,
            {"forgery", "impersonation", "replay", "unauthorized_verification", "channel_manipulation"},
        )


if __name__ == "__main__":
    unittest.main()
