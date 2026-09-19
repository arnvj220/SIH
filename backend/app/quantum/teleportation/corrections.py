"""
Pauli correction operations used in quantum teleportation.

The two classical measurement bits determine which correction
Bob must apply to his qubit.

Mapping:
    00 -> I
    01 -> X
    10 -> Z
    11 -> XZ
"""

from __future__ import annotations

from ..gates import IDENTITY, PAULI_X, PAULI_Z
from ..states.state_utils import ComplexMatrix


CORRECTION_OPERATORS: dict[str, ComplexMatrix] = {
    "00": IDENTITY,
    "01": PAULI_X,
    "10": PAULI_Z,
    "11": PAULI_X @ PAULI_Z,
}


def get_correction(measurement_bits: str) -> ComplexMatrix:
    """
    Return the Pauli correction corresponding to two
    classical measurement bits.

    Args:
        measurement_bits: A two-bit string: 00, 01, 10, or 11.

    Returns:
        The corresponding 2x2 correction matrix.

    Raises:
        ValueError: If the input is not a valid two-bit result.
    """
    if measurement_bits not in CORRECTION_OPERATORS:
        raise ValueError(
            "Measurement bits must be one of: 00, 01, 10, 11."
        )

    return CORRECTION_OPERATORS[measurement_bits].copy()