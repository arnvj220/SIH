import numpy as np
import pytest

from app.quantum.measurements.evidence import QuantumEvidence
from app.quantum.states.pauli_states import zero_state


def test_quantum_evidence_stores_all_fields():
    input_state = zero_state()
    before = np.array(
        [1.0, 0.0],
        dtype=np.complex128,
    )
    after = np.array(
        [1.0, 0.0],
        dtype=np.complex128,
    )

    evidence = QuantumEvidence(
        input_state=input_state,
        measurement_bits="00",
        correction_bits="00",
        correction_operator="I",
        bob_state_before_correction=before,
        bob_state_after_correction=after,
        seed=42,
    )

    assert np.allclose(evidence.input_state, input_state)
    assert evidence.measurement_bits == "00"
    assert evidence.correction_bits == "00"
    assert evidence.correction_operator == "I"
    assert np.allclose(evidence.bob_state_before_correction, before)
    assert np.allclose(evidence.bob_state_after_correction, after)
    assert evidence.seed == 42


def test_seed_can_be_none():
    evidence = QuantumEvidence(
        input_state=zero_state(),
        measurement_bits="01",
        correction_bits="01",
        correction_operator="X",
        bob_state_before_correction=zero_state(),
        bob_state_after_correction=zero_state(),
        seed=None,
    )

    assert evidence.seed is None


def test_evidence_is_immutable():
    evidence = QuantumEvidence(
        input_state=zero_state(),
        measurement_bits="00",
        correction_bits="00",
        correction_operator="I",
        bob_state_before_correction=zero_state(),
        bob_state_after_correction=zero_state(),
        seed=42,
    )

    with pytest.raises(AttributeError):
        evidence.measurement_bits = "01"