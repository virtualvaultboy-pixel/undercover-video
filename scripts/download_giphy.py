"""
Ajoute des paires de GIFs/MP4 surrealistes depuis Giphy a videos.json.
Usage: python download_giphy.py <GIPHY_API_KEY>
"""
import sys
import json
import os
import urllib.request
import urllib.parse

if len(sys.argv) < 2:
    print("Usage: python download_giphy.py <GIPHY_API_KEY>")
    sys.exit(1)

API_KEY = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(ROOT, "videos")
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
os.makedirs(VIDEOS_DIR, exist_ok=True)

# Paires surreallistes / cartoon / fun
SURREAL_PAIRS = [
    {"id": "animal-danse", "name": "Animal qui danse", "emoji": "💃",
     "items": [
         ("cat dancing", "Chat qui danse"),
         ("dog dancing", "Chien qui danse"),
     ]},
    {"id": "engin-volant", "name": "Engin volant fantastique", "emoji": "🚀",
     "items": [
         ("flying car cartoon", "Voiture volante"),
         ("flying ship cartoon", "Bateau volant"),
     ]},
    {"id": "creature-mythique", "name": "Creature mythique", "emoji": "🦄",
     "items": [
         ("unicorn cartoon", "Licorne"),
         ("dragon cartoon", "Dragon"),
     ]},
    {"id": "magie-cartoon", "name": "Magie cartoon", "emoji": "🧙",
     "items": [
         ("wizard magic spell cartoon", "Magicien"),
         ("witch magic spell cartoon", "Sorciere"),
     ]},
    {"id": "nourriture-vivante", "name": "Nourriture qui bouge", "emoji": "🍕",
     "items": [
         ("dancing pizza", "Pizza qui danse"),
         ("dancing banana", "Banane qui danse"),
     ]},
    {"id": "reaction-meme", "name": "Reaction expressive", "emoji": "🤯",
     "items": [
         ("mind blown explosion", "Mind blown"),
         ("shocked surprised meme", "Choque"),
     ]},
    # --- Pack 2 ---
    {"id": "monstre-nuit", "name": "Monstre de la nuit", "emoji": "🧛",
     "items": [
         ("zombie cartoon", "Zombie"),
         ("vampire cartoon", "Vampire"),
     ]},
    {"id": "etre-etrange", "name": "Etre etrange", "emoji": "👽",
     "items": [
         ("alien cartoon", "Alien"),
         ("robot cartoon", "Robot"),
     ]},
    {"id": "animal-calin", "name": "Animal calin", "emoji": "🐼",
     "items": [
         ("panda cute", "Panda"),
         ("koala cute", "Koala"),
     ]},
    {"id": "super-heros", "name": "Super heros", "emoji": "🦸",
     "items": [
         ("batman cartoon", "Batman"),
         ("superman cartoon", "Superman"),
     ]},
    {"id": "halloween", "name": "Halloween", "emoji": "🎃",
     "items": [
         ("pumpkin halloween", "Citrouille"),
         ("bat halloween", "Chauve-souris"),
     ]},
    {"id": "reaction-sociale", "name": "Reaction sociale", "emoji": "🙄",
     "items": [
         ("facepalm meme", "Facepalm"),
         ("applause clapping", "Applaudissements"),
     ]},
    # --- Pack 3 ---
    {"id": "perso-jeuvideo", "name": "Personnage jeu video", "emoji": "🎮",
     "items": [
         ("pikachu pokemon", "Pikachu"),
         ("mario nintendo", "Mario"),
     ]},
    {"id": "combattant", "name": "Combattant japonais", "emoji": "🥷",
     "items": [
         ("ninja anime", "Ninja"),
         ("samurai anime", "Samourai"),
     ]},
    {"id": "emotion-forte", "name": "Emotion forte", "emoji": "😂",
     "items": [
         ("crying laughing", "Pleurer"),
         ("laughing hard", "Rire"),
     ]},
    {"id": "doge-meme", "name": "Chien meme", "emoji": "🐕",
     "items": [
         ("doge meme", "Doge"),
         ("cheems meme", "Cheems"),
     ]},
    # --- Pack 4 (gros) ---
    {"id": "sous-marin", "name": "Dessin anime sous-marin", "emoji": "🧽",
     "items": [
         ("spongebob", "SpongeBob"),
         ("patrick star spongebob", "Patrick"),
     ]},
    {"id": "vilain-dc", "name": "Vilain DC", "emoji": "🃏",
     "items": [
         ("joker dc", "Joker"),
         ("riddler dc", "Riddler"),
     ]},
    {"id": "simpsons", "name": "Famille Simpson", "emoji": "🍩",
     "items": [
         ("bart simpson", "Bart"),
         ("homer simpson", "Homer"),
     ]},
    {"id": "sonic-univers", "name": "Univers Sonic", "emoji": "🦔",
     "items": [
         ("sonic the hedgehog", "Sonic"),
         ("tails sonic", "Tails"),
     ]},
    {"id": "jeu-retro", "name": "Jeu retro", "emoji": "🕹️",
     "items": [
         ("tetris game", "Tetris"),
         ("pac man", "Pac-Man"),
     ]},
    {"id": "primate", "name": "Primate", "emoji": "🐒",
     "items": [
         ("monkey funny", "Singe"),
         ("gorilla funny", "Gorille"),
     ]},
    {"id": "petit-animal", "name": "Petit animal", "emoji": "🐰",
     "items": [
         ("rabbit cute", "Lapin"),
         ("hamster cute", "Hamster"),
     ]},
    {"id": "snack-rapide", "name": "Snack rapide", "emoji": "🌭",
     "items": [
         ("burger cartoon", "Burger"),
         ("hot dog cartoon", "Hot dog"),
     ]},
    {"id": "patisserie", "name": "Patisserie", "emoji": "🍰",
     "items": [
         ("donut cartoon", "Donut"),
         ("cupcake cartoon", "Cupcake"),
     ]},
    {"id": "sport-combat", "name": "Sport de combat", "emoji": "🥊",
     "items": [
         ("boxing punch", "Boxe"),
         ("karate kick", "Karate"),
     ]},
    {"id": "engin-aerien", "name": "Engin aerien", "emoji": "✈️",
     "items": [
         ("airplane cartoon", "Avion"),
         ("helicopter cartoon", "Helicoptere"),
     ]},
    {"id": "medical", "name": "Personnel medical", "emoji": "👨‍⚕️",
     "items": [
         ("doctor cartoon", "Docteur"),
         ("nurse cartoon", "Infirmiere"),
     ]},
    {"id": "metier-aventure", "name": "Metier d'aventure", "emoji": "🚀",
     "items": [
         ("pilot cartoon", "Pilote"),
         ("astronaut cartoon", "Astronaute"),
     ]},
    {"id": "catastrophe", "name": "Catastrophe naturelle", "emoji": "🌋",
     "items": [
         ("volcano eruption cartoon", "Volcan"),
         ("tornado cartoon", "Tornade"),
     ]},
    {"id": "phenomene-ciel", "name": "Phenomene celeste", "emoji": "🌈",
     "items": [
         ("rainbow cartoon", "Arc-en-ciel"),
         ("lightning cartoon", "Eclair"),
     ]},
]


def search_giphy(query):
    url = f"https://api.giphy.com/v1/gifs/search?api_key={API_KEY}&q={urllib.parse.quote(query)}&limit=5&rating=g"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 UndercoverApp"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())

    if not data.get("data"):
        return None

    # Premier resultat avec un MP4 dispo
    for gif in data["data"]:
        images = gif.get("images", {})
        original = images.get("original", {})
        mp4_url = original.get("mp4")
        if mp4_url:
            return mp4_url
        # Fallback: convertir le GIF en MP4 url
        if original.get("url") and original["url"].endswith(".gif"):
            return original["url"].replace(".gif", ".mp4")
    return None


def download(url, dest):
    print(f"  -> download {dest}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())
    size_kb = os.path.getsize(dest) // 1024
    print(f"    {size_kb} KB")


def main():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"categories": []}

    existing_ids = {c["id"] for c in data["categories"]}

    for pair in SURREAL_PAIRS:
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
            filename = f"{pair['id']}_{i+1}.mp4"
            dest = os.path.join(VIDEOS_DIR, filename)
            try:
                download(link, dest)
                videos.append({
                    "source": "local",
                    "url": f"videos/{filename}",
                    "title": title,
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
