"""
Construit des planches contact pour audit visuel des paires de videos.
Extrait 1 frame a ~2s de chaque MP4, compose des grilles de 6 paires
(12 thumbnails) avec titres. Output dans audit-frames/.
"""
import os
import json
import subprocess
import shutil
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
OUT_DIR = os.path.join(ROOT, "audit-frames")
TMP_DIR = os.path.join(OUT_DIR, "_thumbs")

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# Dimensions
THUMB_W, THUMB_H = 200, 356  # 9:16
TITLE_H = 60
HEADER_H = 50
PAIRS_PER_SHEET = 6  # 6 paires = 12 thumbs par planche
GAP = 8


def font(sz):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def extract_frame(video_path, out_png, ts="2"):
    """Extrait 1 frame du video. Si echec, essaie a ts=0."""
    if os.path.exists(out_png):
        os.remove(out_png)
    try:
        subprocess.run(
            [FFMPEG, "-y", "-ss", ts, "-i", video_path, "-frames:v", "1",
             "-q:v", "3", "-vf", f"scale={THUMB_W}:{THUMB_H}:force_original_aspect_ratio=increase,crop={THUMB_W}:{THUMB_H}", out_png],
            check=False, capture_output=True, timeout=30,
        )
    except Exception:
        pass
    if not os.path.exists(out_png) or os.path.getsize(out_png) < 100:
        # Retry au tout debut
        subprocess.run(
            [FFMPEG, "-y", "-i", video_path, "-frames:v", "1",
             "-q:v", "3", "-vf", f"scale={THUMB_W}:{THUMB_H}:force_original_aspect_ratio=increase,crop={THUMB_W}:{THUMB_H}", out_png],
            check=False, capture_output=True, timeout=30,
        )


def truncate(s, max_chars=22):
    return s if len(s) <= max_chars else s[:max_chars - 1] + "…"


def make_sheet(pairs, sheet_idx, out_path):
    """Compose une planche avec N paires."""
    cols = 2
    rows = len(pairs)
    sheet_w = HEADER_H + (THUMB_W * cols) + (GAP * (cols + 1)) + 320  # 320 pour titre cat a gauche
    sheet_h = (THUMB_H + TITLE_H + GAP) * rows + GAP + HEADER_H

    img = Image.new("RGB", (sheet_w, sheet_h), (13, 13, 18))
    d = ImageDraw.Draw(img)
    title_font = font(22)
    sub_font = font(16)
    cat_font = font(18)
    head_font = font(28)

    # Header
    d.text((20, 12), f"Planche {sheet_idx + 1} — paires #{sheet_idx * PAIRS_PER_SHEET + 1} a {sheet_idx * PAIRS_PER_SHEET + len(pairs)}",
           font=head_font, fill=(245, 245, 247))

    for row_idx, pair in enumerate(pairs):
        y = HEADER_H + row_idx * (THUMB_H + TITLE_H + GAP) + GAP

        # Colonne de gauche : nom + id de la categorie
        d.text((10, y + 30), pair["emoji"] + " " + truncate(pair["name"], 18),
               font=cat_font, fill=(245, 245, 247))
        d.text((10, y + 60), pair["id"], font=sub_font, fill=(153, 153, 168))
        d.text((10, y + 90), f"#{sheet_idx * PAIRS_PER_SHEET + row_idx + 1}", font=sub_font, fill=(102, 51, 255))

        # 2 thumbnails cote a cote
        for col_idx, video in enumerate(pair["videos"]):
            thumb_path = pair["_thumbs"][col_idx]
            x = 320 + GAP + col_idx * (THUMB_W + GAP)
            try:
                t = Image.open(thumb_path)
                img.paste(t, (x, y))
            except Exception:
                d.rectangle([x, y, x + THUMB_W, y + THUMB_H], fill=(50, 50, 60))
                d.text((x + 10, y + 10), "(no thumb)", font=sub_font, fill=(200, 100, 100))
            # Titre dessous
            d.rectangle([x, y + THUMB_H, x + THUMB_W, y + THUMB_H + TITLE_H], fill=(30, 30, 40))
            title_text = truncate(video["title"], 22)
            tb = d.textbbox((0, 0), title_text, font=title_font)
            tw = tb[2] - tb[0]
            d.text((x + (THUMB_W - tw) // 2, y + THUMB_H + 18), title_text, font=title_font, fill=(245, 245, 247))

    img.save(out_path, "PNG", optimize=True)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    os.makedirs(TMP_DIR)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    cats = data["categories"]
    print(f"[INFO] {len(cats)} categories a auditer = {len(cats) * 2} thumbnails")

    # Extraction des thumbnails
    for idx, cat in enumerate(cats):
        cat["_thumbs"] = []
        for v_idx, v in enumerate(cat["videos"]):
            src = os.path.join(ROOT, v["url"])
            dst = os.path.join(TMP_DIR, f"{cat['id']}_{v_idx}.png")
            extract_frame(src, dst)
            cat["_thumbs"].append(dst)
        if (idx + 1) % 10 == 0:
            print(f"  ... {idx + 1}/{len(cats)} cats")
    print(f"[OK] Thumbnails extraits")

    # Composition des planches
    n_sheets = (len(cats) + PAIRS_PER_SHEET - 1) // PAIRS_PER_SHEET
    for sheet_idx in range(n_sheets):
        chunk = cats[sheet_idx * PAIRS_PER_SHEET:(sheet_idx + 1) * PAIRS_PER_SHEET]
        out_path = os.path.join(OUT_DIR, f"planche-{sheet_idx + 1:02d}.png")
        make_sheet(chunk, sheet_idx, out_path)
        size_kb = os.path.getsize(out_path) // 1024
        print(f"[OK] planche-{sheet_idx + 1:02d}.png ({size_kb} KB)")

    print(f"\n[DONE] {n_sheets} planches dans {OUT_DIR}")


if __name__ == "__main__":
    main()
