/**
 * Network optimization utilities for React applications
 */

import { useCallback, useMemo, useRef, useEffect } from 'react';

/**
 * Request deduplication manager
 */
class RequestDeduplicationManager {
  constructor() {
    this.pendingRequests = new Map();
    this.requestCache = new Map();
    this.cacheTimeout = 30000; // 30 seconds
  }

  /**
   * Deduplicate request
   * @param {string} key - Request key
   * @param {Function} requestFn - Request function
   * @returns {Promise} Request result
   */
  async deduplicateRequest(key, requestFn) {
    // Check if request is already pending
    if (this.pendingRequests.has(key)) {
      return this.pendingRequests.get(key);
    }

    // Check cache
    const cached = this.requestCache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    // Create new request
    const requestPromise = requestFn().then(result => {
      // Cache result
      this.requestCache.set(key, {
        data: result,
        timestamp: Date.now()
      });

      // Remove from pending
      this.pendingRequests.delete(key);

      return result;
    }).catch(error => {
      // Remove from pending on error
      this.pendingRequests.delete(key);
      throw error;
    });

    // Add to pending requests
    this.pendingRequests.set(key, requestPromise);

    return requestPromise;
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.requestCache.clear();
  }

  /**
   * Get cache statistics
   * @returns {Object} Cache statistics
   */
  getCacheStats() {
    return {
      pendingRequests: this.pendingRequests.size,
      cachedRequests: this.requestCache.size,
      cacheTimeout: this.cacheTimeout
    };
  }
}

// Global request deduplication manager
const requestDeduplicationManager = new RequestDeduplicationManager();

/**
 * API call queue manager
 */
class APICallQueueManager {
  constructor() {
    this.queue = [];
    this.isProcessing = false;
    this.maxConcurrent = 5;
    this.currentConcurrent = 0;
    this.retryAttempts = 3;
    this.retryDelay = 1000;
  }

  /**
   * Add request to queue
   * @param {Object} request - Request object
   * @returns {Promise} Request result
   */
  async addRequest(request) {
    return new Promise((resolve, reject) => {
      this.queue.push({
        ...request,
        resolve,
        reject,
        attempts: 0
      });

      this.processQueue();
    });
  }

  /**
   * Process queue
   */
  async processQueue() {
    if (this.isProcessing || this.queue.length === 0) return;

    this.isProcessing = true;

    while (this.queue.length > 0 && this.currentConcurrent < this.maxConcurrent) {
      const request = this.queue.shift();
      this.currentConcurrent++;

      this.executeRequest(request);
    }

    this.isProcessing = false;
  }

