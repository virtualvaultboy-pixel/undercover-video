"""Pack 4 : +50 paires Pexels supplementaires (sujets jamais utilises)."""
import sys, json, os, time, urllib.request, urllib.parse

if len(sys.argv) < 2:
    print("Usage: python rebuild_pexels_pack4.py <PEXELS_API_KEY>")
    sys.exit(1)

API_KEY = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(ROOT, "videos")
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
TR_PATH = os.path.join(ROOT, "data", "translations.json")
os.makedirs(VIDEOS_DIR, exist_ok=True)

PAIRS = [
    # Fruits/legumes nouveaux
    ("poivron-couleur", "Poivron",           "🫑", [("red bell pepper closeup","Poivron rouge","Red pepper","Pimiento rojo"),("yellow bell pepper","Poivron jaune","Yellow pepper","Pimiento amarillo")]),
    ("champignon",      "Champignon",        "🍄", [("mushroom forest","Cèpe","Mushroom","Seta"),("white champignon fresh","Champignon blanc","White mushroom","Champiñón")]),
    ("graine-cereale",  "Céréale",           "🌾", [("rice cooked bowl","Riz","Rice","Arroz"),("quinoa grain bowl","Quinoa","Quinoa","Quinoa")]),
    ("baie-rouge",      "Baie rouge",        "🫐", [("blueberries fresh","Myrtille","Blueberry","Arándano"),("cranberry fresh","Cranberry","Cranberry","Arándano rojo")]),
    # Animaux nouveaux
    ("sauvage-savane",  "Sauvage savane",    "🦓", [("zebra wildlife","Zèbre","Zebra","Cebra"),("hippopotamus wildlife","Hippopotame","Hippo","Hipopótamo")]),
    ("sauvage-arctique","Animal arctique",   "🐧", [("penguin colony snow","Pingouin","Penguin","Pingüino"),("walrus arctic","Morse","Walrus","Morsa")]),
    ("oiseau-couleur",  "Oiseau coloré",     "🦚", [("peacock feathers","Paon","Peacock","Pavo real"),("flamingo pink","Flamant rose","Flamingo","Flamenco")]),
    ("reptile-trop",    "Reptile tropical",  "🦎", [("iguana wildlife","Iguane","Iguana","Iguana"),("chameleon closeup","Caméléon","Chameleon","Camaleón")]),
    ("insecte-rampant", "Insecte rampant",   "🪲", [("beetle macro","Scarabée","Beetle","Escarabajo"),("centipede macro","Mille-pattes","Centipede","Ciempiés")]),
    ("rongeur-grand",   "Gros rongeur",      "🦫", [("capybara wildlife","Capybara","Capybara","Carpincho"),("beaver river","Castor","Beaver","Castor")]),
    # Sports nouveaux
    ("sport-equestre",  "Sport équestre",    "🏇", [("horse jumping equestrian","Saut obstacle","Show jumping","Salto"),("polo horse player","Polo","Polo","Polo")]),
    ("sport-aventure",  "Sport aventure",    "🧗", [("rock climbing mountain","Escalade","Climbing","Escalada"),("rafting whitewater","Rafting","Rafting","Rafting")]),
    ("art-martial",     "Art martial",       "🥋", [("judo throw match","Judo","Judo","Judo"),("aikido training dojo","Aikido","Aikido","Aikido")]),
    ("sport-piscine",   "Sport piscine",     "🏊", [("swimming pool lap","Nage couloir","Lap swim","Natación"),("diving board olympic","Plongeon","Diving","Salto")]),
    ("sport-glisse-snow","Glisse neige",     "🛷", [("luge winter","Luge","Sledding","Trineo"),("bobsled track","Bobsleigh","Bobsled","Bobsleigh")]),
    # Metiers
    ("metier-batiment", "Métier bâtiment",   "🧱", [("mason bricklayer wall","Maçon","Mason","Albañil"),("carpenter wood working","Charpentier","Carpenter","Carpintero")]),
    ("metier-creatif",  "Métier créatif",    "🎨", [("graphic designer computer","Graphiste","Designer","Diseñador"),("architect blueprint","Architecte","Architect","Arquitecto")]),
    ("metier-sante",    "Métier santé",      "🩺", [("dentist patient chair","Dentiste","Dentist","Dentista"),("surgeon operating room","Chirurgien","Surgeon","Cirujano")]),
    ("metier-bien-etre","Bien-être",         "💆", [("yoga coach class","Coach yoga","Coach","Entrenador"),("massage therapist spa","Masseur","Massage","Masajista")]),
    # Tech
    ("jeu-video",       "Jeu vidéo",         "🎮", [("game console controller","Console","Console","Consola"),("playing video game tv","Manette","Controller","Mando")]),
    ("realite-virt",    "Réalité virtuelle", "🥽", [("vr headset gaming","Casque VR","VR headset","Casco VR"),("drawing tablet artist","Tablette graphique","Drawing tablet","Tableta gráfica")]),
    ("photo-equipement","Photo équipement",  "📸", [("tripod camera setup","Trépied","Tripod","Trípode"),("camera lens closeup","Objectif","Lens","Objetivo")]),
    # Voyage
    ("avion-aeroport",  "Aéroport",          "✈️", [("airplane runway takeoff","Tarmac","Runway","Pista"),("airport terminal travelers","Terminal","Terminal","Terminal")]),
    ("hotel-luxe",      "Hôtel luxe",        "🏩", [("luxury hotel suite","Suite","Suite","Suite"),("spa pool relax hotel","Spa hôtel","Hotel spa","Spa hotel")]),
    # Meubles
    ("meuble-rangement","Rangement",         "🗄️", [("wardrobe closet bedroom","Armoire","Wardrobe","Armario"),("dresser drawer wooden","Commode","Dresser","Cómoda")]),
    ("deco-mur",        "Décoration murale", "🖼️", [("framed painting wall","Tableau","Painting","Cuadro"),("decorative vase modern","Vase","Vase","Jarrón")]),
    ("petit-electro",   "Petit électroménager","☕", [("electric kettle steam","Bouilloire","Kettle","Hervidor"),("coffee machine drip","Cafetière","Coffee maker","Cafetera")]),
    ("eclairage-deco",  "Éclairage déco",    "🕯️", [("candle holder dinner","Bougeoir","Candle holder","Candelabro"),("string lights cozy","Guirlande","String lights","Guirnalda")]),
    # Emotions
    ("emotion-tendresse","Tendresse",        "🤗", [("hug couple sweet","Câlin","Hug","Abrazo"),("kiss couple romantic","Bisou","Kiss","Beso")]),
    ("emotion-action",  "Action expressive", "🗣️", [("person shouting angry","Cri","Shout","Grito"),("frustrated face person","Frustration","Frustration","Frustración")]),
    # Nature
    ("paysage-rural",   "Paysage rural",     "🌾", [("wheat field summer","Champ de blé","Wheat field","Trigal"),("vineyard grapes row","Vigne","Vineyard","Viñedo")]),
    ("paysage-urbain",  "Paysage urbain",    "🏙️", [("city skyline night","Skyline","Skyline","Skyline"),("city avenue cars","Avenue","Avenue","Avenida")]),
    ("jardin-fleur",    "Jardin fleuri",     "🌸", [("flower bed garden colorful","Massif","Flower bed","Macizo"),("garden path flowers","Allée fleurie","Garden path","Sendero floral")]),
    # Sucre
    ("dessert-fruit",   "Dessert aux fruits","🍰", [("fruit tart sliced","Tarte fruits","Fruit tart","Tarta de frutas"),("fruit salad bowl","Salade fruits","Fruit salad","Ensalada frutas")]),
    ("viennoiserie",    "Viennoiserie",      "🥐", [("croissant fresh bakery","Croissant","Croissant","Croissant"),("chocolate pastry bakery","Pain au chocolat","Chocolate pastry","Napolitana")]),
    ("chocolat-forme",  "Chocolat",          "🍫", [("chocolate bar squares","Tablette","Chocolate bar","Tableta"),("chocolate truffle","Truffe","Truffle","Trufa")]),
    # Boissons
    ("boisson-petit-dej","Petit-déj boisson","🥛", [("smoothie glass fruits","Smoothie","Smoothie","Batido"),("hot chocolate cup","Chocolat chaud","Hot chocolate","Chocolate caliente")]),
    # Vetements
    ("vetement-femme",  "Tenue femme",       "👗", [("dress fashion woman","Robe","Dress","Vestido"),("skirt fashion pleated","Jupe","Skirt","Falda")]),
    ("vetement-homme",  "Tenue homme",       "🤵", [("man suit formal","Costume","Suit","Traje"),("blazer fashion man","Blazer","Blazer","Blazer")]),
    # Métier transport
    ("metier-route",    "Métier route",      "🚛", [("truck driver wheel","Camionneur","Truck driver","Camionero"),("taxi driver city","Chauffeur taxi","Taxi driver","Taxista")]),
    # Aquatique
    ("vie-marine",      "Vie marine",        "🐚", [("starfish underwater","Étoile de mer","Starfish","Estrella mar"),("seahorse aquarium","Hippocampe","Seahorse","Caballito mar")]),
    # Outils jardin
    ("outil-jardin",    "Outil de jardin",   "🪴", [("watering can plants","Arrosoir","Watering can","Regadera"),("garden shovel dig","Pelle","Shovel","Pala")]),
    # Boissons spec
    ("eau-petillante",  "Eau pétillante",    "🥤", [("sparkling water bubbles","Eau pétillante","Sparkling water","Agua con gas"),("flavored water glass","Eau aromatisée","Flavored water","Agua aromática")]),
    # Cuisine ustensiles
    ("ustensile-trance","Ustensile coupe",   "🔪", [("kitchen knife chopping","Couteau cuisine","Knife","Cuchillo"),("scissors cutting fabric","Ciseaux","Scissors","Tijeras")]),
    # Animaux ferme
    ("animal-laine",    "Animal à laine",    "🐑", [("sheep farm grass","Mouton","Sheep","Oveja"),("goat farm closeup","Chèvre","Goat","Cabra")]),
    # Confort
    ("repos-detente",   "Repos détente",     "🛀", [("bathtub bubbles relax","Bain","Bath","Baño"),("hammock backyard summer","Hamac","Hammock","Hamaca")]),
    # Hobby/loisir
    ("loisir-creatif",  "Loisir créatif",    "🧶", [("knitting yarn hands","Tricot","Knitting","Tejer"),("origami paper folding","Origami","Origami","Origami")]),
    # Symboles divers
    ("evenement-sport", "Événement sport",   "🏆", [("trophy gold winner","Trophée","Trophy","Trofeo"),("medal gold athlete","Médaille","Medal","Medalla")]),
    # Bureau divers
    ("papeterie",       "Papeterie",         "📐", [("ruler pencils desk","Règle crayons","Ruler pencils","Regla lápices"),("notebook open writing","Cahier ouvert","Notebook","Cuaderno")]),
    # Hygiene
    ("salle-bain-acces","Accessoire bain",   "🪥", [("razor shaving foam","Rasoir","Razor","Cuchilla"),("towel folded bath","Serviette","Towel","Toalla")]),
]

