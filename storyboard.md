# SafeWalk (RaahSaathi) — Video Demo Storyboard & Visual Director's Guide

**Presenter:** Prince Pundir  
**Target Video Format:** 1080p 16:9 (1920x1080), 30 FPS  
**Total Runtime:** ~4 Minutes (242 Seconds)  
**Audio Voiceover Engine:** Neural TTS (Indian English Tech Presenter - `en-IN-PrabhatNeural`)  
**Subtitles:** Embedded / Synchronized `final_demo_subtitles.srt`

---

## 🎬 Scene Breakdown & Visual Layout

### Scene 1: Introduction & The Core Problem
- **Time:** `00:00 - 00:39` (39.43s)
- **Audio Clip:** `video-production/voiceover/scene_01.mp3`
- **Primary Visual:** Title Sequence & SafeWalk Homepage Overview (`01_home_screen.png`).
- **Overlay Elements:**
  - Badge: `🛡️ SafeWalk (RaahSaathi) | National Hackathon 2026`
  - Problem Callout Card: `"Conventional Routing: Speed-Only Optimization (Distance / Time)"`
  - Highlighting: Unmonitored routes vs Safe human-centric navigation.
- **Narration:**
  > *"Hello everyone! I am Prince Pundir, and today I am excited to present SafeWalk RaahSaathi, an autonomous, AI-grounded women's safety navigation platform. Every day, millions of women commute home from universities and workplaces. Mainstream navigation apps optimize purely for speed, often routing women through dark, unmonitored alleys just to save ninety seconds. SafeWalk redefines navigation by prioritizing human safety over transit time, combining real road geometry, verified assistance havens, and explainable spatial intelligence."*

---

### Scene 2: Dual-Route Planning & Segment Intelligence
- **Time:** `00:39 - 01:21` (42.17s)
- **Audio Clip:** `video-production/voiceover/scene_02.mp3`
- **Primary Visual:** Dual-route interactive map (`02_dual_route_map.png`).
- **Overlay Elements:**
  - Route Comparison: Emerald Green (`Safest Route`) vs Coral Red Dashed (`Fastest Route`).
  - Feature Callout: `"Explainable Segment-Level Intelligence (100m - 200m Road Sections)"`.
  - 4-Pillar Confidence Breakdown: Commercial footfall, streetlight coverage, diurnal penalty.
- **Narration:**
  > *"Let us see it in action. Starting our journey in Dehradun at 10:00 PM, notice our dual routing: the red dashed line is the shortest path, cutting through high-risk stretches. The emerald line is our Safest Route. SafeWalk introduces Explainable Segment-Level Route Intelligence, dividing the walking path into 100 to 200 meter sections. For each segment, our engine reveals exact evidence: commercial footfall, street lighting, and diurnal time penalties. Most importantly, we distinguish safety from data confidence so unmonitored roads are never falsely marked safe."*

---

### Scene 3: SafeStops — Verified Nearby Assistance
- **Time:** `01:21 - 01:57` (36.14s)
- **Audio Clip:** `video-production/voiceover/scene_03.mp3`
- **Primary Visual:** SafeStops Assistance Directory & Map (`03_safestops.png`).
- **Overlay Elements:**
  - Provenance Badges: `[PARTNER-VERIFIED]` vs `[PUBLIC FACILITY]`.
  - Action Focus: `"🚨 Navigate to Nearest Help Point"` with instant dynamic rerouting.
- **Narration:**
  > *"When a user feels uncomfortable or followed, she opens SafeStops. SafeStops indexes vetted assistance havens: 24/7 police stations, campus security desks, emergency hospitals, and verified late-night pharmacies. We enforce strict data provenance, distinguishing open public facilities from partner-verified institutional desks. With one tap on Navigate to Nearest Help Point, SafeWalk calculates the safest walking path directly to the closest safe haven with instant contact options."*

---

