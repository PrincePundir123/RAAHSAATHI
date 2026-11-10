import asyncio
import os
import edge_tts

# 8 High-Impact Scenes calibrated for ~4.5 minutes (270s) at a natural, energetic tech-pitch pace (+8%)
scenes_master = [
    {
        "id": "scene_01",
        "title": "Introduction & The Navigation Dilemma",
        "tag": "THE BLINDSPOT OF MODERN NAVIGATION",
        "visual_type": "graphic",
        "visual_file": "video-production/graphics/graphic_01_problem_matrix.png",
        "pill": "🚨 Speed-First Navigation vs Human Safety Optimization",
        "text": "Hello everyone! I am Prince Pundir, and welcome to the presentation of SafeWalk RaahSaathi, an autonomous, AI-grounded women's safety navigation platform. Every evening, millions of women commute home from universities, corporate offices, and transit hubs. When they open standard navigation apps, every major service optimizes for one single dimension: speed. Distance divided by time. They will gladly route a woman walking alone late at night through an unlit underpass or an isolated alley just to save ninety seconds. SafeWalk redefines navigation by prioritizing human safety, combining verified road geometry, assistance havens, and explainable spatial intelligence."
    },
    {
        "id": "scene_02",
        "title": "4-Pillar Scoring Architecture",
        "tag": "EXPLAINABLE INTELLIGENCE BLUEPRINT",
        "visual_type": "graphic",
        "visual_file": "video-production/graphics/graphic_02_architecture.png",
        "pill": "📐 4-Pillar Spatial Scoring & Diurnal Night Penalty",
        "text": "Before seeing the live app, look under the hood. Conventional safety apps rely on subjective user ratings. SafeWalk introduces a deterministic four-pillar route scoring engine. We compute verified streetlight illumination from OpenStreetMap surveys, natural commercial footfall from active late-night storefronts and chemists, a continuous diurnal temporal penalty for night journeys, and community-verified incident reports. Furthermore, our spatial segmenter slices walking routes into 100 to 200 meter atomic sections, providing full audit transparency rather than a single black-box score."
    },
    {
        "id": "scene_03",
        "title": "Live Dual-Route Navigation & Segment Deep-Dive",
        "tag": "REAL-TIME SEGMENT AUDIT",
        "visual_type": "ui",
        "visual_file": "video-production/images/02_dual_route_map.png",
        "pill": "🟢 Safest Route (Emerald) vs 🔴 Fastest Route (Coral)",
        "text": "Here is SafeWalk in action. When planning a walk in Dehradun at 10 PM, our dual-route engine renders two paths: the coral dashed line is the shortest path, but it traverses dangerous low-lit stretches. The emerald line is our Safest Route. Notice the Segment-Level Deep Dive card: each segment explains its score in plain language, such as eight commercial storefronts offsetting missing streetlights. Most importantly, we strictly separate safety score from data confidence. A road with zero reports is never falsely labeled safe: it is marked as low confidence until verified."
    },
    {
        "id": "scene_04",
        "title": "SafeStops Verified Assistance Havens",
        "tag": "EMERGENCY SAFE HAVENS",
        "visual_type": "ui",
        "visual_file": "video-production/images/03_safestops.png",
        "pill": "🚨 1-Tap Emergency Rerouting to Verified Assistance Desks",
        "text": "What happens if a woman feels uncomfortable, followed, or in distress during her commute? She does not have time to browse web directories. She opens SafeStops. SafeStops indexes vetted assistance havens: 24/7 police stations, campus security desks, emergency trauma centers, and verified pharmacies. We enforce strict data provenance: public datasets are marked Public Facility, while university security booths are labeled Partner-Verified. With one single tap on Navigate to Nearest Help Point, SafeWalk calculates the safest walking path directly to the closest safe haven with instant phone links."
    },
    {
        "id": "scene_05",
        "title": "Live Journey Guardian & Cryptographic Security",
        "tag": "SECURITY & PRIVACY BLUEPRINT",
        "visual_type": "graphic",
        "visual_file": "video-production/graphics/graphic_03_guardian_security.png",
        "pill": "🛡️ 32-Byte Cryptographic Tokens & Autonomous Server Escalation",
        "text": "For lone journeys, users activate Live Journey Guardian. Designed with privacy by default, the user gives explicit consent and chooses her check-in interval, for example every five minutes with a two-minute grace period. SafeWalk issues a high-entropy 32-byte cryptographic sharing token, storing hashes using SHA-256 and never exposing database IDs. Periodic prompts confirm user safety. If a check-in is missed, our server triggers simulated alerts with GPS coordinates to trusted contacts, who can tap I am responding to confirm help is underway."
    },
    {
        "id": "scene_06",
        "title": "Live Guardian Interface & Simulated Alerts",
        "tag": "AUTONOMOUS CHECK-IN ENGINE",
        "visual_type": "ui",
        "visual_file": "video-production/images/04_journey_guardian.png",
        "pill": "⏱️ Real-time 'Are You Okay?' Countdown & Contact Escalation",
        "text": "On the Live Guardian dashboard, you can see the active session in real-time. The user sees the remaining grace period, battery-efficient tracking, and emergency panic buttons. In our simulated contact viewer, trusted family members and campus security can monitor the journey securely without creating user accounts. The moment an alert is acknowledged, the user interface updates with an empathetic confirmation badge."
    },
    {
        "id": "scene_07",
        "title": "Multilingual AI Voice Reporting & Offline PWA Sync",
        "tag": "NATURAL LANGUAGE & RESILIENCE",
        "visual_type": "ui",
        "visual_file": "video-production/images/05_voice_reporting.png",
        "pill": "🎙️ Hinglish/Hindi Natural Voice & Idempotent Offline Cache",
        "text": "Filling out forms in the dark is frustrating and slow. SafeWalk supports Multilingual AI Voice Reporting. Users speak naturally in Hindi, English, or Hinglish: for example, Bus stand ke paas light nahi jal rahi hai aur raat mein bahut andhera rehta hai. Our NLP engine classifies the incident category, extracts a normalized draft, and requires user confirmation before saving. Even in basement parking or low-signal zones, our PWA offline queue stores reports locally with cryptographic idempotency keys, syncing seamlessly once online."
    },
    {
        "id": "scene_08",
        "title": "Safety Intelligence Dashboard & Conclusion",
        "tag": "INSTITUTIONAL OVERSIGHT & CLOSING",
        "visual_type": "ui",
        "visual_file": "video-production/images/06_safety_intelligence.png",
        "pill": "📊 1.1km Privacy-Preserving Risk Clusters • Prince Pundir",
        "text": "Finally, SafeWalk empowers campus administrations and municipal authorities through our Safety Intelligence Dashboard. All statistics are computed live from active database records. Authorities can monitor infrastructure gaps like recurring streetlight outages and examine privacy-preserving 1.1-kilometer spatial clusters without compromising individual travel histories. SafeWalk RaahSaathi bridges the gap between raw maps and genuine peace of mind. Every woman deserves the safest journey home. Once again, I am Prince Pundir, and thank you for watching!"
    }
]

async def generate_master_voiceovers():
    voice = "en-IN-PrabhatNeural"
    os.makedirs("video-production/voiceover", exist_ok=True)
    print(f"Generating 8 voiceover scenes using {voice} at energetic pitch (+8%)...")
    for s in scenes_master:
        path = f"video-production/voiceover/{s['id']}_master.mp3"
        print(f"Synthesizing {path}...")
        comm = edge_tts.Communicate(s['text'], voice, rate="+8%")
        await comm.save(path)
    print("ALL_MASTER_VOICEOVERS_DONE")

if __name__ == "__main__":
    asyncio.run(generate_master_voiceovers())
