/* Patient Care PWA — Service Worker
 * Handles offline caching (app shell) + background notifications.
 */
const CACHE = 'patient-care-v1';
const SHELL = [
  './',
  './index.html',
  './manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

/* Network-first for navigation (so updates land), cache-first for the rest. */
self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Never intercept Supabase / cross-origin API traffic — let it hit the network.
  if (url.origin !== self.location.origin) return;

  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
        return res;
      }).catch(() => caches.match(req).then((r) => r || caches.match('./index.html')))
    );
    return;
  }

  event.respondWith(
    caches.match(req).then((cached) => cached || fetch(req).then((res) => {
      if (res && res.status === 200 && res.type === 'basic') {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
      }
      return res;
    }).catch(() => cached))
  );
});

/* ---- Notifications ----
 * The page posts { type:'notify', title, body, tag } and we show it, so
 * alerts still fire when the tab is backgrounded (SW stays alive briefly).
 */
self.addEventListener('message', (event) => {
  const data = event.data || {};
  if (data.type === 'notify') {
    self.registration.showNotification(data.title || 'Patient Care', {
      body: data.body || '',
      tag: data.tag || 'patient-care',
      renotify: true,
      icon: data.icon,
      badge: data.icon,
      vibrate: [200, 100, 200],
      requireInteraction: !!data.sticky,
      data: { url: data.url || './' }
    });
  }
});

self.addEventListener('push', (event) => {
  let payload = { title: 'Patient Care', body: 'You have a scheduled task due.' };
  try { if (event.data) payload = Object.assign(payload, event.data.json()); } catch (e) {}
  event.waitUntil(self.registration.showNotification(payload.title, {
    body: payload.body,
    tag: payload.tag || 'patient-care-push',
    renotify: true,
    vibrate: [200, 100, 200],
    data: { url: payload.url || './' }
  }));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const target = (event.notification.data && event.notification.data.url) || './';
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((list) => {
      for (const c of list) {
        if ('focus' in c) return c.focus();
      }
      if (self.clients.openWindow) return self.clients.openWindow(target);
    })
  );
});
