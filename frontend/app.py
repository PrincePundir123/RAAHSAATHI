# app.py - SafeWalk Streamlit Frontend (Clean Emoji-Free Typography & Modern Popping UI)
import os
import sys
import uuid
import html
from datetime import datetime
import streamlit as st
from streamlit_folium import st_folium

# Path setup for root, backend, and ai_backend packages
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
AI_BACKEND_DIR = os.path.join(BASE_DIR, "AI_BACKEND")

for p in [BASE_DIR, BACKEND_DIR, AI_BACKEND_DIR, os.path.dirname(os.path.abspath(__file__))]:
    if p not in sys.path:
        sys.path.insert(0, p)

from map_builder import build_safety_map, add_routes_to_map, add_safestops_to_map

# Imports from unified safewalk_service API
from safewalk_service import (
    initialize_safewalk_system,
    plan_safe_route,
    process_and_save_user_report,
    ingest_city_news_reports,
    handle_vote,
    ask_safewalk_ai,
    find_nearby_safestops,
    add_community_safestop,
    get_trusted_contacts,
    add_trusted_contact,
    delete_trusted_contact,
    create_journey,
    record_location_update,
    confirm_checkin,
    process_server_side_escalations,
    acknowledge_alert,
    complete_or_cancel_journey,
    get_journey_by_share_token,
    get_latest_journey_location
)
from report_manager import get_city_stats, get_recent_reports_in_city, upvote_incident, downvote_incident
from geocoder import geocode_address, get_city_country_from_coords, get_city_landmark_suggestions
from genai_layer import generate_safety_briefing, generate_sos_message, process_incident_report, get_city_safety_overview

