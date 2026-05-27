// ============================================================
// Image Generator via LoremFlickr (photos Flickr taggees)
// Gratuit, instant, sans token. Plus fiable que les services IA gratuits
// qui sont systematiquement satures en 2026 (Pollinations 402, Horde 1400s queue).
// https://loremflickr.com
// ============================================================

const FLICKR_BASE = 'https://loremflickr.com';

const aiGenerator = {
  /**
   * Convertit une saisie utilisateur libre en tags Flickr.
   * "un chat qui mange une pizza" -> "chat,mange,pizza"
   */
  toTags(text) {
    const stopWords = new Set([
      'un', 'une', 'des', 'le', 'la', 'les', 'du', 'de', 'qui', 'que', 'a', 'au', 'aux',
      'the', 'a', 'an', 'and', 'or', 'of', 'in', 'on', 'with', 'who', 'that',
      'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'que',
    ]);
    return text
      .toLowerCase()
      .normalize('NFD').replace(/[̀-ͯ]/g, '') // retire accents
      .replace(/[^a-z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length > 1 && !stopWords.has(w))
      .slice(0, 4) // max 4 tags
      .join(',') || 'image';
  },

  /**
   * Construit l'URL d'une image Flickr matching les tags.
   */
  buildUrl(idea, opts = {}) {
    const { width = 512, height = 720, lock = null } = opts;
    const tags = this.toTags(idea);
    const seed = lock || Math.floor(Math.random() * 1_000_000);
    return `${FLICKR_BASE}/${width}/${height}/${tags}?lock=${seed}`;
  },

  /**
   * Genere une paire d'images "proches mais differentes" a partir de 2 idees.
   * Pas de polling, URLs immediates.
   */
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
