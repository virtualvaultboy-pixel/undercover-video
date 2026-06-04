"""
Purge des paires que l'utilisateur a flagged visuellement
(via preview.html / audit.html).
"""
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
TR_PATH = os.path.join(ROOT, "data", "translations.json")

FLAGGED = {
    "slow-motion",       # Eclat d'eau pas d'eau
    "combattant",        # Ninja en double
    "felin-sauvage",     # Leopard pas reconnaissable
    "catastrophe",       # Tornade pas bonne (ours qui fait pipi)
    "boisson-fete",      # Pas de champagne
    "metier-uniforme",   # Policier pas identifiable
    "legume-vert",       # Pas d'epinard (texte uniquement)
    "cuisine-indienne",  # Trop specifique
    "boisson-froide",    # Limonade + The glace incomprehensibles
    "oiseau-proie",      # Faucon = Eid Mubarak
    "accessoire-poignet",# Bracelet = texte rose
    "lecture",           # Magazine = skateboard
    "couvre-chef",       # Chapeau = mec random
}


def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    removed, kept, files_removed = [], [], 0
    for cat in data["categories"]:
        if cat["id"] in FLAGGED:
            removed.append(cat["id"])
            for v in cat["videos"]:
                p = os.path.join(ROOT, v.get("url", ""))
                if os.path.exists(p):
                    os.remove(p)
                    files_removed += 1
        else:
            kept.append(cat)

    data["categories"] = kept
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    if os.path.exists(TR_PATH):
        with open(TR_PATH, "r", encoding="utf-8") as f:
            tr = json.load(f)
        for cid in removed:
            tr["categories"].pop(cid, None)
        with open(TR_PATH, "w", encoding="utf-8") as f:
            json.dump(tr, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(removed)} categories user-flagged retirees")
    print(f"[OK] {files_removed} fichiers MP4 supprimes")
    print(f"[OK] {len(kept)} categories restantes")


if __name__ == "__main__":
    main()
