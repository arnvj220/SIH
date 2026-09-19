from __future__ import annotations

from typing import Any

from .base import AttackConfigError, AttackScenario, check_choice, check_number, randomize_rounds
from .contracts import AttackedSample, ThreatType, VerificationContext, derive_auth_fingerprint


class ImpersonationAttack(AttackScenario):
    attack_type = ThreatType.IMPERSONATION
    name = "impersonation"
    description = "Act as another signer: swap the identity or present the wrong credential."
    MODES = ("identity_swap", "stolen_identity")
    defaults = {
        "mode": "identity_swap",
        "attacker_id": "usr_mallory",
        "measurement_mismatch": 0.0,
    }

    def validate(self, params: dict[str, Any]) -> None:
        check_choice("mode", params["mode"], self.MODES)
        if not isinstance(params["attacker_id"], str) or not params["attacker_id"]:
            raise AttackConfigError("attacker_id must be a non-empty string")
        check_number("measurement_mismatch", params["measurement_mismatch"], 0.0, 1.0)

    def execute(self, target: VerificationContext) -> list[AttackedSample]:
        mode = self.parameters["mode"]
        attacker = self.parameters["attacker_id"]
        if attacker == target.expected_signer_id:
            raise AttackConfigError(
                "attacker_id equals the victim's id; an attacker cannot impersonate themselves"
            )

        changes: dict[str, Any] = {
            "context_id": self._new_id("ctx"),
            "auth_fingerprint": derive_auth_fingerprint(attacker),
        }
        if mode == "identity_swap":
            changes["signer_id"] = attacker
        # stolen_identity keeps signer_id == victim but with the attacker's credential

        mismatch = self.parameters["measurement_mismatch"]
        changed = 0
        if mismatch > 0:
            changes["measurements"], changed = randomize_rounds(
                self._rng, target.measurements, mismatch
            )
        changes["metadata"] = self._tag(target, attack_mode=mode, attacker_id=attacker)

        forged = target.clone(**changes)
        self._count()
        return [
            AttackedSample(
                forged,
                True,
                self.attack_type,
                "attack",
                {
                    "mode": mode,
                    "victim": target.expected_signer_id,
                    "attacker": attacker,
                    "claimed_signer": forged.signer_id,
                    "rounds_actually_changed": changed,
                },
            )
        ]
