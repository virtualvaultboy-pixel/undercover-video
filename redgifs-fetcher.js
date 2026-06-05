// ============================================================
// Redgifs Fetcher (mode adulte 18+ uniquement)
// Aucun contenu n'est heberge dans ce projet : on fetche depuis
// Redgifs.com via leur API publique. URLs videos = leurs CDN.
//
// Doc API : https://github.com/Redgifs/api/wiki
// Token temporaire (23h), cache en sessionStorage.
// ============================================================

// Redgifs CORS = redgifs.com seul -> on passe par un proxy.
// Worker Cloudflare deploye par defaut (URL du proprietaire de l'app).
// L'utilisateur peut override avec son propre Worker via localStorage.
const DEFAULT_WORKER = 'https://undercover-cors.virtual-vaultboy.workers.dev';

function getProxies() {
  const customWorker = (localStorage.getItem('rg_worker_url') || '').trim() || DEFAULT_WORKER;
  const base = customWorker.replace(/\/+$/, '');
  const publicProxies = [
    (u) => 'https://corsproxy.io/?' + encodeURIComponent(u),
    (u) => 'https://api.allorigins.win/raw?url=' + encodeURIComponent(u),
    (u) => 'https://api.codetabs.com/v1/proxy?quest=' + encodeURIComponent(u),
    (u) => 'https://proxy.cors.sh/' + u,
  ];
  // Worker en PREMIER (fiable). Proxies publics en fallback.
  return [(u) => base + '/?url=' + encodeURIComponent(u), ...publicProxies];
}
const PROXIES = getProxies();
const REDGIFS_BASE = 'https://api.redgifs.com/v2';
const TOKEN_KEY = 'rg_tok';
const TOKEN_TTL_MS = 23 * 60 * 60 * 1000; // 23h

/** Tente la requete via chaque proxy avec timeout 8s, jusqu'a un 2xx. */
async function fetchViaProxies(url, opts = {}, perProxyTimeoutMs = 12000) {
  let lastErr;
  // Re-evaluation pour prendre en compte localStorage modifie depuis le chargement
  const proxies = getProxies();
  for (let i = 0; i < proxies.length; i++) {
    const buildUrl = proxies[i];
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), perProxyTimeoutMs);
    try {
      console.log('[Redgifs] try proxy', i + 1, '/', proxies.length, '→', buildUrl(url).slice(0, 80));
      const r = await fetch(buildUrl(url), { ...opts, signal: controller.signal });
      clearTimeout(timer);
      if (r.ok) {
        console.log('[Redgifs] ✅ proxy', i + 1, 'OK');
        return r;
      }
      lastErr = new Error('proxy_' + (i + 1) + '_status_' + r.status);
      console.warn('[Redgifs] ❌ proxy', i + 1, 'HTTP', r.status);
    } catch (e) {
      clearTimeout(timer);
      lastErr = e;
      console.warn('[Redgifs] ❌ proxy', i + 1, 'error:', e.message);
    }
  }
  throw new Error('all_' + proxies.length + '_proxies_failed_last_' + (lastErr && lastErr.message || '?'));
}

async function getToken() {
  try {
    const cached = JSON.parse(sessionStorage.getItem(TOKEN_KEY) || 'null');
    if (cached && cached.token && Date.now() < cached.expires) {
      return cached.token;
    }
  } catch {}
  const r = await fetchViaProxies(`${REDGIFS_BASE}/auth/temporary`);
  const data = await r.json();
  if (!data || !data.token) throw new Error('redgifs_no_token');
  sessionStorage.setItem(TOKEN_KEY, JSON.stringify({
    token: data.token,
    expires: Date.now() + TOKEN_TTL_MS,
  }));
  return data.token;
}

async function search(query, count = 30, order = 'trending') {
  const token = await getToken();
  const url = `${REDGIFS_BASE}/gifs/search?search_text=${encodeURIComponent(query)}&count=${count}&order=${order}`;
  const r = await fetchViaProxies(url, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  const data = await r.json();
  // Si vide ou erreur, retry avec order=recent (plus permissif)
  if (!data || !Array.isArray(data.gifs) || data.gifs.length === 0) {
    if (order !== 'recent') {
      console.warn('[Redgifs] empty result for', query, 'with order', order, '-> retry recent');
      return search(query, count, 'recent');
    }
  }
  return data;
}

/**
 * Tire une video aleatoire matching la query (cache 30 candidates, en prend 1).
 * Renvoie { source: 'redgifs', url, title, duration, id }.
 * IMPORTANT : l'URL renvoyee passe DEJA par le Worker car le CDN Redgifs
 * (files.redgifs.com) bloque les requetes sans Referer redgifs.com.
 */
async function fetchRandomVideo(query) {
  const data = await search(query, 30);
  // Filtre : duration > 6s (evite teasers/photos), urls hd ou sd dispo
  const gifs = (data.gifs || []).filter(g => g.urls && (g.urls.hd || g.urls.sd) && (g.duration || 10) > 6);
  if (gifs.length === 0) throw new Error('no_results_for_' + query);
  // Shuffle, prend 4 candidates : si la 1ere plante au <video> load,
  // le tag video essaie la suivante automatiquement.
  const shuffled = [...gifs].sort(() => Math.random() - 0.5).slice(0, 4);
  const workerBase = ((localStorage.getItem('rg_worker_url') || '').trim() || DEFAULT_WORKER).replace(/\/+$/, '');
  const wrap = (u) => workerBase + '/?url=' + encodeURIComponent(u);
  const candidates = shuffled.map(g => wrap(g.urls.hd || g.urls.sd));
  const first = shuffled[0];
  return {
    source: 'redgifs',
    url: candidates[0],
    candidates,
    originalUrl: first.urls.hd || first.urls.sd,
    title: (first.tags && first.tags[0]) || query,
    duration: first.duration || 10,
    id: first.id,
  };
}

/**
 * Genere une paire de videos (civils + undercover) a partir de 2 queries.
 * Tente Promise.all ; si echec, retry sequentiel pour avoir des erreurs claires.
 */
async function generatePair(query1, query2) {
  try {
    const [v1, v2] = await Promise.all([
      fetchRandomVideo(query1),
      fetchRandomVideo(query2),
    ]);
    return {
      civils: { ...v1, title: query1.trim() },
      undercover: { ...v2, title: query2.trim() },
    };
  } catch (e) {
    // Re-essaie en sequentiel pour identifier laquelle a foire
    let v1, v2;
    try { v1 = await fetchRandomVideo(query1); }
    catch (e1) { throw new Error('civils_failed_' + query1 + ': ' + e1.message); }
    try { v2 = await fetchRandomVideo(query2); }
    catch (e2) { throw new Error('undercover_failed_' + query2 + ': ' + e2.message); }
    return {
      civils: { ...v1, title: query1.trim() },
      undercover: { ...v2, title: query2.trim() },
    };
  }
}

window.redgifsFetcher = { fetchRandomVideo, generatePair, search };
