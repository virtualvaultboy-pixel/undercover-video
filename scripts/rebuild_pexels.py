"""
Reconstitue les paires purgees (audit round 2) en re-telechargeant
uniquement depuis Pexels (vraies videos stock, pas de memes/stickers).

Ajoute les nouvelles paires SANS ecraser celles existantes dans
videos.json. Met aussi a jour translations.json (FR/EN/ES).

Usage : python rebuild_pexels.py <PEXELS_API_KEY>
"""
import sys
import json
import os
import time
import urllib.request
import urllib.parse

if len(sys.argv) < 2:
    print("Usage: python rebuild_pexels.py <PEXELS_API_KEY>")
    sys.exit(1)

API_KEY = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(ROOT, "videos")
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
TR_PATH = os.path.join(ROOT, "data", "translations.json")
os.makedirs(VIDEOS_DIR, exist_ok=True)

# Sujets a reconstituer : tous concrets, filmables, Pexels-friendly.
# Format : (id, name, emoji, [(query_pexels, title_fr, title_en, title_es), ...])
PAIRS = [
    # Cuisine - concret
    ("petit-dej", "Petit-déjeuner", "🥞", [
        ("pancakes stack", "Pancakes", "Pancakes", "Tortitas"),
        ("waffle breakfast", "Gaufres", "Waffles", "Gofres"),
    ]),
    ("patisserie-fine", "Pâtisserie fine", "🥐", [
        ("eclair pastry", "Éclair", "Eclair", "Pepito"),
        ("macaron french", "Macaron", "Macaron", "Macaron"),
    ]),
    ("fruit-exotique", "Fruit exotique", "🥭", [
        ("mango fruit closeup", "Mangue", "Mango", "Mango"),
        ("pineapple fruit", "Ananas", "Pineapple", "Piña"),
    ]),
    ("dessert-glace", "Dessert glacé", "🍧", [
        ("ice cream scoop", "Glace boule", "Ice cream", "Helado"),
        ("ice cream sundae", "Sundae", "Sundae", "Sundae"),
    ]),
    ("snack-rapide", "Snack rapide", "🍔", [
        ("burger fast food", "Burger", "Burger", "Hamburguesa"),
        ("hot dog street", "Hot dog", "Hot dog", "Perrito caliente"),
    ]),
    ("gourmand", "Sucrerie", "🍫", [
        ("chocolate melting", "Chocolat", "Chocolate", "Chocolate"),
        ("candy colorful", "Bonbons", "Candy", "Caramelos"),
    ]),
    ("fruit-pop", "Fruit populaire", "🍎", [
        ("apple red fresh", "Pomme", "Apple", "Manzana"),
        ("banana fresh", "Banane", "Banana", "Plátano"),
    ]),
    ("fruit-simple", "Fruit simple", "🍐", [
        ("pear fruit", "Poire", "Pear", "Pera"),
        ("peach fresh", "Pêche", "Peach", "Melocotón"),
    ]),
    ("plat-italien", "Plat italien", "🍝", [
        ("pasta cooking", "Pâtes", "Pasta", "Pasta"),
        ("pizza oven", "Pizza", "Pizza", "Pizza"),
    ]),
    ("boisson-chaude", "Boisson chaude", "☕", [
        ("coffee pouring cup", "Café", "Coffee", "Café"),
        ("tea pouring cup", "Thé", "Tea", "Té"),
    ]),
    ("boisson-tropicale", "Boisson tropicale", "🍹", [
        ("mojito cocktail", "Mojito", "Mojito", "Mojito"),
        ("pina colada cocktail", "Piña colada", "Pina colada", "Piña colada"),
    ]),
    ("boisson-fraiche", "Boisson fraîche", "🥤", [
        ("soda glass pouring", "Soda", "Soda", "Refresco"),
        ("orange juice glass", "Jus d'orange", "Orange juice", "Zumo de naranja"),
    ]),
    ("boulangerie", "Boulangerie", "🥖", [
        ("baguette bread french", "Baguette", "Baguette", "Baguette"),
        ("sliced bread loaf", "Pain de mie", "Sliced bread", "Pan de molde"),
    ]),
    ("racine-comestible", "Racine comestible", "🥕", [
        ("carrot fresh", "Carotte", "Carrot", "Zanahoria"),
        ("radish fresh", "Radis", "Radish", "Rábano"),
    ]),
    ("liquide-blanc", "Liquide blanc", "🥛", [
        ("milk pouring glass", "Lait", "Milk", "Leche"),
        ("yogurt spoon", "Yaourt", "Yogurt", "Yogur"),
    ]),

    # Animaux concrets
    ("animal-ferme", "Animal de ferme", "🐄", [
        ("cow farm", "Vache", "Cow", "Vaca"),
        ("pig farm", "Cochon", "Pig", "Cerdo"),
    ]),
    ("animal-ferme-2", "Volaille", "🐔", [
        ("chicken farm", "Poule", "Chicken", "Gallina"),
        ("duck pond", "Canard", "Duck", "Pato"),
    ]),
    ("animal-savane", "Animal de savane", "🦒", [
        ("giraffe wildlife", "Girafe", "Giraffe", "Jirafa"),
        ("elephant wildlife", "Éléphant", "Elephant", "Elefante"),
    ]),
    ("primate", "Primate", "🐒", [
        ("monkey jungle", "Singe", "Monkey", "Mono"),
        ("gorilla closeup", "Gorille", "Gorilla", "Gorila"),
    ]),
    ("animal-calin", "Animal câlin", "🐼", [
        ("panda eating", "Panda", "Panda", "Panda"),
        ("koala tree", "Koala", "Koala", "Koala"),
    ]),
    ("marin-mammif", "Mammifère marin", "🐬", [
        ("dolphin swimming", "Dauphin", "Dolphin", "Delfín"),
        ("whale ocean", "Baleine", "Whale", "Ballena"),
    ]),
    ("mammifere-marin-2", "Mammifère marin 2", "🦭", [
        ("seal beach", "Phoque", "Seal", "Foca"),
        ("sea lion ocean", "Otarie", "Sea lion", "León marino"),
    ]),
    ("reptile-lent", "Reptile lent", "🐢", [
        ("turtle sea", "Tortue", "Turtle", "Tortuga"),
        ("lizard closeup", "Lézard", "Lizard", "Lagarto"),
    ]),
    ("oiseau-tropical", "Oiseau tropical", "🦜", [
        ("parrot colorful", "Perroquet", "Parrot", "Loro"),
        ("toucan bird", "Toucan", "Toucan", "Tucán"),
    ]),
    ("creature-marine", "Créature marine", "🐙", [
        ("octopus underwater", "Pieuvre", "Octopus", "Pulpo"),
        ("jellyfish ocean", "Méduse", "Jellyfish", "Medusa"),
    ]),
    ("rongeur-mignon", "Petit rongeur", "🐹", [
        ("hamster eating", "Hamster", "Hamster", "Hámster"),
        ("squirrel park", "Écureuil", "Squirrel", "Ardilla"),
    ]),

    # Sports concrets
    ("sport-glace", "Sport de glace", "⛸️", [
        ("ice hockey game", "Hockey", "Hockey", "Hockey"),
        ("figure skating", "Patinage", "Skating", "Patinaje"),
    ]),
    ("sport-nautique", "Sport nautique", "⛵", [
        ("sailing boat sea", "Voile", "Sailing", "Vela"),
        ("kayak river", "Kayak", "Kayak", "Kayak"),
    ]),
    ("sport-hiver", "Sport d'hiver", "🎿", [
        ("skiing snow mountain", "Ski", "Skiing", "Esquí"),
        ("snowboarding mountain", "Snowboard", "Snowboard", "Snowboard"),
    ]),
    ("sport-raquette", "Sport de raquette", "🎾", [
        ("tennis match", "Tennis", "Tennis", "Tenis"),
        ("badminton player", "Badminton", "Badminton", "Bádminton"),
    ]),

    # Objets concrets
    ("outil-bricolage", "Outil de bricolage", "🔨", [
        ("hammer nail wood", "Marteau", "Hammer", "Martillo"),
        ("saw cutting wood", "Scie", "Saw", "Sierra"),
    ]),
    ("instrument-musique", "Instrument", "🎸", [
        ("guitar playing", "Guitare", "Guitar", "Guitarra"),
        ("piano playing keys", "Piano", "Piano", "Piano"),
    ]),
    ("outil-cuisine", "Ustensile cuisine", "🍳", [
        ("frying pan cooking", "Poêle", "Frying pan", "Sartén"),
        ("pot boiling cooking", "Casserole", "Pot", "Cacerola"),
    ]),
    ("couvert-repas", "Couvert", "🍴", [
        ("knife cutting food", "Couteau", "Knife", "Cuchillo"),
        ("fork eating pasta", "Fourchette", "Fork", "Tenedor"),
    ]),
    ("contenant-boisson", "Contenant à boisson", "🥛", [
        ("water glass clear", "Verre", "Glass", "Vaso"),
        ("coffee mug ceramic", "Tasse", "Mug", "Taza"),
    ]),
    ("boisson-fermee", "Boisson fermée", "🥤", [
        ("water bottle plastic", "Bouteille", "Bottle", "Botella"),
        ("soda can metal", "Canette", "Can", "Lata"),
    ]),
    ("sac-porter", "Sac à porter", "👜", [
        ("handbag fashion", "Sac à main", "Handbag", "Bolso"),
        ("tote bag market", "Cabas", "Tote bag", "Bolsa"),
    ]),
    ("bagage", "Bagage", "🧳", [
        ("backpack hiking travel", "Sac à dos", "Backpack", "Mochila"),
        ("suitcase airport rolling", "Valise", "Suitcase", "Maleta"),
    ]),
    ("informatique-input", "Périphérique ordi", "⌨️", [
        ("keyboard typing closeup", "Clavier", "Keyboard", "Teclado"),
        ("computer mouse desk", "Souris", "Mouse", "Ratón"),
    ]),
    ("haut-chaud", "Haut chaud", "🧥", [
        ("winter coat fashion", "Manteau", "Coat", "Abrigo"),
        ("leather jacket fashion", "Veste", "Jacket", "Chaqueta"),
    ]),
    ("haut-leger", "Haut léger", "👕", [
        ("white t-shirt fashion", "T-shirt", "T-shirt", "Camiseta"),
        ("blouse fashion woman", "Blouse", "Blouse", "Blusa"),
    ]),
    ("bas-long", "Bas long", "👖", [
        ("jeans denim fashion", "Jean", "Jeans", "Vaqueros"),
        ("trousers formal", "Pantalon", "Trousers", "Pantalón"),
    ]),
    ("siege", "Siège", "🪑", [
        ("wooden chair", "Chaise", "Chair", "Silla"),
        ("bar stool wooden", "Tabouret", "Stool", "Taburete"),
    ]),
    ("literie-moelleux", "Literie moelleuse", "🛏️", [
        ("pillow soft bed", "Oreiller", "Pillow", "Almohada"),
        ("cushion sofa decor", "Coussin", "Cushion", "Cojín"),
    ]),
    ("literie-couverture", "Couverture de lit", "🛌", [
        ("blanket knitted soft", "Couverture", "Blanket", "Manta"),
        ("white bed sheets", "Drap", "Sheet", "Sábana"),
    ]),
    ("mesure-temps", "Mesure du temps", "⏰", [
        ("alarm clock vintage", "Réveil", "Alarm clock", "Despertador"),
        ("wall clock ticking", "Horloge murale", "Wall clock", "Reloj de pared"),
    ]),
    ("papier-range", "Papier rangé", "📓", [
        ("notebook pages writing", "Cahier", "Notebook", "Cuaderno"),
        ("office binder folder", "Classeur", "Binder", "Carpeta"),
    ]),
    ("petite-fixation", "Petite fixation", "🔩", [
        ("screw closeup metal", "Vis", "Screw", "Tornillo"),
        ("nail hammer wood", "Clou", "Nail", "Clavo"),
    ]),
    ("outils-menage", "Outil de ménage", "🧹", [
        ("vacuum cleaner home", "Aspirateur", "Vacuum", "Aspiradora"),
        ("broom sweeping floor", "Balai", "Broom", "Escoba"),
    ]),
    ("ustensile-creux", "Ustensile creux", "🥄", [
        ("spoon stirring soup", "Cuillère", "Spoon", "Cuchara"),
        ("ladle soup pot", "Louche", "Ladle", "Cucharón"),
    ]),
    ("outil-main", "Outil à main", "🔧", [
        ("pliers tool work", "Pince", "Pliers", "Alicates"),
        ("screwdriver tool", "Tournevis", "Screwdriver", "Destornillador"),
    ]),

    # Activites
    ("medical", "Personnel médical", "👨‍⚕️", [
        ("doctor hospital coat", "Docteur", "Doctor", "Doctor"),
        ("nurse hospital uniform", "Infirmière", "Nurse", "Enfermera"),
    ]),
    ("vehicule-utilitaire", "Véhicule utilitaire", "🚒", [
        ("fire truck firefighter", "Camion pompier", "Fire truck", "Camión bomberos"),
        ("ambulance siren lights", "Ambulance", "Ambulance", "Ambulancia"),
    ]),
    ("plante-deco", "Plante déco", "🪴", [
        ("monstera plant leaves", "Monstera", "Monstera", "Monstera"),
        ("cactus desert closeup", "Cactus", "Cactus", "Cactus"),
    ]),
    ("geste-victoire", "Geste de victoire", "💪", [
        ("thumbs up gesture", "Pouce levé", "Thumbs up", "Pulgar arriba"),
        ("flexing biceps muscle", "Biceps", "Biceps", "Bíceps"),
    ]),
]


