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
# Categories deja supprimees pour copyright - on les skip definitivement
# pour eviter qu'elles soient re-telechargees a chaque run.
COPYRIGHT_BLOCKED = {
    "perso-jeuvideo", "sous-marin", "vilain-dc", "simpsons", "sonic-univers",
    "jeu-retro", "personnage-disney", "anti-heros", "studio-ghibli",
    "personnage-marvel", "manga-shonen", "super-heros", "freres-mario",
    "pokemon-starter", "meme-culte", "doge-meme",
}

# Categories supprimees apres audit de qualite de paires (audit v2.3):
# paires trop eloignees ou doublons - cassent le doute permanent du jeu.
WEAK_BLOCKED = {
    "spectacle-nuit", "engin-volant", "nourriture-vivante", "etre-etrange",
    "reaction-sociale", "animal-majestueux", "phenomene-ciel", "insecte",
    "poisson", "legume", "pirate-mer", "danse-classique",
    "activite-quotidienne", "paysage-montagne", "fast-cooking",
    "fromage-charcuterie", "art-corporel", "activite-matin",
}

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
    # --- Pack 5 (gros, viser Play Store) ---
    {"id": "ours", "name": "Ours", "emoji": "🐻",
     "items": [("brown bear cartoon", "Ours brun"), ("polar bear cartoon", "Ours polaire")]},
    {"id": "felin-sauvage", "name": "Felin sauvage", "emoji": "🐆",
     "items": [("tiger cartoon", "Tigre"), ("leopard cartoon", "Leopard")]},
    {"id": "reptile", "name": "Reptile", "emoji": "🐍",
     "items": [("snake cartoon", "Serpent"), ("crocodile cartoon", "Crocodile")]},
    {"id": "oiseau-tropical", "name": "Oiseau tropical", "emoji": "🦜",
     "items": [("parrot cartoon", "Perroquet"), ("toucan cartoon", "Toucan")]},
    {"id": "insecte", "name": "Insecte", "emoji": "🦋",
     "items": [("butterfly cartoon", "Papillon"), ("bee cartoon", "Abeille")]},
    {"id": "poisson", "name": "Poisson", "emoji": "🐠",
     "items": [("clownfish cartoon", "Poisson clown"), ("shark cartoon", "Requin")]},
    {"id": "marin-mammif", "name": "Mammifere marin", "emoji": "🐬",
     "items": [("dolphin cartoon", "Dauphin"), ("whale cartoon", "Baleine")]},
    {"id": "boisson-fete", "name": "Boisson de fete", "emoji": "🍹",
     "items": [("cocktail drink", "Cocktail"), ("champagne pour", "Champagne")]},
    {"id": "gourmand", "name": "Sucrerie", "emoji": "🍫",
     "items": [("chocolate melting", "Chocolat"), ("ice cream cartoon", "Glace")]},
    {"id": "fruit-pop", "name": "Fruit populaire", "emoji": "🍎",
     "items": [("apple cartoon", "Pomme"), ("banana cartoon", "Banane")]},
    {"id": "legume", "name": "Legume", "emoji": "🥕",
     "items": [("carrot cartoon", "Carotte"), ("broccoli cartoon", "Brocoli")]},
    {"id": "personnage-disney", "name": "Personnage Disney", "emoji": "🐭",
     "items": [("mickey mouse", "Mickey"), ("donald duck", "Donald")]},
    {"id": "anti-heros", "name": "Anti-heros Marvel", "emoji": "🦹",
     "items": [("deadpool", "Deadpool"), ("venom marvel", "Venom")]},
    {"id": "studio-ghibli", "name": "Studio Ghibli", "emoji": "🐱",
     "items": [("totoro", "Totoro"), ("ponyo", "Ponyo")]},
    {"id": "duo-clown", "name": "Duo clown classique", "emoji": "🤡",
     "items": [("clown happy", "Clown joyeux"), ("clown scary", "Clown effrayant")]},
    {"id": "pirate-mer", "name": "Pirate des mers", "emoji": "🏴‍☠️",
     "items": [("pirate ship", "Pirate"), ("ship at sea", "Navire")]},
    {"id": "espace", "name": "Espace", "emoji": "🌌",
     "items": [("planet earth", "Terre"), ("saturn planet", "Saturne")]},
    {"id": "vacances-ete", "name": "Vacances d'ete", "emoji": "🏖️",
     "items": [("beach vacation", "Plage vacances"), ("sunbathing", "Bronzage")]},
    {"id": "saison-hiver", "name": "Hiver enneige", "emoji": "❄️",
     "items": [("snowman", "Bonhomme de neige"), ("snowflake", "Flocon")]},
    {"id": "outil-bricolage", "name": "Outil de bricolage", "emoji": "🔨",
     "items": [("hammer tool", "Marteau"), ("saw tool", "Scie")]},
    {"id": "instrument-musique", "name": "Instrument de musique", "emoji": "🎸",
     "items": [("guitar play", "Guitare"), ("piano play", "Piano")]},
    {"id": "danse-classique", "name": "Danse classique", "emoji": "🩰",
     "items": [("ballet dance", "Ballet"), ("salsa dance", "Salsa")]},
    {"id": "spectacle-cirque", "name": "Spectacle de cirque", "emoji": "🎪",
     "items": [("juggling circus", "Jongleur"), ("acrobat circus", "Acrobate")]},
    {"id": "metier-uniforme", "name": "Metier en uniforme", "emoji": "👮",
     "items": [("police officer cartoon", "Policier"), ("firefighter cartoon", "Pompier")]},
    {"id": "creature-marine", "name": "Creature marine etrange", "emoji": "🐙",
     "items": [("octopus cartoon", "Pieuvre"), ("jellyfish cartoon", "Meduse")]},
    {"id": "dinosaure", "name": "Dinosaure", "emoji": "🦖",
     "items": [("trex dinosaur", "T-Rex"), ("velociraptor dinosaur", "Velociraptor")]},
    {"id": "vehicule-utilitaire", "name": "Vehicule utilitaire", "emoji": "🚒",
     "items": [("fire truck cartoon", "Camion pompier"), ("ambulance cartoon", "Ambulance")]},
    {"id": "moyen-transport", "name": "Moyen de transport", "emoji": "🚂",
     "items": [("train cartoon", "Train"), ("bus cartoon", "Bus")]},
    {"id": "geste-victoire", "name": "Geste de victoire", "emoji": "💪",
     "items": [("thumbs up", "Pouce leve"), ("flex muscle", "Biceps")]},
    {"id": "salutation", "name": "Salutation", "emoji": "👋",
     "items": [("waving hello", "Coucou"), ("blowing kiss", "Bisou")]},
    # --- Pack 6 ---
    {"id": "activite-quotidienne", "name": "Activite quotidienne", "emoji": "😴",
     "items": [("sleeping cartoon", "Dormir"), ("waking up cartoon", "Se reveiller")]},
    {"id": "genre-musique", "name": "Genre de musique", "emoji": "🎸",
     "items": [("rock guitar concert", "Rock"), ("dj techno music", "Techno")]},
    {"id": "saison-douce", "name": "Saison douce", "emoji": "🍂",
     "items": [("autumn leaves", "Automne"), ("spring flowers", "Printemps")]},
    {"id": "outil-cuisine", "name": "Outil de cuisine", "emoji": "🍳",
     "items": [("frying pan cartoon", "Poele"), ("cooking pot cartoon", "Casserole")]},
    {"id": "boisson-fraiche", "name": "Boisson fraiche", "emoji": "🥤",
     "items": [("soda drink cartoon", "Soda"), ("juice glass cartoon", "Jus")]},
    {"id": "personnage-marvel", "name": "Personnage Marvel", "emoji": "🕷️",
     "items": [("spiderman cartoon", "Spider-Man"), ("hulk cartoon", "Hulk")]},
    {"id": "manga-shonen", "name": "Manga shonen", "emoji": "🍥",
     "items": [("naruto anime", "Naruto"), ("goku dragon ball", "Goku")]},
    {"id": "meme-culte", "name": "Meme culte", "emoji": "🤨",
     "items": [("surprised pikachu meme", "Pikachu surpris"), ("drake meme", "Drake")]},
    {"id": "animal-ferme", "name": "Animal de ferme", "emoji": "🐄",
     "items": [("cow cartoon", "Vache"), ("pig cartoon", "Cochon")]},
    {"id": "animal-savane", "name": "Animal de savane", "emoji": "🦒",
     "items": [("giraffe cartoon", "Girafe"), ("elephant cartoon", "Elephant")]},
    {"id": "sport-olympique", "name": "Sport olympique", "emoji": "🏊",
     "items": [("swimming pool race", "Natation"), ("athletics running", "Athletisme")]},
    {"id": "freres-mario", "name": "Freres Mario", "emoji": "🍄",
     "items": [("mario nintendo jumping", "Mario"), ("luigi nintendo", "Luigi")]},
    {"id": "pokemon-starter", "name": "Pokemon starter", "emoji": "🐢",
     "items": [("squirtle pokemon", "Carapuce"), ("bulbasaur pokemon", "Bulbizarre")]},
    {"id": "celebration", "name": "Celebration", "emoji": "🙌",
     "items": [("high five cartoon", "High five"), ("dance party celebration", "Fete")]},
    {"id": "emoji-coeur", "name": "Emoji coeur", "emoji": "❤️",
     "items": [("heart eyes love", "Coeur dans les yeux"), ("kissing heart emoji", "Bisou coeur")]},
    # --- Pack 7 ---
    {"id": "lever-coucher", "name": "Lever ou coucher de soleil", "emoji": "🌅",
     "items": [("sunrise time lapse", "Lever de soleil"), ("sunset time lapse", "Coucher de soleil")]},
    {"id": "ile-paradis", "name": "Ile paradisiaque", "emoji": "🏝️",
     "items": [("tropical beach palm tree", "Plage tropicale"), ("blue lagoon island", "Lagon bleu")]},
    {"id": "fete-evenement", "name": "Fete d'evenement", "emoji": "🎂",
     "items": [("wedding party dance", "Mariage"), ("birthday party cake", "Anniversaire")]},
    {"id": "boisson-tropicale", "name": "Boisson tropicale", "emoji": "🍹",
     "items": [("mojito cocktail tropical", "Mojito"), ("pina colada drink", "Pina colada")]},
    {"id": "plat-italien", "name": "Plat italien", "emoji": "🍝",
     "items": [("spaghetti pasta", "Pates"), ("risotto cooking", "Risotto")]},
    {"id": "fromage-charcuterie", "name": "Fromage ou charcuterie", "emoji": "🧀",
     "items": [("cheese melting fondue", "Fromage"), ("salami charcuterie board", "Charcuterie")]},
    {"id": "phenomene-rare", "name": "Phenomene celeste rare", "emoji": "🌌",
     "items": [("northern lights aurora", "Aurore boreale"), ("shooting stars meteor", "Etoiles filantes")]},
    {"id": "art-creatif", "name": "Art creatif", "emoji": "🎨",
     "items": [("watercolor painting brush", "Aquarelle"), ("oil painting canvas", "Peinture huile")]},
    {"id": "sport-raquette", "name": "Sport de raquette", "emoji": "🎾",
     "items": [("tennis serve point", "Tennis"), ("badminton smash", "Badminton")]},
    {"id": "sport-glace", "name": "Sport de glace", "emoji": "⛸️",
     "items": [("ice hockey goal", "Hockey"), ("figure skating spin", "Patinage")]},
    {"id": "sport-nautique", "name": "Sport nautique", "emoji": "⛵",
     "items": [("sailing boat sea", "Voile"), ("kayak river paddle", "Kayak")]},
    {"id": "deux-roues", "name": "Vehicule deux roues", "emoji": "🚲",
     "items": [("cycling road bike", "Velo"), ("electric scooter ride", "Trottinette")]},
    {"id": "sport-hiver", "name": "Sport d'hiver", "emoji": "🎿",
     "items": [("skiing slope mountain", "Ski"), ("snowboarding jump", "Snowboard")]},
    {"id": "rongeur-mignon", "name": "Petit rongeur", "emoji": "🐹",
     "items": [("hamster wheel cute", "Hamster"), ("squirrel eating nut", "Ecureuil")]},
    {"id": "canide-sauvage", "name": "Canide sauvage", "emoji": "🦊",
     "items": [("fox forest wild", "Renard"), ("wolf howling forest", "Loup")]},
    {"id": "mammifere-marin-2", "name": "Mammifere marin 2", "emoji": "🦭",
     "items": [("seal swimming ocean", "Phoque"), ("sea lion rocks", "Otarie")]},
    {"id": "reptile-lent", "name": "Reptile lent", "emoji": "🐢",
     "items": [("turtle slow walking", "Tortue"), ("lizard sun rock", "Lezard")]},
    {"id": "creature-mer-mystere", "name": "Creature de mer mysterieuse", "emoji": "🪼",
     "items": [("jellyfish glowing dark", "Meduse"), ("starfish ocean floor", "Etoile de mer")]},
    {"id": "art-japonais", "name": "Art japonais", "emoji": "🎴",
     "items": [("origami paper folding", "Origami"), ("japanese calligraphy ink", "Calligraphie")]},
    {"id": "metro-tram", "name": "Transport urbain rail", "emoji": "🚇",
     "items": [("subway train station", "Metro"), ("tramway city center", "Tramway")]},
    # --- Pack 8 ---
    {"id": "cocktail-color", "name": "Cocktail coloré", "emoji": "🍸",
     "items": [("margarita cocktail glass", "Margarita"), ("daiquiri pink drink", "Daiquiri")]},
    {"id": "cuisine-asiatique", "name": "Cuisine asiatique", "emoji": "🍜",
     "items": [("ramen bowl noodles", "Ramen"), ("pho vietnamese soup", "Pho")]},
    {"id": "petit-dej", "name": "Petit-déjeuner", "emoji": "🥞",
     "items": [("pancakes syrup breakfast", "Pancakes"), ("waffles powder sugar", "Gaufres")]},
    {"id": "patisserie-fine", "name": "Pâtisserie fine", "emoji": "🍰",
     "items": [("eclair pastry cream", "Eclair"), ("macaron colorful", "Macaron")]},
    {"id": "fruit-exotique", "name": "Fruit exotique", "emoji": "🥭",
     "items": [("mango fruit slice", "Mangue"), ("pineapple tropical", "Ananas")]},
    {"id": "legume-vert", "name": "Légume vert", "emoji": "🥦",
     "items": [("spinach leaves fresh", "Epinard"), ("broccoli florets", "Brocoli")]},
    {"id": "plante-deco", "name": "Plante déco", "emoji": "🌵",
     "items": [("monstera plant leaves", "Monstera"), ("cactus pot desert", "Cactus")]},
    {"id": "street-food", "name": "Street food", "emoji": "🌮",
     "items": [("tacos mexican street", "Tacos"), ("kebab grill rotating", "Kebab")]},
    {"id": "cuisine-indienne", "name": "Cuisine indienne", "emoji": "🍛",
     "items": [("curry indian spices", "Curry"), ("biryani rice dish", "Biryani")]},
    {"id": "dessert-glace", "name": "Dessert glacé", "emoji": "🍨",
     "items": [("sorbet fruit dessert", "Sorbet"), ("sundae ice cream cherry", "Sundae")]},
    {"id": "boisson-froide", "name": "Boisson froide", "emoji": "🍋",
     "items": [("lemonade summer drink", "Limonade"), ("iced tea glass mint", "The glace")]},
    {"id": "activite-matin", "name": "Activité matinale", "emoji": "🧘",
     "items": [("jogging morning park", "Jogging"), ("yoga pose sunrise", "Yoga")]},
    {"id": "animal-ferme-2", "name": "Animal de basse-cour", "emoji": "🐓",
     "items": [("chicken farm pecking", "Poule"), ("duck swimming pond", "Canard")]},
    {"id": "oiseau-proie", "name": "Oiseau de proie", "emoji": "🦅",
     "items": [("eagle soaring sky", "Aigle"), ("falcon diving fast", "Faucon")]},
    {"id": "insecte-rond", "name": "Petit insecte rond", "emoji": "🐞",
     "items": [("ladybug leaf macro", "Coccinelle"), ("beetle shiny green", "Scarabee")]},
    {"id": "art-corporel", "name": "Art corporel", "emoji": "💅",
     "items": [("nail art design", "Nail art"), ("tattoo arm artist", "Tatouage")]},
    {"id": "sport-extreme-2", "name": "Sport extrême 2", "emoji": "🪂",
     "items": [("paragliding mountain view", "Parapente"), ("bungee jumping bridge", "Saut elastique")]},
    {"id": "outils-menage", "name": "Outil de ménage", "emoji": "🧹",
     "items": [("vacuum cleaner home", "Aspirateur"), ("broom sweeping floor", "Balai")]},
    {"id": "lumiere-spectacle", "name": "Lumière spectacle", "emoji": "💡",
     "items": [("disco ball lights party", "Boule disco"), ("laser show concert", "Laser")]},
    {"id": "fete-foraine", "name": "Fête foraine", "emoji": "🎡",
     "items": [("ferris wheel night", "Grande roue"), ("carousel horses lights", "Carrousel")]},
    # --- Pack 9 : paires PROCHES sémantiquement (difficile pour les joueurs habitués) ---
    {"id": "accessoire-poignet", "name": "Accessoire au poignet", "emoji": "⌚",
     "items": [("watch wrist closeup", "Montre"), ("bracelet wrist gold", "Bracelet")]},
    {"id": "siege", "name": "Siège", "emoji": "🪑",
     "items": [("wooden chair empty", "Chaise"), ("bar stool wooden", "Tabouret")]},
    {"id": "outil-ecriture", "name": "Outil d'écriture", "emoji": "✏️",
     "items": [("ballpoint pen writing", "Stylo"), ("pencil writing paper", "Crayon")]},
    {"id": "contenant-boisson", "name": "Contenant à boisson", "emoji": "🥃",
     "items": [("water glass pouring", "Verre"), ("mug coffee ceramic", "Tasse")]},
    {"id": "couvert-repas", "name": "Couvert", "emoji": "🍴",
     "items": [("knife cutting board", "Couteau"), ("fork twirling pasta", "Fourchette")]},
    {"id": "meuble-allonge", "name": "Meuble pour s'allonger", "emoji": "🛋️",
     "items": [("bed bedroom", "Lit"), ("sofa living room", "Canapé")]},
    {"id": "boisson-fermee", "name": "Boisson en récipient fermé", "emoji": "🥤",
     "items": [("glass bottle drink", "Bouteille"), ("aluminum can soda", "Canette")]},
    {"id": "sac-porter", "name": "Sac à porter", "emoji": "👜",
     "items": [("handbag woman fashion", "Sac à main"), ("shopping tote bag", "Cabas")]},
    {"id": "lecture", "name": "Support de lecture", "emoji": "📖",
     "items": [("book reading pages", "Livre"), ("magazine flipping", "Magazine")]},
    {"id": "informatique-input", "name": "Périphérique ordinateur", "emoji": "⌨️",
     "items": [("keyboard typing fast", "Clavier"), ("computer mouse clicking", "Souris")]},
    {"id": "lunettes", "name": "Lunettes", "emoji": "👓",
     "items": [("glasses on eyes", "Lunettes de vue"), ("sunglasses cool", "Lunettes de soleil")]},
    {"id": "boulangerie", "name": "Boulangerie", "emoji": "🥖",
     "items": [("french baguette bread", "Baguette"), ("loaf bread sliced", "Pain de mie")]},
    {"id": "fruit-simple", "name": "Fruit simple", "emoji": "🍎",
     "items": [("apple red shiny", "Pomme"), ("pear yellow", "Poire")]},
    {"id": "couvre-chef", "name": "Couvre-chef", "emoji": "🧢",
     "items": [("baseball cap", "Casquette"), ("fedora hat man", "Chapeau")]},
    {"id": "haut-chaud", "name": "Haut chaud", "emoji": "🧥",
     "items": [("winter coat snow", "Manteau"), ("jacket leather", "Veste")]},
    {"id": "pied-au-chaud", "name": "Pied au chaud", "emoji": "🧦",
     "items": [("warm socks knit", "Chaussettes"), ("slippers cozy fireplace", "Chaussons")]},
    {"id": "chaussure", "name": "Chaussure", "emoji": "👞",
     "items": [("leather boots winter", "Bottes"), ("summer sandals beach", "Sandales")]},
    {"id": "bagage", "name": "Bagage", "emoji": "🎒",
     "items": [("backpack hiking", "Sac à dos"), ("suitcase rolling airport", "Valise")]},
    {"id": "protection-meteo", "name": "Protection météo", "emoji": "☂️",
     "items": [("umbrella rain", "Parapluie"), ("parasol beach sun", "Ombrelle")]},
    {"id": "ustensile-creux", "name": "Ustensile creux", "emoji": "🥄",
     "items": [("spoon stirring soup", "Cuillère"), ("ladle pouring broth", "Louche")]},
    {"id": "outil-main", "name": "Outil à main", "emoji": "🔨",
     "items": [("hammer nail wood", "Marteau"), ("screwdriver phillips", "Tournevis")]},
    {"id": "petite-fixation", "name": "Petite fixation", "emoji": "📌",
     "items": [("screw screwing", "Vis"), ("nail hammering wood", "Clou")]},
    {"id": "legume-rouge", "name": "Légume rouge", "emoji": "🍅",
     "items": [("tomato slicing fresh", "Tomate"), ("bell pepper red", "Poivron")]},
    {"id": "racine-comestible", "name": "Racine comestible", "emoji": "🥕",
     "items": [("carrot vegetable", "Carotte"), ("radish red round", "Radis")]},
    {"id": "liquide-chaud", "name": "Liquide chaud", "emoji": "🍲",
     "items": [("soup hot bowl", "Soupe"), ("broth simmering pot", "Bouillon")]},
    # --- Pack 10 : objets du quotidien tres proches ---
    {"id": "liquide-blanc", "name": "Liquide blanc", "emoji": "🥛",
     "items": [("milk pouring glass", "Lait"), ("cream pouring spoon", "Crème")]},
    {"id": "poudre-blanche", "name": "Poudre blanche cuisine", "emoji": "🧂",
     "items": [("sugar pouring spoon", "Sucre"), ("salt grinding salt shaker", "Sel")]},
    {"id": "matiere-grasse", "name": "Matière grasse", "emoji": "🧈",
     "items": [("butter melting pan", "Beurre"), ("margarine spread bread", "Margarine")]},
    {"id": "sandwich-rapide", "name": "Sandwich rapide", "emoji": "🥪",
     "items": [("sandwich bite eating", "Sandwich"), ("wrap roll burrito", "Wrap")]},
    {"id": "literie-moelleux", "name": "Literie moelleuse", "emoji": "🛌",
     "items": [("pillow fluff bed", "Oreiller"), ("cushion sofa decor", "Coussin")]},
    {"id": "literie-couverture", "name": "Couverture de lit", "emoji": "🛏️",
     "items": [("duvet bed cover", "Couette"), ("bedsheet pulling bed", "Drap")]},
    {"id": "brosse", "name": "Brosse hygiène", "emoji": "🪥",
     "items": [("toothbrush brushing teeth", "Brosse à dents"), ("hairbrush brushing hair", "Brosse à cheveux")]},
    {"id": "eclairage-maison", "name": "Éclairage maison", "emoji": "💡",
     "items": [("desk lamp turning on", "Lampe de bureau"), ("chandelier crystal lights", "Lustre")]},
    {"id": "mesure-temps", "name": "Mesure du temps", "emoji": "⏰",
     "items": [("alarm clock ringing", "Réveil"), ("wall clock ticking", "Horloge murale")]},
    {"id": "papier-range", "name": "Papier rangé", "emoji": "📓",
     "items": [("notebook writing", "Cahier"), ("binder folder office", "Classeur")]},
    {"id": "outil-application", "name": "Outil d'application", "emoji": "🖌️",
     "items": [("paintbrush painting wall", "Pinceau"), ("sponge cleaning wipe", "Éponge")]},
    {"id": "anneau-doigt", "name": "Anneau au doigt", "emoji": "💍",
     "items": [("engagement ring closeup", "Bague"), ("wedding band gold", "Alliance")]},
    {"id": "haut-leger", "name": "Haut léger", "emoji": "👕",
     "items": [("tshirt folding", "T-shirt"), ("tank top hanging", "Débardeur")]},
    {"id": "bas-long", "name": "Bas long", "emoji": "👖",
     "items": [("trousers folding", "Pantalon"), ("blue jeans denim", "Jean")]},
    {"id": "vetement-feminin", "name": "Vêtement féminin", "emoji": "👗",
     "items": [("dress twirling woman", "Robe"), ("skirt pleated fashion", "Jupe")]},
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
        if pair["id"] in COPYRIGHT_BLOCKED:
            print(f"\n[BLOCK] {pair['name']} (copyright)")
            continue
        if pair["id"] in WEAK_BLOCKED:
            print(f"\n[BLOCK] {pair['name']} (paire faible)")
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
