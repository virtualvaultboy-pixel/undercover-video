/**
 * Undercover Video — Cloudflare Worker CORS Proxy
 *
 * Proxie les requetes vers Redgifs.com en ajoutant les headers
 * Origin/Referer requis + CORS pour qu'elles soient autorisees
 * depuis ton site github.io.
 *
 * Free tier Cloudflare : 100 000 requetes/jour. Largement suffisant.
 *
 * Deploiement (voir README.md) :
 *   1. https://dash.cloudflare.com/ -> Workers -> Create Worker
 *   2. Colle ce fichier dans l'editeur
 *   3. Deploy
 *   4. Copie l'URL (https://undercover-cors.TON-COMPTE.workers.dev)
 *   5. Colle-la dans l'app Undercover (Options > URL Worker custom)
 */

export default {
  async fetch(request) {
    const url = new URL(request.url);

    // Preflight CORS
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Max-Age': '86400',
        },
      });
    }

    const target = url.searchParams.get('url');
    if (!target) {
      return new Response('Missing ?url= parameter', { status: 400 });
    }

    // Forward la requete avec spoof Origin/Referer Redgifs (sinon CDN bloque)
    const headers = new Headers();
    const auth = request.headers.get('Authorization');
    if (auth) headers.set('Authorization', auth);
    headers.set('User-Agent', 'Mozilla/5.0 UndercoverVideo/1.0');
    headers.set('Origin', 'https://www.redgifs.com');
    headers.set('Referer', 'https://www.redgifs.com/');

    let response;
    try {
      response = await fetch(target, {
        method: request.method,
        headers,
        redirect: 'follow',
      });
    } catch (e) {
      return new Response('Upstream error: ' + e.message, {
        status: 502,
        headers: { 'Access-Control-Allow-Origin': '*' },
      });
    }

    // Renvoie avec headers CORS permissifs
    const respHeaders = new Headers(response.headers);
    respHeaders.set('Access-Control-Allow-Origin', '*');
    respHeaders.set('Access-Control-Allow-Headers', '*');
    respHeaders.set('Access-Control-Expose-Headers', '*');

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: respHeaders,
    });
  },
};
