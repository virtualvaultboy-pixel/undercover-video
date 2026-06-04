"""
Audit visuel V2 : multi-frame contact sheets.

Au lieu d'1 frame par video, on extrait 4 frames etalees (10%, 35%, 60%, 85%)
et on les compose en strip horizontale. Une paire = 2 strips empilees = 8 frames.
Beaucoup plus fiable pour identifier le contenu (mouvement, scenes).

Output : audit-frames-v2/planche-NN.png
"""
import os
import json
import shutil
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
OUT_DIR = os.path.join(ROOT, "audit-frames-v2")

# Dimensions par thumb individuel (9:16)
THUMB_W, THUMB_H = 110, 196
FRAMES_PER_VIDEO = 4   # 4 frames par video
STRIP_W = THUMB_W * FRAMES_PER_VIDEO  # 440
STRIP_H = THUMB_H                       # 196
PAIR_H = STRIP_H * 2 + 18              # 2 strips + petit gap
TITLE_BAND_H = 24                        # bande pour titre dessous chaque strip
PAIRS_PER_SHEET = 5                      # 5 paires par planche
LEFT_COL_W = 220                         # nom categorie a gauche
HEADER_H = 60
GAP = 12


def font(sz):
    for c in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
              "C:/Windows/Fonts/arial.ttf"]:
        try:
            return ImageFont.truetype(c, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def extract_strip(video_path):
    """Extrait FRAMES_PER_VIDEO frames etalees et compose une strip."""
    if not os.path.exists(video_path):
        return None
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total < 2:
        cap.release()
        return None

    strip = Image.new("RGB", (STRIP_W, STRIP_H), (20, 20, 28))
    # Positions : 10%, 35%, 60%, 85%
    positions = [0.10, 0.35, 0.60, 0.85] if FRAMES_PER_VIDEO == 4 else \
                [(i + 0.5) / FRAMES_PER_VIDEO for i in range(FRAMES_PER_VIDEO)]

    for i, pct in enumerate(positions):
        frame_idx = max(0, min(total - 1, int(total * pct)))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = cap.read()
        if not ok:
            continue
        # BGR -> RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        # Resize cover (fill, crop)
        src_ratio = img.width / img.height
        tgt_ratio = THUMB_W / THUMB_H
        if src_ratio > tgt_ratio:
            # source plus large : scale par hauteur, crop largeur
            new_h = THUMB_H
            new_w = int(THUMB_H * src_ratio)
        else:
            new_w = THUMB_W
            new_h = int(THUMB_W / src_ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - THUMB_W) // 2
        top = (new_h - THUMB_H) // 2
        img = img.crop((left, top, left + THUMB_W, top + THUMB_H))
        strip.paste(img, (i * THUMB_W, 0))

    cap.release()
    return strip


def truncate(s, n=28):
    return s if len(s) <= n else s[:n - 1] + "…"


def make_sheet(pairs, sheet_idx, out_path):
    rows = len(pairs)
    sheet_w = LEFT_COL_W + STRIP_W + GAP * 2
    pair_block_h = STRIP_H * 2 + TITLE_BAND_H * 2 + GAP * 2
    sheet_h = HEADER_H + (pair_block_h + GAP) * rows + GAP

    img = Image.new("RGB", (sheet_w, sheet_h), (12, 12, 16))
    d = ImageDraw.Draw(img)
    head_f = font(24)
    cat_f = font(17)
    sub_f = font(13)
    title_f = font(14)
    idx_f = font(15)

    d.text((16, 16), f"Planche {sheet_idx + 1} - paires #{sheet_idx * PAIRS_PER_SHEET + 1} a {sheet_idx * PAIRS_PER_SHEET + rows}  (multi-frame V2)",
           font=head_f, fill=(245, 245, 247))

    for row_idx, pair in enumerate(pairs):
        y = HEADER_H + row_idx * (pair_block_h + GAP) + GAP

        # Col gauche : emoji + name + id + index
        d.text((10, y + 6), pair["emoji"] + " " + truncate(pair["name"], 18),
               font=cat_f, fill=(245, 245, 247))
        d.text((10, y + 30), pair["id"], font=sub_f, fill=(140, 140, 160))
        d.text((10, y + 52), f"#{sheet_idx * PAIRS_PER_SHEET + row_idx + 1}",
               font=idx_f, fill=(102, 51, 255))

        for v_idx, video in enumerate(pair["videos"][:2]):
            strip_y = y + v_idx * (STRIP_H + TITLE_BAND_H)
            strip = pair["_strips"][v_idx]
            if strip:
                img.paste(strip, (LEFT_COL_W + GAP, strip_y))
            else:
                d.rectangle([LEFT_COL_W + GAP, strip_y,
                             LEFT_COL_W + GAP + STRIP_W, strip_y + STRIP_H],
                            fill=(50, 50, 60))
                d.text((LEFT_COL_W + GAP + 8, strip_y + 8),
                       "(no frames)", font=sub_f, fill=(200, 100, 100))
            # Bande titre sous la strip
            title_y = strip_y + STRIP_H
            d.rectangle([LEFT_COL_W + GAP, title_y,
                         LEFT_COL_W + GAP + STRIP_W, title_y + TITLE_BAND_H],
                        fill=(28, 28, 38))
            t = truncate(video["title"], 38)
            tb = d.textbbox((0, 0), t, font=title_f)
            tw = tb[2] - tb[0]
            d.text((LEFT_COL_W + GAP + (STRIP_W - tw) // 2, title_y + 4),
                   t, font=title_f, fill=(240, 240, 245))

    img.save(out_path, "PNG", optimize=True)


def main():
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    cats = data["categories"]
    print(f"[INFO] {len(cats)} categories, {len(cats) * 2} videos a analyser")

    # Extraction multi-frame strips
    for idx, cat in enumerate(cats):
        cat["_strips"] = []
        for v in cat["videos"][:2]:
            src = os.path.join(ROOT, v["url"])
            try:
                strip = extract_strip(src)
            except Exception as e:
                print(f"  [!] {cat['id']}: {e}")
                strip = None
            cat["_strips"].append(strip)
        if (idx + 1) % 10 == 0:
            print(f"  ... {idx + 1}/{len(cats)} cats")
    print(f"[OK] Strips extraites")

    n = (len(cats) + PAIRS_PER_SHEET - 1) // PAIRS_PER_SHEET
    for i in range(n):
        chunk = cats[i * PAIRS_PER_SHEET:(i + 1) * PAIRS_PER_SHEET]
        out = os.path.join(OUT_DIR, f"planche-{i + 1:02d}.png")
        make_sheet(chunk, i, out)
        print(f"[OK] planche-{i + 1:02d}.png ({os.path.getsize(out) // 1024} KB)")

    print(f"\n[DONE] {n} planches dans {OUT_DIR}")


if __name__ == "__main__":
    main()
