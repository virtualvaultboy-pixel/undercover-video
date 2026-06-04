"""Pack 3 : +30 paires Pexels nouveaux sujets."""
import sys
import json
import os
import time
import urllib.request
import urllib.parse

if len(sys.argv) < 2:
    print("Usage: python rebuild_pexels_pack3.py <PEXELS_API_KEY>")
    sys.exit(1)

API_KEY = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(ROOT, "videos")
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
TR_PATH = os.path.join(ROOT, "data", "translations.json")
os.makedirs(VIDEOS_DIR, exist_ok=True)

PAIRS = [
    # Cuisine
    ("viande-grillee", "Viande grillée", "🥩", [
        ("grilled steak meat closeup", "Steak", "Steak", "Bistec"),
        ("grilled chicken bbq", "Poulet grillé", "Grilled chicken", "Pollo a la parrilla"),
    ]),
    ("fromage", "Fromage", "🧀", [
        ("camembert cheese board", "Camembert", "Camembert", "Camembert"),
        ("parmesan cheese grated", "Parmesan", "Parmesan", "Parmesano"),
    ]),
    ("pates-italiennes", "Pâtes italiennes", "🍝", [
        ("spaghetti pasta plate", "Spaghetti", "Spaghetti", "Espaguetis"),
        ("tagliatelle pasta carbonara", "Tagliatelle", "Tagliatelle", "Tagliatelle"),
    ]),
    ("noix-graines", "Noix et graines", "🥜", [
        ("almonds nuts closeup", "Amandes", "Almonds", "Almendras"),
        ("peanuts roasted", "Cacahuètes", "Peanuts", "Cacahuetes"),
    ]),
    ("epice-cuisine", "Épice cuisine", "🌶️", [
        ("cinnamon sticks closeup", "Cannelle", "Cinnamon", "Canela"),
        ("paprika red spice powder", "Paprika", "Paprika", "Pimentón"),
    ]),
    ("legume-tubercule", "Légume tubercule", "🥔", [
        ("potatoes harvest", "Pomme de terre", "Potato", "Patata"),
        ("onion sliced cutting", "Oignon", "Onion", "Cebolla"),
    ]),
    # Nature
    ("fleur-jaune", "Fleur jaune", "🌻", [
        ("sunflower field summer", "Tournesol", "Sunflower", "Girasol"),
        ("yellow daisy flower", "Marguerite", "Daisy", "Margarita"),
    ]),
    ("arbre-feuille", "Arbre", "🌳", [
        ("oak tree autumn", "Chêne", "Oak tree", "Roble"),
        ("palm tree tropical beach", "Palmier", "Palm tree", "Palmera"),
    ]),
    # Animaux
    ("animal-foret", "Animal de forêt", "🦌", [
        ("deer forest closeup", "Cerf", "Deer", "Ciervo"),
        ("wild boar forest", "Sanglier", "Wild boar", "Jabalí"),
    ]),
    ("oiseau-nuit", "Oiseau de nuit", "🦉", [
        ("owl flying night", "Hibou", "Owl", "Búho"),
        ("bat flying cave", "Chauve-souris", "Bat", "Murciélago"),
    ]),
    ("amphibien", "Amphibien", "🐸", [
        ("frog closeup water", "Grenouille", "Frog", "Rana"),
        ("salamander wildlife forest", "Salamandre", "Salamander", "Salamandra"),
    ]),
    # Sports
    ("sport-glisse-eau", "Sport de glisse", "🏄", [
        ("surfing big waves", "Surf", "Surfing", "Surf"),
        ("wakeboard speed water", "Wakeboard", "Wakeboard", "Wakeboard"),
    ]),
    ("sport-velo", "Sport vélo", "🚵", [
        ("mountain biking trail", "VTT", "Mountain bike", "Bicicleta de montaña"),
        ("road cycling race", "Vélo route", "Road bike", "Bicicleta de carretera"),
    ]),
    ("danse-classique", "Danse classique", "🩰", [
        ("ballet dancer stage", "Ballet", "Ballet", "Ballet"),
        ("ballroom waltz couple", "Valse", "Waltz", "Vals"),
    ]),
    # Musique
    ("musique-classique", "Musique classique", "🎻", [
        ("violin playing closeup", "Violon", "Violin", "Violín"),
        ("cello musician orchestra", "Violoncelle", "Cello", "Violonchelo"),
    ]),
    ("musique-vent", "Musique à vent", "🎷", [
        ("saxophone jazz musician", "Saxophone", "Saxophone", "Saxofón"),
        ("trumpet musician playing", "Trompette", "Trumpet", "Trompeta"),
    ]),
    # Art
    ("art-mur", "Art mural", "🎨", [
        ("graffiti street art urban", "Graffiti", "Graffiti", "Grafiti"),
        ("mural wall painting outdoor", "Fresque", "Mural", "Mural"),
    ]),
    ("art-objet", "Art objet", "🏺", [
        ("sculpture marble museum", "Sculpture", "Sculpture", "Escultura"),
        ("pottery clay hands wheel", "Poterie", "Pottery", "Cerámica"),
    ]),
    # Transport
    ("transport-luxe", "Transport luxe", "🛥️", [
        ("limousine luxury black car", "Limousine", "Limousine", "Limusina"),
        ("yacht luxury sea sunset", "Yacht", "Yacht", "Yate"),
    ]),
    # Camping
    ("camping-nature", "Camping", "⛺", [
        ("camping tent forest", "Tente", "Tent", "Tienda"),
        ("campfire night woods sparks", "Feu de camp nuit", "Campfire", "Hoguera"),
    ]),
    # Tech
    ("ordinateur-cas", "Type d'ordinateur", "🖥️", [
        ("desktop computer monitor office", "PC fixe", "Desktop PC", "PC fijo"),
        ("gaming laptop rgb keyboard", "PC portable gaming", "Gaming laptop", "Portátil gaming"),
    ]),
    # Voyage
    ("voyage-monument", "Monument célèbre", "🗽", [
        ("eiffel tower paris day", "Tour Eiffel", "Eiffel tower", "Torre Eiffel"),
        ("colosseum rome ancient", "Colisée", "Colosseum", "Coliseo"),
    ]),
    # Météo
    ("phenomene-eau", "Phénomène d'eau", "🌊", [
        ("waterfall mountain cascade", "Cascade montagne", "Mountain waterfall", "Cascada"),
        ("geyser eruption iceland", "Geyser", "Geyser", "Géiser"),
    ]),
    # Hygiène
    ("hygiene-perso", "Hygiène", "🧴", [
        ("toothbrush teeth bathroom", "Brosse à dents", "Toothbrush", "Cepillo dental"),
        ("soap bar bubbles closeup", "Savon", "Soap", "Jabón"),
    ]),
    ("nettoyage-prod", "Produit ménager", "🧼", [
        ("dish soap kitchen sink suds", "Liquide vaisselle", "Dish soap", "Lavavajillas"),
        ("laundry detergent washing", "Lessive", "Laundry", "Detergente"),
    ]),
    # Bureau
    ("fourniture-bureau", "Fourniture bureau", "📎", [
        ("paperclips colorful desk", "Trombones", "Paperclips", "Clips"),
        ("stapler office paper", "Agrafeuse", "Stapler", "Grapadora"),
    ]),
    # Électroménager
    ("electromenager-pain", "Petit électroménager", "🍞", [
        ("toaster bread popping kitchen", "Grille-pain", "Toaster", "Tostadora"),
        ("microwave heating kitchen", "Micro-ondes", "Microwave", "Microondas"),
    ]),
    ("electromenager-froid", "Électroménager froid", "🧊", [
        ("refrigerator open kitchen modern", "Frigo", "Refrigerator", "Refrigerador"),
        ("freezer ice cube kitchen", "Congélateur", "Freezer", "Congelador"),
    ]),
    # Fêtes
    ("fete-religieuse", "Fête religieuse", "🎄", [
        ("christmas tree lights decoration", "Noël", "Christmas", "Navidad"),
        ("easter eggs basket colorful", "Pâques", "Easter", "Pascua"),
    ]),
    # Mer
    ("rivage-mer", "Rivage", "🏖️", [
        ("rocky cliff ocean waves", "Falaise", "Cliff", "Acantilado"),
        ("sandy beach sunset", "Plage sable", "Sandy beach", "Playa arena"),
    ]),
]

