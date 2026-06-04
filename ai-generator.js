// ============================================================
// Image Generator via LoremFlickr (photos Flickr taggees)
//
// Etat 2026 des services AI gratuits :
// - Pollinations.ai : HTTP 402 Payment Required (passe payant)
// - Stable Horde : queue infinie (24min+)
// - Unsplash Source : 503 deprecated
// - HF Inference / Replicate / Cloudflare AI : necessitent token API
//
// Donc fallback sur LoremFlickr (photos Flickr indexees par tags)
// avec mini-traducteur FR/ES -> EN pour matcher les tags Flickr
// qui sont en anglais.
// ============================================================

const FLICKR_BASE = 'https://loremflickr.com';

// Mini-dico FR/ES -> EN pour traduire les mots-cles avant Flickr.
// Etoffer au besoin. Les mots inconnus passent tels quels.
const FR_ES_TO_EN = {
  // Animaux
  'chat':'cat','chien':'dog','cheval':'horse','vache':'cow','cochon':'pig',
  'oiseau':'bird','poisson':'fish','lion':'lion','tigre':'tiger','ours':'bear',
  'loup':'wolf','renard':'fox','singe':'monkey','elephant':'elephant',
  'girafe':'giraffe','souris':'mouse','lapin':'rabbit','poule':'chicken',
  'canard':'duck','serpent':'snake','tortue':'turtle','grenouille':'frog',
  'papillon':'butterfly','abeille':'bee','araignee':'spider','dauphin':'dolphin',
  'requin':'shark','baleine':'whale','pieuvre':'octopus','gato':'cat','perro':'dog',
  // Aliments
  'pomme':'apple','banane':'banana','orange':'orange','citron':'lemon',
  'fraise':'strawberry','raisin':'grape','pizza':'pizza','burger':'burger',
  'frites':'fries','pates':'pasta','riz':'rice','pain':'bread','fromage':'cheese',
  'chocolat':'chocolate','glace':'ice cream','gateau':'cake','salade':'salad',
  'soupe':'soup','steak':'steak','poulet':'chicken','poisson':'fish','sushi':'sushi',
  // Boissons
  'cafe':'coffee','the':'tea','vin':'wine','biere':'beer','jus':'juice',
  'lait':'milk','eau':'water','soda':'soda','cocktail':'cocktail',
  // Couleurs
  'rouge':'red','bleu':'blue','vert':'green','jaune':'yellow','noir':'black',
  'blanc':'white','orange':'orange','rose':'pink','violet':'purple','marron':'brown',
  'gris':'gray','dore':'golden','argent':'silver',
  // Nature
  'arbre':'tree','fleur':'flower','feuille':'leaf','herbe':'grass','foret':'forest',
  'montagne':'mountain','mer':'sea','plage':'beach','ocean':'ocean','lac':'lake',
  'riviere':'river','desert':'desert','ciel':'sky','nuage':'cloud','soleil':'sun',
  'lune':'moon','etoile':'star','pluie':'rain','neige':'snow','feu':'fire',
  // Humains
  'homme':'man','femme':'woman','enfant':'child','bebe':'baby','garcon':'boy',
  'fille':'girl','vieux':'old','jeune':'young','famille':'family',
  // Objets
  'voiture':'car','moto':'motorcycle','velo':'bicycle','avion':'plane',
  'train':'train','bateau':'boat','bus':'bus','maison':'house','immeuble':'building',
  'ville':'city','pont':'bridge','chateau':'castle','tour':'tower','livre':'book',
  'telephone':'phone','ordinateur':'computer','montre':'watch','chaise':'chair',
  'table':'table','lit':'bed','porte':'door','fenetre':'window',
  // Activites
  'manger':'eating','boire':'drinking','dormir':'sleeping','courir':'running',
  'marcher':'walking','danser':'dancing','chanter':'singing','jouer':'playing',
  'lire':'reading','ecrire':'writing','rire':'laughing','pleurer':'crying',
  // Vetements
  'chemise':'shirt','pantalon':'pants','robe':'dress','chaussure':'shoes',
  'chapeau':'hat','manteau':'coat','sac':'bag','lunettes':'glasses',
  // Tailles
  'gros':'big','grand':'tall','petit':'small','geant':'giant',
  // Esp -> EN
  'agua':'water','fuego':'fire','arbol':'tree','flor':'flower','casa':'house',
  'coche':'car','rojo':'red','azul':'blue','verde':'green','amarillo':'yellow',
};

const STOPWORDS = new Set([
  'un','une','des','le','la','les','du','de','qui','que','a','au','aux','et','ou',
  'the','a','an','and','or','of','in','on','with','who','that','for','to',
  'el','los','las','un','una','unos','unas','del','que','y','o','en','con',
]);

const aiGenerator = {
  /**
   * Convertit "un chat jaune" -> "cat,yellow"
   * Retire stopwords + traduit FR/ES vers EN si possible.
   */
  toTags(text) {
    return text
      .toLowerCase()
      .normalize('NFD').replace(/[̀-ͯ]/g, '') // retire accents
      .replace(/[^a-z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length > 1 && !STOPWORDS.has(w))
      .map(w => FR_ES_TO_EN[w] || w)
      .slice(0, 4) // max 4 tags
      .join(',') || 'colorful';
  },

  buildUrl(idea, opts = {}) {
    const { width = 720, height = 1280, lock = null } = opts;
    const tags = this.toTags(idea);
    // Seed deterministe par idee : meme prompt = meme image
    let h = 0;
    for (let i = 0; i < idea.length; i++) h = ((h << 5) - h + idea.charCodeAt(i)) | 0;
    const seed = lock || (Math.abs(h) % 1_000_000);
    return `${FLICKR_BASE}/${width}/${height}/${tags}?lock=${seed}`;
  },

  async generatePair(idea1, idea2, onProgress = null) {
    if (onProgress) onProgress('civils', { phase: 'submit' });
    const url1 = this.buildUrl(idea1);
    if (onProgress) onProgress('undercover', { phase: 'submit' });
    const url2 = this.buildUrl(idea2);

    return {
      civils:     { source: 'ai-image', url: url1, title: idea1.trim() },
      undercover: { source: 'ai-image', url: url2, title: idea2.trim() },
    };
  },
};

window.aiGenerator = aiGenerator;
