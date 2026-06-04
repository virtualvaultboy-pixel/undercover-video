"""Purge round 6 : 9 paires flaguees par audit multi-frame V2 (agent)."""
import os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
TR_PATH = os.path.join(ROOT, "data", "translations.json")

FLAGGED_R6 = {
    "danse-urbaine",     # Hip-hop vs Breakdance trop similaires
    "magie-cartoon",     # cartoon pas identifiable
    "macro-insecte",     # sujets flous
    "protection-meteo",  # meme texte "AN UMBRELLA" repete (confirme visuellement)
    "sport-glace",       # hockey pas clair vs patinage
    "couvert-repas",     # couteau/fourchette peu lisibles
    "outils-menage",     # personnages flous, outils peu visibles
    "sport-fitness",     # musculation/pilates pas clairs
    "bijou",             # bague/collier trop similaires (gros plans)
}

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    removed, kept, files_removed = [], [], 0
    for cat in data["categories"]:
        if cat["id"] in FLAGGED_R6:
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
