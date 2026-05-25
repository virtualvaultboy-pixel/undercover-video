"""
Genere des screenshots mockup pour le manifest PWA.
A remplacer par de vrais screenshots avant publication Play Store.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 540, 1170
DARK = (13, 13, 18)
BG_ELEV = (26, 26, 36)
BORDER = (42, 42, 56)
TEXT = (245, 245, 247)
TEXT_DIM = (153, 153, 168)
ACCENT = (255, 51, 102)
ACCENT_2 = (102, 51, 255)
SUCCESS = (51, 204, 136)


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


def base_canvas():
    img = Image.new("RGB", (W, H), DARK)
    return img


def draw_gradient_text(draw, text, y, size, bold=True):
    """Texte centre avec font."""
    font = load_font(size, bold=bold)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    draw.text((x, y), text, font=font, fill=TEXT)


def draw_dim_text(draw, text, y, size=22):
    font = load_font(size)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    draw.text((x, y), text, font=font, fill=TEXT_DIM)


def draw_pill_button(draw, label, y, color=ACCENT):
    """Gros bouton centre."""
    bw, bh = 360, 76
    x = (W - bw) // 2
    draw.rounded_rectangle([x, y, x + bw, y + bh], radius=20, fill=color)
    font = load_font(28, bold=True)
    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = x + (bw - tw) // 2
    ty = y + (bh - th) // 2 - 5
    draw.text((tx, ty), label, font=font, fill=TEXT)


def draw_card(draw, x, y, w, h):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=BG_ELEV, outline=BORDER, width=2)


# ----- Screen 1 : Accueil -----
def screen_setup():
    img = base_canvas()
    d = ImageDraw.Draw(img)
    draw_gradient_text(d, "Undercover Vidéo", 130, 50)
    draw_dim_text(d, "L'app distribue les rôles. À vous de jouer.", 200)

    # Counter joueurs
    draw_dim_text(d, "NOMBRE DE JOUEURS", 310, 18)
    draw_card(d, 90, 350, 360, 90)
    f = load_font(54, bold=True)
    bbox = d.textbbox((0, 0), "4", font=f)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2, 360), "4", font=f, fill=TEXT)
    d.text((130, 380), "−", font=load_font(40, bold=True), fill=TEXT_DIM)
    d.text((395, 380), "+", font=load_font(40, bold=True), fill=TEXT_DIM)

    # Catégorie
    draw_dim_text(d, "CATÉGORIE", 490, 18)
    draw_card(d, 90, 530, 360, 70)
    d.text((140, 548), "🎲  Aléatoire", font=load_font(24), fill=TEXT)

    draw_pill_button(d, "Suivant", 700, ACCENT)
    draw_dim_text(d, "75 catégories disponibles", 820, 18)
    return img


# ----- Screen 2 : Vidéo -----
def screen_video():
    img = base_canvas()
    d = ImageDraw.Draw(img)
    # Zone vidéo
    draw_card(d, 40, 80, W - 80, 800)
    # Triangle play centre
    cx, cy = W // 2, 480
    d.polygon([(cx - 40, cy - 50), (cx - 40, cy + 50), (cx + 50, cy)], fill=(255, 255, 255, 100))
    draw_dim_text(d, "🎬  Vidéo secrète en cours", 900, 22)
    draw_pill_button(d, "✅ J'ai vu, cacher", 970)
    return img


# ----- Screen 3 : Vote -----
def screen_vote():
    img = base_canvas()
    d = ImageDraw.Draw(img)
    draw_gradient_text(d, "🗳️ Qui est l'undercover ?", 110, 36)
    draw_dim_text(d, "Touchez le nom du joueur suspect.", 175)

    names = ["Alice", "Bob", "Charlie", "Diane", "Eve", "Frank"]
    grid_w = 380
    cell_w = 180
    cell_h = 120
    start_x = (W - grid_w) // 2
    start_y = 260
    for i, name in enumerate(names):
        col = i % 2
        row = i // 2
        x = start_x + col * (cell_w + 20)
        y = start_y + row * (cell_h + 20)
        draw_card(d, x, y, cell_w, cell_h)
        font = load_font(26, bold=True)
        bbox = d.textbbox((0, 0), name, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        d.text((x + (cell_w - tw) // 2, y + (cell_h - th) // 2 - 5), name, font=font, fill=TEXT)
    return img


# ----- Screen 4 : Victoire (comparatif) -----
def screen_victory():
    img = base_canvas()
    d = ImageDraw.Draw(img)
    draw_gradient_text(d, "🎉 Civils victorieux !", 100, 38)
    f = load_font(60, bold=True)
    bbox = d.textbbox((0, 0), "Alice", font=f)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2, 170), "Alice", font=f, fill=SUCCESS)
    draw_dim_text(d, "était bien l'undercover.", 260)

    # 2 vignettes comparatif
    vw = 230
    vh = 410
    gap = 16
    start_x = (W - (vw * 2 + gap)) // 2
    sy = 340

    for i, (label, title) in enumerate([("👥 CIVILS", "Pizza"), ("🕵️ UNDERCOVER", "Burger")]):
        x = start_x + i * (vw + gap)
        d.text((x, sy), label, font=load_font(16, bold=True), fill=TEXT_DIM)
        draw_card(d, x, sy + 30, vw, vh)
        d.text((x + 30, sy + vh + 50), title, font=load_font(22, bold=True), fill=TEXT)

    draw_pill_button(d, "Nouvelle partie", 950)
    return img


# Generation
shots = [
    ("screen-setup.png", screen_setup),
    ("screen-video.png", screen_video),
    ("screen-vote.png", screen_vote),
    ("screen-victory.png", screen_victory),
]

for name, fn in shots:
    img = fn()
    out = os.path.join(OUT_DIR, name)
    img.save(out, "PNG", optimize=True)
    print(f"[OK] {name} -> {os.path.getsize(out)//1024} KB")

print(f"\n[DONE] {len(shots)} screenshots generes dans screenshots/")
