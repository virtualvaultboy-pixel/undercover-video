# 📦 Publier Undercover Vidéo sur le Play Store

Guide pas-à-pas pour passer de la PWA à une vraie app Android publiée.

---

## ✅ Pré-requis (déjà OK)

- [x] App déployée sur HTTPS : https://virtualvaultboy-pixel.github.io/undercover-video/
- [x] Manifest PWA valide
- [x] Service Worker fonctionnel
- [x] Icônes PNG 192 et 512 (avec une maskable)
- [x] Politique de confidentialité publique : https://virtualvaultboy-pixel.github.io/undercover-video/privacy.html
- [x] 75 catégories de vidéos
- [x] Compte Google Play Developer (25$)

---

## 1. Pousser les dernières modifs sur GitHub

Avant de générer l'AAB, push tout ce qui a été ajouté (icônes, manifest amélioré, politique) :

```powershell
cd C:\Users\qfichet\undercover-video
git add .
git commit -m "Play Store ready: icones HD, manifest enrichi, politique de confidentialite, 75 categories"
git push
```

Attends 2 min que GitHub Pages redéploie.

Vérifie sur https://virtualvaultboy-pixel.github.io/undercover-video/manifest.json que tu vois bien les nouvelles icônes.

---

## 2. Générer l'AAB via PWABuilder (5 min)

1. Va sur **https://www.pwabuilder.com/**
2. Colle l'URL : `https://virtualvaultboy-pixel.github.io/undercover-video/`
3. Clique **"Start"** → analyse le site
4. Tu vois ton score PWA. Idéalement ≥ 100. Si certains items rouges :
   - Fix les warnings affichés
   - Re-push, relance
5. Clique **"Package For Stores"** (en haut à droite)
6. Choisis **"Android"** → **"Generate Package"**
7. Dans le formulaire :
   - **Package ID** : `com.deponchystudio.undercovervideo`
   - **App name** : `Undercover Vidéo`
   - **Short name** : `Undercover`
   - **Launcher name** : `Undercover Vidéo`
   - **App version** : `1.0.0`
   - **App version code** : `1`
   - **Signing key** : choisis **"Generate new signing key"** (PWABuilder en crée une)
     - ⚠️ **TÉLÉCHARGE ET GARDE LE FICHIER `.keystore` PRÉCIEUSEMENT**
     - Tu en auras besoin pour TOUTES les futures mises à jour
     - Note aussi : key password + keystore password + key alias
   - **Display mode** : `standalone`
   - **Orientation** : `portrait`
   - **Status bar color** : `#0d0d12`
   - **Background color** : `#0d0d12`
   - **Splash color** : `#0d0d12`
   - **Theme color** : `#0d0d12`
   - **Include source code** : optionnel (cocher si tu veux le projet Android Studio)
8. Clique **"Download"**
9. Tu obtiens un ZIP contenant :
   - `app-release-signed.aab` ← le fichier à uploader sur Play Console
   - `app-release-signed.apk` ← pour tester en local
   - `signing.keystore` + `key-info.txt` ← À CONSERVER ABSOLUMENT
   - `assetlinks.json` ← À mettre sur ton site (voir étape 3)

---

## 3. Lier l'app au site (Digital Asset Links)

Pour que l'app soit reconnue comme un TWA "validé" (sans barre d'URL Chrome), il faut publier
un fichier `.well-known/assetlinks.json` sur le site.

1. Décompresse le ZIP PWABuilder et trouve `assetlinks.json`
2. Crée le dossier dans le projet :

```powershell
mkdir C:\Users\qfichet\undercover-video\.well-known
copy chemin\vers\assetlinks.json C:\Users\qfichet\undercover-video\.well-known\
```

3. Push :

```powershell
cd C:\Users\qfichet\undercover-video
git add .well-known/
git commit -m "Add assetlinks.json for TWA validation"
git push
```

4. Vérifie qu'il est accessible : https://virtualvaultboy-pixel.github.io/undercover-video/.well-known/assetlinks.json

---

## 4. Uploader sur Play Console

