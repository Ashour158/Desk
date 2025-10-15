/**
 * Bundle Analysis and Size Monitoring Utilities
 * Provides real-time bundle size analysis and optimization recommendations
 */

/**
 * Bundle size analyzer class
 */
class BundleAnalyzer {
  constructor() {
    this.bundleData = {};
    this.performanceObserver = null;
    this.resourceTimings = [];
    this.initialized = false;
  }

  /**
   * Initialize bundle analyzer
   */
  async initialize() {
    if (this.initialized) return;

    try {
      // Get initial bundle data
      await this.analyzeCurrentBundle();
      
      // Set up performance monitoring
      this.setupPerformanceMonitoring();
      
      // Set up resource monitoring
      this.setupResourceMonitoring();
      
      this.initialized = true;
      console.log('Bundle Analyzer initialized');
    } catch (error) {
      console.error('Failed to initialize Bundle Analyzer:', error);
    }
  }

  /**
   * Analyze current bundle size
   */
  async analyzeCurrentBundle() {
    try {
      // Get all script and link elements
      const scripts = Array.from(document.querySelectorAll('script[src]'));
      const stylesheets = Array.from(document.querySelectorAll('link[rel="stylesheet"]'));
      
      const bundleData = {
        scripts: [],
        stylesheets: [],
        totalSize: 0,
        timestamp: new Date().toISOString()
      };

      // Analyze scripts
      for (const script of scripts) {
        const size = await this.getResourceSize(script.src);
        bundleData.scripts.push({
          src: script.src,
          size: size,
          type: this.getResourceType(script.src)
        });
        bundleData.totalSize += size;
      }

      // Analyze stylesheets
      for (const stylesheet of stylesheets) {
        const size = await this.getResourceSize(stylesheet.href);
        bundleData.stylesheets.push({
          href: stylesheet.href,
          size: size,
          type: 'css'
        });
        bundleData.totalSize += size;
      }

      this.bundleData = bundleData;
      return bundleData;
    } catch (error) {
      console.error('Failed to analyze bundle:', error);
      return null;
    }
  }

  /**
   * Get resource size
   */
  async getResourceSize(url) {
    try {
      const response = await fetch(url, { method: 'HEAD' });
      const contentLength = response.headers.get('content-length');
      return contentLength ? parseInt(contentLength) : 0;
    } catch (error) {
      console.warn(`Failed to get size for ${url}:`, error);
      return 0;
    }
  }

  /**
   * Get resource type from URL
   */
  getResourceType(url) {
    if (url.includes('vendor') || url.includes('chunk')) return 'vendor';
    if (url.includes('main') || url.includes('app')) return 'main';
    if (url.includes('react')) return 'react';
    if (url.includes('router')) return 'router';
    return 'other';
  }

