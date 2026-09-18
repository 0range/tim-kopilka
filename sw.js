'use strict';

// Bump the version when changing the shell or icons. Game saves live in localStorage.
const CACHE = 'tim-kopilka-shell-v3';
const PHOTOS = 'tim-kopilka-photos-v1';
const GALLERY = new URL('assets/gallery/', self.registration.scope).href;
const SHELL = new URL('index.html', self.registration.scope).href;
const ASSETS = ['index.html', 'manifest.webmanifest', 'icons/coin-192.png',
  'icons/coin-512.png', 'icons/apple-touch-icon.png'];
const assetURLs = new Set(ASSETS.map(path => new URL(path, self.registration.scope).href));

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(ASSETS))
    .then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys
    .filter(key => key.startsWith('tim-kopilka-shell-') && key !== CACHE)
    .map(key => caches.delete(key)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  url.search = '';
  const isGame = url.href === self.registration.scope || url.href === SHELL
    || url.href === new URL('tim-kopilka-v4.html', self.registration.scope).href;
  if (event.request.mode === 'navigate' && isGame) {
    event.respondWith((async () => {
      try {
        const response = await fetch(event.request);
        if (!response.ok) throw new Error('Site unavailable');
        if (response.headers.get('Content-Type')?.includes('text/html')) {
          const cache = await caches.open(CACHE);
          // Never cache the legacy redirect in place of the game.
          if (url.href !== new URL('tim-kopilka-v4.html', self.registration.scope).href) {
            try { await cache.put(SHELL, response.clone()); } catch { /* Cache may be full. */ }
          }
        }
        return response;
      } catch {
        const saved = await caches.match(SHELL);
        return saved || Response.error();
      }
    })());
  } else if (url.href.startsWith(GALLERY) && url.pathname.endsWith('.webp')) {
    // Content-hashed local photos are immutable. Save only those the child views.
    event.respondWith((async () => {
      const cache = await caches.open(PHOTOS);
      const saved = await cache.match(url.href);
      if (saved) return saved;
      const response = await fetch(event.request);
      if (response.ok && response.headers.get('Content-Type')?.startsWith('image/')) {
        try { await cache.put(url.href, response.clone()); } catch { /* Keep playing if full. */ }
      }
      return response;
    })());
  } else if (assetURLs.has(url.href)) {
    event.respondWith(caches.match(url.href).then(saved => saved || fetch(event.request)));
  }
});
