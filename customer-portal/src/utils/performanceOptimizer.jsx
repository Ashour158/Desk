/**
 * Performance optimization utilities for React applications
 */

/**
 * Debounce function for performance optimization
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @param {boolean} immediate - Whether to call immediately
 * @returns {Function} Debounced function
 */
export const debounce = (func, wait, immediate = false) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func(...args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func(...args);
  };
};

/**
 * Throttle function for performance optimization
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
export const throttle = (func, limit) => {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

/**
 * Check if WebP is supported
 * @returns {Promise<boolean>} WebP support status
 */
export const checkWebPSupport = () => {
  return new Promise((resolve) => {
    const webP = new Image();
    webP.onload = webP.onerror = () => {
      resolve(webP.height === 2);
    };
    webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
  });
};

/**
 * Generate responsive image URLs
 * @param {string} src - Original image source
 * @param {Object} options - Options for image generation
 * @returns {Object} Responsive image data
 */
export const generateResponsiveImages = (src, options = {}) => {
  const {
    widths = [320, 640, 768, 1024, 1280, 1920],
    quality = 80,
    format = 'auto',
    fit = 'crop'
  } = options;

  const baseUrl = new URL(src, window.location.origin);
  
  const generateSrcSet = (format) => {
    return widths
      .map(width => {
        const url = new URL(baseUrl);
        url.searchParams.set('w', width.toString());
        url.searchParams.set('h', Math.round(width * 0.75).toString());
        url.searchParams.set('fit', fit);
        url.searchParams.set('q', quality.toString());
        
        if (format === 'webp') {
          url.pathname = url.pathname.replace(/\.(jpg|jpeg|png)$/i, '.webp');
        }
        
        return `${url.toString()} ${width}w`;
      })
      .join(', ');
  };

  return {
    src: baseUrl.toString(),
    srcSet: generateSrcSet(format),
    webpSrcSet: generateSrcSet('webp'),
    sizes: '(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw'
  };
};

/**
 * Preload critical resources
 * @param {Array} resources - Array of resource objects
 */
export const preloadCriticalResources = (resources) => {
  resources.forEach(resource => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = resource.as || 'image';
    link.href = resource.href;
    if (resource.type) link.type = resource.type;
    if (resource.crossOrigin) link.crossOrigin = resource.crossOrigin;
    document.head.appendChild(link);
  });
};

/**
 * Lazy load images with Intersection Observer
 * @param {NodeList} images - Images to lazy load
 * @param {Object} options - Observer options
 */
export const lazyLoadImages = (images, options = {}) => {
  const {
    rootMargin = '50px',
    threshold = 0.1
  } = options;

  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) {
          img.src = img.dataset.src;
          img.classList.remove('lazy');
          imageObserver.unobserve(img);
        }
      }
    });
  }, { rootMargin, threshold });

  images.forEach(img => imageObserver.observe(img));
};

/**
 * Optimize bundle splitting
 * @param {Object} webpackConfig - Webpack configuration
 * @returns {Object} Optimized webpack configuration
 */
export const optimizeBundleSplitting = (webpackConfig) => {
  return {
    ...webpackConfig,
    optimization: {
      ...webpackConfig.optimization,
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 10
          },
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            priority: 5,
            enforce: true
          },
          react: {
            test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
            name: 'react',
            chunks: 'all',
            priority: 20
          }
        }
      }
    }
  };
};

/**
 * Service worker registration
 * @param {string} swPath - Service worker path
 * @returns {Promise<ServiceWorkerRegistration>} Registration promise
 */
export const registerServiceWorker = async (swPath = '/sw.js') => {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register(swPath);
      console.log('Service worker registered:', registration);
      return registration;
    } catch (error) {
      console.error('Service worker registration failed:', error);
      throw error;
    }
  }
  throw new Error('Service workers not supported');
};

/**
 * Performance monitoring
 */
export class PerformanceMonitor {
  constructor() {
    this.metrics = new Map();
    this.observers = new Set();
  }

  /**
   * Measure render performance
   * @param {string} componentName - Component name
   * @param {Function} renderFunction - Render function
   * @returns {any} Render result
   */
  measureRender(componentName, renderFunction) {
    const startTime = performance.now();
    const result = renderFunction();
    const endTime = performance.now();
    
    const duration = endTime - startTime;
    this.metrics.set(`render_${componentName}`, {
      duration,
      timestamp: Date.now(),
      renderCount: (this.metrics.get(`render_${componentName}`)?.renderCount || 0) + 1
    });
    
    return result;
  }

  /**
   * Measure API call performance
   * @param {string} endpoint - API endpoint
   * @param {Function} apiCall - API call function
   * @returns {Promise<any>} API call result
   */
  async measureApiCall(endpoint, apiCall) {
    const startTime = performance.now();
    try {
      const result = await apiCall();
      const endTime = performance.now();
      
      const duration = endTime - startTime;
      this.metrics.set(`api_${endpoint}`, {
        duration,
        timestamp: Date.now(),
        success: true
      });
      
      return result;
    } catch (error) {
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      this.metrics.set(`api_${endpoint}`, {
        duration,
        timestamp: Date.now(),
        success: false,
        error: error.message
      });
      
      throw error;
    }
  }

  /**
   * Get performance metrics
   * @returns {Object} Performance metrics
   */
  getMetrics() {
    return Object.fromEntries(this.metrics);
  }

  /**
   * Clear metrics
   */
  clearMetrics() {
    this.metrics.clear();
  }
}

// Create global performance monitor instance
export const performanceMonitor = new PerformanceMonitor();

/**
 * React Profiler integration
 */
export const Profiler = ({ children, id }) => {
  const onRenderCallback = (id, phase, actualDuration, baseDuration, startTime, commitTime) => {
    const data = {
      component: id,
      phase,
      actualDuration,
      baseDuration,
      startTime,
      commitTime,
      renderCount: performanceMonitor.metrics.get(`render_${id}`)?.renderCount || 0
    };

    console.log(`React Profiler: ${id}`, actualDuration, data);
    performanceMonitor.metrics.set(`profiler_${id}`, data);
  };

  return (
    <React.Profiler id={id} onRender={onRenderCallback}>
      {children}
    </React.Profiler>
  );
};

/**
 * HOC for automatic performance monitoring
 */
export const withPerformanceMonitoring = (WrappedComponent, componentName) => {
  return React.memo((props) => {
    return performanceMonitor.measureRender(componentName, () => (
      <WrappedComponent {...props} />
    ));
  });
};

/**
 * Hook for performance monitoring
 */
export const usePerformanceMonitoring = (componentName) => {
  const [metrics, setMetrics] = useState({});
  
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(performanceMonitor.getMetrics());
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  return metrics;
};

export default {
  debounce,
  throttle,
  checkWebPSupport,
  generateResponsiveImages,
  preloadCriticalResources,
  lazyLoadImages,
  optimizeBundleSplitting,
  registerServiceWorker,
  PerformanceMonitor,
  performanceMonitor,
  Profiler,
  withPerformanceMonitoring,
  usePerformanceMonitoring
};
