"""
Purge round 2 : paires identifiees comme mismatch lors de l'audit
visuel via planches contact (frames extraites).
"""
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, "data", "videos.json")
TR_PATH = os.path.join(ROOT, "data", "translations.json")

# Identifies par audit des 20 planches contact (frames a 2s)
# Cause racine : Giphy renvoie GIFs/memes/stickers qui contiennent juste
# le mot-cle dans leur title, sans rapport visuel avec le sujet.
FLAGGED_R2 = {
    # Planche 1
    "boisson-chaude",        # the verse = cocktail violet
    # Planche 2
    "animal-danse",          # chat danse = cartoon rose flou
    "creature-mythique",     # licorne = fille troll-doll
    # Planche 3
    "monstre-nuit",          # zombie = Scooby Doo, vampire = Minion
    "animal-calin",          # panda invisible
    # Planche 4
    "primate",               # singe et gorille visuellement identiques
    "snack-rapide",          # burger = dessin chien
    # Planche 5
    "medical",               # docteur = ourson Care Bear
    "metier-aventure",       # pilote = Mario kart
    "oiseau-tropical",       # toucan = trone royal
    # Planche 6
    "marin-mammif",          # dauphin = close-up bouche
    "gourmand",              # glace = sticker SpongeBob
    "fruit-pop",             # pomme=Chip&Dale, banane=texte
    "duo-clown",             # clown effrayant = astronaute lune
    # Planche 7
    "outil-bricolage",       # scie = boite DeWALT
    "instrument-musique",    # guitare = personnage flute
    "spectacle-cirque",      # jongleur = 3 chats
    "creature-marine",       # meduse = Bob l'eponge
    # Planche 8
    "vehicule-utilitaire",   # camion pompier = arbre vert
    "geste-victoire",        # pouce leve = enfant face
    "salutation",            # coucou = mec dans champ
    # Planche 9
    "outil-cuisine",         # ustensiles invisibles, juste personnages
    "boisson-fraiche",       # soda = texte + Yogi Bear
    "animal-ferme",          # vache = texte + image floue
    "animal-savane",         # girafe et elephant = ballons abstraits
    # Planche 11
    "boisson-tropicale",     # mojito = bouteille de gel
    "plat-italien",          # pates et risotto = humains, plats invisibles
    "sport-raquette",        # badminton = volants/sushi flou
    # Planche 12
    "sport-glace",           # hockey = bowling
    "sport-nautique",        # voile = selfie sans bateau
    "sport-hiver",           # ski = Tux, snowboard = juste montagne
    "rongeur-mignon",        # hamster = rond noir, ecureuil = texte
    # Planche 13
    "mammifere-marin-2",     # phoque = poisson, otarie = sticker chien
    "reptile-lent",          # tortue = castor, lezard = perroquet
    "creature-mer-mystere",  # etoile de mer = texte
    "art-japonais",          # calligraphie = femme kimono
    # Planche 14
    "petit-dej",             # gaufres = mec chef
    "patisserie-fine",       # macaron = sticker chien
    "fruit-exotique",        # mangue = jus generique, ananas = flamingo
    "dessert-glace",         # sundae = Donald Duck
    "animal-ferme-2",        # poule image blanche, canard juste paysage
    # Planche 15
    "sport-extreme-2",       # parapente et saut elastique invisibles
    "plante-deco",           # monstera = portrait fille
    # Planche 16
    "contenant-boisson",     # tasse = personnage cartoon
    "couvert-repas",         # couteau = rasoir
    "boisson-fermee",        # bouteille = DiCaprio meme
    "sac-porter",            # sac a main = HIGH BANK, cabas = Recycle us
    "informatique-input",    # clavier = Kermit, souris = gant
    # Planche 17
    "fruit-simple",          # pomme = Hey Arnold meme
    "haut-chaud",            # manteau = chien dormant
    "bagage",                # valise = mec rouge invisible
    # Planche 18
    "ustensile-creux",       # cuillere = spirale, louche = texte
    "outil-main",            # marteau = briques, tournevis = bois
    "racine-comestible",     # carotte et radis = Veggie Power cartoon
    "outils-menage",         # balai = juste texte WEE
    # Planche 19
    "siege",                 # tabouret = texte FANTASY
    "boulangerie",           # baguette = Kermit, pain de mie = cartoon
    "petite-fixation",       # vis = ressort
    "liquide-blanc",         # lait = bottle cartoon, creme = mec
    # Planche 20
    "literie-moelleux",      # coussin = ballon foot
    "literie-couverture",    # couette = paint, drap = croquis
    "mesure-temps",          # horloge murale = Shia LaBeouf meme
    "papier-range",          # classeur = palme + texte
    "haut-leger",            # t-shirt et debardeur invisibles
    "bas-long",              # pantalon = texte DUNTY FOLI
}


def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_ids = {c["id"] for c in data["categories"]}
    not_found = FLAGGED_R2 - existing_ids
    if not_found:
        print(f"[WARN] IDs introuvables dans videos.json: {not_found}")

    removed, kept, files_removed = [], [], 0
    for cat in data["categories"]:
        if cat["id"] in FLAGGED_R2:
            removed.append(cat["id"])
            for v in cat["videos"]:
                p = os.path.join(ROOT, v.get("url", ""))
                if os.path.exists(p):
                    os.remove(p)
                    files_removed += 1
        else:
            kept.append(cat)

    data["categories"] = kept
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    if os.path.exists(TR_PATH):
        with open(TR_PATH, "r", encoding="utf-8") as f:
            tr = json.load(f)
        for cid in removed:
            tr.get("categories", {}).pop(cid, None)
        with open(TR_PATH, "w", encoding="utf-8") as f:
            json.dump(tr, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(removed)} categories round-2 retirees")
    print(f"[OK] {files_removed} fichiers MP4 supprimes")
    print(f"[OK] {len(kept)} categories restantes")


if __name__ == "__main__":
    main()
