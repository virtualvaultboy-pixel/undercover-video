"""Purge round 7 : 15 paires flaguees par audit agent multi-frame V2 (153->138)."""
import os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
TR_PATH = os.path.join(ROOT, "data", "translations.json")

FLAGGED_R7 = {
    "eau",                # vagues/cascade quasi-identiques
    "halloween",          # citrouille + chauve-souris en cartoon
    "patisserie",         # donut/cupcake cartoons
    "engin-aerien",       # avion/helico en illustration enfantine
    "ours",               # ours brun cartoon + peluche au lieu de reels
    "reptile",            # serpent/crocodile illustrations
    "moyen-transport",    # une video = jeu video Mario avec texte
    "celebration",        # Scooby-Doo identifiable (copyright)
    "emoji-coeur",        # emojis stylises, trop abstrait
    "fete-evenement",     # texte "HAPPY BIRTHDAY" dominant
    "lunettes",           # illustrations cartoon
    "liquide-chaud",      # texte "it simmer it simmer" dominant
    "chaussure",          # image promo "SANDAL SEASON" avec texte
    "animal-calin",       # 2 videos koala quasi-identiques
    "sac-porter",         # 2 videos cabas quasi-identiques
}

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    removed, kept, files_removed = [], [], 0
    for cat in data["categories"]:
        if cat["id"] in FLAGGED_R7:
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
