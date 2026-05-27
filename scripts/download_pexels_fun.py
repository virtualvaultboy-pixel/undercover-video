"""
Ajoute des paires de videos fun a videos.json (sans ecraser l'existant).
Usage: python download_pexels_fun.py <API_KEY>
"""
import sys
import json
import os
import urllib.request
import urllib.parse

if len(sys.argv) < 2:
    print("Usage: python download_pexels_fun.py <PEXELS_API_KEY>")
    sys.exit(1)

API_KEY = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(ROOT, "videos")
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
os.makedirs(VIDEOS_DIR, exist_ok=True)

FUN_PAIRS = [
    {"id": "sport-extreme", "name": "Sport extreme", "emoji": "🛹",
     "items": [
         ("skateboard trick", "Skate trick"),
         ("bmx trick", "BMX trick"),
     ]},
    {"id": "spectacle-nuit", "name": "Spectacle nocturne", "emoji": "🎆",
     "items": [
         ("fireworks night", "Feu d'artifice"),
         ("lightning storm", "Orage"),
     ]},
    {"id": "slow-motion", "name": "Slow motion eclat", "emoji": "💥",
     "items": [
         ("water splash slow motion", "Eclat d'eau"),
         ("paint splash slow motion", "Eclat de peinture"),
     ]},
    {"id": "vue-aerienne", "name": "Vue aerienne", "emoji": "🚁",
     "items": [
         ("drone forest", "Drone foret"),
         ("drone ocean", "Drone ocean"),
     ]},
    {"id": "flammes", "name": "Flammes", "emoji": "🔥",
     "items": [
         ("campfire night", "Feu de camp"),
         ("candle flame close up", "Bougie"),
     ]},
    {"id": "danse-urbaine", "name": "Danse urbaine", "emoji": "🕺",
     "items": [
         ("hip hop dance", "Hip-hop"),
         ("breakdance", "Breakdance"),
     ]},
    # --- Pack 3 ---
    {"id": "animal-majestueux", "name": "Animal majestueux", "emoji": "🦅",
     "items": [
         ("eagle flying", "Aigle"),
         ("wolf howling", "Loup"),
     ]},
    {"id": "ville-nuit", "name": "Ville la nuit", "emoji": "🌃",
     "items": [
         ("tokyo neon night", "Tokyo"),
         ("new york night", "New York"),
     ]},
    # --- Pack 7 ---
    {"id": "paysage-montagne", "name": "Paysage de montagne", "emoji": "🏔️",
     "items": [
         ("snow mountain peak", "Montagne enneigee"),
         ("mountain forest valley", "Vallee verte"),
     ]},
    {"id": "espace-cosmos", "name": "Espace cosmique", "emoji": "🌠",
     "items": [
         ("galaxy stars cosmos", "Galaxie"),
         ("planet earth space", "Planete"),
     ]},
    {"id": "fast-cooking", "name": "Cuisine rapide", "emoji": "🍔",
     "items": [
         ("chef cooking pan flame", "Cuisson poele"),
         ("dough kneading bread", "Petrissage pate"),
     ]},
    {"id": "macro-insecte", "name": "Macro insecte", "emoji": "🪲",
     "items": [
         ("bee flower macro", "Abeille fleur"),
         ("butterfly wings macro", "Papillon ailes"),
     ]},
    {"id": "course-vitesse", "name": "Course de vitesse", "emoji": "🏎️",
     "items": [
         ("formula car race track", "Voiture course"),
         ("motorcycle race speed", "Moto course"),
     ]},
]


def search_pexels(query):
    url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&per_page=5&orientation=portrait"
    req = urllib.request.Request(url, headers={"Authorization": API_KEY, "User-Agent": "Mozilla/5.0 UndercoverApp"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())

    if not data.get("videos"):
        url2 = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&per_page=5"
        req2 = urllib.request.Request(url2, headers={"Authorization": API_KEY, "User-Agent": "Mozilla/5.0 UndercoverApp"})
        with urllib.request.urlopen(req2, timeout=30) as r2:
            data = json.loads(r2.read())

    if not data.get("videos"):
        return None, None

    # Filtrer vid trop longues (>20s pour eviter les enormes fichiers)
    candidates = [v for v in data["videos"] if v.get("duration", 0) <= 20]
    if not candidates:
        candidates = data["videos"]
    candidates = sorted(candidates, key=lambda v: abs(v.get("duration", 30) - 8))
    video = candidates[0]

    files = [f for f in video["video_files"] if f["file_type"] == "video/mp4"]
    files = sorted(files, key=lambda f: abs(f["width"] - 540))
    if not files:
        return None, None
    return files[0]["link"], video["duration"]


def download(url, dest):
    print(f"  -> download {dest}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())
    size_kb = os.path.getsize(dest) // 1024
    print(f"    {size_kb} KB")


def main():
    # Charger JSON existant
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"categories": []}

    existing_ids = {c["id"] for c in data["categories"]}

    for pair in FUN_PAIRS:
        if pair["id"] in existing_ids:
            print(f"\n[SKIP] {pair['name']} deja present")
            continue

        print(f"\n=== {pair['name']} ===")
        videos = []
        for i, (query, title) in enumerate(pair["items"]):
            print(f"  [{i+1}] {query!r}")
            link, dur = search_pexels(query)
            if not link:
                print(f"  [!] Pas de resultat, skip.")
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
                print(f"  [X] Erreur : {e}")

        if len(videos) >= 2:
            data["categories"].append({
                "id": pair["id"],
                "name": pair["name"],
                "emoji": pair["emoji"],
                "videos": videos,
            })

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Total: {len(data['categories'])} categories dans videos.json")


if __name__ == "__main__":
    main()
