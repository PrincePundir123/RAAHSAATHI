import pytest
from backend.safety_scorer import calculate_safety_score

def test_safety_score_range():
    route_coords = [
        (30.3255, 78.0436),
        (30.3260, 78.0440),
        (30.3270, 78.0450)
    ]
    # Day time (14:00)
    score_day = calculate_safety_score(route_coords, hour_of_day=14)
    assert 0 <= score_day <= 100

    # Night time (02:00) - should generally be lower or equal due to time penalties
    score_night = calculate_safety_score(route_coords, hour_of_day=2)
    assert 0 <= score_night <= 100
    assert score_night <= score_day

def test_safety_score_empty_route():
    score = calculate_safety_score([], hour_of_day=12)
    assert 0 <= score <= 100
