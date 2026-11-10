# map_builder.py - Map Builder Engine with Folium, HeatMap, and Markers (Light Mode Theme)
import os
import sys
import sqlite3
from datetime import datetime

try:
    import folium
    from folium.plugins import HeatMap, MarkerCluster
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in [BASE_DIR, os.path.join(BASE_DIR, 'backend'), os.path.join(BASE_DIR, 'ai_backend'), os.path.dirname(os.path.abspath(__file__))]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from report_manager import update_all_weights
except ImportError:
    def update_all_weights():
        pass


def build_safety_map(center=[28.6139, 77.2090], zoom=13):
    if not HAS_FOLIUM:
        return None

    try:
        update_all_weights()
    except Exception:
        pass

    # Check for Stadia Maps or CARTO API key, otherwise default to OpenStreetMap
    stadia_api_key = os.getenv("STADIA_API_KEY", "").strip() or os.getenv("MAP_API_KEY", "").strip()
    carto_api_key = os.getenv("CARTO_API_KEY", "").strip()

    if stadia_api_key:
        # Stadia Maps Alidade Smooth - crisp modern style
        tiles = f"https://tiles.stadiamaps.com/tiles/alidade_smooth/{{z}}/{{x}}/{{y}}{{r}}.png?api_key={stadia_api_key}"
        attr = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        m = folium.Map(location=center, zoom_start=zoom, tiles=tiles, attr=attr)
    elif carto_api_key:
        tiles = f"https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png?api_key={carto_api_key}"
        attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
        m = folium.Map(location=center, zoom_start=zoom, tiles=tiles, attr=attr)
    else:
        # Standard OpenStreetMap: 100% free, no API key required
        m = folium.Map(location=center, zoom_start=zoom, tiles='OpenStreetMap')

    db_path = os.path.join(BASE_DIR, 'backend', 'safewalk.db')
    if not os.path.exists(db_path):
        db_path = os.path.join(BASE_DIR, 'safewalk.db')
    if not os.path.exists(db_path):
        db_path = 'safewalk.db'

    rows = []
    try:
        conn = sqlite3.connect(db_path)
        rows = conn.execute('''
            SELECT lat, lng, severity, type, timestamp,
                   upvotes, verified, weight, description, id
            FROM incidents WHERE weight > 0.05
            ORDER BY weight DESC
        ''').fetchall()
        conn.close()
    except Exception:
        rows = []

    now = datetime.now()
    if rows:
        HeatMap([[r[0], r[1], r[7]] for r in rows],
                gradient={0.2: '#10B981', 0.5: '#F59E0B', 0.8: '#EF4444', 1.0: '#991B1B'},
                radius=25, blur=15, min_opacity=0.35).add_to(m)
        
        cluster = MarkerCluster().add_to(m)
        for lat, lng, sev, inc_type, ts_str, up, ver, wt, desc, inc_id in rows:
            color = '#E11D48' if sev == 3 else '#F59E0B' if sev == 2 else '#EAB308'
            wt_val = float(wt) if wt is not None else 1.0
            radius = max(7, min(18, int(wt_val * 13)))
            try:
                ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                h = (now - ts).total_seconds() / 3600
                t = f'{int(h*60)}m ago' if h < 1 else f'{int(h)}h ago' if h < 24 else f'{int(h/24)}d ago'
            except Exception:
                t = 'Recent'
            badge = ' ✔ Verified' if ver else ''
            popup_html = (f'<div style="font-family:sans-serif; font-size:12px; color:#0F172A;">'
                          f'<b style="color:{color}; font-size:14px;">{str(inc_type).upper()}{badge}</b><br>'
                          f'<span style="color:#475569;">🕒 {t} • 👍 {up} • Severity: {sev}/3</span>'
                          + (f'<br><small style="color:#64748B;">{desc[:100]}</small>' if desc else '')
                          + '</div>')
            folium.CircleMarker([lat, lng], radius=radius,
                                color=color, fill=True, fill_color=color, fill_opacity=0.85,
                                popup=folium.Popup(popup_html, max_width=220)).add_to(cluster)
    return m


