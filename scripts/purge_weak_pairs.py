"""
Purge des paires considerees trop eloignees ou trop incoherentes pour
le jeu Undercover. Le but du jeu = doute permanent. Si les 2 videos
sont trop differentes, l'undercover se fait griller en 1 phrase.

Audit manuel par le user et reviewer. Liste validee.
"""
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
TR_PATH = os.path.join(ROOT, "data", "translations.json")
VIDEOS_DIR = os.path.join(ROOT, "videos")

WEAK_IDS = {
    "spectacle-nuit",        # Feu d'artifice / Orage - rien a voir
    "engin-volant",          # Voiture / Bateau volant - 2 vehicules eloignes
    "nourriture-vivante",    # Pizza / Banane qui danse - aliments eloignes
    "etre-etrange",          # Alien / Robot - pas de lien
    "reaction-sociale",      # Facepalm / Applaudissements - opposes
    "animal-majestueux",     # Aigle / Loup - oiseau vs mammifere
    "phenomene-ciel",        # Arc-en-ciel / Eclair - paisible vs violent
    "poisson",               # Poisson clown / Requin - taille opposee
    "legume",                # Carotte / Brocoli - doublon (Carotte ailleurs, Brocoli ailleurs)
    "pirate-mer",            # Pirate / Navire - personne vs objet
    "danse-classique",       # Ballet / Salsa - styles tres differents
    "paysage-montagne",      # Enneigee / Vallee verte - opposes
    "fast-cooking",          # Cuisson / Petrissage - actions differentes
    "fromage-charcuterie",   # Fromage / Charcuterie - 2 categories
    "insecte",               # Papillon / Abeille - DOUBLON de macro-insecte
    "activite-matin",        # Jogging / Yoga - trop differents
    "art-corporel",          # Nail art / Tatouage - lieux differents
    "activite-quotidienne",  # Dormir / Se reveiller - opposes
}


def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    removed = []
    kept = []
    files_removed = 0

    for cat in data["categories"]:
        if cat["id"] in WEAK_IDS:
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

    # Maj translations.json
    if os.path.exists(TR_PATH):
        with open(TR_PATH, "r", encoding="utf-8") as f:
            tr = json.load(f)
        for cid in removed:
            tr["categories"].pop(cid, None)
        with open(TR_PATH, "w", encoding="utf-8") as f:
            json.dump(tr, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(removed)} categories faibles retirees:")
    for r in removed:
        print(f"  - {r}")
    print(f"[OK] {files_removed} fichiers MP4 supprimes")
    print(f"[OK] {len(kept)} categories solides restantes")


if __name__ == "__main__":
    main()
