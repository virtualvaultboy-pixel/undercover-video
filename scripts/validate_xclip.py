"""
Validation automatique X-CLIP zero-shot des paires de videos.json.

Pour chaque video :
- Score X-CLIP contre [titre_attendu, "a meme with text", "a cartoon character",
  "abstract image", "unrelated content"]
- Si le titre attendu n'est PAS top-1 ou si top-1 est meme/cartoon/abstract -> SUSPECT

Output : audit-xclip.json avec details + liste IDs a purger.

Usage :
  python validate_xclip.py                # valide tout videos.json
  python validate_xclip.py id1 id2 ...    # valide seulement ces IDs
"""
import os
import sys
import json
import av
import numpy as np
import torch
from transformers import XCLIPProcessor, XCLIPModel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
TR_PATH = os.path.join(ROOT, "data", "translations.json")
OUT_JSON = os.path.join(ROOT, "audit-xclip.json")

NEGATIVE_LABELS = [
    "a meme with text overlay",
    "a cartoon character animation",
    "abstract irrelevant pattern",
    "blurry unclear footage",
]

MODEL_NAME = "microsoft/xclip-base-patch32"


def read_video_frames(path, num_frames=8):
    container = av.open(path)
    stream = container.streams.video[0]
    total = stream.frames or 0
    if total < 1:
        frames = [f for f in container.decode(video=0)]
        total = len(frames)
        if total < 1:
            return []
        indices = np.linspace(0, total - 1, num_frames).astype(int)
        return [frames[i].to_ndarray(format="rgb24") for i in indices]
    indices = set(int(i) for i in np.linspace(0, total - 1, num_frames).astype(int))
    frames = []
    idx = 0
    container.seek(0)
    for f in container.decode(video=0):
        if idx in indices:
            frames.append(f.to_ndarray(format="rgb24"))
            if len(frames) >= num_frames:
                break
        idx += 1
    container.close()
    return frames


def get_en_label(cat_id, video_idx, cat_name_fr, video_title_fr, translations):
    """Recupere le label EN depuis translations.json (multi-formats).
    Fallback : nom categorie EN, puis dico FR->EN, puis titre FR."""
    entry = translations.get("categories", {}).get(cat_id, {})
    en = entry.get("en")

    # Format 1 : {en: {name, videos: [{title}, ...]}}
    if isinstance(en, dict):
        videos = en.get("videos", [])
        if video_idx < len(videos):
            t = videos[video_idx].get("title")
            if t:
                return f"a video of {t.lower()}"
        n = en.get("name")
        if n:
            return f"a video of {n.lower()}"

    # Format 2 : {en: "Category Name"}
    if isinstance(en, str):
        return f"a video of {en.lower()}"

    # Fallback : mini-dico FR -> EN
    mapping = {
        "café": "coffee", "the": "tea", "vin": "wine", "biere": "beer",
        "chat": "cat", "chien": "dog", "cheval": "horse", "vache": "cow",
        "ours": "bear", "lion": "lion", "tigre": "tiger", "loup": "wolf",
        "voiture": "car", "moto": "motorcycle", "velo": "bicycle",
        "salade": "salad", "burger": "burger", "pizza": "pizza",
        "course": "running", "yoga": "yoga", "foot": "soccer",
        "plage": "beach", "ocean": "ocean", "montagne": "mountain",
        "feu": "fire", "neige": "snow", "pluie": "rain", "bougie": "candle",
        "tulipe": "tulip", "rose": "rose", "fleur": "flower",
        "vagues": "ocean waves", "cascade": "waterfall",
        "orange": "orange fruit", "citron": "lemon",
        "magicien": "wizard", "sorciere": "witch",
        "ninja": "ninja", "samourai": "samurai",
    }
    t = video_title_fr.lower()
    for fr, en_w in mapping.items():
        if fr in t:
            return f"a video of {en_w}"
    # Dernier recours : nom catégorie FR
    return f"a video of {cat_name_fr.lower()}"


def main():
    targets = sys.argv[1:]  # IDs a filtrer (optionnel)

    print(f"[INFO] Loading X-CLIP {MODEL_NAME}...")
    proc = XCLIPProcessor.from_pretrained(MODEL_NAME)
    model = XCLIPModel.from_pretrained(MODEL_NAME)
    print("[OK] Model loaded")

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    translations = {"categories": {}}
    if os.path.exists(TR_PATH):
        with open(TR_PATH, "r", encoding="utf-8") as f:
            translations = json.load(f)

    cats = data["categories"]
    if targets:
        cats = [c for c in cats if c["id"] in set(targets)]
        print(f"[INFO] Filtre sur {len(cats)} IDs")
    else:
        print(f"[INFO] Validation {len(cats)} categories")

    results = []
    suspect_ids = []

    for ci, cat in enumerate(cats):
        cat_result = {"id": cat["id"], "name": cat["name"], "videos": []}
        cat_suspect = False
        for vi, video in enumerate(cat["videos"][:2]):
            src = os.path.join(ROOT, video["url"])
            if not os.path.exists(src):
                cat_result["videos"].append({"title": video["title"], "error": "missing"})
                cat_suspect = True
                continue
            try:
                frames = read_video_frames(src, num_frames=8)
                if len(frames) < 8:
                    cat_result["videos"].append({"title": video["title"], "error": f"only_{len(frames)}_frames"})
                    cat_suspect = True
                    continue

                expected = get_en_label(cat["id"], vi, cat["name"], video["title"], translations)
                labels = [expected] + NEGATIVE_LABELS
                inputs = proc(text=labels, videos=list(frames), return_tensors="pt", padding=True)
                with torch.no_grad():
                    out = model(**inputs)
                probs = out.logits_per_video[0].softmax(dim=-1).numpy()

                top_idx = int(probs.argmax())
                top_pct = float(probs[top_idx] * 100)
                expected_pct = float(probs[0] * 100)
                top_label = labels[top_idx]

                video_result = {
                    "title": video["title"],
                    "expected_label": expected,
                    "expected_pct": round(expected_pct, 1),
                    "top_label": top_label,
                    "top_pct": round(top_pct, 1),
                }
                # SUSPECT si top != expected, OU si expected < 25%
                if top_idx != 0 or expected_pct < 25.0:
                    video_result["verdict"] = "SUSPECT"
                    cat_suspect = True
                else:
                    video_result["verdict"] = "OK"

                cat_result["videos"].append(video_result)
            except Exception as e:
                cat_result["videos"].append({"title": video["title"], "error": str(e)})
                cat_suspect = True

        cat_result["suspect"] = cat_suspect
        if cat_suspect:
            suspect_ids.append(cat["id"])
        results.append(cat_result)
        print(f"  [{ci+1}/{len(cats)}] {cat['id']:25s} {'SUSPECT' if cat_suspect else 'OK'}")

    out = {
        "total": len(cats),
        "suspect_count": len(suspect_ids),
        "suspect_ids": suspect_ids,
        "details": results,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] {len(suspect_ids)}/{len(cats)} SUSPECT")
    print(f"[DONE] Details dans {OUT_JSON}")
    print(f"[DONE] Suspects : {', '.join(suspect_ids[:20])}{'...' if len(suspect_ids) > 20 else ''}")


if __name__ == "__main__":
    main()
