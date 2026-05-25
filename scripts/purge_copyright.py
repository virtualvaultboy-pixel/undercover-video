"""
Purge les categories contenant du contenu copyrighte d'une marque.
- Retire les categories de data/videos.json
- Retire les traductions correspondantes de data/translations.json
- Supprime les fichiers MP4 associes dans videos/
"""
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(ROOT, "videos")
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
TR_PATH = os.path.join(ROOT, "data", "translations.json")

# Categories problematiques pour le copyright Play Store
COPYRIGHT_IDS = {
    "perso-jeuvideo",      # Pikachu / Mario (Nintendo, Game Freak)
    "sous-marin",          # SpongeBob / Patrick (Viacom)
    "vilain-dc",           # Joker / Riddler (Warner DC)
    "simpsons",            # Bart / Homer (Fox)
    "sonic-univers",       # Sonic / Tails (Sega)
    "jeu-retro",           # Tetris / Pac-Man (Tetris Holding, Bandai Namco)
    "personnage-disney",   # Mickey / Donald (Disney)
    "anti-heros",          # Deadpool / Venom (Marvel)
    "studio-ghibli",       # Totoro / Ponyo (Studio Ghibli)
    "personnage-marvel",   # Spider-Man / Hulk (Marvel)
    "manga-shonen",        # Naruto / Goku (Shueisha, Toei)
    "super-heros",         # Batman / Superman (DC Warner)
    "freres-mario",        # Mario / Luigi (Nintendo)
    "pokemon-starter",     # Carapuce / Bulbizarre (Nintendo, Game Freak)
    "meme-culte",          # Surprised Pikachu, Drake (Nintendo + droits perso)
    "doge-meme",           # Doge / Cheems (droits incertains, photos chien)
}


def main():
    # Charger videos.json
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    removed = []
    kept = []
    files_to_remove = []

    for cat in data["categories"]:
        if cat["id"] in COPYRIGHT_IDS:
            removed.append(cat["id"])
            for v in cat["videos"]:
                url = v.get("url", "")
                if url.startswith("videos/"):
                    files_to_remove.append(os.path.join(ROOT, url))
        else:
            kept.append(cat)

    data["categories"] = kept

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Purger les traductions
    with open(TR_PATH, "r", encoding="utf-8") as f:
        tr = json.load(f)
    for cid in removed:
        tr["categories"].pop(cid, None)
    with open(TR_PATH, "w", encoding="utf-8") as f:
        json.dump(tr, f, ensure_ascii=False, indent=2)

    # Supprimer les fichiers MP4
    for path in files_to_remove:
        if os.path.exists(path):
            os.remove(path)
            print(f"[RM]  {os.path.basename(path)}")

    print()
    print(f"[OK] {len(removed)} categories retirees:")
    for r in removed:
        print(f"  - {r}")
    print(f"[OK] {len(kept)} categories restantes dans videos.json")


if __name__ == "__main__":
    main()
