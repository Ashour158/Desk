/**
 * Critical Rendering Path Optimization
 * Optimizes the critical rendering path for better performance
 */

/**
 * Initialize critical rendering path optimizations
 * @param {Object} options - Configuration options
 * @param {boolean} options.preloadResources - Preload critical resources
 * @param {boolean} options.preloadFonts - Preload critical fonts
 * @param {boolean} options.prefetchPages - Prefetch likely next pages
 * @param {boolean} options.addResourceHints - Add resource hints
 * @param {boolean} options.optimizeFonts - Optimize font loading
 * @param {boolean} options.deferResources - Defer non-critical resources
 * @param {boolean} options.inlineCriticalCSS - Inline critical CSS
 * @param {boolean} options.loadNonCriticalCSS - Load non-critical CSS asynchronously
 * @param {boolean} options.optimizeImages - Optimize image loading
 * @param {boolean} options.implementLazyLoading - Implement lazy loading
 * @param {boolean} options.optimizeJS - Optimize JavaScript loading
 */
export const initializeCriticalRenderingPath = (options = {}) => {
  const {
    preloadResources = true,
    preloadFonts = true,
    prefetchPages = true,
    addResourceHints = true,
    optimizeFonts = true,
    deferResources = true,
    inlineCriticalCSS = true,
    loadNonCriticalCSS = true,
    optimizeImages = true,
    implementLazyLoading = true,
    optimizeJS = true
  } = options;

  console.log('🚀 Initializing Critical Rendering Path Optimization');

  // Preload critical resources
  if (preloadResources) {
    preloadCriticalResources();
  }

  // Preload critical fonts
  if (preloadFonts) {
    preloadCriticalFonts();
  }

  // Prefetch likely next pages
  if (prefetchPages) {
    prefetchNextPages();
  }

  // Add resource hints
  if (addResourceHints) {
    addResourceHintsToHead();
  }

  // Optimize font loading
  if (optimizeFonts) {
    optimizeFontLoading();
  }

  // Defer non-critical resources
  if (deferResources) {
    deferNonCriticalResources();
  }

  // Inline critical CSS
  if (inlineCriticalCSS) {
    inlineCriticalCSS();
  }

  // Load non-critical CSS asynchronously
  if (loadNonCriticalCSS) {
    loadNonCriticalCSSAsync();
  }

  // Optimize image loading
  if (optimizeImages) {
    optimizeImageLoading();
  }

  // Implement lazy loading
  if (implementLazyLoading) {
    implementLazyLoading();
  }

  // Optimize JavaScript loading
  if (optimizeJS) {
    optimizeJavaScriptLoading();
  }

  console.log('✅ Critical Rendering Path Optimization Complete');
};

/**
 * Preload critical resources
 */
const preloadCriticalResources = () => {
  const criticalResources = [
    '/assets/critical.css',
    '/assets/critical.js',
    '/api/v1/auth/user/',
    '/api/v1/features/flags/'
  ];

  criticalResources.forEach(resource => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = resource;
    link.as = resource.endsWith('.css') ? 'style' : 'script';
    document.head.appendChild(link);
  });
};

/**
 * Preload critical fonts
 */
const preloadCriticalFonts = () => {
  const criticalFonts = [
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'
  ];

  criticalFonts.forEach(font => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = font;
    link.as = 'style';
    link.crossOrigin = 'anonymous';
    document.head.appendChild(link);
  });
};

/**
 * Prefetch likely next pages
 */
const prefetchNextPages = () => {
  const likelyPages = [
    '/dashboard',
    '/tickets',
    '/knowledge-base',
    '/profile'
  ];

  // Prefetch after initial load
  setTimeout(() => {
    likelyPages.forEach(page => {
      const link = document.createElement('link');
      link.rel = 'prefetch';
      link.href = page;
      document.head.appendChild(link);
    });
  }, 2000);
};

/**
 * Add resource hints to head
 */
const addResourceHintsToHead = () => {
  // DNS prefetch for external domains
  const externalDomains = [
    'https://fonts.googleapis.com',
    'https://fonts.gstatic.com',
    'https://cdn.jsdelivr.net'
  ];

  externalDomains.forEach(domain => {
    const link = document.createElement('link');
    link.rel = 'dns-prefetch';
    link.href = domain;
    document.head.appendChild(link);
  });
};

