// ============================================================
// Redgifs Fetcher (mode adulte 18+ uniquement)
// Aucun contenu n'est heberge dans ce projet : on fetche depuis
// Redgifs.com via leur API publique. URLs videos = leurs CDN.
//
// Doc API : https://github.com/Redgifs/api/wiki
// Token temporaire (23h), cache en sessionStorage.
// ============================================================

const REDGIFS_BASE = 'https://api.redgifs.com/v2';
const TOKEN_KEY = 'rg_tok';
const TOKEN_TTL_MS = 23 * 60 * 60 * 1000; // 23h

async function getToken() {
  try {
    const cached = JSON.parse(sessionStorage.getItem(TOKEN_KEY) || 'null');
    if (cached && cached.token && Date.now() < cached.expires) {
      return cached.token;
    }
  } catch {}
  const r = await fetch(`${REDGIFS_BASE}/auth/temporary`);
  if (!r.ok) throw new Error('redgifs_auth_failed_' + r.status);
  const data = await r.json();
  sessionStorage.setItem(TOKEN_KEY, JSON.stringify({
    token: data.token,
    expires: Date.now() + TOKEN_TTL_MS,
  }));
  return data.token;
}

async function search(query, count = 20, order = 'trending') {
  const token = await getToken();
  const url = `${REDGIFS_BASE}/gifs/search?search_text=${encodeURIComponent(query)}&count=${count}&order=${order}`;
  const r = await fetch(url, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  if (!r.ok) throw new Error('redgifs_search_failed_' + r.status);
  return await r.json();
}

/**
 * Tire une video aleatoire matching la query (cache 30 candidates, en prend 1).
 * Renvoie { source: 'redgifs', url, title, duration, id }.
 */
async function fetchRandomVideo(query) {
  const data = await search(query, 30);
  const gifs = (data.gifs || []).filter(g => g.urls && (g.urls.hd || g.urls.sd));
  if (gifs.length === 0) throw new Error('no_results_for_' + query);
  const gif = gifs[Math.floor(Math.random() * gifs.length)];
  const url = gif.urls.hd || gif.urls.sd;
  return {
    source: 'redgifs',
    url,
    title: (gif.tags && gif.tags[0]) || query,
    duration: gif.duration || 10,
    id: gif.id,
  };
}

/**
 * Genere une paire de videos (civils + undercover) a partir de 2 queries.
 * Comme Custom AI mais avec Redgifs.
 */
async function generatePair(query1, query2) {
  const [v1, v2] = await Promise.all([
    fetchRandomVideo(query1),
    fetchRandomVideo(query2),
  ]);
  return {
    civils: { ...v1, title: query1.trim() },
    undercover: { ...v2, title: query2.trim() },
  };
}

window.redgifsFetcher = { fetchRandomVideo, generatePair, search };
