// ============================================================
// AI Image Generator via Pollinations.ai
// Gratuit, sans cle API. Avec retry + fallback de modele.
// https://pollinations.ai
// ============================================================

const POLLINATIONS_BASE = 'https://image.pollinations.ai/prompt/';
// Pollinations propose plusieurs modeles ; "turbo" est nettement plus rapide
// et plus stable que "flux" en cas de surcharge. On le prefere par defaut.
const PREFERRED_MODELS = ['turbo', 'flux'];

const aiGenerator = {
  /**
   * Construit l'URL d'une image generee.
   */
  buildUrl(prompt, opts = {}) {
    const {
      width = 720,
      height = 1024,
      seed = Math.floor(Math.random() * 1_000_000),
      model = 'turbo',
      nologo = true,
      enhance = true,
      nofeed = true, // ne publie pas l'image dans le feed public Pollinations
    } = opts;

    const params = new URLSearchParams({
      width: String(width),
      height: String(height),
      seed: String(seed),
      model,
      nologo: nologo ? 'true' : 'false',
      enhance: enhance ? 'true' : 'false',
      nofeed: nofeed ? 'true' : 'false',
    });
    const cleanPrompt = encodeURIComponent(prompt.trim());
    return `${POLLINATIONS_BASE}${cleanPrompt}?${params.toString()}`;
  },

  /**
   * Genere une paire d'images "proches mais differentes".
   * Le seed partage assure une composition similaire.
   * Retourne 3 URLs candidates par image (modeles + fallback) que l'app
   * tentera de charger l'une apres l'autre en cas d'echec.
   */
  generatePair(idea1, idea2) {
    const styleBoost = ', cinematic lighting, vivid colors, high quality, centered subject';
    const promptA = idea1.trim() + styleBoost;
    const promptB = idea2.trim() + styleBoost;
    const sharedSeed = Math.floor(Math.random() * 1_000_000);

    const buildCandidates = (prompt, seedShift) => {
      const candidates = [];
      // Essai principal + retry avec seed legerement different
      for (const model of PREFERRED_MODELS) {
        candidates.push(this.buildUrl(prompt, { seed: sharedSeed + seedShift, model }));
        candidates.push(this.buildUrl(prompt, { seed: sharedSeed + seedShift + 1000, model }));
      }
      return candidates;
    };

    return {
      civils: {
        source: 'ai-image',
        url: buildCandidates(promptA, 0)[0],
        urls: buildCandidates(promptA, 0),
        title: idea1.trim(),
      },
      undercover: {
        source: 'ai-image',
        url: buildCandidates(promptB, 0)[0],
        urls: buildCandidates(promptB, 0),
        title: idea2.trim(),
      },
    };
  },
};

window.aiGenerator = aiGenerator;
