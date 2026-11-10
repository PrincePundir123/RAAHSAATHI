import time
import os
from playwright.sync_api import sync_playwright

os.makedirs("video-production/images", exist_ok=True)
os.makedirs("video-production/footage", exist_ok=True)

def capture_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use high resolution 1920x1080 viewport
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        print("Navigating to http://localhost:8501 ...")
        page.goto("http://localhost:8501", timeout=30000)
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        # 1. Main Home / Route Planning Screen
        print("Capturing 01_home_screen.png ...")
        page.screenshot(path="video-production/images/01_home_screen.png", full_page=False)

        # Find buttons or tabs
        # Let's inspect tabs
        tabs = page.query_selector_all("button[role='tab']")
        print(f"Found {len(tabs)} tabs.")
        tab_names = [t.inner_text().strip() for t in tabs]
        print("Tab names:", tab_names)

        # Tab 1: Plan Safe Route - trigger a route search if possible or capture the map
        if len(tabs) >= 1:
            tabs[0].click()
            time.sleep(2)
            page.screenshot(path="video-production/images/02_dual_route_map.png")

        # Tab 2: SafeStops Nearby Assistance
        if len(tabs) >= 2:
            print("Switching to Tab 2 (SafeStops)...")
            tabs[1].click()
            time.sleep(3)
            page.screenshot(path="video-production/images/03_safestops.png")

        # Tab 3: Live Journey Guardian
        if len(tabs) >= 3:
            print("Switching to Tab 3 (Journey Guardian)...")
            tabs[2].click()
            time.sleep(3)
            page.screenshot(path="video-production/images/04_journey_guardian.png")

        # Tab 4: Multilingual Voice & AI Reporting
        if len(tabs) >= 4:
            print("Switching to Tab 4 (Voice & AI Reporting)...")
            tabs[3].click()
            time.sleep(3)
            page.screenshot(path="video-production/images/05_voice_reporting.png")

        # Tab 6: Safety Intelligence Dashboard
        if len(tabs) >= 6:
            print("Switching to Tab 6 (Safety Intelligence)...")
            tabs[5].click()
            time.sleep(3)
            page.screenshot(path="video-production/images/06_safety_intelligence.png")

        browser.close()
        print("All UI frames captured successfully!")

if __name__ == "__main__":
    capture_ui()

