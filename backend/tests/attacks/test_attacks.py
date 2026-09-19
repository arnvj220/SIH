import unittest

from app.attacks.contracts import ThreatType
from app.attacks.baseline import BaselineConfig, BaselineFactory
from app.attacks.contracts import derive_auth_fingerprint
from app.attacks.registry import create_attack


def legit(seed=1, rounds=400, noise=0.01):
    return BaselineFactory(
        BaselineConfig(
            rounds=rounds,
            natural_error_rate=noise
        ),
        seed=seed
    ).make_legitimate()


class BaselineTests(unittest.TestCase):

    def test_deterministic_for_same_seed(self):
        self.assertEqual(
            legit(5).to_dict(),
            legit(5).to_dict()
        )

    def test_legit_is_internally_consistent(self):
        c = legit()

        self.assertEqual(c.signer_id, c.expected_signer_id)
        self.assertEqual(c.message_digest, c.signed_digest)
        self.assertEqual(
            c.auth_fingerprint,
            derive_auth_fingerprint(c.signer_id)
        )


class ForgeryTests(unittest.TestCase):

    def test_message_tamper_changes_digest_only(self):
        target = legit()

        result = create_attack(
            "forgery",
            1,
            {"mode": "message_tamper"}
        ).execute(target)[0]

        self.assertNotEqual(
            result.context.message_digest,
            result.context.signed_digest
        )

        self.assertEqual(
            result.context.measurements,
            target.measurements
        )

        self.assertTrue(result.is_attack)
        self.assertEqual(
            result.expected_threat,
            ThreatType.FORGERY
        )


if __name__ == "__main__":
    unittest.main()