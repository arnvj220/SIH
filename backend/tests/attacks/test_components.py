"""
Status board: which parts of the project are present and importable?

Run with -v:   python -m pytest tests/attacks/test_components.py -v -rs
  PASSED  = present and working
  SKIPPED = not in your checkout yet (the reason is printed), NOT a failure

The REQUIRED group is the attack engine (Arnav's scope) and must always pass.
The OPTIONAL group probes teammates' components at their real module paths so
the board tells the truth about what is actually merged.
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
    """
    Skipped (not failed) when a teammate's part is not on the path.

    Probing real module paths so the status board reflects what is merged.
    """

    def _need(self, module: str, owner: str):
        m, why = _try(module)
        if m is None:
            self.skipTest(f"{module} not available yet ({owner}): {why}")
        return m

    def test_detection_engine(self):
        """Shubh's detection engine: app/detection/engine.py."""
        m = self._need("app.detection", "Shubh")
        # Real exports: DetectionEngine, DEFAULT_RULES, ReplayStore,
        # AuthorizationStore, BaselineProfile.
        self.assertTrue(
            hasattr(m, "DetectionEngine"),
            "app.detection must export DetectionEngine",
        )

    def test_detection_stores(self):
        m = self._need("app.detection.stores", "Shubh")
        self.assertTrue(hasattr(m, "ReplayStore"))
        self.assertTrue(hasattr(m, "AuthorizationStore"))

    def test_experiments_package(self):
        """Shubh's benchmarking lives at app/experiments, not app/benchmarking."""
        m = self._need("app.experiments", "Shubh")

    def test_benchmark_runner(self):
        m = self._need("app.experiments.benchmark", "Shubh")
        self.assertTrue(hasattr(m, "run_benchmark"))
        self.assertTrue(hasattr(m, "BenchmarkMetrics"))

    def test_real_benchmark_runner(self):
        m = self._need("app.experiments.real_benchmark", "Shubh")
        self.assertTrue(hasattr(m, "run_real_benchmark"))

    def test_scenarios(self):
        """Scenario builders live at app/experiments/scenarios.py."""
        m = self._need("app.experiments.scenarios", "Shubh / attack integration")
        for name in (
            "legit_scenario",
            "forgery_scenario",
            "impersonation_scenario",
            "channel_manipulation_scenario",
            "unauthorized_scenario",
        ):
            self.assertTrue(hasattr(m, name), f"scenarios missing {name}")

    def test_quantum_adapter(self):
        self._need("app.attacks.quantum_adapter", "Arnav")

    def test_verifier_adapter_is_wired(self):
        """
        Verifies the integration seam is live: real_verifier_factory must
        return a DetectionEngine rather than raising NotImplementedError.
        """
        m = self._need("app.attacks.verifier_adapter", "Arnav")
        try:
            verifier = m.real_verifier_factory()
        except NotImplementedError:
            self.fail(
                "real_verifier_factory still raises NotImplementedError - "
                "the detection engine is present but the adapter is not wired"
            )
        except ImportError as exc:
            self.skipTest(f"detection engine not on path yet (Shubh): {exc}")
        self.assertTrue(hasattr(verifier, "verify"))

    def test_fastapi_installed(self):
        self._need("fastapi", "pip install -r requirements.txt")

    def test_api_router(self):
        """Attacks router lives at app/api/attacks.py."""
        self._need("app.api.attacks", "Rachit")

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