FALLBACK = {
    "yellow bell pepper": "yellow pepper",
    "rice cooked bowl": "rice",
    "quinoa grain bowl": "quinoa",
    "walrus arctic": "walrus animal",
    "polo horse player": "polo sport",
    "aikido training dojo": "aikido",
    "luge winter": "luge sledding",
    "bobsled track": "bobsled",
    "carpenter wood working": "carpenter",
    "drawing tablet artist": "graphic tablet",
    "garden path flowers": "garden path",
    "flavored water glass": "flavored water",
    "string lights cozy": "fairy lights",
    "scissors cutting fabric": "scissors",
    "frustrated face person": "frustrated person",
}


def search_pexels(query, orientation="portrait"):
    base = "https://api.pexels.com/videos/search?"
    params = f"query={urllib.parse.quote(query)}&per_page=5"
    if orientation: params += f"&orientation={orientation}"
    req = urllib.request.Request(base+params, headers={"Authorization":API_KEY,"User-Agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())
    except Exception as e:
        print(f"  [!] HTTP {e}"); return {"videos":[]}

def pick_best(data, td=8):
    vs = data.get("videos", [])
    if not vs: return None,None
    vs = sorted(vs, key=lambda v: abs(v.get("duration",30)-td))
    v = vs[0]
    fs = [f for f in v.get("video_files",[]) if f.get("file_type")=="video/mp4"]
    fs = sorted(fs, key=lambda f: abs(f.get("width",0)-540))
    if not fs: return None,None
    return fs[0]["link"], v.get("duration")

def find_video(q):
    for orient in ("portrait", None):
        d = search_pexels(q, orient); link,dur = pick_best(d)
        if link: return link,dur
    fb = FALLBACK.get(q)
    if fb:
        print(f"  [retry] {fb!r}")
        for orient in ("portrait", None):
            d = search_pexels(fb, orient); link,dur = pick_best(d)
            if link: return link,dur
    return None,None

def download(url, dst):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dst,"wb") as f: f.write(r.read())
    return os.path.getsize(dst)

def main():
    with open(JSON_PATH,"r",encoding="utf-8") as f: data = json.load(f)
    existing = {c["id"] for c in data["categories"]}
    print(f"[INFO] {len(existing)} existantes, +{len(PAIRS)} max")
    tr = {"categories":{}}
    if os.path.exists(TR_PATH):
        with open(TR_PATH,"r",encoding="utf-8") as f: tr = json.load(f)
    tr.setdefault("categories", {})
    added,skipped,failed = 0,0,0
    for pid, name, emoji, items in PAIRS:
        if pid in existing: print(f"[SKIP] {pid}"); skipped+=1; continue
        print(f"\n=== {pid} : {name} ===")
        videos,t_en,t_es = [],[],[]
        for i,(q,t_fr,te,tes) in enumerate(items):
            print(f"  [{i+1}] {q!r}")
            link,dur = find_video(q)
            if not link: print(f"  [X] echec {q!r}"); continue
            fn = f"{pid}_{i+1}.mp4"; dst = os.path.join(VIDEOS_DIR, fn)
            try:
                sz = download(link, dst)
                print(f"      -> {fn} ({sz//1024} KB)")
                videos.append({"source":"local","url":f"videos/{fn}","title":t_fr,"duration":dur})
                t_en.append(te); t_es.append(tes)
            except Exception as e: print(f"  [X] dl {e}")
            time.sleep(0.3)
        if len(videos)>=2:
            data["categories"].append({"id":pid,"name":name,"emoji":emoji,"videos":videos})
            tr["categories"][pid] = {
                "fr":{"name":name,"videos":[{"title":v["title"]} for v in videos]},
                "en":{"name":name,"videos":[{"title":t} for t in t_en]},
                "es":{"name":name,"videos":[{"title":t} for t in t_es]},
            }
            added += 1; print(f"  [OK] {pid}")
        else:
            failed += 1
            for v in videos:
                p = os.path.join(ROOT, v["url"])
                if os.path.exists(p): os.remove(p)
    with open(JSON_PATH,"w",encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
    with open(TR_PATH,"w",encoding="utf-8") as f: json.dump(tr, f, ensure_ascii=False, indent=2)
    print(f"\n[DONE] +{added}, skip {skipped}, echec {failed} | total {len(data['categories'])}")

if __name__ == "__main__":
    main()
