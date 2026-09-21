from app.detection.decision import combine_decisions


def test_no_rules_accept():
    assert combine_decisions(any_triggered=False) == "ACCEPT"


def test_any_rule_reject():
    assert combine_decisions(any_triggered=True) == "REJECT"