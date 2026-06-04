"""
Pack 2 : +40 paires Pexels supplementaires.
Sujets concrets jamais utilises encore. Sources stock pure (zero Giphy).

Usage : python rebuild_pexels_pack2.py <PEXELS_API_KEY>
"""
import sys
import json
import os
import time
import urllib.request
import urllib.parse

if len(sys.argv) < 2:
    print("Usage: python rebuild_pexels_pack2.py <PEXELS_API_KEY>")
    sys.exit(1)

API_KEY = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(ROOT, "videos")
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
TR_PATH = os.path.join(ROOT, "data", "translations.json")
os.makedirs(VIDEOS_DIR, exist_ok=True)

PAIRS = [
    # === FRUITS & LEGUMES ===
    ("fruit-rouge", "Fruit rouge", "🍓", [
        ("strawberry fresh closeup", "Fraise", "Strawberry", "Fresa"),
        ("raspberry fresh", "Framboise", "Raspberry", "Frambuesa"),
    ]),
    ("fruit-vert", "Fruit vert", "🥝", [
        ("kiwi fruit slice", "Kiwi", "Kiwi", "Kiwi"),
        ("green apple fresh", "Pomme verte", "Green apple", "Manzana verde"),
    ]),
    ("fruit-jaune", "Fruit jaune", "🍋", [
        ("lemon fresh slice", "Citron", "Lemon", "Limón"),
        ("pineapple slice", "Ananas", "Pineapple", "Piña"),
    ]),
    ("legume-vert", "Légume vert", "🥦", [
        ("broccoli fresh closeup", "Brocoli", "Broccoli", "Brócoli"),
        ("lettuce salad fresh", "Salade", "Lettuce", "Lechuga"),
    ]),
    ("legume-orange", "Légume orange", "🎃", [
        ("pumpkin orange autumn", "Citrouille", "Pumpkin", "Calabaza"),
        ("sweet potato kitchen", "Patate douce", "Sweet potato", "Batata"),
    ]),

    # === BOISSONS ===
    ("boisson-alcool", "Boisson alcoolisée", "🍺", [
        ("beer pouring glass", "Bière", "Beer", "Cerveza"),
        ("red wine pouring glass", "Vin", "Wine", "Vino"),
    ]),
    ("boisson-festive", "Boisson festive", "🥂", [
        ("champagne pouring celebration", "Champagne", "Champagne", "Champán"),
        ("whiskey glass ice", "Whisky", "Whiskey", "Whisky"),
    ]),

    # === CUISINE ===
    ("fast-food", "Fast food", "🍟", [
        ("french fries closeup", "Frites", "Fries", "Patatas fritas"),
        ("chicken nuggets fried", "Nuggets", "Nuggets", "Nuggets"),
    ]),
    ("plat-asiatique", "Plat asiatique", "🍣", [
        ("sushi roll closeup", "Sushi", "Sushi", "Sushi"),
        ("indian curry bowl", "Curry", "Curry", "Curry"),
    ]),
    ("dessert-cremeux", "Dessert crémeux", "🍮", [
        ("tiramisu dessert closeup", "Tiramisu", "Tiramisu", "Tiramisú"),
        ("creme brulee dessert", "Crème brûlée", "Creme brulee", "Crema catalana"),
    ]),
    ("snack-sale", "Snack salé", "🥨", [
        ("popcorn movie bucket", "Popcorn", "Popcorn", "Palomitas"),
        ("pretzel snack bread", "Bretzel", "Pretzel", "Pretzel"),
    ]),

    # === ANIMAUX ===
    ("equide", "Équidé", "🐴", [
        ("horse running field", "Cheval", "Horse", "Caballo"),
        ("donkey farm closeup", "Âne", "Donkey", "Burro"),
    ]),
    ("felin-sauvage", "Félin sauvage", "🦁", [
        ("lion roaring closeup", "Lion", "Lion", "León"),
        ("tiger walking jungle", "Tigre", "Tiger", "Tigre"),
    ]),
    ("poisson-aquarium", "Poisson", "🐟", [
        ("aquarium fish swimming", "Poisson rouge", "Goldfish", "Pez dorado"),
        ("tropical fish coral reef", "Poisson tropical", "Tropical fish", "Pez tropical"),
    ]),
    ("oiseau-cour", "Oiseau de cour", "🐓", [
        ("rooster crowing farm", "Coq", "Rooster", "Gallo"),
        ("turkey farm bird", "Dinde", "Turkey", "Pavo"),
    ]),
    ("insecte-volant", "Insecte volant", "🐝", [
        ("bee flower pollen closeup", "Abeille", "Bee", "Abeja"),
        ("dragonfly water closeup", "Libellule", "Dragonfly", "Libélula"),
    ]),

    # === SPORTS ===
    ("sport-equipe", "Sport d'équipe", "⚽", [
        ("soccer football match", "Foot", "Soccer", "Fútbol"),
        ("basketball court game", "Basket", "Basketball", "Baloncesto"),
    ]),
    ("sport-individuel", "Sport individuel", "🏃", [
        ("running marathon road", "Course", "Running", "Carrera"),
        ("yoga pose mat", "Yoga", "Yoga", "Yoga"),
    ]),
    ("sport-precision", "Sport de précision", "🎯", [
        ("golf swing player", "Golf", "Golf", "Golf"),
        ("archery bow arrow", "Tir à l'arc", "Archery", "Tiro con arco"),
    ]),
    ("sport-fitness", "Fitness", "💪", [
        ("gym workout dumbbells", "Musculation", "Weightlifting", "Pesas"),
        ("pilates exercise studio", "Pilates", "Pilates", "Pilates"),
    ]),

    # === ACTIVITES ===
    ("lecture-activite", "Lire", "📖", [
        ("reading book cozy", "Livre", "Book", "Libro"),
        ("reading newspaper morning", "Journal", "Newspaper", "Periódico"),
    ]),
    ("cuisine-activite", "Cuisiner", "👩‍🍳", [
        ("chopping vegetables knife", "Couper", "Chopping", "Cortar"),
        ("stirring pot cooking", "Mélanger", "Stirring", "Mezclar"),
    ]),
    ("jardinage", "Jardinage", "🌱", [
        ("planting flowers garden hands", "Planter", "Planting", "Plantar"),
        ("watering plants garden", "Arroser", "Watering", "Regar"),
    ]),
    ("travail-bureau", "Travail bureau", "💼", [
        ("typing laptop office", "Taper", "Typing", "Teclear"),
        ("writing notebook desk", "Écrire", "Writing", "Escribir"),
    ]),

    # === OBJETS PORTABLES ===
    ("accessoire-tete", "Couvre-chef", "🎩", [
        ("baseball cap fashion", "Casquette", "Cap", "Gorra"),
        ("fedora hat fashion", "Chapeau", "Hat", "Sombrero"),
    ]),
    ("accessoire-cou", "Accessoire de cou", "🧣", [
        ("silk scarf woman fashion", "Foulard", "Scarf", "Pañuelo"),
        ("necktie business knot", "Cravate", "Tie", "Corbata"),
    ]),
    ("bijou", "Bijou", "💍", [
        ("diamond ring closeup", "Bague", "Ring", "Anillo"),
        ("gold necklace chain", "Collier", "Necklace", "Collar"),
    ]),
    ("montre-objet", "Montre", "⌚", [
        ("wristwatch luxury closeup", "Montre", "Watch", "Reloj"),
        ("smartwatch wrist closeup", "Montre connectée", "Smartwatch", "Reloj inteligente"),
    ]),

    # === TECH ===
    ("ecran-info", "Écran info", "💻", [
        ("laptop screen typing", "Laptop", "Laptop", "Portátil"),
        ("tablet touchscreen", "Tablette", "Tablet", "Tableta"),
    ]),
    ("audio-musique", "Audio", "🎧", [
        ("headphones music listening", "Casque audio", "Headphones", "Auriculares"),
        ("bluetooth speaker portable", "Enceinte", "Speaker", "Altavoz"),
    ]),
    ("photo-cam", "Caméra", "📷", [
        ("camera dslr photographer", "Appareil photo", "Camera", "Cámara"),
        ("video camcorder vintage", "Caméscope", "Camcorder", "Videocámara"),
    ]),

    # === MAISON ===
    ("piece-maison", "Pièce maison", "🛋️", [
        ("modern living room interior", "Salon", "Living room", "Salón"),
        ("cozy bedroom interior", "Chambre", "Bedroom", "Dormitorio"),
    ]),
    ("piece-eau", "Pièce d'eau", "🛁", [
        ("bathroom modern interior", "Salle de bain", "Bathroom", "Baño"),
        ("kitchen modern interior", "Cuisine", "Kitchen", "Cocina"),
    ]),
    ("luminaire", "Luminaire", "💡", [
        ("table lamp interior", "Lampe", "Lamp", "Lámpara"),
        ("chandelier crystal", "Lustre", "Chandelier", "Lámpara de araña"),
    ]),

    # === VOYAGE ===
    ("vacances-hotel", "Vacances hôtel", "🏨", [
        ("hotel lobby luxury", "Lobby", "Lobby", "Vestíbulo"),
        ("hotel pool resort", "Piscine hôtel", "Hotel pool", "Piscina hotel"),
    ]),

    # === METEO ===
    ("meteo-pluvieuse", "Météo froide", "🌧️", [
        ("rain window drops closeup", "Pluie", "Rain", "Lluvia"),
        ("snow falling winter", "Neige", "Snow", "Nieve"),
    ]),
    ("meteo-violent", "Météo violente", "⛈️", [
        ("lightning storm sky", "Foudre", "Lightning", "Rayo"),
        ("tornado storm wind", "Tornade", "Tornado", "Tornado"),
    ]),

    # === NATURE ===
    ("paysage-montagne", "Paysage montagne", "🏔️", [
        ("mountain peak snow", "Montagne", "Mountain", "Montaña"),
        ("hill green sunset", "Colline", "Hill", "Colina"),
    ]),
    ("foret-nature", "Forêt", "🌲", [
        ("forest path sunlight", "Forêt jour", "Forest day", "Bosque día"),
        ("forest fog mystic", "Forêt brume", "Misty forest", "Bosque niebla"),
    ]),
    ("desert-nature", "Désert", "🏜️", [
        ("desert dunes sand", "Désert", "Desert", "Desierto"),
        ("oasis palm trees water", "Oasis", "Oasis", "Oasis"),
    ]),
]