### Scene 4: Live Journey Guardian
- **Time:** `01:57 - 02:33` (35.76s)
- **Audio Clip:** `video-production/voiceover/scene_04.mp3`
- **Primary Visual:** Live Journey Guardian Tab & Contact Viewer (`04_journey_guardian.png`).
- **Overlay Elements:**
  - Security Highlight: `32-Byte Cryptographic High-Entropy Sharing Token`.
  - Automated Check-in: `Are you okay?` countdown timer.
  - Emergency Escalation: Server-side dispatch to trusted contacts with acknowledgment status (`"I am responding"`).
- **Narration:**
  > *"For lone journeys, users activate Live Journey Guardian: a privacy-first tracking and automated check-in engine. Users set a check-in interval with a grace period. SafeWalk issues a high-entropy 32-byte cryptographic sharing token, never exposing database IDs. During the trip, periodic check-ins confirm user safety. If a check-in is missed or emergency assistance is triggered, our server immediately dispatches simulated alerts to trusted contacts, who can acknowledge that help is on the way."*

---

### Scene 5: Multilingual AI Voice Reporting & Offline PWA Sync
- **Time:** `02:33 - 03:04` (31.25s)
- **Audio Clip:** `video-production/voiceover/scene_05.mp3`
- **Primary Visual:** Multilingual Voice & AI Reporting Tab (`05_voice_reporting.png`).
- **Overlay Elements:**
  - Spoken Transcript Demo: `"Bus stand ke paas light nahi jal rahi hai..."`
  - Natural Language Processing: Hindi/Hinglish detection & structured category mapping.
  - Offline Resilience: PWA local queue & idempotent sync.
- **Narration:**
  > *"SafeWalk also features Multilingual AI Voice Reporting. Users can speak naturally in Hindi, English, or Hinglish. Our NLP engine detects Romanized Hinglish, preserves spoken transcripts, and drafts structured reports for user confirmation. And in low-connectivity areas, SafeWalk works offline as a PWA, queueing incident reports locally with cryptographic idempotency keys that sync automatically once back online."*

---

### Scene 6: Safety Intelligence & Campus Authority Dashboard
- **Time:** `03:04 - 03:31` (26.74s)
- **Audio Clip:** `video-production/voiceover/scene_06.mp3`
- **Primary Visual:** Institutional Safety Intelligence Dashboard (`06_safety_intelligence.png`).
- **Overlay Elements:**
  - Live Database KPIs: Total incident reports, infrastructure gaps, corroboration rate.
  - Privacy-preserving clustering: 1.1-kilometer spatial cells.
- **Narration:**
  > *"For campus administrations and municipal authorities, SafeWalk provides an interactive Safety Intelligence Dashboard. All metrics are computed directly from live database records. Authorities can monitor infrastructure gaps like streetlight outages and examine privacy-preserving geospatial risk clusters to plan preventive safety audits without compromising individual travel histories."*

---

### Scene 7: Technical Architecture, Security & Conclusion
- **Time:** `03:31 - 04:02` (30.53s)
- **Audio Clip:** `video-production/voiceover/scene_07.mp3`
- **Primary Visual:** Technical Architecture & Project Summary (`01_home_screen.png` + End Credits).
- **Overlay Elements:**
  - Tech Stack Badges: `Python` `Streamlit` `Folium` `SQLite` `OSRM` `OpenStreetMap Overpass` `Gemini AI`.
  - Closing Statement: `"SafeWalk (RaahSaathi) — Presented by Prince Pundir"`.
- **Narration:**
  > *"Under the hood, SafeWalk is built on Python, Streamlit, Folium, and SQLite, powered by OSRM pedestrian routing, OpenStreetMap Overpass spatial queries, and Google Gemini AI grounded in safety standards. With over 35 structured commits and comprehensive tests, SafeWalk RaahSaathi ensures women don't just reach their destination faster, but safer. Once again, I am Prince Pundir, and thank you for watching!"*