# Renforce le tirage : si la query echoue, on tente une 2eme query plus generale.
FALLBACK_QUERIES = {
    "ladle soup pot": "soup ladle kitchen",
    "ice cream sundae": "ice cream dessert",
    "monstera plant leaves": "houseplant leaves green",
    "macaron french": "macaroons colorful",
    "snowboarding mountain": "snowboard winter",
    "blouse fashion woman": "shirt fashion white",
    "carrot fresh": "carrot vegetable",
    "radish fresh": "radish vegetable red",
    "candy colorful": "candies sweet",
    "yogurt spoon": "yogurt bowl spoon",
    "lizard closeup": "lizard reptile",
    "sea lion ocean": "sea lion swimming",
    "toucan bird": "toucan tropical",
    "octopus underwater": "octopus ocean",
    "kayak river": "kayak water",
    "wall clock ticking": "wall clock home",
    "office binder folder": "office desk folder",
    "screw closeup metal": "metal screws",
    "ladle soup pot": "soup serving",
}


def search_pexels(query: str, orientation="portrait"):
    base = "https://api.pexels.com/videos/search?"
    params = f"query={urllib.parse.quote(query)}&per_page=5"
    if orientation:
        params += f"&orientation={orientation}"
    req = urllib.request.Request(base + params, headers={"Authorization": API_KEY, "User-Agent": "Mozilla/5.0 UndercoverApp"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  [!] HTTP error {e}")
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
    data = search_pexels(query, "portrait")
    link, dur = pick_best_video(data)
    if link:
        return link, dur
    # fallback orientation
    data = search_pexels(query, None)
    link, dur = pick_best_video(data)
    if link:
        return link, dur
    # fallback query plus generique
    fb = FALLBACK_QUERIES.get(query)
    if fb:
        print(f"  [retry] -> {fb!r}")
        data = search_pexels(fb, "portrait")
        link, dur = pick_best_video(data)
        if link:
            return link, dur
        data = search_pexels(fb, None)
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

    existing_ids = {c["id"] for c in data["categories"]}
    print(f"[INFO] {len(existing_ids)} categories existantes, ajout de {len(PAIRS)} max")

    tr = {"categories": {}}
    if os.path.exists(TR_PATH):
        with open(TR_PATH, "r", encoding="utf-8") as f:
            tr = json.load(f)
    tr.setdefault("categories", {})

    added, skipped, failed = 0, 0, 0
    for pid, name, emoji, items in PAIRS:
        if pid in existing_ids:
            print(f"[SKIP] {pid} (deja present)")
            skipped += 1
            continue
        print(f"\n=== {pid} : {name} ===")
        videos = []
        titles_en, titles_es = [], []
        for i, (q, t_fr, t_en, t_es) in enumerate(items):
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
                titles_en.append(t_en)
                titles_es.append(t_es)
            except Exception as e:
                print(f"  [X] download err : {e}")
            time.sleep(0.3)

        if len(videos) >= 2:
            data["categories"].append({
                "id": pid, "name": name, "emoji": emoji, "videos": videos,
            })
            tr["categories"][pid] = {
                "fr": {"name": name, "videos": [{"title": v["title"]} for v in videos]},
                "en": {"name": name, "videos": [{"title": t} for t in titles_en]},
                "es": {"name": name, "videos": [{"title": t} for t in titles_es]},
            }
            added += 1
            print(f"  [OK] {pid} ajoute")
        else:
            failed += 1
            # nettoyer les fichiers partiels
            for v in videos:
                p = os.path.join(ROOT, v["url"])
                if os.path.exists(p):
                    os.remove(p)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(TR_PATH, "w", encoding="utf-8") as f:
        json.dump(tr, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] +{added} ajoutees, {skipped} skipped, {failed} echec")
    print(f"[DONE] Total final : {len(data['categories'])} categories")


if __name__ == "__main__":
    main()
