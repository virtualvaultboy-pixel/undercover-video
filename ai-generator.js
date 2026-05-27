// ============================================================
// AI Image Generator via Stable Horde
// 100% gratuit, sans token API. Asynchrone (job + polling).
// https://stablehorde.net
// ============================================================

const HORDE_API = 'https://stablehorde.net/api/v2';
const ANON_KEY = '0000000000'; // clé anonyme officielle
const MAX_DIM = 512; // au-delà il faut des "kudos" (réputation)

const aiGenerator = {
  /**
   * Soumet une génération à Stable Horde, retourne l'ID du job.
   */
  async submit(prompt, opts = {}) {
    const {
      width = MAX_DIM,
      height = MAX_DIM,
      steps = 20,
      seed = null,
    } = opts;

    const body = {
      prompt: prompt.trim() + ', cinematic lighting, vivid colors, high quality, centered subject',
      params: { width, height, steps, n: 1, ...(seed ? { seed: String(seed) } : {}) },
      nsfw: false,
      censor_nsfw: true,
      r2: true, // images servies via R2 (URL publique)
    };

    const res = await fetch(`${HORDE_API}/generate/async`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': ANON_KEY,
        'Client-Agent': 'UndercoverVideo:1.6:bjgenius.contact@gmail.com',
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.text().catch(() => '');
      throw new Error(`submit_failed_${res.status}: ${err.slice(0, 100)}`);
    }
    const data = await res.json();
    return data.id;
  },

  /**
   * Poll le statut d'un job jusqu'à done ou timeout.
   * onProgress(state) appelé à chaque tick avec { waiting, processing, finished, done, queue_position, wait_time }
   */
  async poll(jobId, onProgress = null, opts = {}) {
    const { intervalMs = 3000, timeoutMs = 180000 } = opts;
    const start = Date.now();

    while (Date.now() - start < timeoutMs) {
      const res = await fetch(`${HORDE_API}/generate/check/${jobId}`);
      if (!res.ok) throw new Error(`check_failed_${res.status}`);
      const status = await res.json();
      if (onProgress) onProgress(status);

      if (status.done) {
        // Récupère le résultat final
        const final = await fetch(`${HORDE_API}/generate/status/${jobId}`);
        if (!final.ok) throw new Error(`status_failed_${final.status}`);
        const result = await final.json();
        if (!result.generations || result.generations.length === 0) {
          throw new Error('no_generation');
        }
        return result.generations[0].img; // URL de l'image
      }

      if (status.faulted) throw new Error('horde_faulted');

      await new Promise(r => setTimeout(r, intervalMs));
    }
    throw new Error('horde_timeout');
  },

  /**
   * Génère une paire d'images "proches mais différentes".
   * onProgress(role, status) appelé pour chaque étape.
   */
  async generatePair(idea1, idea2, onProgress = null) {
    const sharedSeed = Math.floor(Math.random() * 1_000_000);

    // 1ère image : civils
    if (onProgress) onProgress('civils', { phase: 'submit' });
    const id1 = await this.submit(idea1, { seed: sharedSeed });
    const url1 = await this.poll(id1, s => onProgress && onProgress('civils', s));

    // 2e image : undercover
    if (onProgress) onProgress('undercover', { phase: 'submit' });
    const id2 = await this.submit(idea2, { seed: sharedSeed });
    const url2 = await this.poll(id2, s => onProgress && onProgress('undercover', s));

    return {
      civils:     { source: 'ai-image', url: url1, title: idea1.trim() },
      undercover: { source: 'ai-image', url: url2, title: idea2.trim() },
    };
  },
};

window.aiGenerator = aiGenerator;
