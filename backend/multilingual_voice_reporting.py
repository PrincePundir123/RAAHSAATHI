# multilingual_voice_reporting.py - Feature 4: Hindi, English & Hinglish Speech & NLP Extraction Engine
import os
import re
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# Reusable Speech & Language Recognition Service Provider
SUPPORTED_LANGUAGES = ["hindi", "english", "hinglish"]

# Common Hindi / Hinglish phonetic keywords for classification & natural normalization
HINGLISH_KEYWORDS = {
    "poor_lighting": ["light", "bijli", "andhera", "dark", "street light", "bulb", "unlit", "roshni", "tube"],
    "harassment": ["chhedkhani", "catcall", "comment", "gali", "chilana", "badtameezi", "shouting", "teasing", "gali galoch"],
    "following": ["peechha", "follow", "picha", "stalk", "piche", "car slow", "suspicious bike", "ghoor"],
    "unsafe_area": ["sunsaan", "unsafe", "khatra", "danger", "isolated", "khali sadak", "darr", "scary", "abandoned"],
    "broken_infrastructure": ["toota", "gadha", "broken", "pothole", "manhole", "footpath band", "blocked", "barrier"]
}


def detect_language(text: str) -> Dict[str, Any]:
    """
    Detects language among Hindi (Devanagari script), English (Latin), or Hinglish (Hindi phonetics in Latin).
    Never discards original language. If confidence is borderline, provides honest classification.
    """
    if not text or not text.strip():
        return {"language": "english", "confidence": 1.0, "script": "latin"}

    clean_text = text.strip()
    
    # Devanagari Unicode Range (\u0900 to \u097F)
    devanagari_chars = len(re.findall(r'[\u0900-\u097F]', clean_text))
    total_chars = len(re.findall(r'\w', clean_text)) or 1

    if devanagari_chars / total_chars > 0.35:
        return {
            "language": "hindi",
            "confidence": round(devanagari_chars / total_chars, 2),
            "script": "devanagari",
            "is_hinglish": False
        }

    # Latin text analysis: Check for common Romanized Hindi particles/keywords
    lower = clean_text.lower()
    hinglish_markers = ["hai", "nahi", "raha", "rahi", "mein", "pe", "bahut", "ke paas", "tha", "thi", "kuch", "idhar", "gaya"]
    matches = sum(1 for m in hinglish_markers if re.search(r'\b' + re.escape(m) + r'\b', lower))

    if matches >= 2:
        return {
            "language": "hinglish",
            "confidence": 0.88,
            "script": "latin",
            "is_hinglish": True
        }
    elif matches == 1:
        return {
            "language": "hinglish",
            "confidence": 0.65,
            "script": "latin",
            "is_hinglish": True
        }

    return {
        "language": "english",
        "confidence": 0.92,
        "script": "latin",
        "is_hinglish": False
    }


