# Cloudflare Worker pour Undercover Vidéo (Mode Adulte)

**But** : éviter les proxies CORS publics instables (`corsproxy.io`, `allorigins`...) qui rate-limit ou tombent. Ce Worker est gratuit, déployé chez toi sur Cloudflare, et marche tout le temps.

## Quotas Cloudflare gratuit
- **100 000 requêtes/jour** (largement suffisant pour des soirées entre potes)
- Pas de carte bancaire demandée
- Aucune perf à payer

## Déploiement en 4 minutes

### 1. Crée un compte Cloudflare (si t'en as pas)
Va sur https://dash.cloudflare.com/sign-up → email + mot de passe.

### 2. Crée un Worker
1. Une fois connecté, menu gauche : **Workers & Pages**
2. Clique **Create application** → **Create Worker**
3. Donne un nom : par exemple `undercover-cors`
4. Clique **Deploy** (déploie l'exemple Hello World)

### 3. Remplace le code par le nôtre
1. Clique **Edit code** (en haut à droite)
2. Sélectionne TOUT le code dans l'éditeur (Ctrl+A) → supprime
3. Colle le contenu de [`worker.js`](./worker.js) (copie depuis ce repo)
4. Clique **Save and deploy** (haut à droite)

### 4. Récupère l'URL et colle-la dans l'app
1. L'URL ressemble à : `https://undercover-cors.TON-PSEUDO.workers.dev`
2. Ouvre l'app Undercover → **Options avancées** → champ **URL Worker custom**
3. Colle l'URL → c'est sauvegardé en local

À partir de là, l'app utilise ton Worker en priorité. Les proxies publics restent en fallback si ton Worker tombe (impossible mais bon).

## Test rapide

Visite `https://undercover-cors.TON-PSEUDO.workers.dev/?url=https://api.redgifs.com/v2/auth/temporary`

Tu devrais voir un JSON avec un token. Si oui = ça marche.

## Désinstallation

Pour virer ton Worker : Cloudflare dashboard → Workers → ton worker → ⋯ → Delete.
