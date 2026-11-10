# route_segmenter.py - Production-Quality Real Road Route Segmentation
import math
from typing import List, Dict, Any, Tuple, Optional


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates geodesic distance in meters between two coordinates."""
    r = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def calculate_polyline_distance_m(points: List[List[float]]) -> float:
    """Calculates cumulative distance along a list of [lat, lng] points in meters."""
    if not points or len(points) < 2:
        return 0.0
    total = 0.0
    for i in range(len(points) - 1):
        total += haversine_distance_m(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
    return total


def calculate_segment_midpoint(points: List[List[float]]) -> Tuple[float, float]:
    """Calculates geographical midpoint / representative coordinate along a polyline."""
    if not points:
        return (0.0, 0.0)
    if len(points) == 1:
        return (points[0][0], points[0][1])

    # Find point closest to 50% cumulative distance along actual polyline
    total_len = calculate_polyline_distance_m(points)
    if total_len == 0.0:
        return (points[0][0], points[0][1])

    target = total_len / 2.0
    acc = 0.0
    for i in range(len(points) - 1):
        seg_d = haversine_distance_m(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        if acc + seg_d >= target and seg_d > 0.0:
            ratio = (target - acc) / seg_d
            lat = points[i][0] + ratio * (points[i+1][0] - points[i][0])
            lng = points[i][1] + ratio * (points[i+1][1] - points[i][1])
            return (round(lat, 6), round(lng, 6))
        acc += seg_d

    idx = len(points) // 2
    return (points[idx][0], points[idx][1])


def _split_dense_points_by_distance(
    points: List[List[float]],
    target_len_m: float = 150.0,
    min_len_m: float = 80.0,
    max_len_m: float = 250.0,
    base_name: str = "Walking Path",
    road_class: str = "footway"
) -> List[Dict[str, Any]]:
    """
    Splits a dense polyline of coordinates along actual road geometry
    into sub-segments roughly target_len_m (100m - 200m).
    Never creates artificial straight lines.
    """
    if not points or len(points) < 2:
        return []

    sub_segments = []
    curr_pts = [points[0]]
    curr_dist = 0.0

    for i in range(len(points) - 1):
        p1, p2 = points[i], points[i+1]
        step_d = haversine_distance_m(p1[0], p1[1], p2[0], p2[1])
        curr_pts.append(p2)
        curr_dist += step_d

        # When segment reaches target length and has points remaining ahead
        if curr_dist >= target_len_m and (len(points) - (i + 1)) >= 2:
            sub_segments.append({
                "points": [list(pt) for pt in curr_pts],
                "distance_m": round(curr_dist, 1),
                "duration_sec": round(curr_dist / 1.15, 1),  # average 1.15 m/s (4.1 km/h) walking speed
                "road_name": base_name or "Pedestrian Way",
                "road_class": road_class
            })
            curr_pts = [p2]
            curr_dist = 0.0

    # Handle remaining points
    if len(curr_pts) >= 2:
        if sub_segments and curr_dist < min_len_m:
            # Merge with previous segment if tail is very short
            prev = sub_segments[-1]
            prev["points"].extend(curr_pts[1:])
            prev["distance_m"] = round(prev["distance_m"] + curr_dist, 1)
            prev["duration_sec"] = round(prev["duration_sec"] + (curr_dist / 1.15), 1)
        else:
            sub_segments.append({
                "points": [list(pt) for pt in curr_pts],
                "distance_m": round(curr_dist, 1),
                "duration_sec": round(curr_dist / 1.15, 1),
                "road_name": base_name or "Pedestrian Way",
                "road_class": road_class
            })

    return sub_segments


def segment_route_geometry(
    raw_osrm_route: Optional[Dict[str, Any]] = None,
    fallback_points: Optional[List[List[float]]] = None,
    target_segment_length_m: float = 150.0
) -> List[Dict[str, Any]]:
    """
    Main Route Segmentation Algorithm:
    Uses actual OSRM step maneuvers, real street geometry, and intersection boundaries.
    Subdivides long street corridors into ~100-200m segments while respecting real geometry.
    If no OSRM steps are available, segments the dense real-road polyline.
    """
    segments: List[Dict[str, Any]] = []

    # Strategy A: Use detailed OSRM steps if present in raw_osrm_route
    steps_available = False
    if raw_osrm_route and "legs" in raw_osrm_route:
        legs = raw_osrm_route.get("legs", [])
        all_steps = []
        for leg in legs:
            all_steps.extend(leg.get("steps", []))

        if all_steps:
            steps_available = True
            for step_idx, step in enumerate(all_steps):
                step_name = step.get("name", "").strip() or f"Section {step_idx + 1}"
                step_dist = float(step.get("distance", 0.0))
                step_dur = float(step.get("duration", 0.0))
                
                # Extract step geometry
                geom = step.get("geometry", {})
                if isinstance(geom, dict) and "coordinates" in geom:
                    step_coords = [[pt[1], pt[0]] for pt in geom["coordinates"]]
                elif isinstance(geom, list):
                    step_coords = geom
                else:
                    step_coords = []

                if len(step_coords) < 2:
                    continue

                road_mode = step.get("mode", "walking")
                maneuver_type = step.get("maneuver", {}).get("type", "turn")

                # If the step is longer than 220m, split it along actual geometry
                if step_dist > 220.0 and len(step_coords) >= 4:
                    sub_splits = _split_dense_points_by_distance(
                        step_coords,
                        target_len_m=target_segment_length_m,
                        base_name=step_name,
                        road_class=road_mode
                    )
                    segments.extend(sub_splits)
                else:
                    segments.append({
                        "points": step_coords,
                        "distance_m": round(step_dist, 1),
                        "duration_sec": round(step_dur, 1),
                        "road_name": step_name,
                        "road_class": road_mode,
                        "maneuver": maneuver_type
                    })

    # Strategy B: If no OSRM step breakdown, partition raw dense road coordinates
    if not segments and fallback_points and len(fallback_points) >= 2:
        segments = _split_dense_points_by_distance(
            fallback_points,
            target_len_m=target_segment_length_m,
            base_name="Route Section",
            road_class="footway"
        )

    # Format output with unique IDs, sequential numbering, and precalculated midpoints
    final_segments = []
    cumulative_dist = 0.0
    for idx, seg in enumerate(segments):
        pts = seg["points"]
        dist = seg["distance_m"]
        dur = seg.get("duration_sec", round(dist / 1.15, 1))
        mid = calculate_segment_midpoint(pts)
        name = seg.get("road_name") or f"Segment {idx + 1}"

        final_segments.append({
            "segment_id": f"seg_{idx + 1:02d}",
            "index": idx,
            "title": f"Segment {idx + 1}: {name}",
            "road_name": name,
            "road_class": seg.get("road_class", "pedestrian"),
            "distance_m": dist,
            "cumulative_start_m": round(cumulative_dist, 1),
            "duration_sec": dur,
            "duration_min": max(1, round(dur / 60.0)),
            "points": pts,
            "start_point": pts[0],
            "end_point": pts[-1],
            "midpoint": [mid[0], mid[1]]
        })
        cumulative_dist += dist

    return final_segments