def extract_incident_draft(
    raw_text: str,
    city: str = "Dehradun",
    country: str = "India"
) -> Dict[str, Any]:
    """
    Transforms unstructured voice or text input into an editable incident draft.
    Does NOT invent exact locations, perpetrator details, or final severity levels.
    All outputs require explicit user confirmation.
    """
    lang_meta = detect_language(raw_text)
    lower = raw_text.lower()

    # Category suggestion
    detected_cat = "unsafe_area"
    highest_score = 0
    for cat, keywords in HINGLISH_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in lower)
        if score > highest_score:
            highest_score = score
            detected_cat = cat

    # Severity suggestion (1: Low/Minor, 2: Moderate/Distress, 3: High/Immediate Danger)
    # Marked as pending user confirmation
    suggested_severity = 2
    if any(w in lower for w in ["chhedkhani", "follow", "peechha", "aggressive", "threat", "weapon", "chaku", "snatch"]):
        suggested_severity = 3
    elif any(w in lower for w in ["light", "bulb", "pothole", "dark", "andhera"]):
        suggested_severity = 1 if "bahut" not in lower else 2

    # Normalization / Translation into English for unified moderation
    normalized_description = raw_text
    if lang_meta["language"] in ("hindi", "hinglish"):
        # Synthetic standard translation bridge
        if detected_cat == "poor_lighting":
            normalized_description = f"Reported non-functional street lighting / poor visibility condition: \"{raw_text}\""
        elif detected_cat == "harassment":
            normalized_description = f"Reported verbal harassment / aggressive confrontation: \"{raw_text}\""
        elif detected_cat == "following":
            normalized_description = f"Reported suspicious following / stalking behaviour: \"{raw_text}\""
        elif detected_cat == "broken_infrastructure":
            normalized_description = f"Reported broken infrastructure / obstructed pedestrian walkway: \"{raw_text}\""
        else:
            normalized_description = f"Reported safety concern in area: \"{raw_text}\""

    # Concise AI Summary
    summary_map = {
        "poor_lighting": "Street lighting outage / unlit pathway",
        "harassment": "Verbal harassment / aggressive conduct",
        "following": "Suspicious following / stalking incident",
        "broken_infrastructure": "Obstructed walkway / hazardous road condition",
        "unsafe_area": "Isolated / unsafe environmental condition"
    }
    short_summary = summary_map.get(detected_cat, "Safety concern report")

    # Landmark candidate extraction (simple heuristic, awaiting user confirm)
    loc_candidate = f"Near location described in {city}"
    for preposition in ["near", "paas", "close to", "opposite", "chowk", "gate", "stand", "metro"]:
        if preposition in lower:
            parts = lower.split(preposition)
            if len(parts) > 1:
                chunk = parts[1].strip().split(".")[0].split(",")[0][:30].strip()
                if chunk:
                    loc_candidate = f"Vicinity of {chunk.capitalize()}"
                    break

    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "original_text": raw_text.strip(),
        "original_language": lang_meta["language"],
        "script": lang_meta["script"],
        "is_hinglish": lang_meta.get("is_hinglish", False),
        "suggested_category": detected_cat,
        "suggested_severity": suggested_severity,
        "normalized_description": normalized_description,
        "ai_short_summary": short_summary,
        "suggested_location": loc_candidate,
        "time_reported": now_iso,
        "extraction_confidence": 0.85 if highest_score > 0 else 0.50,
        "user_confirmed": False
    }


def detect_duplicate_candidates(
    category: str,
    lat: float,
    lng: float,
    existing_reports: List[Dict[str, Any]],
    proximity_radius_m: float = 200.0,
    time_window_hours: float = 4.0
) -> List[Dict[str, Any]]:
    """
    Identifies potential duplicate reports nearby in space and time.
    Returns similarity reasons as an ADVISORY, not an unquestionable deletion trigger.
    """
    from route_segmenter import haversine_distance_m
    duplicates = []
    now = datetime.now()

    for r in existing_reports:
        # Distance calculation
        r_lat = r.get("lat") or r.get("latitude")
        r_lng = r.get("lng") or r.get("longitude")
        if r_lat is None or r_lng is None:
            continue

        dist_m = haversine_distance_m(lat, lng, r_lat, r_lng)
        if dist_m > proximity_radius_m:
            continue

        # Time difference
        ts_str = r.get("timestamp") or r.get("created_at")
        hours_diff = 12.0
        if ts_str:
            try:
                dt = datetime.strptime(ts_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
                hours_diff = abs((now - dt).total_seconds()) / 3600.0
            except Exception:
                pass

        if hours_diff <= time_window_hours:
            same_cat = (r.get("type") == category or r.get("category") == category)
            score = 0.5
            if same_cat:
                score += 0.35
            if dist_m < 80.0:
                score += 0.15

            duplicates.append({
                "existing_id": r.get("id"),
                "category": r.get("type") or r.get("category"),
                "distance_m": round(dist_m),
                "hours_ago": round(hours_diff, 1),
                "similarity_score": round(score, 2),
                "reason": f"Similar '{category}' incident reported {round(dist_m)}m away within the last {round(hours_diff, 1)}h."
            })

    duplicates.sort(key=lambda d: d["distance_m"])
    return duplicates
