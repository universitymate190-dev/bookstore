self.addEventListener('install', function(event) {
    console.log('[Service Worker] Installed');
    self.skipWaiting();
});

self.addEventListener('activate', function(event) {
    console.log('[Service Worker] Activated');
    return self.clients.claim();
});

// Listen for push events (requires a push service integration)
self.addEventListener('push', function(event) {
    console.log('[Service Worker] Push received.');
    let data = {};
    if (event.data) {
        data = event.data.json();
    }
    const title = data.title || 'New Notification';
    const options = {
        body: data.body || '',
        icon: data.icon || '/static/icon.png',
        badge: data.badge || '/static/badge.png'
    };
    event.waitUntil(self.registration.showNotification(title, options));
});

// Notification click handler
self.addEventListener('notificationclick', function(event) {
    console.log('[Service Worker] Notification click Received.');
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/')
    );
});