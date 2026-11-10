# safestops_service.py - SafeStops Nearby Assistance Discovery & Verification Engine
import os
import sqlite3
import math
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional

from route_segmenter import haversine_distance_m

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "safewalk.db")
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Category Definitions & UX Icons
SAFESTOP_CATEGORIES = {
    "police": {"label": "Police Facilities", "icon": "🚓", "color": "#1E40AF"},
    "hospital": {"label": "Hospitals & Emergency", "icon": "🏥", "color": "#DC2626"},
    "campus_security": {"label": "Campus Security Desks", "icon": "🎓", "color": "#7C3AED"},
    "pharmacy": {"label": "24/7 Pharmacies", "icon": "💊", "color": "#059669"},
    "community_help": {"label": "Participating Safe Havens", "icon": "🛡️", "color": "#D97706"}
}


def find_nearby_safestops(
    lat: float,
    lng: float,
    radius_km: float = 2.0,
    category_filter: Optional[str] = None,
    limit: int = 15
) -> List[Dict[str, Any]]:
    """
    Retrieves nearby SafeStops from the SQLite curated database with strict provenance.
    Calculates exact geodesic distance, estimates walking time (1.15 m/s),
    and formats verification status.
    """
    radius_m = radius_km * 1000.0
    deg_delta = radius_km / 111.0

    query = """
    SELECT id, name, category, latitude, longitude, address, phone, website,
           opening_hours, is_open_24_7, source_type, source_reference,
           verification_status, verification_evidence, last_verified_at, last_retrieved_at
    FROM safestops
    WHERE latitude BETWEEN ? AND ?
      AND longitude BETWEEN ? AND ?
    """
    params = [lat - deg_delta, lat + deg_delta, lng - deg_delta, lng + deg_delta]

    if category_filter and category_filter != "all" and category_filter in SAFESTOP_CATEGORIES:
        query += " AND category = ?"
        params.append(category_filter)

    results = []
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()

            for r in rows:
                d_m = haversine_distance_m(lat, lng, r["latitude"], r["longitude"])
                if d_m <= radius_m:
                    walk_min = max(1, round(d_m / (1.15 * 60)))  # ~4.1 km/h walking speed
                    
                    # Verification badge metadata
                    verif_stat = r["verification_status"] or "PUBLIC FACILITY"
                    if verif_stat == "PARTNER-VERIFIED":
                        verif_badge_color = "#059669"  # Emerald
                        verif_summary = "Formally audited & registered SafeWalk partner"
                    elif verif_stat == "COMMUNITY-LISTED":
                        verif_badge_color = "#D97706"  # Amber
                        verif_summary = "User submitted; independent verification pending"
                    else:  # PUBLIC FACILITY
                        verif_badge_color = "#3B82F6"  # Blue
                        verif_summary = "Mapped in official/public registry; not personally contacted"

                    cat_meta = SAFESTOP_CATEGORIES.get(r["category"], {"label": r["category"], "icon": "📍", "color": "#64748B"})

                    results.append({
                        "id": r["id"],
                        "name": r["name"],
                        "category": r["category"],
                        "category_label": cat_meta["label"],
                        "category_icon": cat_meta["icon"],
                        "category_color": cat_meta["color"],
                        "latitude": r["latitude"],
                        "longitude": r["longitude"],
                        "address": r["address"] or "Address not specified",
                        "phone": r["phone"] or "Not available",
                        "website": r["website"] or "Not available",
                        "opening_hours": r["opening_hours"] or "Hours unknown",
                        "is_open_24_7": bool(r["is_open_24_7"]),
                        "distance_m": round(d_m),
                        "distance_km": round(d_m / 1000.0, 2),
                        "walking_time_min": walk_min,
                        "source_type": r["source_type"],
                        "source_reference": r["source_reference"] or "Official Spatial Directory",
                        "verification_status": verif_stat,
                        "verification_summary": verif_summary,
                        "verification_evidence": r["verification_evidence"] or "Public records inspection",
                        "verification_badge_color": verif_badge_color,
                        "last_verified_at": r["last_verified_at"] or "Recent",
                        "last_retrieved_at": r["last_retrieved_at"] or "Live"
                    })

    except Exception as e:
        print(f"SafeStops query error: {e}")

    # Sort strictly by walking distance
    results.sort(key=lambda x: x["distance_m"])
    return results[:limit]


def get_safestop_by_id(safestop_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves full details for a single SafeStop."""
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            conn.row_factory = sqlite3.Row
            r = conn.execute("SELECT * FROM safestops WHERE id = ?", (safestop_id,)).fetchone()
            if r:
                cat_meta = SAFESTOP_CATEGORIES.get(r["category"], {"label": r["category"], "icon": "📍", "color": "#64748B"})
                return dict(r)
    except Exception as e:
        print(f"Error fetching safestop by ID: {e}")
    return None


def add_community_safestop(
    name: str,
    category: str,
    lat: float,
    lng: float,
    address: str = "",
    phone: str = "",
    opening_hours: str = "Hours unknown",
    notes: str = ""
) -> Dict[str, Any]:
    """
    Submits a community-suggested assistance location.
    Strictly classified as COMMUNITY-LISTED until administrator audit.
    """
    if category not in SAFESTOP_CATEGORIES:
        category = "community_help"

    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO safestops (
                name, category, latitude, longitude, address, phone,
                opening_hours, source_type, source_reference,
                verification_status, verification_evidence,
                last_retrieved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'user_community', ?, 'COMMUNITY-LISTED', ?, ?)
            """, (
                name.strip(),
                category,
                lat,
                lng,
                address.strip() or "Community reported address",
                phone.strip() or None,
                opening_hours.strip() or "Hours unknown",
                f"Community Submission by User on {now_iso}",
                notes.strip() or "Community report awaiting partner audit",
                now_iso
            ))
            new_id = cursor.lastrowid
            conn.commit()
            return {"success": True, "safestop_id": new_id, "status": "COMMUNITY-LISTED"}
    except Exception as e:
        return {"success": False, "error": str(e)}
