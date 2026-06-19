from backend.app.processing.risk import risk_level_from_score, weighted_total


def test_weighted_total_range():
    score = weighted_total(
        {
            "volatility_score": 100,
            "drawdown_score": 50,
            "volume_score": 25,
            "valuation_score": 0,
            "fundamental_score": 75,
        }
    )
    assert 0 <= score <= 100
    assert score == 53.75


def test_risk_level_thresholds():
    assert risk_level_from_score(39.99) == "Low"
    assert risk_level_from_score(40) == "Medium"
    assert risk_level_from_score(69.99) == "Medium"
    assert risk_level_from_score(70) == "High"
