const CACHE_NAME = 'fretmaster-cache-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/css/material-theme/dark.css',
    '/offline',
    '/register',
    '/login',
    '/exercises',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png',
    '/manifest.json'
];

const debug = (message) => {
    console.log(`[ServiceWorker] ${message}`);
};

// Install event handler
self.addEventListener('install', event => {
    debug('Installing Service Worker');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                debug('Caching resources');
                return cache.addAll(urlsToCache);
            })
            .then(() => {
                debug('All resources cached successfully');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('[ServiceWorker] Install error:', error);
            })
    );
});

// Activate event handler
self.addEventListener('activate', event => {
    debug('Activating Service Worker');
    event.waitUntil(
        Promise.all([
            caches.keys().then(cacheNames => {
                debug('Cleaning old caches');
                return Promise.all(
                    cacheNames
                        .filter(cacheName => cacheName !== CACHE_NAME)
                        .map(cacheName => {
                            debug(`Deleting old cache: ${cacheName}`);
                            return caches.delete(cacheName);
                        })
                );
            }),
            self.clients.claim()
        ]).then(() => {
            debug('Service Worker activated and controlling pages');
        })
    );
});

// Fetch event handler (network-first strategy like PhotoJournal tutorial)
self.addEventListener('fetch', event => {
    debug(`Fetch request for: ${event.request.url}`);

    // Special handling for navigation requests (HTML pages)
    if (event.request.mode === 'navigate') {
        debug('Handling navigation request');
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    debug(`Network request successful for: ${event.request.url}`);
                    // Cache the page
                    const responseToCache = response.clone();
                    if (response.status === 200) {
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, responseToCache);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    debug('Network request failed, attempting to return offline page');
                    return caches.match(event.request)
                        .then(response => {
                            if (response) {
                                debug('Found cached page');
                                return response;
                            }
                            // Return offline page if nothing cached
                            return caches.match('/offline')
                                .then(offlinePage => {
                                    if (offlinePage) {
                                        return offlinePage;
                                    }
                                    return new Response('<h1>Offline</h1>', {
                                        headers: { 'Content-Type': 'text/html' }
                                    });
                                });
                        });
                })
        );
        return;
    }

    // For non-navigation requests (CSS, JS, images, etc.), use network-first strategy
    event.respondWith(
        fetch(event.request)
            .then(response => {
                debug(`Network request successful for: ${event.request.url}`);
                // Clone the response before caching
                const responseToCache = response.clone();

                // Only cache successful responses
                if (response.status === 200) {
                    caches.open(CACHE_NAME)
                        .then(cache => {
                            cache.put(event.request, responseToCache);
                            debug(`Cached response for: ${event.request.url}`);
                        });
                }

                return response;
            })
            .catch(() => {
                debug(`Network request failed for: ${event.request.url}, checking cache`);
                return caches.match(event.request)
                    .then(response => {
                        if (response) {
                            debug(`Found cached response for: ${event.request.url}`);
                            return response;
                        }
                        debug(`No cached response found for: ${event.request.url}`);
                        return new Response('', {
                            status: 404,
                            statusText: 'Not found'
                        });
                    });
            })
    );
});