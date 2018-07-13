//Latest CACHE_NAME
var CACHE_NAME = '[v0.1.0] spoken-tutorials';

//Files to be Cached - List made in base.html
var urlsToCache = [
    '/static/spoken/css/bootstrap.min.css',
    '/static/spoken/css/font-awesome.min.css',
    '/static/spoken/css/main.css',
    '/static/spoken/css/videojs.min.css',
    '/static/spoken/js/jquery-1.11.0.min.js',
    '/static/spoken/js/bootstrap.min.js',
    '/static/spoken/js/videojs.min.js',
    '/static/spoken/js/popcorn.min.js',
    '/static/spoken/js/video.settings.js',
];

// Perform install steps
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
        return cache.addAll(urlsToCache);
    }).catch(function(Error) {
        console.log(urlsToCache);
        console.log(Error);
    })
  );
});

// Activation is done Everytime a page loads!
self.addEventListener('activate', function(event) {
    console.log('[ServiceWorker] Activated');
    event.waitUntil(
        caches.keys().then(function(keyList) {
            return Promise.all(keyList.map(function(key) {
                if (key !== CACHE_NAME) {
                    console.log('[ServiceWorker] Removing Obselete Cache: ', key);
                    return caches.delete(key);
                }
            }));
        })
    );
    return self.clients.claim();
});


//Called Everytime a resource is needed!
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request, {ignoreSearch:true}).then(response => {
      return response || fetch(event.request);
    })
  );
});