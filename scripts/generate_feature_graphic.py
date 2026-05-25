"""
Genere le Feature Graphic 1024x500 pour la page Play Store.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "store-assets")
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1024, 500
ACCENT = (255, 51, 102)
ACCENT_2 = (102, 51, 255)
DARK = (13, 13, 18)
WHITE = (255, 255, 255)
TEXT_DIM = (200, 200, 220)


def load_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            pass
    return ImageFont.load_default()


def gradient_bg():
    """Fond degrade diagonal sombre vers couleurs vives."""
    img = Image.new("RGB", (W, H), DARK)
    pixels = img.load()
    for y in range(H):
        for x in range(W):
            # Degrade radial depuis le centre
            t = (x / W) * 0.7 + (y / H) * 0.3
            # Mix entre DARK et ACCENT/ACCENT_2
            if t < 0.5:
                # Sombre vers rose
                k = t * 2
                r = int(DARK[0] * (1 - k) + ACCENT[0] * k * 0.55)
                g = int(DARK[1] * (1 - k) + ACCENT[1] * k * 0.55)
                b = int(DARK[2] * (1 - k) + ACCENT[2] * k * 0.55)
            else:
                k = (t - 0.5) * 2
                r = int(ACCENT[0] * (1 - k) * 0.55 + ACCENT_2[0] * k * 0.6)
                g = int(ACCENT[1] * (1 - k) * 0.55 + ACCENT_2[1] * k * 0.6)
                b = int(ACCENT[2] * (1 - k) * 0.55 + ACCENT_2[2] * k * 0.6)
            pixels[x, y] = (r, g, b)
    return img


def draw_mask_icon(draw, cx, cy, scale=1.0):
    """Dessine l'icone masque/lunettes similaire au logo."""
    eye_radius_x = int(80 * scale)
    eye_radius_y = int(65 * scale)
    gap = int(15 * scale)

    left_cx = cx - eye_radius_x - gap // 2
    right_cx = cx + eye_radius_x + gap // 2

    # Pont
    bridge_h = int(10 * scale)
    draw.rectangle([
        left_cx + eye_radius_x - 2, cy - bridge_h // 2,
        right_cx - eye_radius_x + 2, cy + bridge_h // 2
    ], fill=(0, 0, 0, 230))

    # Lunettes
    for ecx in (left_cx, right_cx):
        draw.ellipse([
            ecx - eye_radius_x, cy - eye_radius_y,
            ecx + eye_radius_x, cy + eye_radius_y
        ], fill=(0, 0, 0, 240), outline=WHITE, width=max(2, int(4 * scale)))
        # Reflet
        glint_r = int(14 * scale)
        draw.ellipse([
            ecx + eye_radius_x // 3 - glint_r, cy - eye_radius_y // 2 - glint_r,
            ecx + eye_radius_x // 3 + glint_r, cy - eye_radius_y // 2 + glint_r,
        ], fill=(255, 255, 255, 180))


def main():
    img = gradient_bg()
    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    # Cercle décoratif derrière l'icône (à gauche)
    cx_icon = 220
    cy_icon = H // 2
    halo_r = 200
    halo = Image.new("RGBA", (halo_r * 2, halo_r * 2), (0, 0, 0, 0))
    halo_draw = ImageDraw.Draw(halo)
    for r in range(halo_r, 0, -2):
        alpha = int(60 * (1 - r / halo_r))
        halo_draw.ellipse([halo_r - r, halo_r - r, halo_r + r, halo_r + r],
                          fill=(255, 255, 255, alpha))
    img.alpha_composite(halo, (cx_icon - halo_r, cy_icon - halo_r))

    # Icone masque
    draw_mask_icon(draw, cx_icon, cy_icon, scale=1.6)

    # Titre à droite
    title_x = 460
    title = "UNDERCOVER"
    title_font = load_font(76, bold=True)
    draw.text((title_x, 130), title, font=title_font, fill=WHITE)

    subtitle = "VIDÉO"
    subtitle_font = load_font(76, bold=True)
    draw.text((title_x, 220), subtitle, font=subtitle_font,
              fill=(255, 200, 220))

    # Tagline
    tag_font = load_font(28)
    draw.text((title_x + 4, 330),
              "Le party game pour démasquer l'intrus",
              font=tag_font, fill=TEXT_DIM)

    # Mini chips en bas (features)
    chip_y = 400
    chips = ["3-12 joueurs", "75 catégories", "Sans pub", "Sans compte"]
    chip_x = title_x
    chip_font = load_font(20, bold=True)
    for chip in chips:
        bbox = draw.textbbox((0, 0), chip, font=chip_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        pad_x, pad_y = 18, 10
        cw = tw + 2 * pad_x
        ch = th + 2 * pad_y
        # Chip arrondie semi-transparente
        draw.rounded_rectangle([chip_x, chip_y, chip_x + cw, chip_y + ch],
                               radius=20,
                               fill=(255, 255, 255, 40),
                               outline=(255, 255, 255, 120),
                               width=1)
        draw.text((chip_x + pad_x, chip_y + pad_y - 3), chip,
                  font=chip_font, fill=WHITE)
        chip_x += cw + 14

    out = os.path.join(OUT_DIR, "feature-graphic.png")
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"[OK] feature-graphic.png ({W}x{H}) -> {os.path.getsize(out)//1024} KB")
    print(f"    => {out}")


if __name__ == "__main__":
    main()
