// ============================================================
// Image Generator via Pollinations.ai (Flux model, text-to-image AI)
// Gratuit, sans token, vraie generation AI matching le prompt.
// Multilingue (FR/EN/ES OK). Genere a la demande quand on hit l'URL.
// https://pollinations.ai
// ============================================================

const POLLINATIONS_BASE = 'https://image.pollinations.ai/prompt';

const aiGenerator = {
  /**
   * Construit une URL Pollinations.ai pour generer une image AI
   * a partir d'une description en texte libre.
   * Le modele Flux comprend FR/EN/ES + genere une image coherente
   * avec le prompt (vs LoremFlickr qui ne fait que matching de tags).
   */
  buildUrl(idea, opts = {}) {
    const {
      width = 720,
      height = 1280,
      model = 'flux',
      enhance = true,
    } = opts;
    const prompt = encodeURIComponent(idea.trim());
    // Seed deterministe par prompt (cache cote Pollinations + reproductibilite)
    let h = 0;
    for (let i = 0; i < idea.length; i++) h = ((h << 5) - h + idea.charCodeAt(i)) | 0;
    const seed = Math.abs(h) % 1_000_000;
    const params = new URLSearchParams({
      width: String(width),
      height: String(height),
      seed: String(seed),
      model,
      nologo: 'true',
    });
    if (enhance) params.set('enhance', 'true');
    return `${POLLINATIONS_BASE}/${prompt}?${params.toString()}`;
  },

  /**
   * Genere une paire d'images (civils + undercover) a partir de 2 idees.
   * Pollinations.ai genere a la demande quand l'URL est chargee dans <img>.
   * Temps : 5-25s par image selon charge serveur.
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
