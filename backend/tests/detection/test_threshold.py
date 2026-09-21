from app.detection.thresholds import crosses


def test_greater_than():
    assert crosses(0.5, ">", 0.2) is True
    assert crosses(0.1, ">", 0.2) is False

def test_less_than_or_equal():
    assert crosses(0.2, "<=", 0.2) is True

def test_unknown_operator_raises():
    import pytest
    with pytest.raises(ValueError):
        crosses(0.5, "~=", 0.2)