/**
 * Service Worker for Helpdesk Platform
 * Provides offline support and asset caching
 */

const CACHE_NAME = 'helpdesk-v1.0.0';
const STATIC_CACHE_NAME = 'helpdesk-static-v1.0.0';
const DYNAMIC_CACHE_NAME = 'helpdesk-dynamic-v1.0.0';
const API_CACHE_NAME = 'helpdesk-api-v1.0.0';

// Assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/js/vendor.js',
  '/static/js/react.js',
  '/manifest.json',
  '/favicon.ico',
  '/offline.html'
];

// API endpoints to cache
const API_ENDPOINTS = [
  '/api/v1/tickets/',
  '/api/v1/knowledge-base/',
  '/api/v1/user/profile/',
  '/api/v1/features/flags/'
];

// Cache strategies
const CACHE_STRATEGIES = {
  // Static assets - Cache First
  static: {
    pattern: /\.(css|js|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot)$/,
    strategy: 'cacheFirst',
    cacheName: STATIC_CACHE_NAME
  },
  // API calls - Network First with fallback
  api: {
    pattern: /^\/api\//,
    strategy: 'networkFirst',
    cacheName: API_CACHE_NAME,
    timeout: 5000
  },
  // HTML pages - Stale While Revalidate
  html: {
    pattern: /\.html$/,
    strategy: 'staleWhileRevalidate',
    cacheName: DYNAMIC_CACHE_NAME
  },
  // Default - Network First
  default: {
    strategy: 'networkFirst',
    cacheName: DYNAMIC_CACHE_NAME
  }
};

/**
 * Install event - Cache static assets
 */
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(STATIC_CACHE_NAME).then(cache => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      }),
      // Cache API endpoints
      caches.open(API_CACHE_NAME).then(cache => {
        console.log('Service Worker: Caching API endpoints');
        return Promise.all(API_ENDPOINTS.map(endpoint => 
          cache.add(endpoint).catch(err => 
            console.warn(`Failed to cache ${endpoint}:`, err)
          )
        ));
      })
    ]).then(() => {
      console.log('Service Worker: Installation complete');
      return self.skipWaiting();
    })
  );
});

/**
 * Activate event - Clean up old caches
 */
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== CACHE_NAME && 
                cacheName !== STATIC_CACHE_NAME && 
                cacheName !== DYNAMIC_CACHE_NAME && 
                cacheName !== API_CACHE_NAME) {
              console.log('Service Worker: Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // Take control of all clients
      self.clients.claim()
    ]).then(() => {
      console.log('Service Worker: Activation complete');
    })
  );
});

/**
 * Fetch event - Handle requests with appropriate strategy
 */
self.addEventListener('fetch', event => {
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
  
  // Determine cache strategy
  const strategy = getCacheStrategy(request);
  
  event.respondWith(
    handleRequest(request, strategy)
  );
});

/**
 * Get cache strategy for request
 */
function getCacheStrategy(request) {
  const url = new URL(request.url);
  
  // Check for static assets
  if (CACHE_STRATEGIES.static.pattern.test(url.pathname)) {
    return CACHE_STRATEGIES.static;
  }
  
  // Check for API calls
  if (CACHE_STRATEGIES.api.pattern.test(url.pathname)) {
    return CACHE_STRATEGIES.api;
  }
  
  // Check for HTML pages
  if (CACHE_STRATEGIES.html.pattern.test(url.pathname)) {
    return CACHE_STRATEGIES.html;
  }
  
  // Default strategy
  return CACHE_STRATEGIES.default;
}

/**
 * Handle request with appropriate strategy
 */
async function handleRequest(request, strategy) {
  const cache = await caches.open(strategy.cacheName);
  
  try {
    switch (strategy.strategy) {
      case 'cacheFirst':
        return await cacheFirst(request, cache);
      case 'networkFirst':
        return await networkFirst(request, cache, strategy.timeout);
      case 'staleWhileRevalidate':
        return await staleWhileRevalidate(request, cache);
      default:
        return await networkFirst(request, cache);
    }
  } catch (error) {
    console.error('Service Worker: Error handling request:', error);
    return await getOfflineResponse(request);
  }
}

/**
 * Cache First Strategy
 */
async function cacheFirst(request, cache) {
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    console.log('Service Worker: Serving from cache:', request.url);
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.error('Service Worker: Network error for cache first:', error);
    return await getOfflineResponse(request);
  }
}

/**
 * Network First Strategy
 */
async function networkFirst(request, cache, timeout = 5000) {
  try {
    const networkResponse = await Promise.race([
      fetch(request),
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Network timeout')), timeout)
      )
    ]);
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Network failed, trying cache:', request.url);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    return await getOfflineResponse(request);
  }
}

