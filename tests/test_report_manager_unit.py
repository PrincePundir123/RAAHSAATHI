import pytest
import math
from backend.report_manager import compute_decayed_weight

def test_compute_decayed_weight_zero_hours():
    weight = compute_decayed_weight(hours_ago=0.0)
    assert weight == pytest.approx(1.0, abs=1e-2)

def test_compute_decayed_weight_half_life():
    # 48 hours should be approximately half-life (0.5)
    weight = compute_decayed_weight(hours_ago=48.0)
    assert weight == pytest.approx(0.5, abs=0.05)

def test_compute_decayed_weight_long_past():
    weight = compute_decayed_weight(hours_ago=240.0)
    assert 0.0 <= weight < 0.1