/**
 * Optimize font loading
 */
const optimizeFontLoading = () => {
  // Add font-display: swap to font faces
  const style = document.createElement('style');
  style.textContent = `
    @font-face {
      font-family: 'Inter';
      font-display: swap;
    }
  `;
  document.head.appendChild(style);
};

/**
 * Defer non-critical resources
 */
const deferNonCriticalResources = () => {
  // Defer non-critical scripts
  const scripts = document.querySelectorAll('script[data-defer]');
  scripts.forEach(script => {
    script.defer = true;
  });

  // Defer non-critical stylesheets
  const stylesheets = document.querySelectorAll('link[data-defer]');
  stylesheets.forEach(link => {
    link.media = 'print';
    link.onload = () => {
      link.media = 'all';
    };
  });
};

/**
 * Inline critical CSS
 */
const inlineCriticalCSS = () => {
  // This would typically be done at build time
  // For runtime, we can add critical styles
  const criticalCSS = `
    body { font-family: Inter, sans-serif; }
    .loading { display: flex; justify-content: center; align-items: center; }
    .error { color: #e53e3e; }
  `;

  const style = document.createElement('style');
  style.textContent = criticalCSS;
  document.head.appendChild(style);
};

/**
 * Load non-critical CSS asynchronously
 */
const loadNonCriticalCSSAsync = () => {
  const nonCriticalCSS = [
    '/assets/non-critical.css',
    '/assets/print.css'
  ];

  nonCriticalCSS.forEach(css => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = css;
    link.as = 'style';
    link.onload = () => {
      link.rel = 'stylesheet';
    };
    document.head.appendChild(link);
  });
};

/**
 * Optimize image loading
 */
const optimizeImageLoading = () => {
  // Add loading="lazy" to images below the fold
  const images = document.querySelectorAll('img[data-lazy]');
  images.forEach(img => {
    img.loading = 'lazy';
  });

  // Add responsive image attributes
  const responsiveImages = document.querySelectorAll('img[data-responsive]');
  responsiveImages.forEach(img => {
    img.sizes = '(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw';
    img.srcset = img.src;
  });
};

/**
 * Implement lazy loading
 */
const implementLazyLoading = () => {
  // Use Intersection Observer for lazy loading
  if ('IntersectionObserver' in window) {
    const lazyElements = document.querySelectorAll('[data-lazy]');
    const lazyObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const element = entry.target;
          if (element.dataset.src) {
            element.src = element.dataset.src;
            element.classList.remove('lazy');
            lazyObserver.unobserve(element);
          }
        }
      });
    });

    lazyElements.forEach(element => {
      lazyObserver.observe(element);
    });
  }
};

/**
 * Optimize JavaScript loading
 */
const optimizeJavaScriptLoading = () => {
  // Add async/defer attributes to scripts
  const scripts = document.querySelectorAll('script[data-optimize]');
  scripts.forEach(script => {
    if (script.dataset.optimize === 'async') {
      script.async = true;
    } else if (script.dataset.optimize === 'defer') {
      script.defer = true;
    }
  });
};

/**
 * Get performance metrics
 */
export const getPerformanceMetrics = () => {
  if ('performance' in window) {
    const navigation = performance.getEntriesByType('navigation')[0];
    const paint = performance.getEntriesByType('paint');
    
    return {
      domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
      loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
      firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
      firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0
    };
  }
  return null;
};

/**
 * Monitor performance
 */
export const monitorPerformance = () => {
  const metrics = getPerformanceMetrics();
  if (metrics) {
    console.log('📊 Performance Metrics:', metrics);
    
    // Send metrics to analytics
    if (window.gtag) {
      window.gtag('event', 'performance_metrics', {
        event_category: 'performance',
        event_label: 'critical_rendering_path',
        value: Math.round(metrics.domContentLoaded)
      });
    }
  }
};

export default {
  initializeCriticalRenderingPath,
  getPerformanceMetrics,
  monitorPerformance
};