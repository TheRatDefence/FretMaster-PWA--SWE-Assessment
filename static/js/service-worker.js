const CACHE_NAME = 'fretmaster-cache-v1';

const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/css/material-theme/dark.css',
    '/exercises',
    '/login',
    '/register',
    '/manifest.json'
];

const debug = (message) => {
    console.log(`[ServiceWorker] ${message}`);
};

self.addEventListener('install', event => {
    debug('Installing Service Worker');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                debug('Caching resources');
                return cache.addAll(urlsToCache);
            })
            .then(() => {
                debug('Service Worker installed successfully');
            })
            .catch(error => {
                debug('Error during installation: ' + error);
            })
    );
});

self.addEventListener('activate', event => {
    debug('Activating Service Worker');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        debug('Deleting old cache: ' + cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    debug('Serving from cache: ' + event.request.url);
                    return response;
                }

                debug('Fetching from network: ' + event.request.url);
                return fetch(event.request);
            })
            .catch(() => {
                debug('Fetch failed for: ' + event.request.url);
            })
    );
});