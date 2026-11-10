import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
os.makedirs("docs/screenshots", exist_ok=True)
os.makedirs("video-production/graphics", exist_ok=True)

# Crisp large fonts
font_title = ImageFont.truetype("segoeui.ttf", 36)
font_subtitle = ImageFont.truetype("segoeui.ttf", 22)
font_category = ImageFont.truetype("segoeui.ttf", 20)
font_col_header = ImageFont.truetype("segoeui.ttf", 28)
font_card_title = ImageFont.truetype("segoeui.ttf", 24)
font_card_body = ImageFont.truetype("segoeui.ttf", 19)

def draw_header(draw, title, category):
    draw.rectangle([0, 0, W, 140], fill=(15, 23, 42, 255))
    draw.rectangle([0, 136, W, 140], fill=(16, 185, 129, 255))
    # Category Pill
    draw.rounded_rectangle([60, 35, 340, 85], radius=10, fill=(30, 41, 59, 255), outline=(52, 211, 153, 255), width=2)
    draw.text((95, 47), category, font=font_category, fill=(52, 211, 153, 255))
    # Title & Subtitle
    draw.text((370, 35), title, font=font_title, fill=(255, 255, 255, 255))
    draw.text((370, 85), "SafeWalk (RaahSaathi) | Presented by Prince Pundir", font=font_subtitle, fill=(148, 163, 184, 255))

def generate_crisp_graphic_01():
    img = Image.new("RGBA", (W, H), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)
    draw_header(draw, "The Navigation Blindspot: Speed vs Human Safety", "PROBLEM ANALYSIS")

    # Column 1: Conventional Navigation
    draw.rounded_rectangle([80, 180, 930, 1020], radius=24, fill=(30, 41, 59, 240), outline=(239, 68, 68, 255), width=3)
    draw.rounded_rectangle([120, 215, 520, 275], radius=12, fill=(239, 68, 68, 50), outline=(239, 68, 68, 200), width=2)
    draw.text((140, 230), "CONVENTIONAL APPS", font=font_col_header, fill=(248, 113, 113, 255))
    
    p1 = [
        ("Single Optimization Metric", "Optimizes purely for speed: Distance divided by Time."),
        ("Dangerous Dark Shortcuts", "Directs users through dark alleys & empty flyovers to save 60s."),
        ("Zero Streetlight Awareness", "Completely blind to streetlights, broken fixtures, and pitch darkness."),
        ("No Physical Safe Havens", "No directory of open, verified 24/7 assistance points or emergency desks."),
        ("Black-box Scoring", "Users have zero transparency into why an unsafe route was suggested.")
    ]
    for i, (hd, sub) in enumerate(p1):
        y = 310 + i * 135
        draw.rounded_rectangle([120, y, 890, y + 115], radius=16, fill=(15, 23, 42, 230), outline=(71, 85, 105, 200), width=1)
        draw.text((150, y + 20), f"[X]  {hd}", font=font_card_title, fill=(255, 255, 255, 255))
        draw.text((150, y + 65), sub, font=font_card_body, fill=(148, 163, 184, 255))

    # Column 2: SafeWalk (RaahSaathi)
    draw.rounded_rectangle([990, 180, 1840, 1020], radius=24, fill=(16, 185, 129, 25), outline=(16, 185, 129, 255), width=3)
    draw.rounded_rectangle([1030, 215, 1490, 275], radius=12, fill=(16, 185, 129, 60), outline=(52, 211, 153, 220), width=2)
    draw.text((1050, 230), "SAFEWALK (RAAHSAATHI)", font=font_col_header, fill=(52, 211, 153, 255))

    p2 = [
        ("Human Safety Optimization", "Prioritizes survival, lighting, crowd presence & active emergency desks."),
        ("Explainable Route Segments", "Slices paths into 100-200m atomic sections with evidence."),
        ("Real Diurnal Lighting & POIs", "Dynamic day/night model strictly penalizing late-night unlit journeys."),
        ("SafeStops Verified Havens", "1-Tap emergency reroute to vetted police, trauma centers & security booths."),
        ("Autonomous Journey Guardian", "Cryptographic tracking, automated check-in pings & SMS escalation.")
    ]
    for i, (hd, sub) in enumerate(p2):
        y = 310 + i * 135
        draw.rounded_rectangle([1030, y, 1800, y + 115], radius=16, fill=(15, 23, 42, 240), outline=(16, 185, 129, 160), width=1)
        draw.text((1060, y + 20), f"[OK]  {hd}", font=font_card_title, fill=(52, 211, 153, 255))
        draw.text((1060, y + 65), sub, font=font_card_body, fill=(226, 232, 240, 255))

    img.convert("RGB").save("docs/screenshots/graphic_01_problem_matrix.png")
    img.convert("RGB").save("video-production/graphics/graphic_01_problem_matrix.png")
    print("Regenerated crisp graphic_01_problem_matrix.png with high-res typography!")