  /**
   * Execute request
   * @param {Object} request - Request object
   */
  async executeRequest(request) {
    try {
      const response = await fetch(request.url, {
        method: request.method || 'GET',
        headers: request.headers || {},
        body: request.body
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      request.resolve(data);
    } catch (error) {
      if (request.attempts < this.retryAttempts) {
        request.attempts++;
        setTimeout(() => {
          this.queue.unshift(request);
          this.processQueue();
        }, this.retryDelay * request.attempts);
      } else {
        request.reject(error);
      }
    } finally {
      this.currentConcurrent--;
      this.processQueue();
    }
  }

  /**
   * Get queue statistics
   * @returns {Object} Queue statistics
   */
  getQueueStats() {
    return {
      queueLength: this.queue.length,
      currentConcurrent: this.currentConcurrent,
      maxConcurrent: this.maxConcurrent,
      isProcessing: this.isProcessing
    };
  }
}

// Global API call queue manager
const apiCallQueueManager = new APICallQueueManager();

/**
 * Request caching manager
 */
class RequestCachingManager {
  constructor() {
    this.cache = new Map();
    this.cacheTimeout = 300000; // 5 minutes
    this.maxCacheSize = 100;
  }

  /**
   * Get cached request
   * @param {string} key - Cache key
   * @returns {Object|null} Cached data or null
   */
  getCachedRequest(key) {
    const cached = this.cache.get(key);
    
    if (!cached) return null;
    
    if (Date.now() - cached.timestamp > this.cacheTimeout) {
      this.cache.delete(key);
      return null;
    }
    
    return cached.data;
  }

  /**
   * Set cached request
   * @param {string} key - Cache key
   * @param {any} data - Data to cache
   */
  setCachedRequest(key, data) {
    // Remove oldest entries if cache is full
    if (this.cache.size >= this.maxCacheSize) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }
    
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
  }

  /**
   * Get cache statistics
   * @returns {Object} Cache statistics
   */
  getCacheStats() {
    return {
      cacheSize: this.cache.size,
      maxCacheSize: this.maxCacheSize,
      cacheTimeout: this.cacheTimeout
    };
  }
}

// Global request caching manager
const requestCachingManager = new RequestCachingManager();

/**
 * Optimized fetch function with deduplication and caching
 * @param {string} url - Request URL
 * @param {Object} options - Fetch options
 * @returns {Promise} Request result
 */
export const optimizedFetch = async (url, options = {}) => {
  const {
    enableDeduplication = true,
    enableCaching = true,
    cacheTimeout = 300000, // 5 minutes
    ...fetchOptions
  } = options;

  const cacheKey = `${url}-${JSON.stringify(fetchOptions)}`;

  // Check cache first
  if (enableCaching) {
    const cached = requestCachingManager.getCachedRequest(cacheKey);
    if (cached) {
      return cached;
    }
  }

  // Deduplicate request if enabled
  if (enableDeduplication) {
    return requestDeduplicationManager.deduplicateRequest(cacheKey, async () => {
      const response = await fetch(url, fetchOptions);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Cache result
      if (enableCaching) {
        requestCachingManager.setCachedRequest(cacheKey, data);
      }
      
      return data;
    });
  }

  // Direct request without deduplication
  const response = await fetch(url, fetchOptions);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  
  // Cache result
  if (enableCaching) {
    requestCachingManager.setCachedRequest(cacheKey, data);
  }
  
  return data;
};

/**
 * Batch API requests
 * @param {Array} requests - Array of request objects
 * @param {Object} options - Batch options
 * @returns {Promise<Array>} Batch results
 */
export const batchAPIRequests = async (requests, options = {}) => {
  const {
    maxConcurrent = 5,
    enableDeduplication = true,
    enableCaching = true,
    retryAttempts = 3,
    retryDelay = 1000
  } = options;

  const results = [];
  const errors = [];

  // Process requests in batches
  for (let i = 0; i < requests.length; i += maxConcurrent) {
    const batch = requests.slice(i, i + maxConcurrent);
    
    const batchPromises = batch.map(async (request, index) => {
      try {
        const result = await optimizedFetch(request.url, {
          ...request.options,
          enableDeduplication,
          enableCaching
        });
        
        return { index: i + index, result, error: null };
      } catch (error) {
        return { index: i + index, result: null, error };
      }
    });

    const batchResults = await Promise.allSettled(batchPromises);
    
    batchResults.forEach((result, index) => {
      if (result.status === 'fulfilled') {
        const { index: originalIndex, result: data, error } = result.value;
        if (error) {
          errors[originalIndex] = error;
        } else {
          results[originalIndex] = data;
        }
      } else {
        errors[i + index] = result.reason;
      }
    });
  }

  return { results, errors };
};

/**
 * Request throttling
 * @param {Function} fn - Function to throttle
 * @param {number} delay - Throttle delay in milliseconds
 * @returns {Function} Throttled function
 */
export const throttleRequest = (fn, delay) => {
  let lastCall = 0;
  let timeoutId = null;

  return (...args) => {
    const now = Date.now();
    const timeSinceLastCall = now - lastCall;

    if (timeSinceLastCall >= delay) {
      lastCall = now;
      return fn(...args);
    } else {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      
      timeoutId = setTimeout(() => {
        lastCall = Date.now();
        fn(...args);
      }, delay - timeSinceLastCall);
    }
  };
};

/**
 * Request debouncing
 * @param {Function} fn - Function to debounce
 * @param {number} delay - Debounce delay in milliseconds
 * @returns {Function} Debounced function
 */
export const debounceRequest = (fn, delay) => {
  let timeoutId = null;

  return (...args) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    
    timeoutId = setTimeout(() => {
      fn(...args);
    }, delay);
  };
};

/**
 * Network performance monitor
 */
class NetworkPerformanceMonitor {
  constructor() {
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0,
      totalDataTransferred: 0,
      cacheHitRate: 0
    };
    
