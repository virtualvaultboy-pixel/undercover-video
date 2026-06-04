"""Purge round 5 : 13 nouvelles paires Pexels pack 2 avec match faible."""
import os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
TR_PATH = os.path.join(ROOT, "data", "translations.json")

FLAGGED_R5 = {
    "fruit-jaune",       # ananas = gateau
    "legume-orange",     # citrouille = tomates rouges
    "plat-asiatique",    # sushi = boulette de pate
    "snack-sale",        # popcorn = ours en peluche
    "felin-sauvage",     # lion = biche/gazelle
    "oiseau-cour",       # dinde = chinchilla blanc
    "sport-precision",   # tir a l'arc pas convaincant
    "lecture-activite",  # journal = mec qui boit cafe
    "cuisine-activite",  # Melanger : frame extract failed (no thumb)
    "accessoire-cou",    # foulard = femme voilee (pas accessoire decoratif)
    "audio-musique",     # enceinte = mecs dans salle
    "photo-cam",         # camescope = mains avec objet vert
    "meteo-violent",     # tornade = silhouettes arbres pas claire
}

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    removed, kept, files_removed = [], [], 0
    for cat in data["categories"]:
        if cat["id"] in FLAGGED_R5:
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
