"""
Capture de vrais screenshots de l'application via Playwright.
Necessite que le serveur tourne sur http://localhost:8000.
"""
import os
import time
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

URL = "http://localhost:8000/"
# Format Play Store recommande : 9:16 portrait, ex Pixel 6 : 1080x2400 -> on garde 540x1170 pour compat manifest
DEVICE = {"viewport": {"width": 540, "height": 1170}, "device_scale_factor": 2, "is_mobile": True}


def wait_for_screen(page, screen_id):
    page.wait_for_selector(f"#{screen_id}.active", timeout=10000)
    page.wait_for_timeout(400)


def shot(page, name):
    out = os.path.join(OUT_DIR, name)
    page.screenshot(path=out, full_page=False)
    print(f"[OK] {name} -> {os.path.getsize(out)//1024} KB")


with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(
        viewport=DEVICE["viewport"],
        device_scale_factor=DEVICE["device_scale_factor"],
        is_mobile=DEVICE["is_mobile"],
        locale="fr-FR",
    )
    page = ctx.new_page()

    # 1. Accueil
    page.goto(URL, wait_until="networkidle")
    # On attend que le select soit peuple (au moins 5 options chargees depuis videos.json)
    page.wait_for_function("document.querySelectorAll('#category-select option').length > 5", timeout=10000)
    page.wait_for_timeout(800)
    shot(page, "screen-setup.png")

    # 2. Comment jouer
    page.click("#btn-help")
    wait_for_screen(page, "screen-help")
    shot(page, "screen-help.png")
    page.click("#btn-help-close")
    wait_for_screen(page, "screen-setup")

    # 3. Noms
    page.click("#btn-start")
    wait_for_screen(page, "screen-names")
    inputs = page.query_selector_all("#names-list input")
    for i, inp in enumerate(inputs):
        inp.fill(["Alice", "Bob", "Charlie", "Diane"][i])
    page.wait_for_timeout(300)
    shot(page, "screen-names.png")

    # 4. Transition (passe le tel)
    page.click("#btn-names-confirm")
    wait_for_screen(page, "screen-transition")
    shot(page, "screen-transition.png")

    # 5. Video (afficher l'ecran video — la video locale chargera)
    page.click("#btn-ready")
    page.wait_for_selector("#screen-video.active", timeout=10000)
    page.wait_for_timeout(1800)  # laisse la video commencer
    shot(page, "screen-video.png")

    # Skip tous les joueurs pour aller au vote
    for _ in range(4):
        page.click("#btn-hide")
        page.wait_for_timeout(400)
        # si transition, valider, sinon screen-play
        if page.locator("#screen-transition.active").count() > 0:
            page.click("#btn-ready")
            page.wait_for_timeout(400)

    # 6. Ecran "a vous de jouer"
    wait_for_screen(page, "screen-play")
    shot(page, "screen-play.png")

    # 7. Vote
    page.click("#btn-go-vote")
    wait_for_screen(page, "screen-vote")
    shot(page, "screen-vote.png")

    # 8. Victoire ou rate — on tente la 1ere option de vote (50/50 que ce soit l'undercover)
    page.click(".vote-btn")
    page.wait_for_timeout(800)
    if page.locator("#screen-victory.active").count() > 0:
        wait_for_screen(page, "screen-victory")
        page.wait_for_timeout(1500)
        shot(page, "screen-victory.png")
    elif page.locator("#screen-undercover-wins.active").count() > 0:
        wait_for_screen(page, "screen-undercover-wins")
        page.wait_for_timeout(1500)
        shot(page, "screen-undercover-wins.png")
    else:
        # Sinon vote rate, on continue
        wait_for_screen(page, "screen-miss")
        shot(page, "screen-miss.png")

    browser.close()
    print("\n[DONE] Screenshots dans screenshots/")
