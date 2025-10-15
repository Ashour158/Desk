/**
 * Service Worker registration and management for offline support and caching
 */

/**
 * Register service worker for offline support and caching
 * @param {string} swPath - Service worker path
 * @returns {Promise<ServiceWorkerRegistration>} Registration promise
 */
export const registerServiceWorker = async (swPath = '/sw.js') => {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register(swPath, {
        scope: '/',
        updateViaCache: 'none'
      });
      
      console.log('Service worker registered:', registration);
      
      // Handle updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed') {
            if (navigator.serviceWorker.controller) {
              // New content is available, show update notification
              showUpdateNotification();
            } else {
              // First time installation
              console.log('Service Worker installed for the first time');
            }
          }
        });
      });
      
      // Handle controller change
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        window.location.reload();
      });
      
      return registration;
    } catch (error) {
      console.error('Service worker registration failed:', error);
      throw error;
    }
  }
  throw new Error('Service workers not supported');
};

/**
 * Unregister service worker
 * @returns {Promise<boolean>} Unregistration result
 */
export const unregisterServiceWorker = async () => {
  if ('serviceWorker' in navigator) {
    try {
      const registrations = await navigator.serviceWorker.getRegistrations();
      await Promise.all(registrations.map(registration => registration.unregister()));
      console.log('Service workers unregistered');
      return true;
    } catch (error) {
      console.error('Service worker unregistration failed:', error);
      return false;
    }
  }
  return false;
};

/**
 * Check if service worker is supported
 * @returns {boolean} Support status
 */
export const isServiceWorkerSupported = () => {
  return 'serviceWorker' in navigator;
};

/**
 * Get service worker registration
 * @returns {Promise<ServiceWorkerRegistration|null>} Registration or null
 */
export const getServiceWorkerRegistration = async () => {
  if ('serviceWorker' in navigator) {
    try {
      return await navigator.serviceWorker.ready;
    } catch (error) {
      console.error('Failed to get service worker registration:', error);
      return null;
    }
  }
  return null;
};

/**
 * Send message to service worker
 * @param {any} message - Message to send
 * @returns {Promise<any>} Response from service worker
 */
export const sendMessageToServiceWorker = async (message) => {
  if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
    return new Promise((resolve, reject) => {
      const messageChannel = new MessageChannel();
      messageChannel.port1.onmessage = (event) => {
        if (event.data.error) {
          reject(event.data.error);
        } else {
          resolve(event.data);
        }
      };
      
      navigator.serviceWorker.controller.postMessage(message, [messageChannel.port2]);
    });
  }
  throw new Error('Service worker not available');
};

/**
 * Clear all caches
 * @returns {Promise<void>}
 */
export const clearAllCaches = async () => {
  if ('caches' in window) {
    const cacheNames = await caches.keys();
    await Promise.all(
      cacheNames.map(cacheName => caches.delete(cacheName))
    );
    console.log('All caches cleared');
  }
};

/**
 * Get cache storage info
 * @returns {Promise<Object>} Cache storage information
 */
export const getCacheStorageInfo = async () => {
  if ('caches' in window) {
    const cacheNames = await caches.keys();
    const cacheInfo = {};
    
    for (const cacheName of cacheNames) {
      const cache = await caches.open(cacheName);
      const keys = await cache.keys();
      cacheInfo[cacheName] = {
        size: keys.length,
        keys: keys.map(request => request.url)
      };
    }
    
    return cacheInfo;
  }
  return {};
};

/**
 * Show update notification
 */
function showUpdateNotification() {
  // Create a custom notification
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #007bff;
    color: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 10000;
    max-width: 300px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  `;
  
  notification.innerHTML = `
    <div style="display: flex; align-items: center; justify-content: space-between;">
      <div>
        <strong>Update Available</strong>
        <div style="font-size: 0.9rem; margin-top: 0.25rem;">
          A new version is ready to install.
        </div>
      </div>
      <button onclick="this.parentElement.parentElement.remove()" 
              style="background: none; border: none; color: white; font-size: 1.2rem; cursor: pointer; margin-left: 1rem;">
        ×
      </button>
    </div>
    <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
      <button onclick="window.location.reload()" 
              style="background: white; color: #007bff; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; font-weight: 500;">
        Update Now
      </button>
      <button onclick="this.parentElement.parentElement.remove()" 
              style="background: transparent; color: white; border: 1px solid white; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer;">
        Later
      </button>
    </div>
  `;
  
  document.body.appendChild(notification);
  
  // Auto-remove after 10 seconds
  setTimeout(() => {
    if (notification.parentElement) {
      notification.remove();
    }
  }, 10000);
}

export default {
  registerServiceWorker,
  unregisterServiceWorker,
  isServiceWorkerSupported,
  getServiceWorkerRegistration,
  sendMessageToServiceWorker,
  clearAllCaches,
  getCacheStorageInfo
};
