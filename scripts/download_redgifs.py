"""
Telecharge des paires de videos NSFW niveau 2/3 (lingerie / topless / softcore)
depuis Redgifs.com. Ecrit dans videos-nsfw.json et videos/nsfw/.

ATTENTION: contenu pour adultes (18+) uniquement.
Le repo GitHub Pages peut etre supprime si signale.
Sauvegarde locale recommandee.
"""
import os
import json
import time
import urllib.request
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(ROOT, "videos", "nsfw")
JSON_PATH = os.path.join(ROOT, "data", "videos-nsfw.json")
os.makedirs(VIDEOS_DIR, exist_ok=True)

API = "https://api.redgifs.com/v2"
UA = "Mozilla/5.0 UndercoverApp"

# Paires Redgifs niveau 2/3 (tease, lingerie, softcore)
# Note: les termes sont choisis pour rester dans le softcore (pas de hardcore)
PAIRS = [
    {"id": "rg-lingerie-couleur", "name": "Lingerie couleur", "emoji": "👙",
     "items": [("red lingerie", "Lingerie rouge"), ("black lingerie", "Lingerie noire")]},
    {"id": "rg-tease-bain", "name": "Tease au bain", "emoji": "🛁",
     "items": [("bathtub tease", "Bain"), ("shower tease", "Douche")]},
    {"id": "rg-tease-lit", "name": "Tease au lit", "emoji": "🛏️",
     "items": [("bedroom tease", "Tease lit"), ("morning bed", "Reveil au lit")]},
    {"id": "rg-piscine", "name": "Au bord de la piscine", "emoji": "🏊‍♀️",
     "items": [("bikini pool", "Bikini piscine"), ("wet pool", "Mouille piscine")]},
    {"id": "rg-jeans", "name": "Jeans serre", "emoji": "👖",
     "items": [("tight jeans", "Jeans serre"), ("jean shorts", "Short jean")]},
    {"id": "rg-mini-jupe", "name": "Mini-jupe", "emoji": "👗",
     "items": [("mini skirt", "Mini-jupe"), ("pleated skirt", "Jupe plissee")]},
    {"id": "rg-collant", "name": "Bas / Collant", "emoji": "🧦",
     "items": [("fishnet stockings", "Bas resille"), ("thigh high stockings", "Bas hauts")]},
    {"id": "rg-sport-girl", "name": "Sport girl", "emoji": "🏋️‍♀️",
     "items": [("gym workout", "Salle de sport"), ("yoga pants", "Pantalon yoga")]},
    {"id": "rg-cosplay", "name": "Cosplay", "emoji": "🎭",
     "items": [("schoolgirl cosplay", "Ecoliere"), ("maid cosplay", "Servante")]},
    {"id": "rg-bouche-langue", "name": "Bouche et langue", "emoji": "👅",
     "items": [("tongue out", "Tirer la langue"), ("biting lip", "Mordre lèvre")]},
    {"id": "rg-tatouages", "name": "Tatouages", "emoji": "🖋️",
     "items": [("tattoo girl", "Tatouages"), ("tattooed back", "Dos tatoue")]},
    {"id": "rg-cheveux", "name": "Cheveux", "emoji": "💇‍♀️",
     "items": [("blonde girl", "Blonde"), ("brunette girl", "Brune")]},
    {"id": "rg-soutien-gorge", "name": "Soutien-gorge", "emoji": "🎀",
     "items": [("lace bra", "Soutien dentelle"), ("sports bra", "Sports bra")]},
    {"id": "rg-strip", "name": "Strip tease", "emoji": "👚",
     "items": [("undressing", "Deshabille"), ("clothes off", "Enleve haut")]},
    {"id": "rg-dos-nu", "name": "Dos nu", "emoji": "🦴",
     "items": [("backless", "Dos nu"), ("back arch", "Cambre")]},
    {"id": "rg-topless-couvert", "name": "Topless main", "emoji": "✋",
     "items": [("hand bra", "Main soutien"), ("handbra topless", "Cache poitrine")]},
    {"id": "rg-bikini-style", "name": "Style de bikini", "emoji": "👙",
     "items": [("micro bikini", "Micro bikini"), ("string bikini", "String bikini")]},
    {"id": "rg-couleur-cheveux", "name": "Couleur cheveux fun", "emoji": "🌈",
     "items": [("pink hair", "Cheveux roses"), ("blue hair", "Cheveux bleus")]},
    {"id": "rg-couette", "name": "Sous la couette", "emoji": "🌙",
     "items": [("under blanket", "Couette"), ("bedsheet wrap", "Drap")]},
    {"id": "rg-baillon-cliche", "name": "Mouvement classique", "emoji": "💋",
     "items": [("hair flip", "Cheveux flip"), ("over shoulder", "Par dessus epaule")]},
]


def get_token():
    req = urllib.request.Request(f"{API}/auth/temporary", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    return data["token"]


def search(token, query):
    """Retourne l'URL SD du 1er gif trending pour cette query."""
    url = f"{API}/gifs/search?search_text={urllib.parse.quote(query)}&order=trending&count=5"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    for gif in data.get("gifs", []):
        urls = gif.get("urls", {})
        # Preferer sd (mobile-friendly, plus leger) - fallback hd
        u = urls.get("sd") or urls.get("hd")
        if u:
            return u, gif.get("id")
    return None, None


def download(url, dest):
    print(f"  -> download {os.path.basename(dest)}")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://www.redgifs.com/"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())
    print(f"    {os.path.getsize(dest)//1024} KB")


def main():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"categories": []}

    existing_ids = {c["id"] for c in data["categories"]}
    token = get_token()
    print(f"[OK] Token Redgifs ({len(token)} chars)")

    for pair in PAIRS:
        if pair["id"] in existing_ids:
            print(f"\n[SKIP] {pair['name']} deja present")
            continue

        print(f"\n=== {pair['name']} ===")
        videos = []
        seen_ids = set()
        for i, (query, title) in enumerate(pair["items"]):
            print(f"  [{i+1}] {query!r}")
            # Petite pause entre requetes pour rester gentil avec l'API
            time.sleep(0.5)
            try:
                link, gif_id = search(token, query)
            except Exception as e:
                print(f"  [X] search failed: {e}")
                continue
            if not link or gif_id in seen_ids:
                print(f"  [!] pas de resultat utilisable")
                continue
            seen_ids.add(gif_id)

            clean_id = pair["id"][len("rg-"):] if pair["id"].startswith("rg-") else pair["id"]
            filename = f"{clean_id}_{i+1}.mp4"
            dest = os.path.join(VIDEOS_DIR, filename)
            try:
                download(link, dest)
                videos.append({
                    "source": "local",
                    "url": f"videos/nsfw/{filename}",
                    "title": title,
                })
            except Exception as e:
                print(f"  [X] Erreur download: {e}")

        if len(videos) >= 2:
            data["categories"].append({
                "id": pair["id"],
                "name": pair["name"],
                "emoji": pair["emoji"],
                "videos": videos,
            })

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Total: {len(data['categories'])} categories NSFW dans videos-nsfw.json")


if __name__ == "__main__":
    main()