1. Va sur **https://play.google.com/console/**
2. Clique **"Créer une application"**
3. Remplis :
   - **Nom de l'application** : `Undercover Vidéo`
   - **Langue par défaut** : `Français (France)`
   - **Type** : `Jeu`
   - **Gratuit ou payant** : `Gratuit`
   - Coche les déclarations obligatoires (conditions, lois d'export US, etc.)
4. **Tableau de bord** → suis les étapes guidées :

### 4.1 Configurer l'application
- **Confidentialité** : URL `https://virtualvaultboy-pixel.github.io/undercover-video/privacy.html`
- **Accès à l'application** : "Toutes les fonctionnalités sont disponibles sans restriction"
- **Annonces** : "Mon app ne contient pas d'annonces" (pour la v1)
- **Classification du contenu** : remplir le questionnaire IARC (5 min)
  - Tous publics, pas de violence, pas de contenu suggestif → PEGI 3
- **Public cible et contenu** : 13+ (à cause des contenus chargés en ligne)
- **Application gouvernementale** : non
- **Catégorie** : `Jeux > Cartes & Casino` ou `Jeux > Familial`

### 4.2 Sécurité des données
- **Collecte de données** : Non
- **Données partagées avec des tiers** : Non
- **Pratiques de sécurité** : "Les données sont chiffrées en transit", "L'utilisateur peut demander la suppression des données"

### 4.3 Fiche du Play Store
- **Nom** : `Undercover Vidéo`
- **Description courte (80 caractères)** :
  > Le party game Undercover en version vidéo. Démasquez le joueur intrus !
- **Description complète (4000 caractères)** :
  > 🎬 Undercover Vidéo — Le party game qui met l'ambiance entre amis
  >
  > Inspiré du célèbre jeu Undercover, cette version utilise des vidéos surprenantes pour pimenter chaque partie. Idéal pour les soirées, les apéros et les week-ends entre amis.
  >
  > 🎮 LE PRINCIPE
  > L'app se passe de main en main. Chaque joueur regarde sa vidéo secrète à l'abri des regards. Tous voient la même vidéo... sauf un : l'undercover, qui en a une légèrement différente. À l'oral, vous décrivez votre vidéo à tour de rôle pour démasquer l'intrus, sans trop en dire pour ne pas vous faire griller si c'est vous !
  >
  > ✨ FONCTIONNALITÉS
  > • 75 catégories de paires de vidéos (et ça grandit !)
  > • Mode pass-and-play : un seul téléphone suffit
  > • De 3 à 12 joueurs
  > • Saisie des prénoms pour personnaliser
  > • Système de vote intégré : tente de démasquer l'undercover
  > • Si tu votes mal, on continue avec un nouveau tour de parole
  > • Si l'undercover survit, il gagne la partie !
  > • Comparatif des 2 vidéos en fin de partie pour rigoler
  > • Anti-répétition : tu ne reverras pas la même catégorie de suite
  > • Pas de pubs, pas de compte, pas de tracking
  >
  > 🎬 DES VIDÉOS POUR TOUS LES GOÛTS
  > De vraies vidéos (sport, nature, animaux, slow motion) aux dessins animés surréalistes (chat qui danse, bateau volant, dragons, super-héros, memes...), il y en a pour tous les goûts et tous les âges.
  >
  > 🛡️ RESPECTUEUX
  > Aucun compte, aucune collecte de données, aucune permission abusive. Juste un bon moment entre potes.

- **Icône** : `icons/icon-512.png`
- **Feature graphic 1024×500** : ⚠️ à créer (voir étape 5)
- **Screenshots téléphone (min 2, max 8)** : utilise les screenshots du dossier `screenshots/`
  - ⚠️ Idéalement, prends-en des vrais avec ton tél en mode standalone après l'install : plus convaincants

### 4.4 Publication
- **Version de production** → **"Créer une version"**
- Upload **`app-release-signed.aab`**
- Notes de version (français) :
  > 🎉 Version 1.0 — première sortie publique
  > • 75 catégories de paires de vidéos
  > • Mode pass-and-play pour 3 à 12 joueurs
  > • Système de vote et comparatif des vidéos
  > • Aucune pub, aucune collecte de données

5. **Vérifier la version** → si tout est vert, **Envoyer pour examen**.
6. Délai de review : **1 à 7 jours** (en général 1-3 jours pour les apps simples).

---

## 5. Feature graphic 1024×500 (à créer)

Tu peux la faire avec :
- **Canva** (template "Feature Graphic Google Play")
- **Figma**
- **Photoshop**

Contenu recommandé :
- Fond dégradé rose → violet (couleurs de l'app)
- Logo / icône à gauche
- Titre "UNDERCOVER VIDÉO" en gros
- Sous-titre "Le party game pour démasquer l'intrus"
- Quelques mockups de l'app sur la droite

Sauvegarde en PNG, max 1 MB.

Si tu veux, je peux te générer une version basique en Python via PIL (dis-moi).

---

## 6. Après la review

Une fois l'app approuvée :
- Elle apparaît sur Google Play
- Tu obtiens une URL publique type `https://play.google.com/store/apps/details?id=com.deponchystudio.undercovervideo`
- Tu peux la partager partout

---

## 🔄 Mises à jour

Quand tu veux publier une nouvelle version (nouvelles vidéos, fix, etc.) :

1. Si tu changes juste les vidéos (sur GitHub Pages) → **rien à faire côté Play Store**, l'app récupère les nouvelles vidéos en ligne.
2. Si tu changes le code de l'app (manifest, logique JS, etc.) :
   - Push les modifs sur GitHub
   - Re-génère un AAB via PWABuilder (incrémente `version` → `1.0.1` et `versionCode` → `2`)
   - Upload sur Play Console → nouvelle version → soumets

---

## 🆘 En cas de problème

- **Score PWA bas sur PWABuilder** : vérifie le manifest, les icônes, le SW
- **Review Play Store rejetée** : lis le motif, corrige, ré-uploade
- **L'app ne s'ouvre pas en plein écran (avec barre Chrome)** : c'est que l'`assetlinks.json` n'est pas valide
- **Vidéos ne se chargent pas dans l'app installée** : vérifie que GitHub Pages est toujours UP

Bon courage 🚀
