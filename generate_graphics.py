import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
os.makedirs("video-production/graphics", exist_ok=True)

def draw_header(draw, title, category):
    draw.rectangle([0, 0, W, 130], fill=(15, 23, 42, 250))
    draw.rectangle([0, 126, W, 130], fill=(16, 185, 129, 255))
    draw.rounded_rectangle([60, 30, 380, 75], radius=10, fill=(30, 41, 59, 255), outline=(52, 211, 153, 255), width=2)
    draw.text((80, 43), category, fill=(52, 211, 153, 255))
    draw.text((410, 35), title, fill=(255, 255, 255, 255))
    draw.text((410, 80), "SafeWalk (RaahSaathi) | Presented by Prince Pundir", fill=(148, 163, 184, 255))

def create_graphic_01():
    # PROBLEM COMPARISON MATRIX: Mainstream Navigation vs SafeWalk
    img = Image.new("RGBA", (W, H), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)
    draw_header(draw, "The Navigation Blindspot: Speed vs Safety", "PROBLEM ANALYSIS")

    # Column 1: Conventional Apps (Google Maps, Apple Maps)
    draw.rounded_rectangle([100, 180, 910, 960], radius=24, fill=(30, 41, 59, 240), outline=(239, 68, 68, 255), width=2)
    draw.rounded_rectangle([130, 210, 460, 260], radius=12, fill=(239, 68, 68, 40), outline=(239, 68, 68, 180), width=1)
    draw.text((150, 226), "❌ CONVENTIONAL NAVIGATION", fill=(248, 113, 113, 255))
    
    p1 = [
        ("Single Optimization Metric", "Optimizes purely for speed: Distance ÷ Time."),
        ("Dangerous Shortcuts", "Directs users through dark alleys & empty flyovers to save 60s."),
        ("Zero Lighting Awareness", "No knowledge of streetlights, broken bulbs, or darkness."),
        ("No Help Integration", "No directory of open, verified physical safe havens."),
        ("Black-box Routing", "Users have zero idea why a certain path was chosen.")
    ]
    for i, (hd, sub) in enumerate(p1):
        y = 300 + i * 125
        draw.rounded_rectangle([140, y, 870, y + 100], radius=16, fill=(15, 23, 42, 200), outline=(51, 65, 85, 200), width=1)
        draw.text((170, y + 18), f"⚠️ {hd}", fill=(255, 255, 255, 255))
        draw.text((170, y + 55), sub, fill=(148, 163, 184, 255))

    # Column 2: SafeWalk (RaahSaathi)
    draw.rounded_rectangle([1010, 180, 1820, 960], radius=24, fill=(16, 185, 129, 20), outline=(16, 185, 129, 255), width=2)
    draw.rounded_rectangle([1040, 210, 1420, 260], radius=12, fill=(16, 185, 129, 50), outline=(52, 211, 153, 200), width=1)
    draw.text((1060, 226), "🛡️ SAFEST WALK (RAAHSAATHI)", fill=(52, 211, 153, 255))

    p2 = [
        ("Human Safety Optimization", "Prioritizes survival, lighting & crowd presence over raw seconds."),
        ("Explainable Route Segments", "Breaks walks into 100-200m atomic sections with evidence."),
        ("Real Diurnal Lighting & POIs", "Dynamic day/night models penalizing unlit night journeys."),
        ("SafeStops Verified Havens", "1-Tap emergency reroute to vetted police, hospitals & campus booths."),
        ("Live Autonomous Guardian", "Cryptographic tracking, automated check-in & SMS dispatch.")
    ]
    for i, (hd, sub) in enumerate(p2):
        y = 300 + i * 125
        draw.rounded_rectangle([1050, y, 1780, y + 100], radius=16, fill=(15, 23, 42, 230), outline=(16, 185, 129, 120), width=1)
        draw.text((1080, y + 18), f"✅ {hd}", fill=(52, 211, 153, 255))
        draw.text((1080, y + 55), sub, fill=(226, 232, 240, 255))

    img.convert("RGB").save("video-production/graphics/graphic_01_problem_matrix.png")
    print("Saved graphic_01_problem_matrix.png")

