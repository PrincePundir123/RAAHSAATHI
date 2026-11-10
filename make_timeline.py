import json

scenes = [
    {
        'id': 'scene_01',
        'title': 'Introduction & The Core Problem',
        'text': "Hello everyone! I am Prince Pundir, and today I am excited to present SafeWalk RaahSaathi, an autonomous, AI-grounded women's safety navigation platform. Every day, millions of women commute home from universities and workplaces. Mainstream navigation apps optimize purely for speed, often routing women through dark, unmonitored alleys just to save ninety seconds. SafeWalk redefines navigation by prioritizing human safety over transit time, combining real road geometry, verified assistance havens, and explainable spatial intelligence."
    },
    {
        'id': 'scene_02',
        'title': 'Dual-Route Planning & Segment Intelligence',
        'text': "Let us see it in action. Starting our journey in Dehradun at 10:00 PM, notice our dual routing: the red dashed line is the shortest path, cutting through high-risk stretches. The emerald line is our Safest Route. SafeWalk introduces Explainable Segment-Level Route Intelligence, dividing the walking path into 100 to 200 meter sections. For each segment, our engine reveals exact evidence: commercial footfall, street lighting, and diurnal time penalties. Most importantly, we distinguish safety from data confidence so unmonitored roads are never falsely marked safe."
    },
    {
        'id': 'scene_03',
        'title': 'SafeStops Nearby Assistance',
        'text': "When a user feels uncomfortable or followed, she opens SafeStops. SafeStops indexes vetted assistance havens: 24/7 police stations, campus security desks, emergency hospitals, and verified late-night pharmacies. We enforce strict data provenance, distinguishing open public facilities from partner-verified institutional desks. With one tap on Navigate to Nearest Help Point, SafeWalk calculates the safest walking path directly to the closest safe haven with instant contact options."
    },
    {
        'id': 'scene_04',
        'title': 'Live Journey Guardian',
        'text': "For lone journeys, users activate Live Journey Guardian: a privacy-first tracking and automated check-in engine. Users set a check-in interval with a grace period. SafeWalk issues a high-entropy 32-byte cryptographic sharing token, never exposing database IDs. During the trip, periodic check-ins confirm user safety. If a check-in is missed or emergency assistance is triggered, our server immediately dispatches simulated alerts to trusted contacts, who can acknowledge that help is on the way."
    },
    {
        'id': 'scene_05',
        'title': 'Multilingual AI Voice Reporting & Offline PWA',
        'text': "SafeWalk also features Multilingual AI Voice Reporting. Users can speak naturally in Hindi, English, or Hinglish. Our NLP engine detects Romanized Hinglish, preserves spoken transcripts, and drafts structured reports for user confirmation. And in low-connectivity areas, SafeWalk works offline as a PWA, queueing incident reports locally with cryptographic idempotency keys that sync automatically once back online."
    },
    {
        'id': 'scene_06',
        'title': 'Safety Intelligence & Campus Dashboard',
        'text': "For campus administrations and municipal authorities, SafeWalk provides an interactive Safety Intelligence Dashboard. All metrics are computed directly from live database records. Authorities can monitor infrastructure gaps like streetlight outages and examine privacy-preserving geospatial risk clusters to plan preventive safety audits without compromising individual travel histories."
    },
    {
        'id': 'scene_07',
        'title': 'Technical Architecture & Conclusion',
        'text': "Under the hood, SafeWalk is built on Python, Streamlit, Folium, and SQLite, powered by OSRM pedestrian routing, OpenStreetMap Overpass spatial queries, and Google Gemini AI grounded in safety standards. With over 35 structured commits and comprehensive tests, SafeWalk RaahSaathi ensures women don't just reach their destination faster, but safer. Once again, I am Prince Pundir, and thank you for watching!"
    }
]

def format_timestamp(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milli = int(round((seconds - int(seconds)) * 1000))
    if milli >= 1000:
        secs += 1
        milli = 0
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{milli:03d}"

def run():
    with open("video-production/voiceover/voiceover_metadata.json", "r") as f:
        meta = json.load(f)
    durations = meta["durations"]

    current_time = 0.0
    timeline = []
    srt_entries = []
    timing_lines = []
    srt_index = 1

    for s in scenes:
        sid = s["id"]
        title = s["title"]
        text = s["text"]
        dur = durations[sid]
        start = current_time
        end = current_time + dur
        
        timeline.append({
            "scene_id": sid,
            "title": title,
            "start_time": start,
            "end_time": end,
            "duration": dur,
            "text": text
        })
        timing_lines.append(f"[{format_timestamp(start)} --> {format_timestamp(end)}] {sid.upper()} ({title})")
        timing_lines.append(f"Text: {text}\n")
        
        sentences = [sent.strip() for sent in text.replace("!", ".").replace("?", ".").split(".") if sent.strip()]
        sent_dur = dur / len(sentences)
        for i, sent in enumerate(sentences):
            sub_start = start + i * sent_dur
            sub_end = start + (i + 1) * sent_dur
            srt_entries.append(f"{srt_index}\n{format_timestamp(sub_start)} --> {format_timestamp(sub_end)}\n{sent}\n")
            srt_index += 1
        current_time = end

    with open("scene_timeline.json", "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2)
    with open("video-production/scene_timeline.json", "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2)
    with open("final_demo_subtitles.srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))
    with open("video-production/final_demo_subtitles.srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))
    with open("video-production/voiceover/voiceover_timing.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(timing_lines))

    print("Subtitles, timeline, and timing files written successfully!")

if __name__ == "__main__":
    run()

