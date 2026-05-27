// Service Worker — cache du shell de l'app
const CACHE_NAME = 'undercover-video-v9';
const SHELL_FILES = [
  './',
  'index.html',
  'app.js',
  'i18n.js',
  'play-billing.js',
  'ai-generator.js',
  'style.css',
  'manifest.json',
  'privacy.html',
  'data/videos.json',
  'data/translations.json',
  'icons/icon-192.png',
  'icons/icon-512.png',
  'icons/icon-maskable-512.png',
  'icons/apple-touch-icon.png',
  'icons/favicon-32.png',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(SHELL_FILES))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  const isVideo = url.pathname.match(/\.(mp4|webm|mov)$/i);

  // Stratégie cache-first pour les vidéos (mises en cache à la 1ère lecture)
  if (isVideo) {
    event.respondWith(
      caches.open(CACHE_NAME).then(cache =>
        cache.match(event.request).then(cached => {
          if (cached) return cached;
          // Pas en cache : fetch + stockage. Vidéo peut être lourde, on utilise no-cors si besoin.
          return fetch(event.request).then(res => {
            if (res.ok) cache.put(event.request, res.clone());
            return res;
          });
        })
      )
    );
    return;
  }

  // Stratégie classique pour le shell
  event.respondWith(
    caches.match(event.request).then(cached =>
      cached || fetch(event.request).then(res => {
        if (res.ok) {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(event.request, clone));
        }
        return res;
      }).catch(() => cached)
    )
  );
});
