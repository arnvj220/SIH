from __future__ import annotations

from typing import Any

from .base import AttackScenario, check_choice, check_number, count_errors_by_basis
from .contracts import BASES, AttackedSample, MeasurementRound, ThreatType, VerificationContext


class ChannelManipulationAttack(AttackScenario):
    attack_type = ThreatType.CHANNEL_MANIPULATION
    name = "channel_manipulation"
    description = "Disturb the simulated quantum channel so measurement statistics deviate."
    MODES = ("depolarizing", "intercept_resend", "basis_dephasing")
    defaults = {"mode": "depolarizing", "perturbation": 0.2}

    def validate(self, params: dict[str, Any]) -> None:
        check_choice("mode", params["mode"], self.MODES)
        check_number("perturbation", params["perturbation"], 0.0, 1.0, lo_open=True)

    def _perturb(self, m: MeasurementRound, mode: str, p: float) -> tuple[MeasurementRound, bool]:
        rng = self._rng
        obs = m.observed
        touched = False
        if mode == "depolarizing":
            if rng.random() < p:
                obs, touched = 1 - obs, True
        elif mode == "intercept_resend":
            if rng.random() < p:
                touched = True
                eve_basis = BASES[int(rng.integers(0, 3))]
                if eve_basis != m.basis:
                    obs = int(rng.integers(0, 2))
        elif mode == "basis_dephasing":
            if m.basis in ("X", "Y") and rng.random() < p:
                obs, touched = 1 - obs, True
        return MeasurementRound(m.index, m.basis, m.expected, obs), touched

    def execute(self, target: VerificationContext) -> list[AttackedSample]:
        mode = self.parameters["mode"]
        p = float(self.parameters["perturbation"])

        new_rounds, touched = [], 0
        for m in target.measurements:
            nm, t = self._perturb(m, mode, p)
            new_rounds.append(nm)
            touched += int(t)
        rounds_t = tuple(new_rounds)

        attacked = target.clone(
            context_id=self._new_id("ctx"),
            measurements=rounds_t,
            metadata=self._tag(target, attack_mode=mode, perturbation=p),
        )
        per_basis = count_errors_by_basis(rounds_t)
        evidence = {
            "mode": mode,
            "perturbation": p,
            "rounds_touched": touched,
            "baseline_error_rate": round(target.error_rate, 4),
            "observed_error_rate": round(attacked.error_rate, 4),
            "per_basis": per_basis,
        }
        self._count()
        self._evidence["last_observed_error_rate"] = evidence["observed_error_rate"]
        return [AttackedSample(attacked, True, self.attack_type, "attack", evidence)]
