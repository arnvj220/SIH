import numpy as np
import pytest

from app.quantum.states.state_utils import (
    validate_state,
    normalize_state,
    tensor_product,
    apply_gate,
)


# ============================================================
# State Validation
# ============================================================

def test_valid_single_qubit_state():
    state = np.array(
        [1 / np.sqrt(2), 1 / np.sqrt(2)],
        dtype=np.complex128,
    )

    # Should not raise an exception
    validate_state(state)


def test_valid_two_qubit_state():
    state = np.array(
        [1 / np.sqrt(2), 0, 0, 1 / np.sqrt(2)],
        dtype=np.complex128,
    )

    validate_state(state)


def test_rejects_non_normalized_state():
    state = np.array(
        [1, 1],
        dtype=np.complex128,
    )

    with pytest.raises(ValueError):
        validate_state(state)


def test_rejects_empty_state():
    state = np.array([], dtype=np.complex128)

    with pytest.raises(ValueError):
        validate_state(state)


def test_rejects_non_power_of_two_dimension():
    state = np.array(
        [1, 0, 0],
        dtype=np.complex128,
    )

    with pytest.raises(ValueError):
        validate_state(state)


def test_rejects_multidimensional_state():
    state = np.array(
        [[1, 0], [0, 1]],
        dtype=np.complex128,
    )

    with pytest.raises(ValueError):
        validate_state(state)


# ============================================================
# Normalization
# ============================================================

def test_normalize_state():
    state = np.array(
        [1, 1],
        dtype=np.complex128,
    )

    normalized = normalize_state(state)

    expected = np.array(
        [1 / np.sqrt(2), 1 / np.sqrt(2)],
        dtype=np.complex128,
    )

    assert np.allclose(normalized, expected)


def test_normalized_state_has_unit_norm():
    state = np.array(
        [2, 2],
        dtype=np.complex128,
    )

    normalized = normalize_state(state)

    assert np.isclose(np.linalg.norm(normalized), 1.0)


def test_normalize_zero_vector_fails():
    state = np.array(
        [0, 0],
        dtype=np.complex128,
    )

    with pytest.raises(ValueError):
        normalize_state(state)


# ============================================================
# Tensor Product
# ============================================================

def test_tensor_product_zero_zero():
    zero = np.array([1, 0], dtype=np.complex128)

    result = tensor_product(zero, zero)

    expected = np.array(
        [1, 0, 0, 0],
        dtype=np.complex128,
    )

    assert np.allclose(result, expected)


def test_tensor_product_zero_one():
    zero = np.array([1, 0], dtype=np.complex128)
    one = np.array([0, 1], dtype=np.complex128)

    result = tensor_product(zero, one)

    expected = np.array(
        [0, 1, 0, 0],
        dtype=np.complex128,
    )

    assert np.allclose(result, expected)


def test_tensor_product_one_zero():
    zero = np.array([1, 0], dtype=np.complex128)
    one = np.array([0, 1], dtype=np.complex128)

    result = tensor_product(one, zero)

    expected = np.array(
        [0, 0, 1, 0],
        dtype=np.complex128,
    )

    assert np.allclose(result, expected)


def test_tensor_product_one_one():
    one = np.array([0, 1], dtype=np.complex128)

    result = tensor_product(one, one)

    expected = np.array(
        [0, 0, 0, 1],
        dtype=np.complex128,
    )

    assert np.allclose(result, expected)


def test_tensor_product_preserves_normalization():
    plus = np.array(
        [1 / np.sqrt(2), 1 / np.sqrt(2)],
        dtype=np.complex128,
    )

    result = tensor_product(plus, plus)

    assert np.isclose(np.linalg.norm(result), 1.0)


# ============================================================
# Gate Application
# ============================================================

def test_apply_x_to_zero():
    X = np.array(
        [
            [0, 1],
            [1, 0],
        ],
        dtype=np.complex128,
    )

    zero = np.array([1, 0], dtype=np.complex128)

    result = apply_gate(X, zero)

    expected = np.array([0, 1], dtype=np.complex128)

    assert np.allclose(result, expected)


def test_apply_x_to_one():
    X = np.array(
        [
            [0, 1],
            [1, 0],
        ],
        dtype=np.complex128,
    )

    one = np.array([0, 1], dtype=np.complex128)

    result = apply_gate(X, one)

    expected = np.array([1, 0], dtype=np.complex128)

    assert np.allclose(result, expected)


def test_apply_h_to_zero():
    H = (1 / np.sqrt(2)) * np.array(
        [
            [1, 1],
            [1, -1],
        ],
        dtype=np.complex128,
    )

    zero = np.array([1, 0], dtype=np.complex128)

    result = apply_gate(H, zero)

    expected = np.array(
        [1 / np.sqrt(2), 1 / np.sqrt(2)],
        dtype=np.complex128,
    )

    assert np.allclose(result, expected)


def test_apply_z_to_one():
    Z = np.array(
        [
            [1, 0],
            [0, -1],
        ],
        dtype=np.complex128,
    )

    one = np.array([0, 1], dtype=np.complex128)

    result = apply_gate(Z, one)

    expected = np.array([0, -1], dtype=np.complex128)

    assert np.allclose(result, expected)


# ============================================================
# Invalid Gate Operations
# ============================================================

def test_rejects_non_square_gate():
    gate = np.array(
        [[1, 0, 0], [0, 1, 0]],
        dtype=np.complex128,
    )

    state = np.array([1, 0], dtype=np.complex128)

    with pytest.raises(ValueError):
        apply_gate(gate, state)


def test_rejects_incompatible_gate():
    gate = np.eye(4, dtype=np.complex128)
    state = np.array([1, 0], dtype=np.complex128)

    with pytest.raises(ValueError):
        apply_gate(gate, state)