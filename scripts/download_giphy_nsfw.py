"""
Ajoute des paires de GIFs humour soiree adulte (rating "r" Giphy).
Marque chaque categorie avec "nsfw": true dans videos.json.
Usage: python download_giphy_nsfw.py <GIPHY_API_KEY>
"""
import sys
import json
import os
import urllib.request
import urllib.parse

if len(sys.argv) < 2:
    print("Usage: python download_giphy_nsfw.py <GIPHY_API_KEY>")
    sys.exit(1)

API_KEY = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(ROOT, "videos", "nsfw")  # ARCHITECTURE MODULAIRE: dossier separe
JSON_PATH = os.path.join(ROOT, "data", "videos-nsfw.json")  # fichier separe
os.makedirs(VIDEOS_DIR, exist_ok=True)

# Paires NSFW - rating "r" sur Giphy = adulte mais pas X (suggestif, humour soiree)
NSFW_PAIRS = [
    {"id": "nsfw-soiree-bourree", "name": "Soirée arrosée", "emoji": "🍻",
     "items": [("beer pong party", "Beer pong"), ("flip cup drinking", "Flip cup")]},
    {"id": "nsfw-shot", "name": "Shot d'alcool fort", "emoji": "🥃",
     "items": [("tequila shot lime", "Shot tequila"), ("vodka shot bar", "Shot vodka")]},
    {"id": "nsfw-avant-apres", "name": "Avant/après alcool", "emoji": "🥴",
     "items": [("sober person classy", "Sobre"), ("drunk dancing chaos", "Bourré")]},
    {"id": "nsfw-gueule-bois", "name": "Gueule de bois", "emoji": "🤢",
     "items": [("hangover headache morning", "Mal de tête"), ("vomit toilet drunk", "Vomi")]},
    {"id": "nsfw-pole-dance", "name": "Pole dance", "emoji": "💃",
     "items": [("pole dance spin", "Pole dance"), ("lap dance club", "Lap dance")]},
    {"id": "nsfw-twerk", "name": "Twerk", "emoji": "🍑",
     "items": [("twerk solo", "Twerk solo"), ("booty drop crew", "Booty crew")]},
    {"id": "nsfw-tinder", "name": "Mood Tinder", "emoji": "💘",
     "items": [("swipe right tinder", "Swipe right"), ("tinder match notification", "Match!")]},
    {"id": "nsfw-drag-queen", "name": "Drag show", "emoji": "👑",
     "items": [("drag queen vogue dance", "Drag queen"), ("burlesque show dancer", "Burlesque")]},
    {"id": "nsfw-cliche-fruit", "name": "Fruit suggestif", "emoji": "🍒",
     "items": [("cherry pop sweet", "Cerise"), ("peach squeeze juicy", "Pêche")]},
    {"id": "nsfw-cliche-legume", "name": "Légume suggestif", "emoji": "🥒",
     "items": [("cucumber slice funny", "Concombre"), ("banana peel funny", "Banane")]},
    {"id": "nsfw-strip", "name": "Strip", "emoji": "👙",
     "items": [("strip tease dance", "Strip tease"), ("striptease pole money", "Stripper")]},
    {"id": "nsfw-sextoy", "name": "Sexy fruit slo-mo", "emoji": "🍆",
     "items": [("eggplant water drop", "Aubergine"), ("banana cream", "Banane")]},
    {"id": "nsfw-make-out", "name": "Make out", "emoji": "💋",
     "items": [("make out couple", "French kiss"), ("slow dance close", "Slow couple")]},
    {"id": "nsfw-meme-bro", "name": "Bro humor", "emoji": "🍺",
     "items": [("beer chug bro", "Boire cul sec"), ("burp loud funny", "Rot")]},
    {"id": "nsfw-mariage-cliche", "name": "Cliché mariage", "emoji": "👰",
     "items": [("garter toss wedding", "Jarretière"), ("bouquet toss bride", "Bouquet")]},
    {"id": "nsfw-bouteille-bar", "name": "Bouteille de bar", "emoji": "🍾",
     "items": [("champagne shower club", "Champagne spray"), ("vodka bottle bar service", "Bouteille bar")]},
    {"id": "nsfw-fail-bourre", "name": "Fail bourré", "emoji": "🤡",
     "items": [("drunk fall ground", "Chute"), ("drunk dance fail", "Danse fail")]},
    {"id": "nsfw-tenue-sexy", "name": "Tenue sexy", "emoji": "👗",
     "items": [("cocktail dress night", "Robe cocktail"), ("mini skirt outfit", "Mini jupe")]},
    {"id": "nsfw-summer-body", "name": "Body d'été", "emoji": "🏖️",
     "items": [("bikini beach summer", "Bikini plage"), ("swimsuit pool party", "Maillot piscine")]},
    {"id": "nsfw-muscle", "name": "Muscle show", "emoji": "💪",
     "items": [("bodybuilder flex pose", "Bodybuilder"), ("six pack abs gym", "Tablette choco")]},
    {"id": "nsfw-flirt-meme", "name": "Flirt meme", "emoji": "😏",
     "items": [("wink flirt meme", "Clin d'oeil"), ("tongue out lick lips", "Lèche-babines")]},
    {"id": "nsfw-langoureux", "name": "Regard langoureux", "emoji": "👀",
     "items": [("eye contact seductive", "Regard chaud"), ("biting lip flirt", "Mordre lèvre")]},
    {"id": "nsfw-rideau-rouge", "name": "Cabaret", "emoji": "🎭",
     "items": [("cabaret feather dance", "Cabaret plumes"), ("moulin rouge can can", "Can-can")]},
    {"id": "nsfw-onlyfans", "name": "Mood Onlyfans", "emoji": "📸",
     "items": [("selfie mirror outfit", "Selfie miroir"), ("lingerie photoshoot", "Lingerie photo")]},
    {"id": "nsfw-shotgun", "name": "Shotgun de bière", "emoji": "🥫",
     "items": [("shotgun beer can", "Shotgun bière"), ("keg stand party", "Keg stand")]},
]


