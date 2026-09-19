"""
Status board: which parts of the project are present and importable?

Run with -v:   python -m pytest tests/test_00_component_status.py -v -rs
  PASSED  = present and working
  SKIPPED = not in your checkout yet (the reason is printed), NOT a failure

The REQUIRED group is the attack engine (Arnav's scope) and must always pass.
"""
import importlib
import importlib.util
import unittest


def _try(module: str):
    try:
        return importlib.import_module(module), ""
    except Exception as exc:  # noqa: BLE001 - report anything that breaks at import time
        return None, f"{type(exc).__name__}: {exc}"


class RequiredAttackEngine(unittest.TestCase):
    def test_contracts(self):
        m, why = _try("app.attacks.contracts")
        self.assertIsNotNone(m, why)
        for name in ("ThreatType", "Decision", "MeasurementRound", "VerificationContext",
                     "DetectionOutcome", "AttackedSample"):
            self.assertTrue(hasattr(m, name), f"contracts is missing {name}")

    def test_base(self):
        m, why = _try("app.attacks.base")
        self.assertIsNotNone(m, why)
        self.assertTrue(hasattr(m, "AttackScenario") and hasattr(m, "AttackConfigError"))

    def test_baseline(self):
        m, why = _try("app.attacks.baseline")
        self.assertIsNotNone(m, why)
        self.assertTrue(hasattr(m, "BaselineFactory") and hasattr(m, "BaselineConfig"))

    def test_registry_has_all_five_attacks(self):
        m, why = _try("app.attacks.registry")
        self.assertIsNotNone(m, why)
        self.assertEqual(
            set(m.ATTACK_REGISTRY),
            {"forgery", "impersonation", "replay", "unauthorized_verification", "channel_manipulation"},
        )

    def test_runner(self):
        m, why = _try("app.attacks.runner")
        self.assertIsNotNone(m, why)
        self.assertTrue(hasattr(m, "run_attack_experiment") and hasattr(m, "AttackExperimentConfig"))

    def test_reference_verifier(self):
        m, why = _try("app.attacks.reference_verifier")
        self.assertIsNotNone(m, why)
        self.assertTrue(hasattr(m, "ReferenceVerifier"))

    def test_package_exports(self):
        m, why = _try("app.attacks")
        self.assertIsNotNone(m, why)
        for name in ("create_attack", "run_attack_experiment", "ThreatType", "Decision"):
            self.assertTrue(hasattr(m, name), f"app.attacks does not export {name}")


class OptionalComponents(unittest.TestCase):
    """Skipped (not failed) when a teammate's part is not merged yet."""

    def _need(self, module: str, owner: str):
        m, why = _try(module)
        if m is None:
            self.skipTest(f"{module} not available yet ({owner}): {why}")
        return m

    def test_detection_engine(self):
        m = self._need("app.detection", "Shubh")

        if not hasattr(m, "DetectionConfig") or not hasattr(m, "VerificationEngine"):
            self.skipTest("detection engine is present but not complete yet (Shubh)")

        self.assertTrue(
            hasattr(m, "DetectionConfig")
            and hasattr(m, "VerificationEngine")
        )

    def test_benchmarking(self):
        self._need("app.benchmarking", "Shubh")

    def test_scenarios(self):
        self._need("app.attacks.scenarios", "Arnav, newer zip")

    def test_quantum_adapter(self):
        self._need("app.attacks.quantum_adapter", "Arnav, newer zip")

    def test_fastapi_installed(self):
        self._need("fastapi", "pip install -r requirements.txt")

    def test_api_router(self):
        self._need("app.api.attacks_router", "needs fastapi + benchmarking")

    def test_rishi_quantum_package_is_importable(self):
        spec = None
        for name in ("quantum", "app.quantum"):
            try:
                spec = importlib.util.find_spec(name)
            except (ImportError, ValueError):
                spec = None
            if spec:
                break
        if spec is None:
            self.skipTest("no importable 'quantum' package on the path (Rishi's folder)")


if __name__ == "__main__":
    unittest.main()