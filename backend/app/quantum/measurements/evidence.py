"""
Structured evidence produced by the quantum simulation layer.

This module stores observable/protocol information that can be passed
to downstream QDS verification and security-analysis components.

It does NOT make security decisions.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..states.state_utils import ComplexVector


@dataclass(frozen=True)
class QuantumEvidence:
    """
    Evidence produced by one quantum teleportation run.

    Attributes:
        input_state:
            Alice's original unknown qubit state.

        measurement_bits:
            Alice's two classical measurement bits.

        correction_bits:
            Same two bits used to determine Bob's correction.

        correction_operator:
            Name of the Pauli correction applied to Bob's qubit.

        bob_state_before_correction:
            Bob's state immediately after Alice's measurement.

        bob_state_after_correction:
            Bob's state after the Pauli correction.

        seed:
            Random seed used for reproducibility.
    """

    input_state: ComplexVector
    measurement_bits: str
    correction_bits: str
    correction_operator: str
    bob_state_before_correction: ComplexVector
    bob_state_after_correction: ComplexVector
    seed: int | None