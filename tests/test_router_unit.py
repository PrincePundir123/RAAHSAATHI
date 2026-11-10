import pytest
from backend.router import haversine_distance

def test_haversine_same_point():
    point = (30.3255, 78.0436)
    dist = haversine_distance(point[0], point[1], point[0], point[1])
    assert dist == pytest.approx(0.0, abs=1e-5)

def test_haversine_known_distance():
    p1 = (30.3255, 78.0436)
    p2 = (30.4158, 77.9659)
    dist = haversine_distance(p1[0], p1[1], p2[0], p2[1])
    # Approximate straight-line distance in km between these two points
    assert 10.0 < dist < 20.0
