from __future__ import annotations

from typing import Any

from .base import AttackScenario, check_choice, check_number, randomize_rounds
from .contracts import AttackedSample, ThreatType, VerificationContext, sha256_hex


class ForgeryAttack(AttackScenario):
    attack_type = ThreatType.FORGERY
    name = "forgery"
    description = (
        "Forge or alter a signature: tamper with the signed message or replace "
        "measurement outcomes with guesses."
    )
    MODES = ("message_tamper", "signature_alter", "blind_guess")
    defaults = {"mode": "signature_alter", "modified_fraction": 0.8}

    def validate(self, params: dict[str, Any]) -> None:
        check_choice("mode", params["mode"], self.MODES)
        check_number("modified_fraction", params["modified_fraction"], 0.0, 1.0, lo_open=True)

    def execute(self, target: VerificationContext) -> list[AttackedSample]:
        mode = self.parameters["mode"]
        evidence: dict[str, Any] = {"mode": mode}
        changes: dict[str, Any] = {"context_id": self._new_id("ctx")}

        if mode == "message_tamper":
            changes["message_digest"] = sha256_hex(f"forged:{target.message_digest}")
            evidence["digest_tampered"] = True
        else:
            fraction = 1.0 if mode == "blind_guess" else self.parameters["modified_fraction"]
            new_rounds, changed = randomize_rounds(self._rng, target.measurements, fraction)
            changes["measurements"] = new_rounds
            evidence.update(
                modified_fraction=fraction,
                rounds_actually_changed=changed,
                expected_added_error_rate=round(0.5 * fraction, 4),
            )

        changes["metadata"] = self._tag(target, attack_mode=mode)
        forged = target.clone(**changes)
        evidence["observed_error_rate"] = round(forged.error_rate, 4)
        self._count()
        return [AttackedSample(forged, True, self.attack_type, "attack", evidence)]