FALLBACK = {
    "wakeboard speed water": "wakeboarding",
    "wild boar forest": "wild pig",
    "salamander wildlife forest": "salamander",
    "ballroom waltz couple": "couple dancing",
    "geyser eruption iceland": "geyser water",
    "limousine luxury black car": "limousine",
    "paperclips colorful desk": "paperclips",
    "easter eggs basket colorful": "easter eggs",
    "yellow daisy flower": "daisy flower",
    "campfire night woods sparks": "campfire night",
    "cinnamon sticks closeup": "cinnamon",
    "saxophone jazz musician": "saxophone",
    "bat flying cave": "bat animal",
    "mural wall painting outdoor": "wall mural art",
    "freezer ice cube kitchen": "ice cubes freezer",
}


def search_pexels(query, orientation="portrait"):
    base = "https://api.pexels.com/videos/search?"
    params = f"query={urllib.parse.quote(query)}&per_page=5"
    if orientation: params += f"&orientation={orientation}"
    req = urllib.request.Request(base + params, headers={"Authorization": API_KEY, "User-Agent": "Mozilla/5.0 UndercoverApp"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  [!] HTTP {e}")
        return {"videos": []}


def pick_best_video(data, target_dur=8):
    videos = data.get("videos", [])
    if not videos: return None, None
    videos = sorted(videos, key=lambda v: abs(v.get("duration", 30) - target_dur))
    video = videos[0]
    files = [f for f in video.get("video_files", []) if f.get("file_type") == "video/mp4"]
    files = sorted(files, key=lambda f: abs(f.get("width", 0) - 540))
    if not files: return None, None
    return files[0]["link"], video.get("duration")


def find_video(query):
    for orient in ("portrait", None):
        data = search_pexels(query, orient)
        link, dur = pick_best_video(data)
        if link: return link, dur
    fb = FALLBACK.get(query)
    if fb:
        print(f"  [retry] -> {fb!r}")
        for orient in ("portrait", None):
            data = search_pexels(fb, orient)
            link, dur = pick_best_video(data)
            if link: return link, dur
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
    print(f"\n[DONE] +{added}, {skipped} skipped, {failed} echec | total {len(data['categories'])}")


if __name__ == "__main__":
    main()