/**
 * Stale While Revalidate Strategy
 */
async function staleWhileRevalidate(request, cache) {
  const cachedResponse = await cache.match(request);
  
  // Update cache in background
  fetch(request).then(networkResponse => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
  }).catch(error => {
    console.warn('Service Worker: Background update failed:', error);
  });
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    return await getOfflineResponse(request);
  }
}

/**
 * Get offline response
 */
async function getOfflineResponse(request) {
  const url = new URL(request.url);
  
  // Return offline page for navigation requests
  if (request.mode === 'navigate') {
    const offlineResponse = await caches.match('/offline.html');
    if (offlineResponse) {
      return offlineResponse;
    }
  }
  
  // Return cached API response if available
  const apiCache = await caches.open(API_CACHE_NAME);
  const cachedResponse = await apiCache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
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

/**
 * Background sync for offline actions
 */
self.addEventListener('sync', event => {
  console.log('Service Worker: Background sync triggered:', event.tag);
  
  if (event.tag === 'ticket-sync') {
    event.waitUntil(syncTickets());
  } else if (event.tag === 'comment-sync') {
    event.waitUntil(syncComments());
  }
});

/**
 * Sync offline tickets
 */
async function syncTickets() {
  try {
    const offlineTickets = await getOfflineData('offline-tickets');
    
    for (const ticket of offlineTickets) {
      try {
        const response = await fetch('/api/v1/tickets/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${ticket.token}`
          },
          body: JSON.stringify(ticket.data)
        });
        
        if (response.ok) {
          await removeOfflineData('offline-tickets', ticket.id);
          console.log('Service Worker: Synced ticket:', ticket.id);
        }
      } catch (error) {
        console.error('Service Worker: Failed to sync ticket:', error);
      }
    }
  } catch (error) {
    console.error('Service Worker: Background sync failed:', error);
  }
}

/**
 * Sync offline comments
 */
async function syncComments() {
  try {
    const offlineComments = await getOfflineData('offline-comments');
    
    for (const comment of offlineComments) {
      try {
        const response = await fetch(`/api/v1/tickets/${comment.ticketId}/comments/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${comment.token}`
          },
          body: JSON.stringify(comment.data)
        });
        
        if (response.ok) {
          await removeOfflineData('offline-comments', comment.id);
          console.log('Service Worker: Synced comment:', comment.id);
        }
      } catch (error) {
        console.error('Service Worker: Failed to sync comment:', error);
      }
    }
  } catch (error) {
    console.error('Service Worker: Comment sync failed:', error);
  }
}

/**
 * Get offline data from IndexedDB
 */
async function getOfflineData(storeName) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('helpdesk-offline', 1);
    
    request.onsuccess = event => {
      const db = event.target.result;
      const transaction = db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const getAllRequest = store.getAll();
      
      getAllRequest.onsuccess = () => resolve(getAllRequest.result);
      getAllRequest.onerror = () => reject(getAllRequest.error);
    };
    
    request.onerror = () => reject(request.error);
  });
}

/**
 * Remove offline data from IndexedDB
 */
async function removeOfflineData(storeName, id) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('helpdesk-offline', 1);
    
    request.onsuccess = event => {
      const db = event.target.result;
      const transaction = db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const deleteRequest = store.delete(id);
      
      deleteRequest.onsuccess = () => resolve();
      deleteRequest.onerror = () => reject(deleteRequest.error);
    };
    
    request.onerror = () => reject(request.error);
  });
}

/**
 * Message handling for communication with main thread
 */
self.addEventListener('message', event => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
    case 'CACHE_URLS':
      cacheUrls(data.urls);
      break;
    case 'CLEAR_CACHE':
      clearCache(data.cacheName);
      break;
    case 'GET_CACHE_SIZE':
      getCacheSize().then(size => {
        event.ports[0].postMessage({ type: 'CACHE_SIZE', size });
      });
      break;
  }
});

/**
 * Cache specific URLs
 */
async function cacheUrls(urls) {
  const cache = await caches.open(DYNAMIC_CACHE_NAME);
  
  for (const url of urls) {
    try {
      await cache.add(url);
      console.log('Service Worker: Cached URL:', url);
    } catch (error) {
      console.warn('Service Worker: Failed to cache URL:', url, error);
    }
  }
}

/**
 * Clear specific cache
 */
async function clearCache(cacheName) {
  const deleted = await caches.delete(cacheName);
  console.log('Service Worker: Cache cleared:', cacheName, deleted);
}

/**
 * Get cache size
 */
async function getCacheSize() {
  const cacheNames = await caches.keys();
  let totalSize = 0;
  
  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    totalSize += keys.length;
  }
  
  return totalSize;
}

console.log('Service Worker: Loaded successfully');