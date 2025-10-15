/**
 * CDN Manager for Asset Optimization
 * Handles CDN integration, asset optimization, and delivery strategies
 */

/**
 * CDN Manager class for asset optimization
 */
export class CDNManager {
  constructor(config = {}) {
    this.config = {
      // CDN configuration
      cdnUrl: process.env.REACT_APP_CDN_URL || 'https://cdn.example.com',
      fallbackUrl: process.env.REACT_APP_FALLBACK_URL || '',
      
      // Asset optimization
      enableWebP: true,
      enableAVIF: true,
      enableCompression: true,
      enableMinification: true,
      
      // Caching strategies
      cacheStrategy: 'aggressive', // aggressive, moderate, conservative
      cacheTTL: 31536000, // 1 year in seconds
      
      // Performance monitoring
      enableMonitoring: true,
      performanceThreshold: 2000, // 2 seconds
      
      // Error handling
      retryAttempts: 3,
      retryDelay: 1000, // 1 second
      
      ...config
    };
    
    this.performanceMetrics = new Map();
    this.failedAssets = new Set();
    this.cache = new Map();
  }

  /**
   * Get optimized asset URL
   */
  getAssetUrl(assetPath, options = {}) {
    const {
      format = 'auto',
      quality = 80,
      width,
      height,
      crop = false,
      blur = false
    } = options;

    // Check cache first
    const cacheKey = this.getCacheKey(assetPath, options);
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    // Generate optimized URL
    const optimizedUrl = this.generateOptimizedUrl(assetPath, {
      format,
      quality,
      width,
      height,
      crop,
      blur
    });

    // Cache the result
    this.cache.set(cacheKey, optimizedUrl);

    return optimizedUrl;
  }

  /**
   * Generate optimized URL with CDN parameters
   */
  generateOptimizedUrl(assetPath, options) {
    const { format, quality, width, height, crop, blur } = options;
    
    // Build CDN URL
    let url = `${this.config.cdnUrl}${assetPath}`;
    
    // Add optimization parameters
    const params = new URLSearchParams();
    
    // Format optimization
    if (format !== 'auto') {
      params.append('f', format);
    } else {
      // Auto-detect best format
      const bestFormat = this.getBestFormat();
      if (bestFormat) {
        params.append('f', bestFormat);
      }
    }
    
    // Quality optimization
    if (quality !== 80) {
      params.append('q', quality);
    }
    
    // Size optimization
    if (width) {
      params.append('w', width);
    }
    if (height) {
      params.append('h', height);
    }
    
    // Crop optimization
    if (crop) {
      params.append('c', '1');
    }
    
    // Blur optimization
    if (blur) {
      params.append('blur', blur);
    }
    
    // Compression
    if (this.config.enableCompression) {
      params.append('compress', '1');
    }
    
    // Minification
    if (this.config.enableMinification) {
      params.append('minify', '1');
    }
    
    // Cache strategy
    params.append('cache', this.config.cacheStrategy);
    
    // Add parameters to URL
    if (params.toString()) {
      url += `?${params.toString()}`;
    }
    
    return url;
  }

  /**
   * Get best format based on browser support
   */
  getBestFormat() {
    if (this.config.enableAVIF && this.supportsAVIF()) {
      return 'avif';
    }
    if (this.config.enableWebP && this.supportsWebP()) {
      return 'webp';
    }
    return null;
  }

  /**
   * Check AVIF support
   */
  supportsAVIF() {
    try {
      const canvas = document.createElement('canvas');
      canvas.width = 1;
      canvas.height = 1;
      return canvas.toDataURL('image/avif').indexOf('data:image/avif') === 0;
    } catch (error) {
      return false;
    }
  }

  /**
   * Check WebP support
   */
  supportsWebP() {
    try {
      const canvas = document.createElement('canvas');
      canvas.width = 1;
      canvas.height = 1;
      return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    } catch (error) {
      return false;
    }
  }

  /**
   * Preload critical assets
   */
  async preloadAssets(assets) {
    const preloadPromises = assets.map(asset => this.preloadAsset(asset));
    return Promise.allSettled(preloadPromises);
  }