def search_giphy(query):
    """Cherche un GIF rating R (adulte mais pas X) correspondant a la query."""
    url = f"https://api.giphy.com/v1/gifs/search?api_key={API_KEY}&q={urllib.parse.quote(query)}&limit=8&rating=r"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 UndercoverApp"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())

    if not data.get("data"):
        return None

    for gif in data["data"]:
        images = gif.get("images", {})
        original = images.get("original", {})
        mp4_url = original.get("mp4")
        if mp4_url:
            return mp4_url
        if original.get("url") and original["url"].endswith(".gif"):
            return original["url"].replace(".gif", ".mp4")
    return None


def download(url, dest):
    print(f"  -> download {os.path.basename(dest)}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
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

    for pair in NSFW_PAIRS:
        if pair["id"] in existing_ids:
            print(f"\n[SKIP] {pair['name']} deja present")
            continue

        print(f"\n=== {pair['name']} ===")
        videos = []
        for i, (query, title) in enumerate(pair["items"]):
            print(f"  [{i+1}] {query!r}")
            link = search_giphy(query)
            if not link:
                print(f"  [!] Pas de resultat, skip.")
                continue
            # Retire le prefixe "nsfw-" du nom (le dossier nsfw/ est deja explicite)
            clean_id = pair['id'][len('nsfw-'):] if pair['id'].startswith('nsfw-') else pair['id']
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
                print(f"  [X] Erreur : {e}")

        if len(videos) >= 2:
            # Toutes les categories de videos-nsfw.json sont marquees nsfw=true
            # par app.js au chargement. Inutile de le repeter dans le JSON.
            data["categories"].append({
                "id": pair["id"],
                "name": pair["name"],
                "emoji": pair["emoji"],
                "videos": videos,
            })

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Total: {len(data['categories'])} categories dans videos.json")
    nsfw_count = sum(1 for c in data["categories"] if c.get("nsfw"))
    print(f"     Dont {nsfw_count} NSFW")


if __name__ == "__main__":
    main()
