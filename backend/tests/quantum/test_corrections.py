import numpy as np
import pytest

from app.quantum.gates import IDENTITY, PAULI_X, PAULI_Z
from app.quantum.teleportation.corrections import get_correction


def test_00_gives_identity():
    correction = get_correction("00")

    assert np.array_equal(correction, IDENTITY)


def test_01_gives_x():
    correction = get_correction("01")

    assert np.array_equal(correction, PAULI_X)


def test_10_gives_z():
    correction = get_correction("10")

    assert np.array_equal(correction, PAULI_Z)


def test_11_gives_xz():
    correction = get_correction("11")

    expected = PAULI_X @ PAULI_Z

    assert np.array_equal(correction, expected)


@pytest.mark.parametrize(
    "measurement_bits",
    ["0", "1", "000", "111", "", "ab", "12"],
)
def test_invalid_measurement_bits_rejected(measurement_bits):
    with pytest.raises(ValueError):
        get_correction(measurement_bits)


def test_corrections_are_2_by_2():
    for bits in ["00", "01", "10", "11"]:
        correction = get_correction(bits)

        assert correction.shape == (2, 2)