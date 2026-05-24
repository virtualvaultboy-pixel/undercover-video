"""
Télécharge des paires de vidéos Pexels et génère un fragment videos.json.
Utilisation : python download_pexels.py <API_KEY>
"""
import sys
import json
import os
import urllib.request
import urllib.parse

if len(sys.argv) < 2:
    print("Usage: python download_pexels.py <PEXELS_API_KEY>")
    sys.exit(1)

API_KEY = sys.argv[1]
VIDEOS_DIR = os.path.join(os.path.dirname(__file__), "..", "videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)

# Paires : "proches mais différentes" — même famille, sujet distinct
PAIRS = [
    {"id": "animal-compagnie", "name": "Animal de compagnie", "emoji": "🐾",
     "items": [
         ("cat closeup", "Chat"),
         ("dog closeup", "Chien"),
     ]},
    {"id": "boisson-chaude", "name": "Boisson chaude", "emoji": "☕",
     "items": [
         ("pouring coffee", "Café versé"),
         ("pouring tea", "Thé versé"),
     ]},
    {"id": "agrume", "name": "Agrume coupé", "emoji": "🍊",
     "items": [
         ("orange slice", "Orange"),
         ("lemon slice", "Citron"),
     ]},
    {"id": "fleur", "name": "Fleur", "emoji": "🌷",
     "items": [
         ("rose flower", "Rose"),
         ("tulip flower", "Tulipe"),
     ]},
    {"id": "vehicule", "name": "Véhicule en mouvement", "emoji": "🚗",
     "items": [
         ("car driving road", "Voiture"),
         ("motorcycle riding road", "Moto"),
     ]},
    {"id": "eau", "name": "Élément d'eau", "emoji": "💧",
     "items": [
         ("ocean waves", "Vagues"),
         ("waterfall", "Cascade"),
     ]},
]


def search_pexels(query: str):
    """Cherche 1 vidéo correspondant à la query, retourne l'URL de la meilleure variante."""
    url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&per_page=3&orientation=portrait"
    req = urllib.request.Request(url, headers={"Authorization": API_KEY, "User-Agent": "Mozilla/5.0 UndercoverApp"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())

    if not data.get("videos"):
        # Fallback sans orientation portrait
        url2 = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&per_page=3"
        req2 = urllib.request.Request(url2, headers={"Authorization": API_KEY})
        with urllib.request.urlopen(req2, timeout=30) as r2:
            data = json.loads(r2.read())

    if not data.get("videos"):
        return None, None

    # Préférer une vidéo courte (≤15s)
    videos = sorted(data["videos"], key=lambda v: abs(v.get("duration", 30) - 8))
    video = videos[0]

    # Choisir un fichier MP4 raisonnable : largeur entre 480 et 720
    files = [f for f in video["video_files"] if f["file_type"] == "video/mp4"]
    files = sorted(files, key=lambda f: abs(f["width"] - 540))
    if not files:
        return None, None
    return files[0]["link"], video["duration"]


def download(url: str, dest: str):
    print(f"  -> download {dest}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())
    size_kb = os.path.getsize(dest) // 1024
    print(f"    {size_kb} KB")


def main():
    categories = []
    for pair in PAIRS:
        print(f"\n=== {pair['name']} ===")
        videos = []
        for i, (query, title) in enumerate(pair["items"]):
            print(f"  [{i+1}] {query!r}")
            link, dur = search_pexels(query)
            if not link:
                print(f"  [!] Pas de resultat pour {query!r}, skip.")
                continue
            filename = f"{pair['id']}_{i+1}.mp4"
            dest = os.path.join(VIDEOS_DIR, filename)
            try:
                download(link, dest)
                videos.append({
                    "source": "local",
                    "url": f"videos/{filename}",
                    "title": title,
                    "duration": dur,
                })
            except Exception as e:
                print(f"  [X] Erreur telechargement : {e}")

        if len(videos) >= 2:
            categories.append({
                "id": pair["id"],
                "name": pair["name"],
                "emoji": pair["emoji"],
                "videos": videos,
            })

    # Écrire le JSON final
    output = {"categories": categories}
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "videos.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] {len(categories)} categories ecrites dans data/videos.json")


if __name__ == "__main__":
    main()
