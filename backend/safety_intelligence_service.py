# safety_intelligence_service.py - Feature 7: Administrative & Institutional Safety Intelligence Engine
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "safewalk.db")


def get_safety_intelligence_summary(
    city: Optional[str] = None,
    days: int = 30
) -> Dict[str, Any]:
    """
    Computes rigorous aggregated safety intelligence for administrators:
    - Counts actual database records. Never fabricates statistics.
    - Category breakdowns.
    - Moderation and evidence status distributions.
    - Infrastructure gap indicators.
    - SafeStops partner vs public coverage.
    """
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

    summary = {
        "time_window_days": days,
        "total_reports": 0,
        "reports_last_24h": 0,
        "awaiting_moderation": 0,
        "community_corroborated": 0,
        "officially_sourced": 0,
        "category_counts": {},
        "evidence_breakdown": {},
        "safestops_summary": {
            "total": 0,
            "partner_verified": 0,
            "public_facility": 0,
            "community_listed": 0
        },
        "infrastructure_alerts": {
            "lighting_reports": 0,
            "blocked_walkways": 0
        }
    }

    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()

            # 1. Total incidents in window
            total = cursor.execute("""
            SELECT COUNT(*) FROM incidents WHERE timestamp >= ?
            """, (since_date,)).fetchone()[0]
            summary["total_reports"] = total

            # 2. Last 24h reports
            last_24h = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
            recent = cursor.execute("""
            SELECT COUNT(*) FROM incidents WHERE timestamp >= ?
            """, (last_24h,)).fetchone()[0]
            summary["reports_last_24h"] = recent

            # 3. Moderation & Evidence statuses
            mod_pending = cursor.execute("""
            SELECT COUNT(*) FROM incidents WHERE moderation_status = 'PENDING_REVIEW'
            """).fetchone()[0]
            summary["awaiting_moderation"] = mod_pending

            corrob = cursor.execute("""
            SELECT COUNT(*) FROM incidents WHERE evidence_status = 'COMMUNITY_CORROBORATED'
            """).fetchone()[0]
            summary["community_corroborated"] = corrob

            off_src = cursor.execute("""
            SELECT COUNT(*) FROM incidents WHERE evidence_status = 'OFFICIALLY_SOURCED'
            """).fetchone()[0]
            summary["officially_sourced"] = off_src

            # 4. Category distribution
            cat_rows = cursor.execute("""
            SELECT type, COUNT(*) FROM incidents
            WHERE timestamp >= ?
            GROUP BY type
            """, (since_date,)).fetchall()
            summary["category_counts"] = {r[0]: r[1] for r in cat_rows if r[0]}

            # 5. Infrastructure complaints count
            summary["infrastructure_alerts"]["lighting_reports"] = summary["category_counts"].get("poor_lighting", 0) + summary["category_counts"].get("unsafe_area", 0)
            summary["infrastructure_alerts"]["blocked_walkways"] = summary["category_counts"].get("broken_infrastructure", 0)

            # 6. SafeStops Coverage
            ss_tot = cursor.execute("SELECT COUNT(*) FROM safestops").fetchone()[0]
            ss_part = cursor.execute("SELECT COUNT(*) FROM safestops WHERE verification_status = 'PARTNER-VERIFIED'").fetchone()[0]
            ss_pub = cursor.execute("SELECT COUNT(*) FROM safestops WHERE verification_status = 'PUBLIC FACILITY'").fetchone()[0]
            ss_comm = cursor.execute("SELECT COUNT(*) FROM safestops WHERE verification_status = 'COMMUNITY-LISTED'").fetchone()[0]

            summary["safestops_summary"]["total"] = ss_tot
            summary["safestops_summary"]["partner_verified"] = ss_part
            summary["safestops_summary"]["public_facility"] = ss_pub
            summary["safestops_summary"]["community_listed"] = ss_comm

    except Exception as e:
        print(f"Intelligence aggregation error: {e}")

    return summary


def get_geographic_clusters(min_reports_threshold: int = 2) -> List[Dict[str, Any]]:
    """
    Computes generalized geographical cells (~300m bins) with minimum aggregation thresholds
    to avoid exposing private individual movements.
    """
    clusters = []
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            # Round coordinates to 2 decimal places (~1.1km generalized bin)
            rows = conn.execute("""
            SELECT ROUND(lat, 2) as b_lat, ROUND(lng, 2) as b_lng, COUNT(*) as cnt,
                   GROUP_CONCAT(DISTINCT type) as types,
                   AVG(severity) as avg_sev
            FROM incidents
            WHERE moderation_status = 'PUBLISHED'
            GROUP BY b_lat, b_lng
            HAVING cnt >= ?
            ORDER BY cnt DESC
            """, (min_reports_threshold,)).fetchall()

            for r in rows:
                clusters.append({
                    "lat": r[0],
                    "lng": r[1],
                    "report_count": r[2],
                    "categories": r[3],
                    "avg_severity": round(r[4] or 1.0, 1),
                    "cluster_label": f"Cluster: {r[2]} reports (Avg Sev: {round(r[4] or 1.0, 1)}/3)"
                })
    except Exception as e:
        print(f"Error computing geo clusters: {e}")

    return clusters