FALLBACK = {
    "donkey farm closeup": "donkey animal",
    "creme brulee dessert": "creme dessert",
    "chicken nuggets fried": "fried chicken",
    "dragonfly water closeup": "dragonfly insect",
    "turkey farm bird": "turkey bird",
    "smartwatch wrist closeup": "smartwatch",
    "fedora hat fashion": "hat fashion",
    "chandelier crystal": "chandelier home",
    "indian curry bowl": "curry food",
    "hotel pool resort": "swimming pool resort",
    "tornado storm wind": "tornado",
    "tiger walking jungle": "tiger animal",
    "raspberry fresh": "raspberry",
    "rooster crowing farm": "rooster",
    "archery bow arrow": "archery",
    "pilates exercise studio": "pilates",
    "sweet potato kitchen": "sweet potato",
    "stirring pot cooking": "cooking pot",
    "tiramisu dessert closeup": "tiramisu",
    "diamond ring closeup": "ring jewelry",
    "video camcorder vintage": "vintage camera",
    "table lamp interior": "lamp light",
    "hill green sunset": "hill landscape",
}


def search_pexels(query, orientation="portrait"):
    base = "https://api.pexels.com/videos/search?"
    params = f"query={urllib.parse.quote(query)}&per_page=5"
    if orientation:
        params += f"&orientation={orientation}"
    req = urllib.request.Request(base + params, headers={"Authorization": API_KEY, "User-Agent": "Mozilla/5.0 UndercoverApp"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  [!] HTTP {e}")
        return {"videos": []}


def pick_best_video(data, target_dur=8):
    videos = data.get("videos", [])
    if not videos:
        return None, None
    videos = sorted(videos, key=lambda v: abs(v.get("duration", 30) - target_dur))
    video = videos[0]
    files = [f for f in video.get("video_files", []) if f.get("file_type") == "video/mp4"]
    files = sorted(files, key=lambda f: abs(f.get("width", 0) - 540))
    if not files:
        return None, None
    return files[0]["link"], video.get("duration")


def find_video(query):
    for orient in ("portrait", None):
        data = search_pexels(query, orient)
        link, dur = pick_best_video(data)
        if link:
            return link, dur
    fb = FALLBACK.get(query)
    if fb:
        print(f"  [retry] -> {fb!r}")
        for orient in ("portrait", None):
            data = search_pexels(fb, orient)
            link, dur = pick_best_video(data)
            if link:
                return link, dur
    return None, None


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())
    return os.path.getsize(dest)


def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    existing = {c["id"] for c in data["categories"]}
    print(f"[INFO] {len(existing)} existantes, +{len(PAIRS)} max")

    tr = {"categories": {}}
    if os.path.exists(TR_PATH):
        with open(TR_PATH, "r", encoding="utf-8") as f:
            tr = json.load(f)
    tr.setdefault("categories", {})

    added, skipped, failed = 0, 0, 0
    for pid, name, emoji, items in PAIRS:
        if pid in existing:
            print(f"[SKIP] {pid}")
            skipped += 1
            continue
        print(f"\n=== {pid} : {name} ===")
        videos, t_en, t_es = [], [], []
        for i, (q, t_fr, te, tes) in enumerate(items):
            print(f"  [{i+1}] {q!r}")
            link, dur = find_video(q)
            if not link:
                print(f"  [X] echec : {q!r}")
                continue
            filename = f"{pid}_{i+1}.mp4"
            dst = os.path.join(VIDEOS_DIR, filename)
            try:
                size = download(link, dst)
                print(f"      -> {filename} ({size // 1024} KB)")
                videos.append({"source": "local", "url": f"videos/{filename}", "title": t_fr, "duration": dur})
                t_en.append(te); t_es.append(tes)
            except Exception as e:
                print(f"  [X] dl err : {e}")
            time.sleep(0.3)

        if len(videos) >= 2:
            data["categories"].append({"id": pid, "name": name, "emoji": emoji, "videos": videos})
            tr["categories"][pid] = {
                "fr": {"name": name, "videos": [{"title": v["title"]} for v in videos]},
                "en": {"name": name, "videos": [{"title": t} for t in t_en]},
                "es": {"name": name, "videos": [{"title": t} for t in t_es]},
            }
            added += 1
            print(f"  [OK] {pid}")
        else:
            failed += 1
            for v in videos:
                p = os.path.join(ROOT, v["url"])
                if os.path.exists(p): os.remove(p)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(TR_PATH, "w", encoding="utf-8") as f:
        json.dump(tr, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] +{added} ajoutees, {skipped} skipped, {failed} echec")
    print(f"[DONE] Total : {len(data['categories'])} categories")


if __name__ == "__main__":
    main()
