import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
for d in [BASE_DIR, BACKEND_DIR]:
    if d not in sys.path:
        sys.path.insert(0, d)

from route_segmenter import segment_route_geometry, calculate_polyline_distance_m
from confidence_engine import calculate_data_confidence
from segment_analyzer import analyze_route_segment, analyze_entire_route


def test_segment_route_geometry_splits_properly():
    # Simulated real road polyline (~600 meters)
    pts = [
        [30.3243, 78.0419],
        [30.3250, 78.0425],
        [30.3260, 78.0435],
        [30.3270, 78.0445],
        [30.3280, 78.0455],
        [30.3290, 78.0465]
    ]
    segments = segment_route_geometry(fallback_points=pts, target_segment_length_m=150.0)
    assert len(segments) >= 2
    for seg in segments:
        assert "segment_id" in seg
        assert "points" in seg
        assert len(seg["points"]) >= 2
        assert seg["distance_m"] > 0
        assert "midpoint" in seg


def test_data_confidence_scoring_independent_from_safety():
    # Case A: Missing all data
    conf_missing = calculate_data_confidence(
        lighting_data={"status": "unknown", "source_type": "none"},
        commercial_data={"status": "unavailable"},
        incidents_data={"status": "unmonitored"},
        emergency_data={"status": "unavailable"},
        road_data={"length_m": 150}
    )
    assert conf_missing["confidence_level"] == "Insufficient data"
    assert conf_missing["coverage_percentage"] == 0

    # Case B: Complete verifiable data
    conf_complete = calculate_data_confidence(
        lighting_data={"status": "present", "source_type": "osm", "retrieved_at": "2026-11-10 12:00:00"},
        commercial_data={"status": "verified_mapped", "retrieved_at": "2026-11-10 12:00:00"},
        incidents_data={"status": "active_reports", "sources": [{"type": "official"}], "retrieved_at": "2026-11-10 12:00:00"},
        emergency_data={"status": "mapped_nearby", "retrieved_at": "2026-11-10 12:00:00"},
        road_data={"length_m": 150}
    )
    assert conf_complete["confidence_level"] in ("High confidence", "Medium confidence")
    assert conf_complete["coverage_percentage"] == 100


def test_segment_analysis_explainable_breakdown():
    seg = {
        "segment_id": "seg_01",
        "index": 0,
        "title": "Segment 1: Rajpur Road",
        "road_name": "Rajpur Road",
        "road_class": "primary",
        "distance_m": 150.0,
        "duration_sec": 120.0,
        "points": [[30.3243, 78.0419], [30.3250, 78.0425]],
        "midpoint": [30.3246, 78.0422]
    }
    # Analyze at night (22:00)
    analysis = analyze_route_segment(seg, hour=22)
    assert 0 <= analysis["safety_score"] <= 100
    assert analysis["qualitative_class"] in [
        "Lower reported-risk indicators",
        "Mixed safety indicators",
        "Elevated reported-risk indicators",
        "Insufficient data"
    ]
    assert "explanation" in analysis
    assert len(analysis["score_breakdown"]) > 0
    assert "confidence" in analysis


def test_analyze_entire_route_reasons_and_metrics():
    segs = [
        {
            "segment_id": "seg_01",
            "index": 0,
            "title": "Segment 1",
            "road_name": "Main Street",
            "road_class": "primary",
            "distance_m": 120.0,
            "duration_sec": 100.0,
            "points": [[30.3243, 78.0419], [30.3250, 78.0425]],
            "midpoint": [30.3246, 78.0422]
        },
        {
            "segment_id": "seg_02",
            "index": 1,
            "title": "Segment 2",
            "road_name": "Alley Way",
            "road_class": "alley",
            "distance_m": 180.0,
            "duration_sec": 150.0,
            "points": [[30.3250, 78.0425], [30.3260, 78.0435]],
            "midpoint": [30.3255, 78.0430]
        }
    ]
    route_summary = analyze_entire_route(segs, hour=14)
    assert route_summary["num_segments"] == 2
    assert route_summary["total_distance_m"] == 300
    assert 0 <= route_summary["overall_score"] <= 100
    assert len(route_summary["summary_reasons"]) > 0
    assert "summary_text" in route_summary