    this.observers = new Set();
  }

  /**
   * Add observer
   * @param {Function} observer - Observer function
   */
  addObserver(observer) {
    this.observers.add(observer);
  }

  /**
   * Remove observer
   * @param {Function} observer - Observer function
   */
  removeObserver(observer) {
    this.observers.delete(observer);
  }

  /**
   * Notify observers
   */
  notifyObservers() {
    this.observers.forEach(observer => {
      try {
        observer(this.metrics);
      } catch (error) {
        console.error('Error in network performance observer:', error);
      }
    });
  }

  /**
   * Record request
   * @param {Object} requestData - Request data
   */
  recordRequest(requestData) {
    const {
      success,
      responseTime,
      dataSize,
      fromCache = false
    } = requestData;

    this.metrics.totalRequests++;
    
    if (success) {
      this.metrics.successfulRequests++;
    } else {
      this.metrics.failedRequests++;
    }
    
    if (responseTime) {
      this.metrics.averageResponseTime = 
        (this.metrics.averageResponseTime * (this.metrics.totalRequests - 1) + responseTime) / 
        this.metrics.totalRequests;
    }
    
    if (dataSize) {
      this.metrics.totalDataTransferred += dataSize;
    }
    
    if (fromCache) {
      this.metrics.cacheHitRate = 
        (this.metrics.cacheHitRate * (this.metrics.totalRequests - 1) + 1) / 
        this.metrics.totalRequests;
    } else {
      this.metrics.cacheHitRate = 
        (this.metrics.cacheHitRate * (this.metrics.totalRequests - 1)) / 
        this.metrics.totalRequests;
    }
    
    this.notifyObservers();
  }

  /**
   * Get metrics
   * @returns {Object} Network metrics
   */
  getMetrics() {
    return { ...this.metrics };
  }

  /**
   * Reset metrics
   */
  resetMetrics() {
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0,
      totalDataTransferred: 0,
      cacheHitRate: 0
    };
    
    this.notifyObservers();
  }
}

// Global network performance monitor
const networkPerformanceMonitor = new NetworkPerformanceMonitor();

/**
 * Network optimization utilities
 */
export const networkOptimizer = {
  /**
   * Optimized fetch with deduplication and caching
   * @param {string} url - Request URL
   * @param {Object} options - Fetch options
   * @returns {Promise} Request result
   */
  fetch: optimizedFetch,
  
  /**
   * Batch API requests
   * @param {Array} requests - Array of request objects
   * @param {Object} options - Batch options
   * @returns {Promise<Array>} Batch results
   */
  batch: batchAPIRequests,
  
  /**
   * Throttle request
   * @param {Function} fn - Function to throttle
   * @param {number} delay - Throttle delay
   * @returns {Function} Throttled function
   */
  throttle: throttleRequest,
  
  /**
   * Debounce request
   * @param {Function} fn - Function to debounce
   * @param {number} delay - Debounce delay
   * @returns {Function} Debounced function
   */
  debounce: debounceRequest,
  
  /**
   * Get deduplication stats
   * @returns {Object} Deduplication statistics
   */
  getDeduplicationStats: () => requestDeduplicationManager.getCacheStats(),
  
  /**
   * Get queue stats
   * @returns {Object} Queue statistics
   */
  getQueueStats: () => apiCallQueueManager.getQueueStats(),
  
  /**
   * Get cache stats
   * @returns {Object} Cache statistics
   */
  getCacheStats: () => requestCachingManager.getCacheStats(),
  
  /**
   * Clear all caches
   */
  clearAllCaches: () => {
    requestDeduplicationManager.clearCache();
    requestCachingManager.clearCache();
  },
  
  /**
   * Add network performance observer
   * @param {Function} observer - Observer function
   */
  addPerformanceObserver: (observer) => networkPerformanceMonitor.addObserver(observer),
  
  /**
   * Remove network performance observer
   * @param {Function} observer - Observer function
   */
  removePerformanceObserver: (observer) => networkPerformanceMonitor.removeObserver(observer),
  
  /**
   * Get network performance metrics
   * @returns {Object} Network performance metrics
   */
  getPerformanceMetrics: () => networkPerformanceMonitor.getMetrics(),
  
  /**
   * Reset network performance metrics
   */
  resetPerformanceMetrics: () => networkPerformanceMonitor.resetMetrics()
};

export default networkOptimizer;
