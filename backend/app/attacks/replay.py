from __future__ import annotations

from typing import Any

from .base import AttackScenario, check_choice, check_number
from .contracts import AttackedSample, ThreatType, VerificationContext


class ReplayAttack(AttackScenario):
    attack_type = ThreatType.REPLAY
    name = "replay"
    description = "Capture a valid transaction and re-submit it one or more times."
    MODES = ("exact", "session_reuse")
    defaults = {"mode": "exact", "replay_count": 3, "delay_seconds": 30.0}

    def initialize(self) -> None:
        super().initialize()
        self._captured: dict[str, VerificationContext] = {}

    def validate(self, params: dict[str, Any]) -> None:
        check_choice("mode", params["mode"], self.MODES)
        check_number("replay_count", params["replay_count"], 1, 1000, integer=True)
        check_number("delay_seconds", params["delay_seconds"], 0.0, 10 * 365 * 86400.0)

    def capture(self, ctx: VerificationContext) -> None:
        """The attacker's 'network tap': store a copy of a valid transaction."""
        self._captured[ctx.context_id] = ctx.clone()

    def execute(self, target: VerificationContext) -> list[AttackedSample]:
        mode = self.parameters["mode"]
        count = int(self.parameters["replay_count"])
        delay = float(self.parameters["delay_seconds"])

        self.capture(target)
        original = self._captured[target.context_id]

        samples = [
            AttackedSample(
                original.clone(),
                is_attack=False,
                expected_threat=ThreatType.NONE,
                role="setup",
                evidence={"note": "original transaction, submit first"},
            )
        ]
        for i in range(1, count + 1):
            changes: dict[str, Any] = {
                "context_id": self._new_id("ctx"),
                "received_at": original.received_at + delay * i,
                "metadata": self._tag(
                    original, attack_mode=mode, replay_of=original.context_id, replay_number=i
                ),
            }
            if mode == "session_reuse":
                changes["nonce"] = self._new_id("nonce", 8)
            samples.append(
                AttackedSample(
                    original.clone(**changes),
                    is_attack=True,
                    expected_threat=self.attack_type,
                    role="attack",
                    evidence={
                        "mode": mode,
                        "replay_of": original.context_id,
                        "replay_number": i,
                        "delay_after_original_s": delay * i,
                    },
                )
            )
        self._count(len(samples))
        self._evidence["captured_total"] = len(self._captured)
        return samples
