"""
Quantum teleportation protocol.

Flow:

    1. Prepare |ψ> ⊗ |00>
    2. Create Bell pair between q1 and q2
    3. Entangle q0 with q1
    4. Measure q0 and q1
    5. Determine Bob's Pauli correction
    6. Apply correction to q2
    7. Return structured quantum evidence

Qubit ordering:

    q0 = Alice's unknown qubit
    q1 = Alice's Bell-pair qubit
    q2 = Bob's Bell-pair qubit
"""

from __future__ import annotations

import numpy as np

from ..measurements.evidence import QuantumEvidence
from ..states.state_utils import ComplexVector, apply_gate
from .circuit import prepare_teleportation_state
from .corrections import get_correction


CORRECTION_NAMES = {
    "00": "I",
    "01": "X",
    "10": "Z",
    "11": "XZ",
}


def _measure_first_two_qubits(
    state: ComplexVector,
    seed: int | None = None,
) -> tuple[str, ComplexVector]:
    """
    Measure Alice's two qubits.

    Returns:
        measurement_bits:
            Alice's two classical measurement bits.

        bob_state:
            Bob's normalized post-measurement state before correction.
    """
    probabilities = {}

    for bits in ("00", "01", "10", "11"):
        indices = [
            index
            for index in range(8)
            if format(index, "03b")[:2] == bits
        ]

        probability = sum(
            abs(state[index]) ** 2
            for index in indices
        )

        probabilities[bits] = float(probability)

    rng = np.random.default_rng(seed)

    measurement_bits = rng.choice(
        list(probabilities.keys()),
        p=list(probabilities.values()),
    )

    bob_amplitudes = np.zeros(2, dtype=np.complex128)

    for bob_bit in ("0", "1"):
        index = int(measurement_bits + bob_bit, 2)
        bob_amplitudes[int(bob_bit)] = state[index]

    norm = np.linalg.norm(bob_amplitudes)

    if np.isclose(norm, 0.0):
        raise ValueError(
            "Selected measurement branch has zero probability."
        )

    bob_state = bob_amplitudes / norm

    return measurement_bits, bob_state


def teleport(
    unknown_state: ComplexVector,
    seed: int | None = None,
) -> QuantumEvidence:
    """
    Teleport an unknown single-qubit state.

    Returns structured evidence describing the quantum operation.

    Args:
        unknown_state: Alice's input state |ψ>.
        seed: Optional random seed for reproducible measurement.

    Returns:
        QuantumEvidence containing the measurement result,
        correction, and Bob's state before and after correction.
    """
    state = prepare_teleportation_state(unknown_state)

    measurement_bits, bob_state_before_correction = (
        _measure_first_two_qubits(
            state,
            seed=seed,
        )
    )

    correction = get_correction(measurement_bits)

    bob_state_after_correction = apply_gate(
        correction,
        bob_state_before_correction,
    )

    return QuantumEvidence(
        input_state=unknown_state.copy(),
        measurement_bits=measurement_bits,
        correction_bits=measurement_bits,
        correction_operator=CORRECTION_NAMES[measurement_bits],
        bob_state_before_correction=bob_state_before_correction.copy(),
        bob_state_after_correction=bob_state_after_correction.copy(),
        seed=seed,
    )