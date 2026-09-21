from app.detection.statistics import (
    error_rate,
    measurement_deviation,
    outcome_probabilities,
    total_variation_distance,
)


def test_error_rate_empty():
    assert error_rate([], []) == 0.0


def test_error_rate_no_errors():
    assert error_rate([0, 0, 1], [0, 0, 1]) == 0.0


def test_error_rate_half():
    assert error_rate([0, 0, 0, 0], [0, 0, 1, 1]) == 0.5


def test_outcome_probabilities_balanced():
    probs = outcome_probabilities([0, 1, 0, 1])
    assert probs == {0: 0.5, 1: 0.5}


def test_tv_distance_identical():
    p = {0: 0.5, 1: 0.5}
    assert total_variation_distance(p, p) == 0.0


def test_tv_distance_disjoint():
    assert total_variation_distance({0: 1.0, 1: 0.0}, {0: 0.0, 1: 1.0}) == 1.0


def test_measurement_deviation_clean():
    # 100 rounds, all 0, expected p0 = 1.0 → no deviation
    assert measurement_deviation([0] * 100, expected_p0=1.0) == 0.0


def test_measurement_deviation_shifted():
    # 100 rounds, all 1, expected p0 = 1.0 → maximum deviation
    assert measurement_deviation([1] * 100, expected_p0=1.0) == 1.0