def create_graphic_02():
    # ARCHITECTURE & 4-PILLAR SCORING PIPELINE
    img = Image.new("RGBA", (W, H), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Under the Hood: Explainable Route Scoring Architecture", "SYSTEM ARCHITECTURE")

    # 4 Pillars
    pillars = [
        ("💡 Streetlight Illumination", "Overpass OSM Surveys & Tag Parsing", "Weight: 25%", (56, 189, 248)),
        ("🏪 Commercial Natural Footfall", "Active POIs, Chemists & Storefronts", "Weight: 30%", (52, 211, 153)),
        ("🌙 Diurnal & Temporal Penalty", "Late-night dynamic decay curve", "Weight: 25%", (251, 191, 36)),
        ("🛡️ Verified Incident Reports", "Community voting & official sources", "Weight: 20%", (248, 113, 113))
    ]

    for i, (name, desc, wt, col) in enumerate(pillars):
        x = 80 + i * 445
        draw.rounded_rectangle([x, 220, x + 415, 520], radius=20, fill=(30, 41, 59, 230), outline=col, width=2)
        draw.rounded_rectangle([x + 20, 245, x + 160, 285], radius=8, fill=(15, 23, 42, 255), outline=col, width=1)
        draw.text((x + 35, 255), f"Pillar {i+1}", fill=col)
        draw.text((x + 20, 310), name, fill=(255, 255, 255, 255))
        draw.text((x + 20, 365), desc, fill=(148, 163, 184, 255))
        draw.rounded_rectangle([x + 20, 430, x + 200, 480], radius=10, fill=(15, 23, 42, 200))
        draw.text((x + 40, 445), wt, fill=col)

    # Core Logic Flow
    draw.rounded_rectangle([80, 580, 1840, 960], radius=20, fill=(15, 23, 42, 220), outline=(52, 211, 153, 200), width=2)
    draw.text((120, 615), "THE TWO-DIMENSION COMPUTATION: SAFETY SCORE vs CONFIDENCE AUDIT", fill=(52, 211, 153, 255))

    boxes = [
        ("1. OSRM Road Geometry", "Continuous walking polyline", 120),
        ("2. Spatial Segmenter", "100-200m atomic road sections", 540),
        ("3. Confidence Engine", "Separates missing data from safety", 960),
        ("4. Explainable Audit", "Transparent audit trail for user", 1380)
    ]
    for title, sub, bx in boxes:
        draw.rounded_rectangle([bx, 680, bx + 360, 890], radius=16, fill=(30, 41, 59, 255), outline=(71, 85, 105, 255), width=2)
        draw.text((bx + 25, 720), title, fill=(255, 255, 255, 255))
        draw.text((bx + 25, 770), sub, fill=(148, 163, 184, 255))

    img.convert("RGB").save("video-production/graphics/graphic_02_architecture.png")
    print("Saved graphic_02_architecture.png")

def create_graphic_03():
    # SECURITY & GUARDIAN BLUEPRINT: Cryptography & Automated Escalation
    img = Image.new("RGBA", (W, H), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Live Journey Guardian: Cryptographic Tracking & Escalation", "SECURITY & PRIVACY")

    steps = [
        ("1. Explicit User Consent", "User opts in and configures check-in interval (e.g. 5m) and grace period (2m).", (52, 211, 153)),
        ("2. Cryptographic Token Issuance", "32-byte high-entropy token generated. Database IDs never exposed. SHA-256 hashed.", (56, 189, 248)),
        ("3. Automated Ping Cycle", "Periodic 'Are you okay?' notification. 1-tap reset countdown timer.", (251, 191, 36)),
        ("4. Autonomous Escalation", "Missed check-in or panic trigger dispatches simulated SMS alerts with last valid GPS.", (248, 113, 113)),
        ("5. Guardian Acknowledgment", "Trusted contact taps 'I am responding' — user sees live response confirmation.", (168, 85, 247))
    ]

    for i, (title, desc, col) in enumerate(steps):
        y = 190 + i * 150
        draw.rounded_rectangle([120, y, 1800, y + 120], radius=18, fill=(30, 41, 59, 240), outline=col, width=2)
        draw.ellipse([150, y + 30, 210, y + 90], fill=col)
        draw.text((172, y + 43), str(i+1), fill=(15, 23, 42, 255))
        draw.text((240, y + 25), title, fill=(255, 255, 255, 255))
        draw.text((240, y + 65), desc, fill=(203, 213, 225, 255))

    img.convert("RGB").save("video-production/graphics/graphic_03_guardian_security.png")
    print("Saved graphic_03_guardian_security.png")

if __name__ == "__main__":
    create_graphic_01()
    create_graphic_02()
    create_graphic_03()