def add_routes_to_map(m, safe_route, fast_route, selected_segment_id=None):
    if not HAS_FOLIUM or m is None:
        return m

    # Fastest Route (Coral / Rose Dashed) shown underneath as baseline comparison
    if fast_route and fast_route.get('points') and fast_route != safe_route:
        folium.PolyLine(fast_route['points'], color='#E11D48', weight=4, opacity=0.6, dash_array='8, 8',
                        tooltip=f"Fastest Route ({fast_route.get('safety_avg', 50)}/100)"
                        ).add_to(m)

    # Check if Segment-Level Intelligence is present on the safe route
    seg_intel = safe_route.get("segment_intelligence")
    segments = seg_intel.get("segments", []) if seg_intel else []

    if segments:
        # Render segmented polyline with accessible, explainable styling
        for seg in segments:
            pts = seg.get("points", [])
            if not pts or len(pts) < 2:
                continue

            seg_id = seg.get("segment_id")
            score = seg.get("safety_score", 70)
            q_class = seg.get("qualitative_class", "Mixed safety indicators")
            conf_level = seg.get("confidence", {}).get("confidence_level", "Medium confidence")
            is_selected = (selected_segment_id == seg_id)

            # Accessible Visual Distinction:
            # - Green: fewer observed risk indicators
            # - Amber: mixed indicators
            # - Red: elevated reported-risk indicators
            # - Grey / dashed: insufficient data
            dash_pattern = None
            if q_class == "Insufficient data" or conf_level == "Insufficient data":
                color = '#64748B'  # Slate grey
                dash_pattern = '6, 6'
            elif score >= 75:
                color = '#059669'  # Emerald green (fewer observed risk indicators)
            elif score >= 50:
                color = '#D97706'  # Amber (mixed indicators)
            else:
                color = '#DC2626'  # Crimson Red (elevated reported-risk indicators)

            # Selected segment highlight
            line_weight = 10 if is_selected else 6
            line_opacity = 1.0 if is_selected else 0.85
            if is_selected:
                # Add a pulsing outer glow for the active selected segment
                folium.PolyLine(
                    pts,
                    color='#38BDF8',
                    weight=16,
                    opacity=0.55
                ).add_to(m)

            tooltip_html = (
                f"<b>{seg.get('title')}</b><br>"
                f"Score: <b>{score}/100</b> ({q_class})<br>"
                f"Confidence: <b>{conf_level}</b><br>"
                f"Length: {round(seg.get('distance_m', 0))}m • {seg.get('road_name')}"
            )

            popup_html = (
                f"<div style='font-family:sans-serif; min-width:180px;'>"
                f"<b style='color:{color}; font-size:13px;'>{seg.get('title')}</b><br>"
                f"<span>Score: <b>{score}/100</b></span><br>"
                f"<span>Status: <i>{q_class}</i></span><br>"
                f"<span>Confidence: <b>{conf_level}</b></span><br>"
                f"<hr style='margin:4px 0;'><small>{seg.get('explanation', '')[:120]}...</small>"
                f"</div>"
            )

            line_args = {
                "locations": pts,
                "color": color,
                "weight": line_weight,
                "opacity": line_opacity,
                "tooltip": folium.Tooltip(tooltip_html),
                "popup": folium.Popup(popup_html, max_width=260)
            }
            if dash_pattern:
                line_args["dash_array"] = dash_pattern

            folium.PolyLine(**line_args).add_to(m)

            # Small clickable midpoint anchor marker
            mid = seg.get("midpoint")
            if mid and len(mid) == 2:
                folium.CircleMarker(
                    location=mid,
                    radius=5 if not is_selected else 8,
                    color="#0F172A",
                    weight=1.5,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.9,
                    tooltip=f"Click to inspect {seg.get('segment_id')}"
                ).add_to(m)

    elif safe_route and safe_route.get('points'):
        # Fallback to single polyline if no segmentation available
        pts = safe_route['points']
        folium.PolyLine(pts, color='#059669', weight=7, opacity=0.9,
                        tooltip=f"Safest Route ({safe_route.get('safety_avg', 70)}/100)"
                        ).add_to(m)

    # Route Origin & Destination Markers
    all_pts = safe_route.get('points', [])
    if all_pts:
        folium.Marker(
            all_pts[0],
            popup="<b>Start Location</b>",
            icon=folium.Icon(color="green", icon="play", prefix="fa")
        ).add_to(m)
        folium.Marker(
            all_pts[-1],
            popup="<b>Destination</b>",
            icon=folium.Icon(color="blue", icon="flag", prefix="fa")
        ).add_to(m)

    # Danger Zones
    for lat, lng in safe_route.get('danger_zones', []) if safe_route else []:
        folium.CircleMarker(
            [lat, lng],
            radius=14,
            color='#E11D48',
            fill=True,
            fill_color='#E11D48',
            fill_opacity=0.35,
            popup='Active Danger / Low-Score Corridor'
        ).add_to(m)

    return m
