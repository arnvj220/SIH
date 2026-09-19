from __future__ import annotations

from typing import Any

from .base import AttackConfigError, AttackScenario, check_choice
from .contracts import AttackedSample, ThreatType, VerificationContext


class UnauthorizedVerificationAttack(AttackScenario):
    attack_type = ThreatType.UNAUTHORIZED_VERIFICATION
    name = "unauthorized_verification"
    description = "Verification requested by an unregistered or revoked verifier."
    MODES = ("unregistered", "revoked")
    defaults = {"mode": "unregistered", "revoked_verifiers": ("ver_revoked_01", "ver_revoked_02")}

    def validate(self, params: dict[str, Any]) -> None:
        check_choice("mode", params["mode"], self.MODES)
        revoked = params["revoked_verifiers"]
        if (
            not isinstance(revoked, (list, tuple))
            or not revoked
            or not all(isinstance(v, str) and v for v in revoked)
        ):
            raise AttackConfigError("'revoked_verifiers' must be a non-empty list of strings")

    def execute(self, target: VerificationContext) -> list[AttackedSample]:
        mode = self.parameters["mode"]
        if mode == "revoked":
            revoked = list(self.parameters["revoked_verifiers"])
            verifier_id = revoked[int(self._rng.integers(0, len(revoked)))]
        else:
            verifier_id = self._new_id("ver_rogue")

        forged = target.clone(
            context_id=self._new_id("ctx"),
            verifier_id=verifier_id,
            metadata=self._tag(target, attack_mode=mode, rogue_verifier=verifier_id),
        )
        self._count()
        return [
            AttackedSample(
                forged,
                True,
                self.attack_type,
                "attack",
                {"mode": mode, "verifier_id": verifier_id, "original_verifier": target.verifier_id},
            )
        ]
