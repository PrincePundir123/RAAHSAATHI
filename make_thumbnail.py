from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs("video-production/images", exist_ok=True)

# 1920x1080 Thumbnail
W, H = 1920, 1080

def create_thumbnail():
    img = Image.new("RGBA", (W, H), (15, 23, 42, 255)) # Dark slate bg
    draw = ImageDraw.Draw(img)

    # Accent gradient / glow background
    for r in range(400, 0, -10):
        alpha = int(35 * (1 - r / 400))
        draw.ellipse([W - 600 - r, H//2 - r, W - 600 + r, H//2 + r], fill=(13, 148, 136, alpha)) # Emerald glow
        draw.ellipse([400 - r, H//2 - r, 400 + r, H//2 + r], fill=(225, 29, 72, alpha)) # Rose glow

    # Title Banner
    draw.rectangle([0, 0, W, 10], fill=(16, 185, 129, 255))

    # Badge
    draw.rounded_rectangle([120, 100, 480, 160], radius=16, fill=(30, 41, 59, 255), outline=(52, 211, 153, 255), width=2)
    draw.text((150, 118), "🛡️ WOMEN'S SAFETY AI PLATFORM", fill=(52, 211, 153, 255))

    # Main Heading
    # SafeWalk (RaahSaathi)
    draw.text((120, 200), "SafeWalk (RaahSaathi)", fill=(255, 255, 255, 255))
    draw.text((120, 310), "Autonomous Journey Guardian &\nSegment-Level Route Intelligence", fill=(148, 163, 184, 255))

    # Feature Pills
    features = [
        "✨ Dual Routing (Safest vs Fastest)",
        "🔍 4-Pillar Explainable Confidence",
        "🚨 SafeStops Emergency Havens",
        "🛡️ Cryptographic Live Guardian",
        "🎙️ Hinglish/Hindi AI Voice Reports",
        "📊 Institutional Safety Intelligence"
    ]
    for i, f in enumerate(features):
        x = 120 + (i % 2) * 440
        y = 520 + (i // 2) * 80
        draw.rounded_rectangle([x, y, x + 410, y + 60], radius=12, fill=(30, 41, 59, 220), outline=(51, 65, 85, 255), width=2)
        draw.text((x + 20, y + 18), f, fill=(241, 245, 249, 255))

    # Presenter card
    draw.rounded_rectangle([120, 840, 600, 940], radius=16, fill=(16, 185, 129, 30), outline=(16, 185, 129, 150), width=2)
    draw.text((150, 860), "Presented by: Prince Pundir", fill=(255, 255, 255, 255))
    draw.text((150, 900), "National Hackathon 2026 Submission", fill=(52, 211, 153, 255))

    # Paste UI Preview mock if exists
    if os.path.exists("video-production/images/02_dual_route_map.png"):
        ui = Image.open("video-production/images/02_dual_route_map.png").convert("RGBA")
        ui_thumb = ui.resize((840, 480))
        # Add shadow & border
        draw.rounded_rectangle([1035, 345, 1885, 835], radius=24, fill=(0, 0, 0, 180))
        img.paste(ui_thumb, (1040, 350))
        draw.rounded_rectangle([1040, 350, 1880, 830], radius=12, outline=(52, 211, 153, 255), width=3)

    img.convert("RGB").save("final_thumbnail.png", "PNG")
    img.convert("RGB").save("video-production/images/final_thumbnail.png", "PNG")
    print("Thumbnail created successfully!")

if __name__ == "__main__":
    create_thumbnail()

