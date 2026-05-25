"""
Genere les icones PNG pour la PWA + Play Store.
Output :
- icons/icon-192.png
- icons/icon-512.png
- icons/icon-maskable-512.png (avec padding pour le format maskable)
- icons/apple-touch-icon.png (180x180)
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS_DIR = os.path.join(ROOT, "icons")
os.makedirs(ICONS_DIR, exist_ok=True)

# Couleurs de la marque
ACCENT = (255, 51, 102)     # #ff3366
ACCENT_2 = (102, 51, 255)   # #6633ff
DARK = (13, 13, 18)         # #0d0d12
WHITE = (255, 255, 255)


def gradient_bg(size):
    """Cree un fond degrade diagonal rose -> violet."""
    img = Image.new("RGB", (size, size), DARK)
    pixels = img.load()
    for y in range(size):
        for x in range(size):
            # Diagonale : t va de 0 a 1
            t = (x + y) / (2 * size)
            r = int(ACCENT[0] * (1 - t) + ACCENT_2[0] * t)
            g = int(ACCENT[1] * (1 - t) + ACCENT_2[1] * t)
            b = int(ACCENT[2] * (1 - t) + ACCENT_2[2] * t)
            pixels[x, y] = (r, g, b)
    return img


def draw_mask_symbol(img, padding_ratio=0.18):
    """Dessine un symbole de masque de bandit / lunettes detective au centre."""
    size = img.size[0]
    draw = ImageDraw.Draw(img, "RGBA")

    # Lunettes : 2 ovales noirs reliés par un pont
    pad = int(size * padding_ratio)
    cy = int(size * 0.45)               # centre vertical des lunettes
    eye_radius_x = int(size * 0.20)
    eye_radius_y = int(size * 0.17)
    gap = int(size * 0.04)              # espace entre les 2 lunettes

    left_cx = size // 2 - eye_radius_x - gap // 2
    right_cx = size // 2 + eye_radius_x + gap // 2

    # Pont
    bridge_h = int(size * 0.025)
    draw.rectangle([
        left_cx + eye_radius_x - 2, cy - bridge_h // 2,
        right_cx - eye_radius_x + 2, cy + bridge_h // 2
    ], fill=(0, 0, 0, 230))

    # Lunettes ovales
    for cx in (left_cx, right_cx):
        draw.ellipse([
            cx - eye_radius_x, cy - eye_radius_y,
            cx + eye_radius_x, cy + eye_radius_y
        ], fill=(0, 0, 0, 240), outline=WHITE, width=max(2, size // 80))

    # Reflet blanc dans chaque lunette
    for cx in (left_cx, right_cx):
        glint_r = int(size * 0.035)
        draw.ellipse([
            cx + eye_radius_x // 3 - glint_r,
            cy - eye_radius_y // 2 - glint_r,
            cx + eye_radius_x // 3 + glint_r,
            cy - eye_radius_y // 2 + glint_r,
        ], fill=(255, 255, 255, 180))

    # Sourire / moustache stylisee en dessous
    mouth_cy = int(size * 0.72)
    mouth_w = int(size * 0.30)
    mouth_h = int(size * 0.12)
    # Forme : un demi-cercle vers le bas (sourire)
    draw.arc([
        size // 2 - mouth_w, mouth_cy - mouth_h,
        size // 2 + mouth_w, mouth_cy + mouth_h
    ], start=10, end=170, fill=(255, 255, 255, 220), width=max(3, size // 50))


def make_icon(size, maskable=False):
    if maskable:
        # Pour maskable : 80% safe zone au centre
        bg = gradient_bg(size)
        # Petite reduction pour avoir une marge safe
        inner = Image.new("RGB", (size, size))
        inner_pixels = inner.load()
        # On dessine un fond plein de la couleur moyenne pour eviter coupures
        for y in range(size):
            for x in range(size):
                inner_pixels[x, y] = bg.getpixel((x, y))
        draw_mask_symbol(inner, padding_ratio=0.28)
        return inner
    else:
        img = gradient_bg(size)
        draw_mask_symbol(img)
        return img


# Generation
sizes = [
    ("icon-192.png", 192, False),
    ("icon-512.png", 512, False),
    ("icon-maskable-512.png", 512, True),
    ("apple-touch-icon.png", 180, False),
    ("favicon-32.png", 32, False),
]

for filename, size, maskable in sizes:
    icon = make_icon(size, maskable=maskable)
    out = os.path.join(ICONS_DIR, filename)
    icon.save(out, "PNG", optimize=True)
    print(f"[OK] {filename} ({size}x{size}) -> {os.path.getsize(out)//1024} KB")

print(f"\n[DONE] {len(sizes)} icones generees dans icons/")
