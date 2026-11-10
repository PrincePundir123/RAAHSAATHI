import asyncio
import os
import edge_tts

# Concise, punchy script calibrated for ~4 to 4.5 minutes total (approx 35-45s per scene)
scenes_concise = [
    {
        "id": "scene_01",
        "title": "Introduction & The Core Problem",
        "text": "Hello everyone! I am Prince Pundir, and today I am excited to present SafeWalk RaahSaathi, an autonomous, AI-grounded women's safety navigation platform. Every day, millions of women commute home from universities and workplaces. Mainstream navigation apps optimize purely for speed, often routing women through dark, unmonitored alleys just to save ninety seconds. SafeWalk redefines navigation by prioritizing human safety over transit time, combining real road geometry, verified assistance havens, and explainable spatial intelligence."
    },
    {
        "id": "scene_02",
        "title": "Dual-Route Planning & Segment Intelligence",
        "text": "Let us see it in action. Starting our journey in Dehradun at 10:00 PM, notice our dual routing: the red dashed line is the shortest path, cutting through high-risk stretches. The emerald line is our Safest Route. SafeWalk introduces Explainable Segment-Level Route Intelligence, dividing the walking path into 100 to 200 meter sections. For each segment, our engine reveals exact evidence: commercial footfall, street lighting, and diurnal time penalties. Most importantly, we distinguish safety from data confidence so unmonitored roads are never falsely marked safe."
    },
    {
        "id": "scene_03",
        "title": "SafeStops Nearby Assistance",
        "text": "When a user feels uncomfortable or followed, she opens SafeStops. SafeStops indexes vetted assistance havens: 24/7 police stations, campus security desks, emergency hospitals, and verified late-night pharmacies. We enforce strict data provenance, distinguishing open public facilities from partner-verified institutional desks. With one tap on Navigate to Nearest Help Point, SafeWalk calculates the safest walking path directly to the closest safe haven with instant contact options."
    },
    {
        "id": "scene_04",
        "title": "Live Journey Guardian",
        "text": "For lone journeys, users activate Live Journey Guardian: a privacy-first tracking and automated check-in engine. Users set a check-in interval with a grace period. SafeWalk issues a high-entropy 32-byte cryptographic sharing token, never exposing database IDs. During the trip, periodic check-ins confirm user safety. If a check-in is missed or emergency assistance is triggered, our server immediately dispatches simulated alerts to trusted contacts, who can acknowledge that help is on the way."
    },
    {
        "id": "scene_05",
        "title": "Multilingual AI Voice Reporting & Offline PWA",
        "text": "SafeWalk also features Multilingual AI Voice Reporting. Users can speak naturally in Hindi, English, or Hinglish. Our NLP engine detects Romanized Hinglish, preserves spoken transcripts, and drafts structured reports for user confirmation. And in low-connectivity areas, SafeWalk works offline as a PWA, queueing incident reports locally with cryptographic idempotency keys that sync automatically once back online."
    },
    {
        "id": "scene_06",
        "title": "Safety Intelligence & Campus Dashboard",
        "text": "For campus administrations and municipal authorities, SafeWalk provides an interactive Safety Intelligence Dashboard. All metrics are computed directly from live database records. Authorities can monitor infrastructure gaps like streetlight outages and examine privacy-preserving geospatial risk clusters to plan preventive safety audits without compromising individual travel histories."
    },
    {
        "id": "scene_07",
        "title": "Technical Architecture & Conclusion",
        "text": "Under the hood, SafeWalk is built on Python, Streamlit, Folium, and SQLite, powered by OSRM pedestrian routing, OpenStreetMap Overpass spatial queries, and Google Gemini AI grounded in safety standards. With over 35 structured commits and comprehensive tests, SafeWalk RaahSaathi ensures women don't just reach their destination faster, but safer. Once again, I am Prince Pundir, and thank you for watching!"
    }
]

async def generate():
    voice = "en-IN-PrabhatNeural"
    os.makedirs("video-production/voiceover", exist_ok=True)
    for s in scenes_concise:
        path = f"video-production/voiceover/{s['id']}.mp3"
        print(f"Generating {path}...")
        comm = edge_tts.Communicate(s['text'], voice, rate="+7%")
        await comm.save(path)
    print("CONCISE_VOICEOVERS_DONE")

if __name__ == "__main__":
    asyncio.run(generate())

