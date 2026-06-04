"""Purge round 4 : 3 nouvelles paires Pexels avec match faible."""
import os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
TR_PATH = os.path.join(ROOT, "data", "translations.json")

FLAGGED_R4 = {
    "informatique-input",  # Souris Pexels = livre rouge avec stylo
    "literie-moelleux",    # Oreiller et coussin trop flous/abstraits
    "ustensile-creux",     # Louche invisible (vue de dessus assiette)
}

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    removed, kept, files_removed = [], [], 0
    for cat in data["categories"]:
        if cat["id"] in FLAGGED_R4:
            removed.append(cat["id"])
            for v in cat["videos"]:
                p = os.path.join(ROOT, v.get("url", ""))
                if os.path.exists(p):
                    os.remove(p); files_removed += 1
        else:
            kept.append(cat)
    data["categories"] = kept
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    if os.path.exists(TR_PATH):
        with open(TR_PATH, "r", encoding="utf-8") as f: tr = json.load(f)
        for cid in removed: tr.get("categories", {}).pop(cid, None)
        with open(TR_PATH, "w", encoding="utf-8") as f:
            json.dump(tr, f, ensure_ascii=False, indent=2)
    print(f"[OK] {len(removed)} retirees, {files_removed} MP4, {len(kept)} restantes")

if __name__ == "__main__":
    main()
