/**
 * Enhanced Service Worker for Offline Functionality
 * Provides comprehensive offline support with caching strategies
 */

const CACHE_NAME = 'customer-portal-v1';
const OFFLINE_CACHE = 'customer-portal-offline-v1';
const API_CACHE = 'customer-portal-api-v1';

// Cache strategies
const CACHE_STRATEGIES = {
  // Cache first, then network
  CACHE_FIRST: 'cache-first',
  // Network first, then cache
  NETWORK_FIRST: 'network-first',
  // Stale while revalidate
  STALE_WHILE_REVALIDATE: 'stale-while-revalidate',
  // Network only
  NETWORK_ONLY: 'network-only',
  // Cache only
  CACHE_ONLY: 'cache-only'
};

// Routes and their caching strategies
const ROUTE_STRATEGIES = {
  // Static assets - cache first
  '/static/': CACHE_STRATEGIES.CACHE_FIRST,
  '/assets/': CACHE_STRATEGIES.CACHE_FIRST,
  '/images/': CACHE_STRATEGIES.CACHE_FIRST,
  
  // API endpoints - network first
  '/api/v1/': CACHE_STRATEGIES.NETWORK_FIRST,
  
  // HTML pages - stale while revalidate
  '/': CACHE_STRATEGIES.STALE_WHILE_REVALIDATE,
  '/dashboard': CACHE_STRATEGIES.STALE_WHILE_REVALIDATE,
  '/tickets': CACHE_STRATEGIES.STALE_WHILE_REVALIDATE
};

// Install event - cache essential resources
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching essential resources');
        return cache.addAll([
          '/',
          '/static/js/bundle.js',
          '/static/css/main.css',
          '/manifest.json',
          '/offline.html'
        ]);
      })
      .then(() => {
        console.log('Service Worker: Installation complete');
        return self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && 
                cacheName !== OFFLINE_CACHE && 
                cacheName !== API_CACHE) {
              console.log('Service Worker: Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip chrome-extension and other non-http requests
  if (!url.protocol.startsWith('http')) {
    return;
  }
  
  // Determine caching strategy based on URL
  const strategy = getCachingStrategy(url.pathname);
  
  event.respondWith(
    handleRequest(request, strategy)
  );
});

// Handle request based on caching strategy
async function handleRequest(request, strategy) {
  const url = new URL(request.url);
  
  try {
    switch (strategy) {
      case CACHE_STRATEGIES.CACHE_FIRST:
        return await cacheFirst(request);
      
      case CACHE_STRATEGIES.NETWORK_FIRST:
        return await networkFirst(request);
      
      case CACHE_STRATEGIES.STALE_WHILE_REVALIDATE:
        return await staleWhileRevalidate(request);
      
      case CACHE_STRATEGIES.NETWORK_ONLY:
        return await networkOnly(request);
      
      case CACHE_STRATEGIES.CACHE_ONLY:
        return await cacheOnly(request);
      
      default:
        return await networkFirst(request);
    }
  } catch (error) {
    console.error('Service Worker: Error handling request:', error);
    return await handleOfflineFallback(request);
  }
}

// Cache first strategy
async function cacheFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  const networkResponse = await fetch(request);
  if (networkResponse.ok) {
    cache.put(request, networkResponse.clone());
  }
  
  return networkResponse;
}

// Network first strategy
async function networkFirst(request) {
  const cache = await caches.open(API_CACHE);
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

// Stale while revalidate strategy
async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  const fetchPromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  });
  
  return cachedResponse || fetchPromise;
}

// Network only strategy
async function networkOnly(request) {
  return await fetch(request);
}

// Cache only strategy
async function cacheOnly(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  if (!cachedResponse) {
    throw new Error('No cached response available');
  }
  
  return cachedResponse;
}

// Handle offline fallback
async function handleOfflineFallback(request) {
  const url = new URL(request.url);
  
  // Return offline page for navigation requests
  if (request.mode === 'navigate') {
    const offlineCache = await caches.open(OFFLINE_CACHE);
    const offlineResponse = await offlineCache.match('/offline.html');
    
    if (offlineResponse) {
      return offlineResponse;
    }
  }
  
  // Return cached API response for API requests
  if (url.pathname.startsWith('/api/')) {
    const apiCache = await caches.open(API_CACHE);
    const cachedResponse = await apiCache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
  }
  
  // Return generic offline response
  return new Response(
    JSON.stringify({
      error: 'Offline',
      message: 'You are currently offline. Please check your connection.',
      timestamp: new Date().toISOString()
    }),
    {
      status: 503,
      statusText: 'Service Unavailable',
      headers: {
        'Content-Type': 'application/json'
      }
    }
  );
}

// Get caching strategy for URL
function getCachingStrategy(pathname) {
  for (const [route, strategy] of Object.entries(ROUTE_STRATEGIES)) {
    if (pathname.startsWith(route)) {
      return strategy;
    }
  }
  
  // Default strategy
  return CACHE_STRATEGIES.NETWORK_FIRST;
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Background sync triggered');
  
  if (event.tag === 'background-sync') {
    event.waitUntil(handleBackgroundSync());
  }
});

// Handle background sync
async function handleBackgroundSync() {
  try {
    // Get pending offline actions
    const pendingActions = await getPendingOfflineActions();
    
    for (const action of pendingActions) {
      await processOfflineAction(action);
    }
    
    console.log('Service Worker: Background sync completed');
  } catch (error) {
    console.error('Service Worker: Background sync failed:', error);
  }
}

// Get pending offline actions from IndexedDB
async function getPendingOfflineActions() {
  // This would typically read from IndexedDB
  // For now, return empty array
  return [];
}

// Process offline action
async function processOfflineAction(action) {
  try {
    const response = await fetch(action.url, {
      method: action.method,
      headers: action.headers,
      body: action.body
    });
    
    if (response.ok) {
      // Remove from pending actions
      await removePendingAction(action.id);
      console.log('Service Worker: Offline action processed:', action.id);
    }
  } catch (error) {
    console.error('Service Worker: Failed to process offline action:', error);
  }
}

// Remove pending action from IndexedDB
async function removePendingAction(actionId) {
  // This would typically remove from IndexedDB
  console.log('Service Worker: Removing pending action:', actionId);
}

// Push notifications
self.addEventListener('push', (event) => {
  console.log('Service Worker: Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'New notification',
    icon: '/icon-192x192.png',
    badge: '/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Details',
        icon: '/icon-192x192.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icon-192x192.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('Customer Portal', options)
  );
});

// Notification click
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Notification clicked');
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/dashboard')
    );
  }
});

// Message handling
self.addEventListener('message', (event) => {
  console.log('Service Worker: Message received:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
});

console.log('Service Worker: Script loaded');