# Page Configuration
st.set_page_config(
    page_title="SafeWalk | AI Women's Safety Navigation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean, Emoji-Free Typography & Ultra-Popping Animated Light Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 40%, #FDF2F8 100%) !important;
        color: #0F172A !important;
    }

    /* Keyframe Animations */
    @keyframes pulseGlow {
        0% { box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35); }
        50% { box-shadow: 0 10px 30px rgba(217, 70, 239, 0.55); }
        100% { box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35); }
    }

    /* Typography & Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 800 !important;
        color: #0F172A !important;
        letter-spacing: -0.4px !important;
    }

    .main-title {
        font-size: 2.7rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 40%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
        letter-spacing: -0.8px;
        filter: drop-shadow(0 2px 8px rgba(99, 102, 241, 0.15));
    }
    
    .sub-title {
        font-size: 1.1rem;
        color: #334155 !important;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }

    /* Sidebar Vibrant Colorful & Interactive Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F8FAFC 0%, #EEF2FF 50%, #FDF2F8 100%) !important;
        border-right: 2px solid #CBD5E1 !important;
        box-shadow: 4px 0 24px rgba(99, 102, 241, 0.08) !important;
    }

    .sidebar-title {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }

    section[data-testid="stSidebar"] h3 {
        color: #4338CA !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        border-bottom: 2px solid #C7D2FE !important;
        padding-bottom: 4px !important;
        margin-top: 1rem !important;
    }

    section[data-testid="stSidebar"] label {
        color: #1E293B !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }

    /* Sidebar Interactive Form Button */
    section[data-testid="stSidebar"] form button {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3) !important;
        transition: all 0.25s ease !important;
    }

    section[data-testid="stSidebar"] form button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.45) !important;
    }

    /* Sidebar Action Buttons */
    div[data-testid="stSidebar"] .stButton > button {
        background: #FFFFFF !important;
        color: #4F46E5 !important;
        border: 2px solid #C7D2FE !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.08) !important;
        transition: all 0.25s ease !important;
    }

    div[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: #FFFFFF !important;
        border-color: #4F46E5 !important;
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.35) !important;
    }

    /* Input Fields POPPING Style */
    div[data-testid="stTextInput"] input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 2px solid #CBD5E1 !important;
        border-radius: 14px !important;
        font-size: 1.02rem !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04), inset 0 2px 4px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 22px rgba(99, 102, 241, 0.35), 0 4px 15px rgba(99, 102, 241, 0.1) !important;
        transform: translateY(-2px) scale(1.01) !important;
    }

    div[data-testid="stTextInput"] label {
        color: #1E293B !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }

    /* Suggestion Chips Uniform Fixed-Height & Perfect Pixel Symmetry */
    div[data-testid="column"] .stButton > button {
        background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%) !important;
        color: #4338CA !important;
        border: 1.5px solid #A5B4FC !important;
        border-radius: 16px !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        padding: 0 12px !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    div[data-testid="column"] .stButton > button:hover {
        transform: translateY(-3px) scale(1.03) !important;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 8px 22px rgba(99, 102, 241, 0.38) !important;
        border-color: #6366F1 !important;
    }

    /* Primary Submit Action Buttons */
    button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1 0%, #D946EF 100%) !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35) !important;
        animation: pulseGlow 3s infinite ease-in-out !important;
        transition: all 0.25s ease-in-out !important;
    }
    
    button[kind="primary"]:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 10px 28px rgba(217, 70, 239, 0.5) !important;
    }

    /* Tab Customization & Visibility (Zero Clipping, Emoji-Free Buttons) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 14px !important;
        background: transparent !important;
        padding: 6px 0px 16px 0px !important;
        border: none !important;
        box-shadow: none !important;
    }

    .stTabs [data-baseweb="tab-highlight-container"],
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: #FFFFFF !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 12px 26px !important;
        color: #334155 !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-3px) scale(1.02) !important;
        background: #EEF2FF !important;
        color: #4338CA !important;
        border-color: #A5B4FC !important;
        box-shadow: 0 8px 22px rgba(99, 102, 241, 0.2) !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.4) !important;
        transform: translateY(-2px) !important;
    }

    .stTabs [aria-selected="true"] * {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* Metrics Cards */
    div[data-testid="stMetricValue"] {
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        color: #4F46E5 !important;
    }

    div[data-testid="stMetricLabel"] {
        font-weight: 700 !important;
        color: #475569 !important;
        font-size: 0.95rem !important;
    }

    /* Info & Briefing Containers */
    .stAlert {
        border-radius: 16px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 1.0rem !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
        border: 1.5px solid #C7D2FE !important;
        background: #EEF2FF !important;
        color: #1E293B !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.08) !important;
    }

    /* Badges */
    .verified-badge {
        background: #ECFDF5 !important;
        color: #047857 !important;
        border: 1.5px solid #A7F3D0 !important;
        padding: 4px 12px !important;
        border-radius: 20px !important;
        font-size: 0.8rem !important;
        font-weight: 800 !important;
        display: inline-block !important;
    }

    .severity-badge-high {
        background: #FFF1F2 !important;
        color: #E11D48 !important;
        border: 1.5px solid #FECDD3 !important;
        padding: 3px 10px !important;
        border-radius: 18px !important;
        font-weight: 800 !important;
        font-size: 0.78rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize DB & Session State
initialize_safewalk_system()

if "session_id" not in st.session_state:
    st.session_state.session_id = f"user_{uuid.uuid4().hex[:8]}"
if "voted" not in st.session_state:
    st.session_state.voted = set()
if "city" not in st.session_state:
    st.session_state.city = "Dehradun"
if "country" not in st.session_state:
    st.session_state.country = "India"
if "routes" not in st.session_state:
    st.session_state.routes = []
if "map_center" not in st.session_state:
    st.session_state.map_center = [30.3243, 78.0419]
if "ai_overview" not in st.session_state:
    st.session_state.ai_overview = None
if "current_briefing" not in st.session_state:
    st.session_state.current_briefing = None
if "rag_last_response" not in st.session_state:
    st.session_state.rag_last_response = None

# Sidebar Controls (Vibrant Interactive Styling & Emojis)
with st.sidebar:
    st.markdown('<div class="sidebar-title">🛡️ SafeWalk v2.0</div>', unsafe_allow_html=True)
    st.caption("⚡ AI-Powered Real-Time Women's Safety Navigation")
    
    st.markdown("### 🌐 Select Active City")
    
    with st.form("city_selector_form"):
        city_options = [
            "Dehradun", "Delhi", "Mumbai", "Bengaluru", "Kolkata", "Chennai", "Hyderabad",
            "Tokyo", "London", "Paris", "New York", "Lagos", "Dubai", "Singapore"
        ]
        
        sel_city = st.selectbox("🏙️ Popular Cities:", city_options, index=0, key="sb_city_select")
        cust_city = st.text_input("✍️ Or Type Custom City Name:", placeholder="e.g. Sydney, Berlin", key="sb_custom_city_input")
        city_submit = st.form_submit_button("📍 Set Active City", use_container_width=True)
        
        if city_submit:
            target_city = cust_city.strip().title() if cust_city.strip() else sel_city
            lat_c, lng_c = geocode_address(target_city)
            if lat_c is not None:
                st.session_state.city = html.escape(target_city)[:40]
                st.session_state.map_center = [lat_c, lng_c]
                city_g, country_g = get_city_country_from_coords(lat_c, lng_c)
                st.session_state.country = html.escape(country_g if country_g != "Unknown Country" else "Worldwide")[:40]
                st.session_state.routes = []
                st.session_state.current_briefing = None
                
                # Update location text input defaults for new city
                new_lms = get_city_landmark_suggestions(st.session_state.city)
                if new_lms:
                    st.session_state["direct_start_text_input"] = new_lms[0]
                    if len(new_lms) > 1:
                        st.session_state["direct_dest_text_input"] = new_lms[1]
                st.success(f"Active city set to **{st.session_state.city}**!")
            else:
                st.error(f"Could not locate '{target_city}'. Please check spelling.")
            
    st.info(f"📍 Active City: **{st.session_state.city}** ({st.session_state.country})")
    
    st.markdown("### 🕒 Travel Time")
    travel_hour = st.slider("Time of Travel (Hour):", 0, 23, 22, key="sb_travel_hour")
    time_icon = "🌙" if travel_hour >= 20 or travel_hour < 6 else "☀️"
    time_label = f"{time_icon} {travel_hour:02d}:00 ({'Night' if travel_hour >= 20 or travel_hour < 6 else 'Day'})"
    st.caption(f"Selected Time: **{time_label}**")
    
    st.divider()
    st.markdown("### 🤖 AI Actions")
    if st.button(f"📰 Fetch AI News for {st.session_state.city}", use_container_width=True, key="sb_news_btn"):
        with st.spinner(f"Ingesting live news & crime reports for {st.session_state.city}..."):
            n_res = ingest_city_news_reports(st.session_state.city, st.session_state.country)
            st.session_state.ai_news_results = (st.session_state.city, n_res)
            st.rerun()

    if st.session_state.get("ai_news_results"):
        news_city, n_res = st.session_state.ai_news_results
        if news_city == st.session_state.city:
            raw_list = n_res.get("raw_news_fetched", [])
            st.success(f"Ingested **{n_res.get('ingested_count', 0)}** News Alerts for **{html.escape(news_city)}**")
            with st.expander(f"View Fetched AI News ({len(raw_list)})", expanded=True):
                for item in raw_list:
                    source = html.escape(str(item.get("news_source", "News Alert")))
                    loc = html.escape(str(item.get("location_description", news_city)))
                    desc = html.escape(str(item.get("description", "")))
                    st.markdown(f"**{loc}** `<small>({source})</small>`", unsafe_allow_html=True)
                    if desc:
                        st.caption(desc)
                    st.divider()

    if st.button("📊 City Safety Overview", use_container_width=True, key="sb_overview_btn"):
        with st.spinner(f"Analyzing safety patterns for {st.session_state.city}..."):
            ov = get_city_safety_overview(st.session_state.city)
            st.session_state.ai_overview = (st.session_state.city, ov)

    if st.session_state.ai_overview:
        ov_c, ov_t = st.session_state.ai_overview
        st.info(f"**Overview for {html.escape(ov_c)}:**\n\n{html.escape(ov_t)}")
        
    st.divider()
    st.caption(f"Session ID: `{st.session_state.session_id}`")

# Header Section
st.markdown('<div class="main-title">SafeWalk — AI Women&#39;s Safety Navigation</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">Real-time crowdsourced safety routes & Gemini AI guidance for <b>{html.escape(st.session_state.city)}, {html.escape(st.session_state.country)}</b></div>', unsafe_allow_html=True)

# Tabs
tab1, tab_safestops, tab_guardian, tab2, tab3, tab4 = st.tabs([
    "Plan Safe Route",
    "SafeStops Help Points",
    "Live Journey Guardian",
    "Report Incident", 
    "Live Community Feed", 
    "Ask SafeWalk AI & SOS"
])

# -----------------------------------------------------------------------------
# TAB 1: ROUTE PLANNING
# -----------------------------------------------------------------------------
with tab1:
    landmarks = get_city_landmark_suggestions(st.session_state.city)
    
    # Auto-update widget state when city changes or defaults are unset
    default_start = landmarks[0] if len(landmarks) > 0 else f"Clock Tower, {st.session_state.city}"
    default_dest = landmarks[1] if len(landmarks) > 1 else f"UPES Bidholi, {st.session_state.city}"

    if "direct_start_text_input" not in st.session_state or st.session_state.get("active_city_tracker") != st.session_state.city:
        st.session_state["direct_start_text_input"] = default_start
    if "direct_dest_text_input" not in st.session_state or st.session_state.get("active_city_tracker") != st.session_state.city:
        st.session_state["direct_dest_text_input"] = default_dest
    st.session_state["active_city_tracker"] = st.session_state.city

    st.markdown(f"#### Quick Destination Suggestions for **{st.session_state.city}**:")
    sug_cols = st.columns(min(len(landmarks), 5))
    for idx, lm in enumerate(landmarks[:5]):
        with sug_cols[idx]:
            raw_title = lm.split(',')[0].strip()
            # Clean shortening for long titles to ensure 100% visual symmetry
            clean_title = raw_title.replace("Bandra Kurla Complex (BKC)", "BKC")\
                                   .replace("Andheri West Metro Station", "Andheri Metro")\
                                   .replace("Forest Research Institute (FRI)", "FRI Institute")\
                                   .replace("Rajiv Chowk Metro Station Exit 2", "Rajiv Chowk Metro")\
                                   .replace("Select Citywalk Mall", "Select Citywalk")\
                                   .replace("UPES Bidholi Campus", "UPES Bidholi")\
                                   .replace("UPES Kandoli Campus", "UPES Kandoli")\
                                   .replace("Pacific Mall, Rajpur Road", "Pacific Mall")\
                                   .replace("Chennai Central Railway Station", "Chennai Central")\
                                   .replace("Secunderabad Railway Station", "Secunderabad Station")\
                                   .replace("Washington Square Park, Greenwich Village", "Washington Square")\
                                   .replace("Howrah Railway Station", "Howrah Station")
            if st.button(clean_title, key=f"lm_chip_{idx}", use_container_width=True):
                st.session_state["direct_dest_text_input"] = lm
                st.rerun()

    with st.form("route_planning_form"):
        col_in1, col_in2, col_go = st.columns([4, 4, 3])
        
        with col_in1:
            start_input = st.text_input(
                f"Start Location in {st.session_state.city}:",
                placeholder=f"Type ANY location in {st.session_state.city}...",
                key="direct_start_text_input"
            )
                
        with col_in2:
            end_input = st.text_input(
                f"Destination in {st.session_state.city}:",
                placeholder=f"Type ANY location in {st.session_state.city}...",
                key="direct_dest_text_input"
            )
                
        with col_go:
            st.write("")
            st.write("")
            go_btn = st.form_submit_button("Find Safest Route", use_container_width=True, type="primary")

    if go_btn:
        s_loc = start_input.strip() if start_input.strip() else default_start
        e_loc = end_input.strip() if end_input.strip() else default_dest
        
        with st.spinner(f"Geocoding & calculating safest walking route in {st.session_state.city}..."):
            r_res = plan_safe_route(s_loc, e_loc, hour=travel_hour, fallback_city=st.session_state.city)
            if r_res["success"]:
                if r_res["city"] and r_res["city"] != "Unknown City":
                    st.session_state.city = r_res["city"]
                st.session_state.country = r_res["country"]
                st.session_state.routes = [r_res["routes"]["safest"], r_res["routes"]["fastest"]]
                st.session_state.map_center = [r_res["start"]["lat"], r_res["start"]["lng"]]
                st.session_state.current_briefing = r_res["ai_safety_briefing"]
            else:
                st.error(r_res.get("error", "Route planning failed."))

    col_map, col_report = st.columns([7, 5])

    # State for selected segment
    if "selected_segment_id" not in st.session_state:
        st.session_state.selected_segment_id = None
    
    with col_map:
        st.markdown(f"### Interactive Map: {html.escape(st.session_state.city)}, {html.escape(st.session_state.country)}")
        
        # Legend for Explainable Segments
        st.markdown("""
        <div style="display:flex; flex-wrap:wrap; gap:12px; margin-bottom:10px; font-size:12px; font-weight:600; color:#334155;">
          <span style="display:inline-flex; align-items:center; gap:5px;"><span style="width:12px; height:12px; border-radius:3px; background:#059669; display:inline-block;"></span> Lower observed risk</span>
          <span style="display:inline-flex; align-items:center; gap:5px;"><span style="width:12px; height:12px; border-radius:3px; background:#D97706; display:inline-block;"></span> Mixed indicators</span>
          <span style="display:inline-flex; align-items:center; gap:5px;"><span style="width:12px; height:12px; border-radius:3px; background:#DC2626; display:inline-block;"></span> Elevated reported-risk</span>
          <span style="display:inline-flex; align-items:center; gap:5px;"><span style="width:12px; height:12px; border-radius:3px; border:2px dashed #64748B; display:inline-block;"></span> Insufficient data</span>
        </div>
        """, unsafe_allow_html=True)

        m = build_safety_map(center=st.session_state.map_center)
        if m is not None:
            if len(st.session_state.routes) >= 2:
                m = add_routes_to_map(
                    m,
                    st.session_state.routes[0],
                    st.session_state.routes[1],
                    selected_segment_id=st.session_state.selected_segment_id
                )
            elif len(st.session_state.routes) == 1:
                m = add_routes_to_map(
                    m,
                    st.session_state.routes[0],
                    st.session_state.routes[0],
                    selected_segment_id=st.session_state.selected_segment_id
                )
            st_folium(m, height=520, use_container_width=True, key="safewalk_map_view")
            
    with col_report:
        if st.session_state.routes:
            safe, fast = st.session_state.routes[0], st.session_state.routes[-1]
            seg_intel = safe.get("segment_intelligence") or {}
            segments_list = seg_intel.get("segments", [])

            # --- OVERALL ROUTE EXPLANATION CARD (FEATURE 6) ---
            st.markdown("### Route Intelligence Overview")
            
            score = seg_intel.get("overall_score", safe.get('safety_avg', 70))
            overall_class = seg_intel.get("overall_classification", "Mixed safety indicators")
            overall_conf = seg_intel.get("overall_confidence", "Medium confidence")
            coverage = seg_intel.get("coverage_percentage", 65)
            
            # Badge styling
            conf_badge_bg = "#ECFDF5" if "High" in overall_conf else "#EFF6FF" if "Medium" in overall_conf else "#FEF3C7" if "Low" in overall_conf else "#F1F5F9"
            conf_badge_color = "#047857" if "High" in overall_conf else "#1D4ED8" if "Medium" in overall_conf else "#B45309" if "Low" in overall_conf else "#475569"

            st.markdown(f"""
            <div style="background:#FFFFFF; border:1.5px solid #E2E8F0; border-radius:14px; padding:16px; margin-bottom:16px; box-shadow:0 4px 14px rgba(0,0,0,0.04);">
              <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                <div>
                  <span style="font-size:12px; font-weight:700; color:#64748B; text-transform:uppercase; letter-spacing:0.5px;">Recommendation</span>
                  <div style="font-size:17px; font-weight:800; color:#0F172A;">{html.escape(overall_class)}</div>
                </div>
                <div style="text-align:right;">
                  <span style="background:{conf_badge_bg}; color:{conf_badge_color}; padding:4px 10px; border-radius:20px; font-size:12px; font-weight:700;">
                    {html.escape(overall_conf)}
                  </span>
                </div>
              </div>
              <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin-top:12px; text-align:center;">
                <div style="background:#F8FAFC; padding:8px; border-radius:10px;">
                  <div style="font-size:11px; color:#64748B; font-weight:600;">Safety Score</div>
                  <div style="font-size:18px; font-weight:800; color:#0F172A;">{score}<small style="font-size:11px; color:#94A3B8;">/100</small></div>
                </div>
                <div style="background:#F8FAFC; padding:8px; border-radius:10px;">
                  <div style="font-size:11px; color:#64748B; font-weight:600;">Data Coverage</div>
                  <div style="font-size:18px; font-weight:800; color:#0F172A;">{coverage}%</div>
                </div>
                <div style="background:#F8FAFC; padding:8px; border-radius:10px;">
                  <div style="font-size:11px; color:#64748B; font-weight:600;">Segments</div>
                  <div style="font-size:18px; font-weight:800; color:#0F172A;">{len(segments_list)}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Route summary reasons
            reasons = seg_intel.get("summary_reasons", [])
            if reasons:
                with st.expander("Why this route was recommended:", expanded=True):
                    for r in reasons:
                        st.markdown(f"• {html.escape(r)}")
                    st.caption("*Note: Safety scores represent relative reported-risk indicators from open data and community reports, not real-world guarantees.*")

            st.divider()

            # --- SEGMENT INFORMATION PANEL (FEATURE 5) ---
            st.markdown("### Segment-Level Deep Dive")
            
            if segments_list:
                # Segment Selector Dropdown
                options = [f"{s['title']} ({s['safety_score']}/100 - {s['qualitative_class']})" for s in segments_list]
                
                # Find default index
                default_idx = 0
                if st.session_state.selected_segment_id:
                    for i, s in enumerate(segments_list):
                        if s["segment_id"] == st.session_state.selected_segment_id:
                            default_idx = i
                            break
                            
                chosen_opt = st.selectbox(
                    "Inspect individual route segment:",
                    options=options,
                    index=default_idx,
                    key="segment_selector_sb"
                )
                
                # Parse chosen segment index
                chosen_idx = options.index(chosen_opt)
                active_seg = segments_list[chosen_idx]
                st.session_state.selected_segment_id = active_seg["segment_id"]

                # Segment Details Card
                seg_conf = active_seg["confidence"]
                seg_score = active_seg["safety_score"]
                seg_class = active_seg["qualitative_class"]
                seg_ev = active_seg["evidence"]

                st.markdown(f"""
                <div style="background:#FFFFFF; border:2px solid {active_seg['status_color']}; border-radius:14px; padding:16px; margin-top:10px;">
                  <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="font-size:15px; color:#0F172A;">{html.escape(active_seg['title'])}</b>
                    <span style="background:{active_seg['status_color']}20; color:{active_seg['status_color']}; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:800;">
                      {html.escape(seg_class)}
                    </span>
                  </div>
                  <div style="font-size:12px; color:#64748B; margin-top:4px;">
                    Length: <b>{round(active_seg['distance_m'])}m</b> • Walking time: ~<b>{round(active_seg['duration_sec'])}s</b> • Road: <b>{html.escape(active_seg['road_name'])}</b>
                  </div>
                  <hr style="margin:10px 0; border:0; border-top:1px solid #E2E8F0;">
                  <div style="font-size:13px; color:#1E293B; line-height:1.5;">
                    <b>Assessment Explanation:</b><br>{html.escape(active_seg['explanation'])}
                  </div>
                </div>
                """, unsafe_allow_html=True)

                # Segment Evidence & Provenance Tabs
                ev_tab1, ev_tab2, ev_tab3 = st.tabs(["Available Evidence", "Score Breakdown", "Confidence Audit"])
                
                with ev_tab1:
                    st.markdown("**1. Street Lighting:**")
                    lit_info = seg_ev.get("lighting", {})
                    lit_icon = "💡" if lit_info.get("status") == "present" else "🌑" if lit_info.get("status") == "absent" else "❓"
                    st.markdown(f"{lit_icon} **Status:** `{lit_info.get('status')}` — {html.escape(lit_info.get('details', ''))}")
                    st.caption(f"Source: *{lit_info.get('source')}* | Retrieved: `{lit_info.get('retrieved_at')}`")

                    st.markdown("**2. Commercial Activity:**")
                    comm_info = seg_ev.get("commercial", {})
                    st.markdown(f"🏪 **Mapped venues:** **{comm_info.get('mapped_count', 0)}** establishments within 150m.")
                    if comm_info.get("sample_places"):
                        sample_names = ", ".join([p["name"] for p in comm_info["sample_places"]])
                        st.caption(f"Establishments: {html.escape(sample_names)}")
                    st.caption(f"Source: *{comm_info.get('source')}* (Note: Real-time open hours not verified)")

                    st.markdown("**3. Community Incidents & Reports:**")
                    inc_info = seg_ev.get("incidents", {})
                    items = inc_info.get("items", [])
                    if items:
                        for inc in items:
                            st.warning(
                                f"⚠️ **{html.escape(inc['category'])}** ({inc['relative_time']})\n\n"
                                f"Distance: {inc['distance_m']}m away | Severity: {inc['severity']}/3 | "
                                f"Status: *{inc['status_label']}*\n\n"
                                f"Ref: `{inc['source_reference']}`\n\n"
                                f"\"{html.escape(inc['description'])}\""
                            )
                    else:
                        st.success("No active community incident reports located within 250m of this section.")

                    st.markdown("**4. Emergency & Assistance Facilities:**")
                    em_info = seg_ev.get("emergency", {})
                    if em_info.get("status") == "mapped_nearby":
                        near = em_info["nearest_facility"]
                        st.info(f"🚓 **{html.escape(near['name'])}** ({near['type']}) mapped **{near['distance_m']}m** away.")
                        st.caption(f"Source: *{em_info.get('source')}* (Operational status not guaranteed)")
                    else:
                        st.caption("No police station or hospital mapped within 800m.")

                with ev_tab2:
                    st.markdown(f"**Baseline Score:** 100/100 ➔ **Final:** `{seg_score}/100`")
                    for factor in active_seg.get("score_breakdown", []):
                        d_val = factor["delta"]
                        color_cls = "green" if d_val > 0 else "red" if d_val < 0 else "gray"
                        sign = "+" if d_val > 0 else ""
                        st.markdown(
                            f"**{factor['factor']}** (`{sign}{d_val}` pts)\n\n"
                            f"<small style='color:#64748B;'>{html.escape(factor['evidence'])} "
                            f"(Source: *{html.escape(factor['source'])}*)</small>",
                            unsafe_allow_html=True
                        )
                        st.divider()

                with ev_tab3:
                    st.markdown(f"**Data Confidence Level:** **{seg_conf['confidence_level']}** ({seg_conf['confidence_score']}/100)")
                    st.progress(seg_conf["confidence_score"] / 100.0)
                    st.markdown(f"**Attribute Coverage:** **{seg_conf['coverage_percentage']}%**")
                    
                    st.markdown(f"• **Confirmed Categories:** {', '.join(seg_conf.get('confirmed_categories', []))}")
                    if seg_conf.get("missing_categories"):
                        st.markdown(f"• **Missing/Unknown:** {', '.join(seg_conf.get('missing_categories', []))}")
                    
                    with st.expander("Confidence Pillars Breakdown"):
                        for p_name, p_val in seg_conf.get("pillar_scores", {}).items():
                            st.write(f"- {p_name.capitalize()}: **{p_val}/100**")
            else:
                st.info("Route segment breakdown is available once a route is generated.")
                
            st.divider()
            st.markdown("### AI Route Safety Briefing")
            brief = st.session_state.get("current_briefing")
            if not brief:
                stats = get_city_stats(st.session_state.city)
                brief = generate_safety_briefing(
                    score, f"{travel_hour:02d}:00", st.session_state.city, st.session_state.country,
                    verified_reports=stats.get("verified", 0), recent_reports=stats.get("last_24h", 0)
                )
            st.info(brief)
        else:
            st.info(f"Select locations above and click **Find Safest Route** to calculate walking routes in **{st.session_state.city}**.")

# -----------------------------------------------------------------------------
# TAB: SAFESTOPS - NEARBY ASSISTANCE LOCATIONS (FEATURE 2)
# -----------------------------------------------------------------------------
with tab_safestops:
    st.markdown("### 🛡️ SafeStops — Find a Nearby Place to Get Assistance")
    st.caption("Locate verified police stations, 24/7 hospitals, campus security booths, partner pharmacies, and community safe havens.")

    c_ss_ctrl1, c_ss_ctrl2, c_ss_ctrl3 = st.columns([3, 3, 4])
    with c_ss_ctrl1:
        ss_cat = st.selectbox(
            "Filter Facility Category:",
            options=["all", "police", "hospital", "campus_security", "pharmacy", "community_help"],
            format_func=lambda x: "All Assistance Types" if x == "all" else {
                "police": "🚓 Police Facilities",
                "hospital": "🏥 Hospitals & Emergency",
                "campus_security": "🎓 Campus Security Desks",
                "pharmacy": "💊 24/7 Pharmacies",
                "community_help": "🛡️ Participating Safe Havens"
            }.get(x, x),
            key="ss_category_select"
        )
    with c_ss_ctrl2:
        ss_radius = st.select_slider(
            "Search Radius:",
            options=[0.5, 1.0, 2.0, 5.0, 10.0],
            value=2.0,
            format_func=lambda r: f"{int(r*1000)}m" if r < 1.0 else f"{int(r)} km",
            key="ss_radius_slider"
        )
    with c_ss_ctrl3:
        st.write("")
        st.write("")
        c_ss_btn1, c_ss_btn2 = st.columns(2)
        with c_ss_btn1:
            refresh_ss = st.button("Search SafeStops", use_container_width=True, type="primary")
        with c_ss_btn2:
            quick_help_btn = st.button("🚨 Navigate to Nearest Help", use_container_width=True)

    # Reference coordinate for SafeStops search
    ref_lat, ref_lng = st.session_state.map_center

    # Query SafeStops
    nearby_stops = find_nearby_safestops(ref_lat, ref_lng, radius_km=ss_radius, category_filter=ss_cat, limit=12)

    # Quick Emergency Action
    if quick_help_btn and nearby_stops:
        target_help = nearby_stops[0]
        st.session_state["direct_start_text_input"] = f"{st.session_state.city}"
        st.session_state["direct_dest_text_input"] = target_help["name"]
        st.success(f"Navigating to nearest help: **{target_help['name']}** ({target_help['distance_m']}m away)!")
        # Auto-trigger route planning
        r_res = plan_safe_route(f"{ref_lat},{ref_lng}", f"{target_help['latitude']},{target_help['longitude']}", hour=travel_hour, fallback_city=st.session_state.city)
        if r_res["success"]:
            st.session_state.routes = [r_res["routes"]["safest"], r_res["routes"]["fastest"]]
            st.session_state.current_briefing = r_res["ai_safety_briefing"]
            st.rerun()

    ss_col_map, ss_col_list = st.columns([7, 5])

    with ss_col_map:
        st.markdown(f"#### SafeStops Map ({len(nearby_stops)} points found within {ss_radius}km)")
        
        # Legend
        st.markdown("""
        <div style="display:flex; flex-wrap:wrap; gap:10px; margin-bottom:8px; font-size:11px; font-weight:700;">
          <span style="color:#1E40AF;">🚓 Police</span>
          <span style="color:#DC2626;">🏥 Hospital/Trauma</span>
          <span style="color:#7C3AED;">🎓 Campus Security</span>
          <span style="color:#059669;">💊 Pharmacy</span>
          <span style="color:#D97706;">🛡️ Safe Haven</span>
          <span style="color:#475569; margin-left:auto;">✔ Verified Partner | 🌐 Public Facility</span>
        </div>
        """, unsafe_allow_html=True)

        ss_map = build_safety_map(center=[ref_lat, ref_lng], zoom=13)
        if ss_map is not None:
            ss_map = add_safestops_to_map(ss_map, nearby_stops, user_location=[ref_lat, ref_lng])
            st_folium(ss_map, height=520, use_container_width=True, key="safestops_map_view")

    with ss_col_list:
        st.markdown(f"#### Nearby Facilities Directory")
        if nearby_stops:
            for s in nearby_stops:
                v_border = s["verification_badge_color"]
                with st.container():
                    st.markdown(f"""
                    <div style="background:#FFFFFF; border-left:4px solid {v_border}; border-top:1px solid #E2E8F0; border-right:1px solid #E2E8F0; border-bottom:1px solid #E2E8F0; border-radius:12px; padding:12px; margin-bottom:12px; box-shadow:0 2px 8px rgba(0,0,0,0.03);">
                      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                          <b style="font-size:14px; color:#0F172A;">{s['category_icon']} {html.escape(s['name'])}</b>
                          <div style="font-size:11px; color:#64748B; margin-top:2px;">📍 {html.escape(s['address'])}</div>
                        </div>
                        <span style="background:{v_border}15; color:{v_border}; font-size:10px; font-weight:800; padding:3px 8px; border-radius:12px; border:1px solid {v_border}40;">
                          {s['verification_status']}
                        </span>
                      </div>
                      <div style="display:flex; gap:16px; font-size:11px; font-weight:600; color:#334155; margin:8px 0;">
                        <span>🚶 <b>{s['distance_m']}m</b> (~{s['walking_time_min']} mins walk)</span>
                        <span>🕒 <b>{html.escape(s['opening_hours'])}</b></span>
                      </div>
                      <div style="font-size:10px; color:#64748B; background:#F8FAFC; padding:6px; border-radius:6px;">
                        <b>Provenance:</b> {html.escape(s['source_reference'])}<br>
                        <b>Evidence:</b> {html.escape(s['verification_evidence'])}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c_act1, c_act2, c_act3 = st.columns([4, 4, 4])
                    with c_act1:
                        if s["phone"] and s["phone"] != "Not available":
                            st.link_button(f"📞 Call {s['phone']}", f"tel:{s['phone']}", use_container_width=True)
                        else:
                            st.caption("Phone unlisted")
                    with c_act2:
                        if s["website"] and s["website"] != "Not available":
                            st.link_button("🌐 Website", s["website"], use_container_width=True)
                        else:
                            st.caption("No website")
                    with c_act3:
                        if st.button("Walk Here ➔", key=f"nav_ss_{s['id']}", use_container_width=True):
                            st.session_state["direct_start_text_input"] = f"{ref_lat},{ref_lng}"
                            st.session_state["direct_dest_text_input"] = f"{s['latitude']},{s['longitude']}"
                            # Calculate route
                            r_res = plan_safe_route(f"{ref_lat},{ref_lng}", f"{s['latitude']},{s['longitude']}", hour=travel_hour, fallback_city=st.session_state.city)
                            if r_res["success"]:
                                st.session_state.routes = [r_res["routes"]["safest"], r_res["routes"]["fastest"]]
                                st.session_state.current_briefing = r_res["ai_safety_briefing"]
                                st.success(f"Route set to {s['name']}! Switch to 'Plan Safe Route' tab to view navigation steps.")
                                st.rerun()
                    st.divider()
        else:
            st.info(f"No SafeStops currently registered within {ss_radius}km. Broaden your search radius above or submit a community location below.")

    # Expandable: Submit a new community safe haven
    with st.expander("➕ Submit a Safe Haven or Assistance Point"):
        st.caption("Community-submitted locations are marked as COMMUNITY-LISTED until audited by SafeWalk administrators.")
        with st.form("community_safestop_form"):
            c_sub1, c_sub2 = st.columns(2)
            with c_sub1:
                cs_name = st.text_input("Location / Facility Name:", placeholder="e.g. 24/7 Medicos Store")
                cs_cat = st.selectbox("Category:", ["police", "hospital", "campus_security", "pharmacy", "community_help"])
                cs_addr = st.text_input("Full Address:", placeholder="e.g. Near Mall Road entrance")
            with c_sub2:
                cs_phone = st.text_input("Contact Number (Optional):", placeholder="+91...")
                cs_hours = st.text_input("Operating Hours:", value="Open 24/7")
                cs_notes = st.text_area("Verification Notes / References:", placeholder="Describe why this location offers safety assistance...")
            
            sub_ss_btn = st.form_submit_button("Submit for Community Listing", type="primary")

        if sub_ss_btn and cs_name.strip():
            # Geocode the address or use map center
            c_lat, c_lng = ref_lat, ref_lng
            res_add = add_community_safestop(
                name=cs_name,
                category=cs_cat,
                lat=c_lat,
                lng=c_lng,
                address=cs_addr,
                phone=cs_phone,
                opening_hours=cs_hours,
                notes=cs_notes
            )
            if res_add["success"]:
                st.success(f"SafeStop '{cs_name}' registered with status: **COMMUNITY-LISTED**.")
                st.rerun()
            else:
                st.error(res_add.get("error", "Failed to add SafeStop."))

# -----------------------------------------------------------------------------
# TAB: LIVE JOURNEY GUARDIAN (FEATURE 3)
# -----------------------------------------------------------------------------
with tab_guardian:
    st.markdown("### 🛡️ Live Journey Guardian — Real-Time Tracking & Trusted Contact Escalation")
    st.caption("Share your journey with family & friends, schedule automated check-in deadlines, and escalate missed check-ins automatically.")

    # Run background escalation cycle
    process_server_side_escalations()

    # Session State for User's Active Journey
    if "active_journey" not in st.session_state:
        st.session_state.active_journey = None

    c_g_user, c_g_contacts = st.columns([7, 5])

    with c_g_user:
        # Check if user has an active journey
        curr_j = st.session_state.active_journey

        if curr_j:
            j_id = curr_j["journey_id"]
            # Fetch latest telemetry
            loc_info = get_latest_journey_location(j_id)
            share_tok = curr_j.get("share_token", "")
            
            st.markdown(f"""
            <div style="background:#F0FDF4; border:2px solid #22C55E; border-radius:14px; padding:16px; margin-bottom:16px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <b style="font-size:16px; color:#15803D;">● Live Protected Journey in Progress</b>
                <span style="background:#22C55E; color:#FFFFFF; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:800;">
                  ACTIVE TELEMETRY
                </span>
              </div>
              <div style="font-size:13px; color:#166534; margin-top:6px;">
                Destination: <b>{curr_j.get('destination_name', 'Destination')}</b> • Expected Arrival: <b>{curr_j.get('expected_arrival', 'N/A')}</b>
              </div>
              <div style="font-size:12px; color:#374151; margin-top:4px;">
                GPS Status: <b>{'Live (~' + str(loc_info['seconds_ago']) + 's ago)' if loc_info and not loc_info['is_stale'] else 'Telemetry Stale (>2m)' if loc_info else 'Awaiting Signal'}</b>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Check-in Action Bar
            st.markdown("#### Check-In Status")
            st.info(f"Next automated check-in scheduled for: **{curr_j.get('next_checkin_deadline', 'Pending')}**")
            
            c_chk1, c_chk2, c_chk3 = st.columns(3)
            with c_chk1:
                if st.button("🟢 I'm Okay", use_container_width=True, type="primary"):
                    c_res = confirm_checkin(j_id, "im_okay")
                    if c_res["success"]:
                        curr_j["next_checkin_deadline"] = c_res["next_deadline"]
                        st.toast("Check-in confirmed! Timer reset.", icon="✅")
                        st.rerun()
            with c_chk2:
                if st.button("🚨 Need Assistance", use_container_width=True):
                    a_res = confirm_checkin(j_id, "need_assistance")
                    st.error("Emergency Alert dispatched to trusted contacts!")
                    st.rerun()
            with c_chk3:
                if st.button("🏁 Complete Journey", use_container_width=True):
                    complete_or_cancel_journey(j_id, is_completed=True)
                    st.session_state.active_journey = None
                    st.success("Journey marked complete. Location sharing terminated.")
                    st.rerun()

            # Shareable Guardian Token Link
            st.markdown("#### Secure Temporary Contact Link")
            st.code(f"https://safewalk.app/guardian?token={share_tok}", language="text")
            st.caption("Only individuals with this unique cryptographically-hashed token can view your live progress. Access expires automatically after your trip ends.")

            # Live GPS Simulation & Telemetry Update
            with st.expander("Update Current GPS Coordinates"):
                c_gps1, c_gps2 = st.columns(2)
                with c_gps1:
                    new_lat = st.number_input("Current Lat:", value=float(ref_lat), format="%.6f", key="sim_lat")
                with c_gps2:
                    new_lng = st.number_input("Current Lng:", value=float(ref_lng), format="%.6f", key="sim_lng")
                if st.button("Broadcast Location Update", use_container_width=True):
                    record_location_update(j_id, new_lat, new_lng, accuracy=8.0)
                    st.success("Location update broadcasted to authorized contact viewers.")
                    st.rerun()

        else:
            # Setup Form to Start New Journey
            st.markdown("#### Start a Protected Journey")
            with st.form("start_journey_form"):
                j_dest = st.text_input("Destination:", value=f"College Hostel, {st.session_state.city}")
                j_start_addr = st.text_input("Starting Address:", value=f"Main Gate, {st.session_state.city}")
                
                c_j_cfg1, c_j_cfg2, c_j_cfg3 = st.columns(3)
                with c_j_cfg1:
                    j_dur = st.number_input("Duration (Mins):", min_value=5, max_value=180, value=25)
                with c_j_cfg2:
                    j_chk_int = st.selectbox("Check-in Interval:", [2, 5, 10, 15], index=1, format_func=lambda m: f"Every {m} mins")
                with c_j_cfg3:
                    j_grace = st.selectbox("Grace Period:", [1, 2, 3, 5], index=1, format_func=lambda g: f"{g} mins grace")

                j_note = st.text_area("Optional Journey Note for Contacts:", placeholder="e.g. Walking home with study group from central library...")
                j_consent = st.checkbox("I explicitly grant permission to share my live location with selected trusted contacts for the duration of this trip.", value=True)
                
                start_j_btn = st.form_submit_button("Start Journey Guardian", type="primary")

            if start_j_btn:
                if not j_consent:
                    st.error("Location sharing permission is required to activate Journey Guardian.")
                else:
                    # Get user contacts
                    all_c = get_trusted_contacts(st.session_state.session_id)
                    contact_ids = [c["id"] for c in all_c]
                    
                    j_res = create_journey(
                        owner_user_id=st.session_state.session_id,
                        start_lat=ref_lat,
                        start_lng=ref_lng,
                        start_address=j_start_addr,
                        dest_lat=ref_lat + 0.015,
                        dest_lng=ref_lng + 0.015,
                        dest_name=j_dest,
                        expected_duration_min=j_dur,
                        checkin_interval_min=j_chk_int,
                        grace_period_min=j_grace,
                        selected_contact_ids=contact_ids,
                        journey_note=j_note
                    )
                    if j_res["success"]:
                        st.session_state.active_journey = {
                            "journey_id": j_res["journey_id"],
                            "destination_name": j_dest,
                            "share_token": j_res["share_token"],
                            "expected_arrival": j_res["expected_arrival"],
                            "next_checkin_deadline": j_res["next_checkin_deadline"]
                        }
                        st.balloons()
                        st.success("Journey Guardian active! Location sharing initiated.")
                        st.rerun()
                    else:
                        st.error(j_res.get("error", "Failed to start journey."))

    with c_g_contacts:
        st.markdown("#### Trusted Contacts Management")
        st.caption("Trusted contacts receive emergency SMS alerts when a check-in is missed or when you request assistance.")

        contacts = get_trusted_contacts(st.session_state.session_id)
        if contacts:
            for c in contacts:
                with st.container():
                    st.markdown(f"""
                    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:10px; margin-bottom:8px;">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="color:#0F172A; font-size:13px;">👤 {html.escape(c['contact_name'])}</b>
                        <span style="font-size:10px; background:#EEF2FF; color:#4338CA; padding:2px 6px; border-radius:8px; font-weight:700;">
                          {html.escape(c['relationship'] or 'Contact')}
                        </span>
                      </div>
                      <div style="font-size:11px; color:#64748B; margin-top:2px;">
                        📞 {html.escape(c['phone'] or 'No phone')} | ✉️ {html.escape(c['email'] or 'No email')}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Remove Contact", key=f"del_c_{c['id']}"):
                        delete_trusted_contact(c["id"], st.session_state.session_id)
                        st.rerun()
        else:
            st.info("No trusted contacts added yet. Add trusted family members or friends below.")

        with st.expander("➕ Add Trusted Contact"):
            with st.form("add_contact_form"):
                tc_name = st.text_input("Full Name:", placeholder="e.g. Sister / Roommate")
                tc_phone = st.text_input("Mobile Phone (E.164):", placeholder="+91 98765 43210")
                tc_email = st.text_input("Email (Optional):", placeholder="contact@example.com")
                tc_rel = st.selectbox("Relationship:", ["Mother", "Father", "Sister", "Brother", "Friend", "Roommate", "Partner", "Guardian"])
                tc_chan = st.selectbox("Preferred Alert Channel:", ["sms", "email", "in_app"])
                
                sub_tc_btn = st.form_submit_button("Save Trusted Contact", type="primary")

            if sub_tc_btn and tc_name.strip():
                add_res = add_trusted_contact(
                    owner_user_id=st.session_state.session_id,
                    name=tc_name,
                    email=tc_email,
                    phone=tc_phone,
                    relationship=tc_rel,
                    preferred_channel=tc_chan
                )
                if add_res["success"]:
                    st.success(f"Added {tc_name} to trusted contacts.")
                    st.rerun()
                else:
                    st.error(add_res.get("error", "Failed to add contact."))

        # Contact Viewer Simulation Mode (Demonstrates Feature 16B - Contact Dashboard)
        with st.expander("👁️ Preview Trusted Contact Dashboard (Token Viewer)"):
            st.caption("Simulate how an invited trusted contact views the shared trip.")
            sim_tok = st.text_input("Enter Share Token:", value=st.session_state.active_journey.get("share_token", "") if st.session_state.active_journey else "")
            if sim_tok:
                view_data = get_journey_by_share_token(sim_tok)
                if view_data:
                    st.markdown(f"""
                    <div style="background:#F8FAFC; border:1.5px solid #CBD5E1; border-radius:12px; padding:12px;">
                      <b style="color:#0F172A;">Trip Destination: {html.escape(view_data.get('destination_name', 'Destination'))}</b><br>
                      <span>Status: <b>{view_data.get('status')}</b></span><br>
                      <span>Expected Arrival: <b>{view_data.get('expected_arrival')}</b></span><br>
                      <hr style="margin:6px 0;">
                      <span>Note from user: <i>"{html.escape(view_data.get('journey_note') or 'None')}"</i></span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🤝 Acknowledge Alert ('I am responding')", key="sim_ack_btn"):
                        ack_res = acknowledge_alert(view_data["journey_id"], contact_id=1, contact_name="Mom")
                        if ack_res["success"]:
                            st.success("Alert acknowledged! Status transitioned to ASSISTANCE_ACKNOWLEDGED.")
                            st.rerun()
                else:
                    st.error("Invalid or expired share token.")

# -----------------------------------------------------------------------------
# TAB 2: INCIDENT REPORTING (NLP)
# -----------------------------------------------------------------------------
with tab2:
    st.markdown(f"### Report an Unsafe Incident in {st.session_state.city}")
    st.caption("No complicated forms. Describe what happened in plain English or Hindi. Gemini NLP extracts location, incident type, and severity automatically.")
    
    with st.form("nlp_report_form"):
        rep_text = st.text_area(
            "What happened and where?", 
            placeholder=f"e.g. Catcalling and aggressive shouting near main station in {st.session_state.city} at 10pm...", 
            height=100,
            key="nlp_report_text_area"
        )
        sub_btn = st.form_submit_button("Submit Incident Report", type="primary")
    
    if sub_btn and rep_text.strip():
        with st.spinner("Processing report with Gemini NLP & updating real-time map weights..."):
            r_out = process_and_save_user_report(rep_text, current_city=st.session_state.city, country=st.session_state.country)
            if r_out["success"]:
                st.balloons()
                st.success(f"Report saved successfully! Geocoded Location: ({r_out['saved_location']['lat']}, {r_out['saved_location']['lng']})")
                st.json(r_out["nlp_parsed"])
                st.rerun()
            else:
                st.error("Could not process report. Please be more specific.")

# -----------------------------------------------------------------------------
# TAB 3: LIVE FEED & VOTING (XSS Protected)
# -----------------------------------------------------------------------------
with tab3:
    st.markdown(f"### Live Community Incident Feed for {st.session_state.city}")
    stats = get_city_stats(st.session_state.city)
    
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Reports", stats.get("total", 0))
    s2.metric("Last 24 Hours", stats.get("last_24h", 0))
    s3.metric("Verified Reports", stats.get("verified", 0))
    s4.metric("Avg Severity", f"{stats.get('avg_severity', 0.0)} / 3")
    
    st.divider()
    recent = get_recent_reports_in_city(st.session_state.city, limit=10)
    if recent:
        for row in recent:
            inc_id, inc_type, sev, ts_str, up, ver, desc, rlat, rlng = row
            try:
                ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                h = (datetime.now() - ts).total_seconds() / 3600
                tlabel = f"{int(h*60)}m ago" if h < 1 else f"{int(h)}h ago" if h < 24 else f"{int(h/24)}d ago"
            except Exception:
                tlabel = "Recent"
                
            badge = " <span class='verified-badge'>Verified</span>" if ver else ""
            sev_class = "severity-badge-high" if sev == 3 else ""
            
            # HTML XSS Sanitization
            safe_desc = html.escape(str(desc)) if desc else ""
            safe_type = html.escape(str(inc_type))
            
            with st.container():
                ci, cv = st.columns([4, 1])
                with ci:
                    st.markdown(f"**[{safe_type.upper()}]{badge}** • <small style='color:#475569;'>{tlabel}</small>", unsafe_allow_html=True)
                    if safe_desc:
                        st.write(safe_desc)
                    st.caption(f"Coordinates: ({rlat}, {rlng}) • Upvotes: {up}")
                with cv:
                    if inc_id in st.session_state.voted:
                        st.caption("Voted")
                    else:
                        v1, v2 = st.columns(2)
                        if v1.button("Upvote", key=f"u_{inc_id}"):
                            if handle_vote(inc_id, st.session_state.session_id, "up")["success"]:
                                st.session_state.voted.add(inc_id)
                                st.rerun()
                        if v2.button("Downvote", key=f"d_{inc_id}"):
                            if handle_vote(inc_id, st.session_state.session_id, "down")["success"]:
                                st.session_state.voted.add(inc_id)
                                st.rerun()
                st.divider()
    else:
        st.info(f"No active reports yet in {st.session_state.city}. Be the first to report or click **Fetch AI News** in the sidebar!")

# -----------------------------------------------------------------------------
# TAB 4: RAG AI ASSISTANT & SOS
# -----------------------------------------------------------------------------
with tab4:
    col_rag, col_sos = st.columns(2)
    
    with col_rag:
        st.markdown("### SafeWalk RAG AI Assistant")
        st.caption(f"Answers grounded in official WHO & NCRB Women's Safety Guidelines for {st.session_state.city}.")
        
        with st.form("rag_assistant_form"):
            user_q = st.text_input(
                "Ask a safety question:", 
                value=f"What should I do if I feel followed by someone at night in {st.session_state.city}?",
                key="rag_safety_question_input"
            )
            rag_ask_btn = st.form_submit_button("Ask AI Assistant")
            
        if rag_ask_btn and user_q.strip():
            with st.spinner("Searching WHO/NCRB knowledge base & Gemini AI..."):
                st.session_state.rag_last_response = ask_safewalk_ai(user_q, city=st.session_state.city, country=st.session_state.country)
                
        if st.session_state.rag_last_response:
            rag_out = st.session_state.rag_last_response
            st.markdown("#### AI Guidance:")
            st.info(rag_out["answer"])
            with st.expander("Show Retrieved Knowledge Base Context"):
                st.text(rag_out.get("retrieved_context", ""))
                    
    with col_sos:
        st.markdown("### Emergency SOS Alert Generator")
        with st.form("sos_generator_form"):
            sos_user = st.text_input("Your Name:", value="Aditi", key="sos_user_name_input")
            sos_start = st.text_input("Current Location:", value=f"Main Square, {st.session_state.city}", key="sos_start_loc_input")
            sos_dest = st.text_input("Destination Location:", value=f"Central Area, {st.session_state.city}", key="sos_dest_loc_input")
            sos_gen_btn = st.form_submit_button("Generate Emergency SMS", type="primary")
            
        if sos_gen_btn:
            if sos_user.strip():
                sms_msg = generate_sos_message(sos_user, sos_start, sos_dest, st.session_state.city)
                st.warning(f"**SMS Alert Text (<160 chars):**\n\n{html.escape(sms_msg)}")
            else:
                st.warning("Please enter your name for the emergency alert.")
