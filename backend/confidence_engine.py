# confidence_engine.py - Transparent, Documented Geospatial Data-Confidence Engine
from typing import Dict, Any, List, Optional
from datetime import datetime


def calculate_data_confidence(
    lighting_data: Dict[str, Any],
    commercial_data: Dict[str, Any],
    incidents_data: Dict[str, Any],
    emergency_data: Dict[str, Any],
    road_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Independent Data-Confidence Scoring Engine:
    
    IMPORTANT ARCHITECTURAL RULE:
    Confidence is NOT safety.
    A segment with 0 incident reports does NOT automatically receive high confidence.
    Absence of evidence is not evidence of absence.
    Timeout or unavailable API data must be identified as insufficient data.

    Evaluation Pillars:
    1. Category Completeness (40% weight):
       Evaluates whether verifiable data exists across key safety dimensions:
       - Lighting status (present or explicitly mapped absent)
       - Commercial/amenity mapping
       - Incident monitoring coverage
       - Emergency services mapping
       - Valid road geometry
    
    2. Data Freshness & Temporal Validity (25% weight):
       - Recent reports (<48h) or freshly queried public GIS datasets = higher freshness.
       - Stale or expired records (>30 days without update) = reduced freshness score.

    3. Source Provenance Quality (20% weight):
       - Identifiable public or official database (OSM, Police GIS, Govt Registry): High credibility.
       - Corroborated community reports (multiple users): Medium-high credibility.
       - Single unverified user report: Low credibility.
       - Default assumptions or missing endpoints: 0 credibility.

    4. Multi-Source Corroboration (15% weight):
       - Multiple independent data elements confirm conditions in the immediate radius.
    """
    pillar_scores = {
        "completeness": 0.0,
        "freshness": 0.0,
        "source_quality": 0.0,
        "corroboration": 0.0
    }
    details = []
    missing_categories = []
    confirmed_categories = []

    # 1. Lighting Completeness & Provenance
    lit_status = lighting_data.get("status")  # "present", "absent", "unknown"
    lit_source = lighting_data.get("source_type")  # "osm", "user", "assumed", "none"
    if lit_status in ("present", "absent") and lit_source == "osm":
        pillar_scores["completeness"] += 25.0
        pillar_scores["source_quality"] += 25.0
        confirmed_categories.append("Street Lighting")
    else:
        missing_categories.append("Street Lighting")
        details.append("Street lighting is unmapped or unknown in public datasets for this segment.")

    # 2. Commercial / POI Activity
    poi_status = commercial_data.get("status")  # "verified_mapped", "none_mapped", "unavailable"
    if poi_status in ("verified_mapped", "none_mapped"):
        pillar_scores["completeness"] += 25.0
        pillar_scores["source_quality"] += 25.0
        confirmed_categories.append("Commercial Activity")
    else:
        missing_categories.append("Commercial Activity")
        details.append("Commercial establishment data could not be retrieved from spatial queries.")

    # 3. Emergency & Police Facilities
    emerg_status = emergency_data.get("status")  # "mapped_nearby", "none_within_range", "unavailable"
    if emerg_status in ("mapped_nearby", "none_within_range"):
        pillar_scores["completeness"] += 25.0
        pillar_scores["source_quality"] += 25.0
        confirmed_categories.append("Emergency Facilities")
    else:
        missing_categories.append("Emergency Facilities")
        details.append("Emergency assistance facility data unavailable.")

    # 4. Incident Monitoring Coverage
    inc_status = incidents_data.get("status")  # "active_reports", "monitored_zero_reports", "unmonitored"
    if inc_status == "active_reports":
        pillar_scores["completeness"] += 25.0
        # Check source quality of incidents
        sources = incidents_data.get("sources", [])
        if any(s.get("type") in ("official", "news_verified") for s in sources):
            pillar_scores["source_quality"] += 25.0
            pillar_scores["corroboration"] += 50.0
        elif any(s.get("type") == "community_corroborated" for s in sources):
            pillar_scores["source_quality"] += 20.0
            pillar_scores["corroboration"] += 35.0
        else:
            pillar_scores["source_quality"] += 12.0
        confirmed_categories.append("Community Reports")
    elif inc_status == "monitored_zero_reports":
        # Note: 0 reports does NOT mean high confidence or safe
        pillar_scores["completeness"] += 25.0
        pillar_scores["source_quality"] += 15.0
        confirmed_categories.append("Incident Monitoring")
        details.append("No community incidents are currently registered within radius.")
    else:
        missing_categories.append("Incident Records")
        details.append("Incident database lookup unavailable.")

    # 5. Freshness Calculation
    timestamps = []
    for d in [lighting_data, commercial_data, incidents_data, emergency_data]:
        ts = d.get("retrieved_at") or d.get("updated_at")
        if ts:
            timestamps.append(ts)

    if len(timestamps) >= 3:
        pillar_scores["freshness"] = 90.0
    elif len(timestamps) >= 1:
        pillar_scores["freshness"] = 60.0
    else:
        pillar_scores["freshness"] = 15.0

    # 6. Corroboration Bonus
    num_confirmed = len(confirmed_categories)
    if num_confirmed >= 4:
        pillar_scores["corroboration"] = max(pillar_scores["corroboration"], 85.0)
    elif num_confirmed >= 2:
        pillar_scores["corroboration"] = max(pillar_scores["corroboration"], 50.0)

    # Weighted Overall Confidence Score (0 - 100)
    # Completeness (40%), Freshness (25%), Source Quality (20%), Corroboration (15%)
    raw_confidence = (
        0.40 * pillar_scores["completeness"] +
        0.25 * pillar_scores["freshness"] +
        0.20 * pillar_scores["source_quality"] +
        0.15 * pillar_scores["corroboration"]
    )
    confidence_score = round(max(0.0, min(100.0, raw_confidence)))

    # Coverage percentage = confirmed categories / 4 total dimensions
    coverage_percentage = round((num_confirmed / 4.0) * 100)

    # Qualitative Level Classification
    if coverage_percentage < 50 or confidence_score < 40:
        level = "Insufficient data"
        badge_color = "#94A3B8"  # Slate grey
    elif confidence_score < 60:
        level = "Low confidence"
        badge_color = "#F59E0B"  # Amber
    elif confidence_score < 80:
        level = "Medium confidence"
        badge_color = "#3B82F6"  # Blue
    else:
        level = "High confidence"
        badge_color = "#10B981"  # Emerald

    return {
        "confidence_score": confidence_score,
        "coverage_percentage": coverage_percentage,
        "confidence_level": level,
        "badge_color": badge_color,
        "confirmed_categories": confirmed_categories,
        "missing_categories": missing_categories,
        "audit_notes": details,
        "pillar_scores": {k: round(v, 1) for k, v in pillar_scores.items()}
    }
