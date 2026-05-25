// ============================================================
// AI Image Generator via Pollinations.ai
// Gratuit, sans cle API, sans rate limit perceptible.
// https://pollinations.ai
// ============================================================

const POLLINATIONS_BASE = 'https://image.pollinations.ai/prompt/';

const aiGenerator = {
  /**
   * Construit l'URL d'une image generee. Pollinations renvoie une PNG directement
   * avec un long pipeline derriere. Le seed assure deux generations differentes
   * meme pour le meme prompt.
   */
  buildUrl(prompt, opts = {}) {
    const {
      width = 720,
      height = 1024,
      seed = Math.floor(Math.random() * 1000000),
      model = 'flux',
      nologo = true,
      enhance = true,
    } = opts;

    const params = new URLSearchParams({
      width: String(width),
      height: String(height),
      seed: String(seed),
      model,
      nologo: nologo ? 'true' : 'false',
      enhance: enhance ? 'true' : 'false',
    });
    const cleanPrompt = encodeURIComponent(prompt.trim());
    return `${POLLINATIONS_BASE}${cleanPrompt}?${params.toString()}`;
  },

  /**
   * Genere une paire d'images a partir de 2 idees utilisateur.
   * Les 2 idees sont enrichies pour avoir un style coherent entre elles
   * (meme style cinematographique, eclairage, etc.) afin de rester dans
   * l'esprit "proches mais differentes" du jeu Undercover.
   */
  generatePair(idea1, idea2, lang = 'fr') {
    // Petit boost de style pour homogeneiser les 2 images
    const styleBoost = ', cinematic lighting, vivid colors, high quality, centered subject';
    const promptA = idea1.trim() + styleBoost;
    const promptB = idea2.trim() + styleBoost;

    // Meme seed pour les 2 images = composition similaire, sujet different
    const sharedSeed = Math.floor(Math.random() * 1000000);

    return {
      civils: {
        source: 'ai-image',
        url: this.buildUrl(promptA, { seed: sharedSeed }),
        title: idea1.trim(),
      },
      undercover: {
        source: 'ai-image',
        url: this.buildUrl(promptB, { seed: sharedSeed }),
        title: idea2.trim(),
      },
    };
  },

  /**
   * Precharge une image en arriere-plan (declenche la generation cote serveur)
   * pour minimiser l'attente au moment de l'afficher.
   */
  prefetch(url) {
    const img = new Image();
    img.src = url;
    return img;
  },
};

window.aiGenerator = aiGenerator;
