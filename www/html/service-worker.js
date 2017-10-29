var cacheName = 'xc_2017-04-30_-_22-08-12';

var filesToCache = [
    '/',
    '/index.html',
    '/scripts/core.js',
    '/styles/inline.css',
    '/images/ic_add_24px.svg',
    '/images/ic_delete_24px.svg',
    '/images/ic_feedback_24px.svg',
    '/images/ic_info_outline_24px.svg',
    '/images/ic_library_books_24px.svg',
    '/images/ic_menu_24px.svg',
    '/images/ic_note_add_24px.svg',
    '/images/ic_restore_24px.svg',
    '/images/ic_settings_24px.svg',
    '/images/side-nav-bg@2x.jpg'
];

self.addEventListener('install', function(e) {
    console.log('[ServiceWorker] Install');
    e.waitUntil(
        caches.open(cacheName).then(function(cache) {
            console.log('[ServiceWorker] Caching app shell');
            return cache.addAll(filesToCache);
        })
    );
});

self.addEventListener('activate', function(e) {
    console.log('[ServiceWorker] Activate');
    e.waitUntil(
    caches.keys().then(function(keyList) {
            return Promise.all(keyList.map(function(key) {
                if (key !== cacheName) {
                    console.log('[ServiceWorker] Removing old cache', key);
                    return caches.delete(key);
                }
            }));
        })
    );
});

self.addEventListener('fetch', function(e) {
    console.log('[ServiceWorker] Fetch', e.request.url);
    e.respondWith(
        caches.match(e.request).then(function(response) {
            return response || fetch(e.request);
        })
    );
});
