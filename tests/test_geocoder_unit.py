import pytest
from backend.geocoder import geocode_address, DEHRADUN_LANDMARKS

def test_dehradun_known_landmarks():
    coords = geocode_address("Clock Tower")
    assert coords is not None
    assert isinstance(coords, tuple)
    assert len(coords) == 2
    assert abs(coords[0] - 30.3255) < 0.01
    assert abs(coords[1] - 78.0436) < 0.01

def test_upes_bidholi_landmark():
    coords = geocode_address("UPES Bidholi")
    assert coords is not None
    assert abs(coords[0] - 30.4158) < 0.01

def test_invalid_address_returns_none():
    coords = geocode_address("zxqwerty1234fakeaddress9876")
    assert coords is None
