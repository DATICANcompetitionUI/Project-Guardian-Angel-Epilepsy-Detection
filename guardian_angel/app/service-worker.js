// Guardian Angel - Service Worker
const CACHE_NAME = 'guardian-angel-v1';
const urlsToCache = [
  '/',
  '/app',
  '/app/manifest.json',
  '/app/icon-192.png',
  '/app/icon-512.png'
];

// Install event - cache assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Activate event - clean old caches
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event - serve from cache first, then network
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }
        return fetch(event.request).then(
          response => {
            // Check if we received a valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clone the response
            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return response;
          }
        );
      })
  );
});

// Push notification support
self.addEventListener('push', event => {
  const options = {
    body: event.data.text(),
    icon: 'icon-192.png',
    badge: 'icon-72.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      { action: 'ok', title: '✅ I\'m Fine' },
      { action: 'help', title: '🚨 I Need Help' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('🚨 Guardian Angel Alert', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'ok') {
    // User is fine - send to app
    event.waitUntil(
      clients.openWindow('/?status=ok')
    );
  } else if (event.action === 'help') {
    // User needs help - emergency
    event.waitUntil(
      clients.openWindow('/?status=emergency')
    );
  } else {
    // Default - open app
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});