  /**
   * Preload single asset
   */
  async preloadAsset(asset) {
    const startTime = performance.now();
    
    try {
      const response = await fetch(asset.url, {
        method: 'HEAD',
        cache: 'no-cache'
      });
      
      const endTime = performance.now();
      const loadTime = endTime - startTime;
      
      // Record performance metrics
      this.recordPerformanceMetrics(asset.url, loadTime, response.ok);
      
      if (response.ok) {
        // Create preload link
        this.createPreloadLink(asset);
        return { success: true, loadTime };
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('CDN Manager: Failed to preload asset:', asset.url, error);
      this.failedAssets.add(asset.url);
      return { success: false, error: error.message };
    }
  }

  /**
   * Create preload link element
   */
  createPreloadLink(asset) {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = asset.url;
    link.as = asset.type || 'image';
    
    if (asset.crossOrigin) {
      link.crossOrigin = asset.crossOrigin;
    }
    
    document.head.appendChild(link);
  }

  /**
   * Record performance metrics
   */
  recordPerformanceMetrics(url, loadTime, success) {
    if (!this.config.enableMonitoring) return;
    
    const metrics = this.performanceMetrics.get(url) || {
      loadTimes: [],
      successCount: 0,
      failureCount: 0,
      averageLoadTime: 0
    };
    
    metrics.loadTimes.push(loadTime);
    metrics.successCount += success ? 1 : 0;
    metrics.failureCount += success ? 0 : 1;
    metrics.averageLoadTime = metrics.loadTimes.reduce((a, b) => a + b, 0) / metrics.loadTimes.length;
    
    this.performanceMetrics.set(url, metrics);
  }

  /**
   * Get performance metrics
   */
  getPerformanceMetrics() {
    const metrics = {};
    
    for (const [url, data] of this.performanceMetrics) {
      metrics[url] = {
        averageLoadTime: data.averageLoadTime,
        successRate: data.successCount / (data.successCount + data.failureCount),
        totalRequests: data.successCount + data.failureCount
      };
    }
    
    return metrics;
  }

  /**
   * Get cache key for asset
   */
  getCacheKey(assetPath, options) {
    return `${assetPath}:${JSON.stringify(options)}`;
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
    this.performanceMetrics.clear();
    this.failedAssets.clear();
  }

  /**
   * Get failed assets
   */
  getFailedAssets() {
    return Array.from(this.failedAssets);
  }

  /**
   * Retry failed assets
   */
  async retryFailedAssets() {
    const failedAssets = this.getFailedAssets();
    const retryPromises = failedAssets.map(asset => this.retryAsset(asset));
    return Promise.allSettled(retryPromises);
  }

  /**
   * Retry single asset
   */
  async retryAsset(assetUrl) {
    for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
      try {
        const response = await fetch(assetUrl, {
          method: 'HEAD',
          cache: 'no-cache'
        });
        
        if (response.ok) {
          this.failedAssets.delete(assetUrl);
          return { success: true, attempt };
        }
      } catch (error) {
        if (attempt === this.config.retryAttempts) {
          return { success: false, error: error.message };
        }
        
        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, this.config.retryDelay * attempt));
      }
    }
  }

  /**
   * Optimize image for different screen sizes
   */
  getResponsiveImageSrcSet(assetPath, options = {}) {
    const { quality = 80, aspectRatio } = options;
    const sizes = [1, 2, 3]; // 1x, 2x, 3x densities
    const breakpoints = [320, 768, 1024, 1920]; // Common breakpoints
    
    const srcSet = [];
    
    // Generate srcset for different densities
    sizes.forEach(density => {
      const width = Math.round(breakpoints[0] * density);
      const height = aspectRatio ? Math.round(width / aspectRatio) : undefined;
      
      const url = this.getAssetUrl(assetPath, {
        ...options,
        width,
        height,
        quality
      });
      
      srcSet.push(`${url} ${density}x`);
    });
    
    // Generate sizes attribute
    const sizesAttr = breakpoints.map((bp, index) => {
      const nextBp = breakpoints[index + 1];
      if (nextBp) {
        return `(max-width: ${bp}px) ${bp}px`;
      }
      return `${bp}px`;
    }).join(', ');
    
    return {
      srcSet: srcSet.join(', '),
      sizes: sizesAttr
    };
  }

  /**
   * Get CDN health status
   */
  async getCDNHealth() {
    try {
      const startTime = performance.now();
      const response = await fetch(`${this.config.cdnUrl}/health`, {
        method: 'HEAD',
        cache: 'no-cache'
      });
      const endTime = performance.now();
      
      return {
        status: response.ok ? 'healthy' : 'unhealthy',
        responseTime: endTime - startTime,
        statusCode: response.status
      };
    } catch (error) {
      return {
        status: 'unreachable',
        responseTime: null,
        error: error.message
      };
    }
  }
}

// Create global CDN manager instance
export const cdnManager = new CDNManager();

/**
 * Hook for using CDN manager
 */
export const useCDNManager = () => {
  const [metrics, setMetrics] = React.useState({});
  const [health, setHealth] = React.useState(null);
  
  React.useEffect(() => {
    const updateMetrics = () => {
      setMetrics(cdnManager.getPerformanceMetrics());
    };
    
    const updateHealth = async () => {
      const healthStatus = await cdnManager.getCDNHealth();
      setHealth(healthStatus);
    };
    
    updateMetrics();
    updateHealth();
    
    // Update metrics periodically
    const interval = setInterval(updateMetrics, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  return {
    metrics,
    health,
    getAssetUrl: (path, options) => cdnManager.getAssetUrl(path, options),
    preloadAssets: (assets) => cdnManager.preloadAssets(assets),
    getResponsiveImageSrcSet: (path, options) => cdnManager.getResponsiveImageSrcSet(path, options),
    retryFailedAssets: () => cdnManager.retryFailedAssets(),
    clearCache: () => cdnManager.clearCache()
  };
};

export default CDNManager;