  /**
   * Set up performance monitoring
   */
  setupPerformanceMonitoring() {
    if ('PerformanceObserver' in window) {
      this.performanceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          if (entry.entryType === 'resource') {
            this.resourceTimings.push({
              name: entry.name,
              size: entry.transferSize || 0,
              duration: entry.duration,
              startTime: entry.startTime,
              type: this.getResourceType(entry.name)
            });
          }
        });
      });

      this.performanceObserver.observe({ entryTypes: ['resource'] });
    }
  }

  /**
   * Set up resource monitoring
   */
  setupResourceMonitoring() {
    // Monitor resource loading
    window.addEventListener('load', () => {
      setTimeout(() => {
        this.analyzeResourcePerformance();
      }, 1000);
    });
  }

  /**
   * Analyze resource performance
   */
  analyzeResourcePerformance() {
    const analysis = {
      totalResources: this.resourceTimings.length,
      totalSize: this.resourceTimings.reduce((sum, resource) => sum + resource.size, 0),
      averageSize: 0,
      largestResources: [],
      slowestResources: [],
      recommendations: []
    };

    if (analysis.totalResources > 0) {
      analysis.averageSize = analysis.totalSize / analysis.totalResources;
      
      // Find largest resources
      analysis.largestResources = this.resourceTimings
        .sort((a, b) => b.size - a.size)
        .slice(0, 5);

      // Find slowest resources
      analysis.slowestResources = this.resourceTimings
        .sort((a, b) => b.duration - a.duration)
        .slice(0, 5);

      // Generate recommendations
      analysis.recommendations = this.generateRecommendations(analysis);
    }

    return analysis;
  }

  /**
   * Generate optimization recommendations
   */
  generateRecommendations(analysis) {
    const recommendations = [];

    // Check for large resources
    const largeResources = analysis.largestResources.filter(r => r.size > 100000); // 100KB
    if (largeResources.length > 0) {
      recommendations.push({
        type: 'warning',
        message: `Large resources detected: ${largeResources.length} resources over 100KB`,
        resources: largeResources.map(r => r.name),
        suggestion: 'Consider code splitting or lazy loading for large resources'
      });
    }

    // Check for slow resources
    const slowResources = analysis.slowestResources.filter(r => r.duration > 1000); // 1s
    if (slowResources.length > 0) {
      recommendations.push({
        type: 'warning',
        message: `Slow resources detected: ${slowResources.length} resources taking over 1s`,
        resources: slowResources.map(r => r.name),
        suggestion: 'Consider optimizing or preloading critical resources'
      });
    }

    // Check total bundle size
    if (analysis.totalSize > 1000000) { // 1MB
      recommendations.push({
        type: 'error',
        message: `Total bundle size is ${(analysis.totalSize / 1024 / 1024).toFixed(2)}MB`,
        suggestion: 'Consider implementing code splitting and tree shaking'
      });
    }

    // Check for duplicate resources
    const resourceCounts = {};
    this.resourceTimings.forEach(resource => {
      resourceCounts[resource.name] = (resourceCounts[resource.name] || 0) + 1;
    });

    const duplicates = Object.entries(resourceCounts).filter(([name, count]) => count > 1);
    if (duplicates.length > 0) {
      recommendations.push({
        type: 'info',
        message: `Duplicate resources detected: ${duplicates.length} resources loaded multiple times`,
        resources: duplicates.map(([name]) => name),
        suggestion: 'Check for duplicate imports or unnecessary resource loading'
      });
    }

    return recommendations;
  }

  /**
   * Get bundle analysis report
   */
  getBundleReport() {
    const resourceAnalysis = this.analyzeResourcePerformance();
    
    return {
      bundleData: this.bundleData,
      resourceAnalysis: resourceAnalysis,
      timestamp: new Date().toISOString(),
      recommendations: resourceAnalysis.recommendations
    };
  }

  /**
   * Get performance metrics
   */
  getPerformanceMetrics() {
    const navigation = performance.getEntriesByType('navigation')[0];
    const paint = performance.getEntriesByType('paint');
    
    return {
      navigation: {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        totalTime: navigation.loadEventEnd - navigation.fetchStart
      },
      paint: {
        firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0
      },
      resources: this.resourceTimings.length,
      totalSize: this.resourceTimings.reduce((sum, r) => sum + r.size, 0)
    };
  }

  /**
   * Export bundle data
   */
  exportBundleData() {
    const report = this.getBundleReport();
    const dataStr = JSON.stringify(report, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `bundle-analysis-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  }

  /**
   * Clean up
   */
  destroy() {
    if (this.performanceObserver) {
      this.performanceObserver.disconnect();
    }
    this.initialized = false;
  }
}

// Create global instance
const bundleAnalyzer = new BundleAnalyzer();

/**
 * Initialize bundle analyzer
 */
export const initializeBundleAnalyzer = async () => {
  await bundleAnalyzer.initialize();
};

/**
 * Get bundle analysis report
 */
export const getBundleReport = () => {
  return bundleAnalyzer.getBundleReport();
};

/**
 * Get performance metrics
 */
export const getPerformanceMetrics = () => {
  return bundleAnalyzer.getPerformanceMetrics();
};

/**
 * Export bundle data
 */
export const exportBundleData = () => {
  bundleAnalyzer.exportBundleData();
};

/**
 * Bundle size monitor component
 */
export const BundleSizeMonitor = ({ onAnalysisComplete }) => {
  const [analysis, setAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const runAnalysis = useCallback(async () => {
    setIsAnalyzing(true);
    try {
      await bundleAnalyzer.initialize();
      const report = bundleAnalyzer.getBundleReport();
      setAnalysis(report);
      if (onAnalysisComplete) {
        onAnalysisComplete(report);
      }
    } catch (error) {
      console.error('Bundle analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  }, [onAnalysisComplete]);

  useEffect(() => {
    runAnalysis();
  }, [runAnalysis]);

  if (!analysis) {
    return (
      <div style={{ padding: '1rem', textAlign: 'center' }}>
        {isAnalyzing ? 'Analyzing bundle...' : 'Bundle analysis not available'}
      </div>
    );
  }

  return (
    <div style={{ padding: '1rem' }}>
      <h3>Bundle Analysis Report</h3>
      
      <div style={{ marginBottom: '1rem' }}>
        <strong>Total Size:</strong> {(analysis.bundleData.totalSize / 1024).toFixed(2)} KB
      </div>
      
      <div style={{ marginBottom: '1rem' }}>
        <strong>Resources:</strong> {analysis.resourceAnalysis.totalResources}
      </div>
      
      {analysis.recommendations.length > 0 && (
        <div>
          <h4>Recommendations:</h4>
          <ul>
            {analysis.recommendations.map((rec, index) => (
              <li key={index} style={{ color: rec.type === 'error' ? 'red' : rec.type === 'warning' ? 'orange' : 'blue' }}>
                {rec.message} - {rec.suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      <button onClick={exportBundleData} style={{ marginTop: '1rem' }}>
        Export Analysis
      </button>
    </div>
  );
};

export default bundleAnalyzer;