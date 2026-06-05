"""Purge round 8 : vetement-homme (Costume/Blazer trop similaires)."""
import os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
TR_PATH = os.path.join(ROOT, "data", "translations.json")
FLAGGED = {"vetement-homme"}

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f: data = json.load(f)
    removed, kept, files = [], [], 0
    for cat in data["categories"]:
        if cat["id"] in FLAGGED:
            removed.append(cat["id"])
            for v in cat["videos"]:
                p = os.path.join(ROOT, v.get("url", ""))
                if os.path.exists(p): os.remove(p); files += 1
        else:
            kept.append(cat)
    data["categories"] = kept
    with open(JSON_PATH, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
    if os.path.exists(TR_PATH):
        with open(TR_PATH, "r", encoding="utf-8") as f: tr = json.load(f)
        for cid in removed: tr.get("categories", {}).pop(cid, None)
        with open(TR_PATH, "w", encoding="utf-8") as f: json.dump(tr, f, ensure_ascii=False, indent=2)
    print(f"[OK] {len(removed)} retirees, {files} MP4, {len(kept)} restantes")

if __name__ == "__main__":
    main()
