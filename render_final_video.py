import os
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
print(f"Using FFmpeg binary: {ffmpeg_exe}")

os.makedirs("video-production/renders", exist_ok=True)
os.makedirs("video-production/footage", exist_ok=True)

# 1. Prepare high-impact slides with real UI captures & crisp overlays
W, H = 1920, 1080

scene_configs = [
    {
        "id": "scene_01",
        "title": "SafeWalk (RaahSaathi) — Redefining Women's Navigation",
        "subtitle": "Presented by Prince Pundir | National Hackathon 2026",
        "tag": "PROBLEM STATEMENT & VALUE PROPOSITION",
        "bg_img": "video-production/images/01_home_screen.png",
        "pill": "🚨 Speed-Only Routing vs Human Safety",
        "audio": "video-production/voiceover/scene_01.mp3"
    },
    {
        "id": "scene_02",
        "title": "Dual-Route Navigation & Explainable Segment Intelligence",
        "subtitle": "100m-200m Road Sections • 4-Pillar Confidence Engine",
        "tag": "CORE ROUTE INTELLIGENCE",
        "bg_img": "video-production/images/02_dual_route_map.png",
        "pill": "🟢 Safest Route (Emerald) vs 🔴 Fastest Route (Coral)",
        "audio": "video-production/voiceover/scene_02.mp3"
    },
    {
        "id": "scene_03",
        "title": "SafeStops — Verified Nearby Assistance Directory",
        "subtitle": "Police, Hospitals, Campus Booths & 24/7 Pharmacies",
        "tag": "EMERGENCY SAFE HAVENS",
        "bg_img": "video-production/images/03_safestops.png",
        "pill": "🚨 Instant 1-Tap Navigation to Nearest Help Point",
        "audio": "video-production/voiceover/scene_03.mp3"
    },
    {
        "id": "scene_04",
        "title": "Live Journey Guardian & Cryptographic Check-ins",
        "subtitle": "32-Byte Security Tokens • Automated Emergency Escalation",
        "tag": "REAL-TIME PROTECTION",
        "bg_img": "video-production/images/04_journey_guardian.png",
        "pill": "🛡️ 'Are You Okay?' Check-in & Trusted Contact SMS Alerts",
        "audio": "video-production/voiceover/scene_04.mp3"
    },
    {
        "id": "scene_05",
        "title": "Multilingual AI Voice Reporting & Offline PWA Sync",
        "subtitle": "Hinglish/Hindi/English NLP • Idempotent Offline Cache",
        "tag": "ACCESSIBLE REPORTING",
        "bg_img": "video-production/images/05_voice_reporting.png",
        "pill": "🎙️ 'Bus stand ke paas light nahi jal rahi hai' -> Auto Draft",
        "audio": "video-production/voiceover/scene_05.mp3"
    },
    {
        "id": "scene_06",
        "title": "Safety Intelligence Dashboard for Authorities",
        "subtitle": "Real Database Statistics • 1.1km Privacy-Preserving Risk Clusters",
        "tag": "INSTITUTIONAL OVERSIGHT",
        "bg_img": "video-production/images/06_safety_intelligence.png",
        "pill": "📊 Infrastructure Audits & Streetlight Outage Heatmaps",
        "audio": "video-production/voiceover/scene_06.mp3"
    },
    {
        "id": "scene_07",
        "title": "Technical Architecture & Hackathon Submission",
        "subtitle": "Python • Streamlit • Folium • OSRM • Gemini AI • SQLite",
        "tag": "PRODUCTION READY",
        "bg_img": "video-production/images/01_home_screen.png",
        "pill": "✨ 35+ Commits • 100% Passing Tests • Prince Pundir",
        "audio": "video-production/voiceover/scene_07.mp3"
    }
]

def render_scene_frames():
    with open("video-production/voiceover/voiceover_metadata.json", "r") as f:
        meta = json.load(f)
    durations = meta["durations"]

    scene_video_parts = []

    for idx, sc in enumerate(scene_configs):
        sid = sc["id"]
        dur = durations[sid]
        print(f"Compositing {sid} (Duration: {dur:.2f}s)...")

        # Create base composited image
        canvas = Image.new("RGBA", (W, H), (15, 23, 42, 255))
        
        # Load screenshot if available
        if os.path.exists(sc["bg_img"]):
            base_ui = Image.open(sc["bg_img"]).convert("RGBA")
            # Fit to canvas with margin
            ui_scaled = base_ui.resize((1840, 900))
            canvas.paste(ui_scaled, (40, 140))
        
        # Render clean header banner
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([0, 0, W, 130], fill=(15, 23, 42, 245))
        draw.rectangle([0, 126, W, 130], fill=(16, 185, 129, 255)) # Green bar
        
        # Category Tag badge
        draw.rounded_rectangle([40, 25, 340, 65], radius=8, fill=(30, 41, 59, 255), outline=(52, 211, 153, 255), width=2)
        draw.text((55, 36), sc["tag"], fill=(52, 211, 153, 255))
        
        # Title text
        draw.text((360, 25), sc["title"], fill=(255, 255, 255, 255))
        draw.text((360, 75), sc["subtitle"], fill=(148, 163, 184, 255))

        # Bottom Feature Pill
        draw.rectangle([0, H - 75, W, H], fill=(15, 23, 42, 240))
        draw.text((60, H - 52), sc["pill"], fill=(241, 245, 249, 255))
        draw.text((W - 380, H - 52), f"Scene {idx+1}/7 | SafeWalk (RaahSaathi)", fill=(148, 163, 184, 255))

        frame_path = f"video-production/footage/{sid}_frame.png"
        canvas.convert("RGB").save(frame_path, "PNG")

        # Generate a video segment with ffmpeg looping this frame for the exact duration of the audio
        out_part = f"video-production/renders/{sid}_part.mp4"
        audio_path = sc["audio"]

        cmd = [
            ffmpeg_exe,
            "-y",
            "-loop", "1",
            "-i", frame_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-r", "30",
            out_part
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            print(f"Error encoding {sid}:", res.stderr.decode()[:200])
        else:
            print(f"Rendered {out_part}")
            scene_video_parts.append(out_part)

    # Concat all 7 parts into final_demo_video.mp4
    print("Concatenating all scene segments into final_demo_video.mp4 ...")
    concat_list_file = "video-production/renders/concat_list.txt"
    with open(concat_list_file, "w") as f:
        for p in scene_video_parts:
            # Absolute path with forward slashes
            abs_p = os.path.abspath(p).replace("\\", "/")
            f.write(f"file '{abs_p}'\n")

    final_video_out = "final_demo_video.mp4"
    concat_cmd = [
        ffmpeg_exe,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_file,
        "-c", "copy",
        final_video_out
    ]
    res = subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 0:
        print(f"SUCCESS: {final_video_out} generated successfully!")
    else:
        print("Concat error:", res.stderr.decode()[:400])

if __name__ == "__main__":
    render_scene_frames()