def generate_crisp_graphic_02():
    img = Image.new("RGBA", (W, H), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Under the Hood: Explainable Route Scoring Architecture", "SYSTEM ARCHITECTURE")

    pillars = [
        ("Streetlight Illumination", "Overpass OSM Surveys & Tag Parsing", "Weight: 25%", (56, 189, 248)),
        ("Commercial Natural Footfall", "Active POIs, Chemists & Storefronts", "Weight: 30%", (52, 211, 153)),
        ("Diurnal & Temporal Penalty", "Late-night continuous decay curve", "Weight: 25%", (251, 191, 36)),
        ("Verified Incident Reports", "Community voting & official sources", "Weight: 20%", (248, 113, 113))
    ]

    for i, (name, desc, wt, col) in enumerate(pillars):
        x = 80 + i * 445
        draw.rounded_rectangle([x, 200, x + 415, 530], radius=20, fill=(30, 41, 59, 240), outline=col, width=2)
        draw.rounded_rectangle([x + 20, 225, x + 160, 275], radius=8, fill=(15, 23, 42, 255), outline=col, width=1)
        draw.text((x + 35, 238), f"Pillar {i+1}", font=font_subtitle, fill=col)
        draw.text((x + 20, 300), name, font=font_card_title, fill=(255, 255, 255, 255))
        draw.text((x + 20, 360), desc, font=font_card_body, fill=(148, 163, 184, 255))
        draw.rounded_rectangle([x + 20, 440, x + 200, 495], radius=10, fill=(15, 23, 42, 220))
        draw.text((x + 40, 455), wt, font=font_subtitle, fill=col)

    draw.rounded_rectangle([80, 580, 1840, 1000], radius=20, fill=(15, 23, 42, 240), outline=(52, 211, 153, 200), width=2)
    draw.text((120, 615), "THE TWO-DIMENSION COMPUTATION: SAFETY SCORE vs CONFIDENCE AUDIT", font=font_card_title, fill=(52, 211, 153, 255))

    boxes = [
        ("1. OSRM Road Geometry", "Continuous walking polyline", 120),
        ("2. Spatial Segmenter", "100-200m atomic road sections", 540),
        ("3. Confidence Engine", "Separates missing data from safety", 960),
        ("4. Explainable Audit", "Transparent audit trail for user", 1380)
    ]
    for title, sub, bx in boxes:
        draw.rounded_rectangle([bx, 680, bx + 360, 930], radius=16, fill=(30, 41, 59, 255), outline=(71, 85, 105, 255), width=2)
        draw.text((bx + 25, 720), title, font=font_card_title, fill=(255, 255, 255, 255))
        draw.text((bx + 25, 780), sub, font=font_card_body, fill=(148, 163, 184, 255))

    img.convert("RGB").save("docs/screenshots/graphic_02_architecture.png")
    img.convert("RGB").save("video-production/graphics/graphic_02_architecture.png")
    print("Regenerated crisp graphic_02_architecture.png!")

def generate_crisp_graphic_03():
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
        y = 180 + i * 160
        draw.rounded_rectangle([120, y, 1800, y + 130], radius=18, fill=(30, 41, 59, 240), outline=col, width=2)
        draw.ellipse([150, y + 35, 215, y + 100], fill=col)
        draw.text((172, y + 48), str(i+1), font=font_card_title, fill=(15, 23, 42, 255))
        draw.text((245, y + 30), title, font=font_card_title, fill=(255, 255, 255, 255))
        draw.text((245, y + 75), desc, font=font_card_body, fill=(203, 213, 225, 255))

    img.convert("RGB").save("docs/screenshots/graphic_03_guardian_security.png")
    img.convert("RGB").save("video-production/graphics/graphic_03_guardian_security.png")
    print("Regenerated crisp graphic_03_guardian_security.png!")

if __name__ == "__main__":
    generate_crisp_graphic_01()
    generate_crisp_graphic_02()
    generate_crisp_graphic_03()
