import copy
import unittest

from app.attacks import (
    ATTACK_REGISTRY,
    AttackConfigError,
    UnknownAttackError,
    create_attack,
    describe_attacks,
)
from app.attacks.baseline import BaselineConfig, BaselineFactory
from app.attacks.contracts import derive_auth_fingerprint


def legit(seed=1, rounds=400, noise=0.01):
    return BaselineFactory(
        BaselineConfig(
            rounds=rounds,
            natural_error_rate=noise,
        ),
        seed=seed,
    ).make_legitimate()


class RegistryEdgeCaseTests(unittest.TestCase):

    def test_every_registered_attack_can_be_created(self):
        for name in ATTACK_REGISTRY:
            with self.subTest(attack=name):
                attack = create_attack(name)
                self.assertIsNotNone(attack)

    def test_unknown_attack_is_rejected(self):
        with self.assertRaises(UnknownAttackError):
            create_attack("invalid_attack")

    def test_empty_attack_name_is_rejected(self):
        with self.assertRaises(UnknownAttackError):
            create_attack("")

    def test_describe_attacks_matches_registry(self):
        described = {item["name"] for item in describe_attacks()}
        registered = set(ATTACK_REGISTRY)

        self.assertEqual(described, registered)


class BaselineEdgeCaseTests(unittest.TestCase):

    def test_zero_noise_produces_zero_or_negligible_errors(self):
        context = legit(
            seed=10,
            rounds=1000,
            noise=0.0,
        )

        self.assertEqual(context.error_rate, 0.0)

    def test_same_seed_same_context_id(self):
        first = legit(seed=123)
        second = legit(seed=123)

        self.assertEqual(
            first.context_id,
            second.context_id,
        )

    def test_different_seeds_produce_different_context_ids(self):
        first = legit(seed=123)
        second = legit(seed=124)

        self.assertNotEqual(
            first.context_id,
            second.context_id,
        )

    def test_auth_fingerprint_is_deterministic(self):
        context = legit()

        first = derive_auth_fingerprint(context.signer_id)
        second = derive_auth_fingerprint(context.signer_id)

        self.assertEqual(first, second)


class AttackIsolationTests(unittest.TestCase):

    def test_attack_does_not_modify_target(self):
        for name in ATTACK_REGISTRY:
            with self.subTest(attack=name):
                target = legit()
                before = copy.deepcopy(target.to_dict())

                create_attack(name, seed=42).execute(target)

                after = target.to_dict()

                self.assertEqual(
                    before,
                    after,
                    f"{name} modified the original target",
                )

    def test_multiple_attacks_do_not_share_target_state(self):
        target_a = legit(seed=1)
        target_b = legit(seed=1)

        create_attack("forgery", seed=10).execute(target_a)

        self.assertEqual(
            target_a.to_dict(),
            target_b.to_dict(),
        )


class ReproducibilityTests(unittest.TestCase):

    def test_same_attack_and_seed_are_reproducible(self):
        target_a = legit(seed=50)
        target_b = legit(seed=50)

        attack_a = create_attack("forgery", seed=99)
        attack_b = create_attack("forgery", seed=99)

        result_a = attack_a.execute(target_a)[0].context.to_dict()
        result_b = attack_b.execute(target_b)[0].context.to_dict()

        self.assertEqual(result_a, result_b)

    def test_different_attack_seeds_can_produce_different_results(self):
        target_a = legit(seed=50)
        target_b = legit(seed=50)

        attack_a = create_attack("forgery", seed=1)
        attack_b = create_attack("forgery", seed=2)

        result_a = attack_a.execute(target_a)[0].context.to_dict()
        result_b = attack_b.execute(target_b)[0].context.to_dict()

        self.assertNotEqual(result_a, result_b)


class ConfigurationEdgeCaseTests(unittest.TestCase):

    def test_none_parameters_are_allowed(self):
        for name in ATTACK_REGISTRY:
            with self.subTest(attack=name):
                attack = create_attack(
                    name,
                    seed=1,
                    parameters=None,
                )

                self.assertIsNotNone(attack)

    def test_empty_parameters_are_allowed_when_defaults_exist(self):
        for name in ATTACK_REGISTRY:
            with self.subTest(attack=name):
                attack = create_attack(
                    name,
                    seed=1,
                    parameters={},
                )

                self.assertIsNotNone(attack)

    def test_unknown_parameter_is_rejected(self):
        with self.assertRaises(AttackConfigError):
            create_attack(
                "forgery",
                seed=1,
                parameters={"this_parameter_does_not_exist": 123},
            )


class ForgeryEdgeCaseTests(unittest.TestCase):

    def test_message_tampering_changes_message_digest(self):
        target = legit()

        result = create_attack(
            "forgery",
            seed=1,
            parameters={"mode": "message_tamper"},
        ).execute(target)[0]

        self.assertNotEqual(
            result.context.message_digest,
            target.message_digest,
        )

    def test_message_tampering_does_not_change_measurements(self):
        target = legit()

        result = create_attack(
            "forgery",
            seed=1,
            parameters={"mode": "message_tamper"},
        ).execute(target)[0]

        self.assertEqual(
            result.context.measurements,
            target.measurements,
        )

    def test_forgery_is_marked_as_attack(self):
        result = create_attack(
            "forgery",
            seed=1,
            parameters={"mode": "message_tamper"},
        ).execute(legit())[0]

        self.assertTrue(result.is_attack)


class ResetTests(unittest.TestCase):

    def test_reset_does_not_change_parameters(self):
        attack = create_attack(
            "forgery",
            seed=10,
            parameters={"mode": "message_tamper"},
        )

        before = dict(attack.parameters)

        attack.reset()

        self.assertEqual(
            attack.parameters,
            before,
        )

    def test_reset_makes_execution_reproducible(self):
        target = legit(seed=100)

        attack = create_attack(
            "forgery",
            seed=20,
            parameters={"mode": "message_tamper"},
        )

        first = attack.execute(target)[0].context.to_dict()

        attack.reset()

        second = attack.execute(target)[0].context.to_dict()

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()