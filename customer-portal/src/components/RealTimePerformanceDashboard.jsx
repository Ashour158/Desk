import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import PropTypes from 'prop-types';
import { memo } from 'react';

/**
 * Real-Time Performance Monitoring Dashboard
 * Comprehensive performance tracking with real-time metrics and recommendations
 */
const RealTimePerformanceDashboard = memo(({ 
  refreshInterval = 2000,
  showCharts = true,
  showRecommendations = true,
  showAlerts = true,
  className = '',
  ...props 
}) => {
  const [metrics, setMetrics] = useState({
    // Core Web Vitals
    webVitals: {
      lcp: null, // Largest Contentful Paint
      fid: null, // First Input Delay
      cls: null, // Cumulative Layout Shift
      fcp: null, // First Contentful Paint
      ttfb: null // Time to First Byte
    },
    
    // Performance Metrics
    performance: {
      memory: null,
      timing: null,
      navigation: null,
      paint: null,
      resource: null
    },
    
    // Bundle Analysis
    bundle: {
      size: null,
      chunks: null,
      loadTime: null,
      compression: null
    },
    
    // Network Metrics
    network: {
      connection: null,
      requests: null,
      bandwidth: null,
      latency: null
    },
    
    // Cache Metrics
    cache: {
      hitRate: null,
      size: null,
      efficiency: null,
      invalidation: null
    },
    
    // User Experience
    ux: {
      interactions: null,
      errors: null,
      accessibility: null,
      responsiveness: null
    }
  });

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [historicalData, setHistoricalData] = useState([]);
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h');
  
  const intervalRef = useRef(null);
  const performanceObserver = useRef(null);
  const memoryObserver = useRef(null);
  const networkObserver = useRef(null);

  // Initialize performance monitoring
  useEffect(() => {
    initializePerformanceMonitoring();
    
    return () => {
      cleanup();
    };
  }, []);

  // Set up real-time monitoring
  useEffect(() => {
    if (refreshInterval > 0) {
      intervalRef.current = setInterval(collectMetrics, refreshInterval);
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [refreshInterval]);

  // Initialize performance monitoring
  const initializePerformanceMonitoring = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Initialize Web Vitals monitoring
      await initializeWebVitals();
      
      // Initialize Performance Observer
      await initializePerformanceObserver();
      
      // Initialize Memory monitoring
      await initializeMemoryMonitoring();
      
      // Initialize Network monitoring
      await initializeNetworkMonitoring();
      
      // Collect initial metrics
      await collectMetrics();
      
    } catch (err) {
      setError(err.message);
      console.error('Failed to initialize performance monitoring:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initialize Web Vitals monitoring
  const initializeWebVitals = useCallback(async () => {
    try {
      // Dynamic import for Web Vitals
      const { getCLS, getFID, getFCP, getLCP, getTTFB } = await import('web-vitals');
      
      // Monitor Core Web Vitals
      getCLS((metric) => {
        setMetrics(prev => ({
          ...prev,
          webVitals: { ...prev.webVitals, cls: metric.value }
        }));
      });
      
      getFID((metric) => {
        setMetrics(prev => ({
          ...prev,
          webVitals: { ...prev.webVitals, fid: metric.value }
        }));
      });
      
      getFCP((metric) => {
        setMetrics(prev => ({
          ...prev,
          webVitals: { ...prev.webVitals, fcp: metric.value }
        }));
      });
      
      getLCP((metric) => {
        setMetrics(prev => ({
          ...prev,
          webVitals: { ...prev.webVitals, lcp: metric.value }
        }));
      });
      
      getTTFB((metric) => {
        setMetrics(prev => ({
          ...prev,
          webVitals: { ...prev.webVitals, ttfb: metric.value }
        }));
      });
      
    } catch (error) {
      console.warn('Web Vitals monitoring not available:', error);
    }
  }, []);

  // Initialize Performance Observer
  const initializePerformanceObserver = useCallback(async () => {
    if (!('PerformanceObserver' in window)) return;
    
    try {
      performanceObserver.current = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        
        entries.forEach(entry => {
          if (entry.entryType === 'paint') {
            setMetrics(prev => ({
              ...prev,
              performance: {
                ...prev.performance,
                paint: {
                  ...prev.performance.paint,
                  [entry.name]: entry.startTime
                }
              }
            }));
          }
          
          if (entry.entryType === 'navigation') {
            setMetrics(prev => ({
              ...prev,
              performance: {
                ...prev.performance,
                navigation: {
                  loadTime: entry.loadEventEnd - entry.loadEventStart,
                  domContentLoaded: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
                  firstByte: entry.responseStart - entry.requestStart
                }
              }
            }));
          }
        });
      });
      
      performanceObserver.current.observe({ entryTypes: ['paint', 'navigation', 'resource'] });
      
    } catch (error) {
      console.warn('Performance Observer not available:', error);
    }
  }, []);

  // Initialize Memory monitoring
  const initializeMemoryMonitoring = useCallback(async () => {
    if (!('memory' in performance)) return;
    
    try {
      memoryObserver.current = setInterval(() => {
        const memory = performance.memory;
        setMetrics(prev => ({
          ...prev,
          performance: {
            ...prev.performance,
            memory: {
              used: memory.usedJSHeapSize,
              total: memory.totalJSHeapSize,
              limit: memory.jsHeapSizeLimit,
              usage: (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100
            }
          }
        }));
      }, 5000);
      
    } catch (error) {
      console.warn('Memory monitoring not available:', error);
    }
  }, []);

  // Initialize Network monitoring
  const initializeNetworkMonitoring = useCallback(async () => {
    if (!('connection' in navigator)) return;
    
    try {
      const connection = navigator.connection;
      setMetrics(prev => ({
        ...prev,
        network: {
          ...prev.network,
          connection: {
            effectiveType: connection.effectiveType,
            downlink: connection.downlink,
            rtt: connection.rtt,
            saveData: connection.saveData
          }
        }
      }));
      
    } catch (error) {
      console.warn('Network monitoring not available:', error);
    }
  }, []);

  // Collect comprehensive metrics
  const collectMetrics = useCallback(async () => {
    try {
      const newMetrics = {
        // Web Vitals (already collected by observers)
        webVitals: metrics.webVitals,
        
        // Performance metrics
        performance: {
          ...metrics.performance,
          timing: performance.timing ? {
            loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
            domReady: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
            firstPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-paint')?.startTime,
            firstContentfulPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-contentful-paint')?.startTime
          } : null
        },
        
        // Bundle analysis
        bundle: await analyzeBundle(),
        
        // Network metrics
        network: {
          ...metrics.network,
          requests: performance.getEntriesByType('resource').length,
          bandwidth: await estimateBandwidth()
        },
        
        // Cache metrics
        cache: await analyzeCache(),
        
        // User experience metrics
        ux: await analyzeUserExperience()
      };
      
      setMetrics(newMetrics);
      
      // Store historical data
      setHistoricalData(prev => {
        const newData = [...prev, { timestamp: Date.now(), metrics: newMetrics }];
        return newData.slice(-100); // Keep last 100 data points
      });
      
      // Generate alerts and recommendations
      await generateAlertsAndRecommendations(newMetrics);
      
    } catch (error) {
      console.error('Failed to collect metrics:', error);
    }
  }, [metrics]);

  // Analyze bundle performance
  const analyzeBundle = useCallback(async () => {
    try {
      const scripts = Array.from(document.scripts);
      const stylesheets = Array.from(document.querySelectorAll('link[rel="stylesheet"]'));
      
      let totalSize = 0;
      const chunks = [];
      
      // Analyze scripts
      for (const script of scripts) {
        if (script.src) {
          try {
            const response = await fetch(script.src, { method: 'HEAD' });
            const size = parseInt(response.headers.get('content-length') || '0');
            totalSize += size;
            chunks.push({ type: 'script', src: script.src, size });
          } catch (error) {
            console.warn('Failed to analyze script:', script.src);
          }
        }
      }
      
      // Analyze stylesheets
      for (const stylesheet of stylesheets) {
        if (stylesheet.href) {
          try {
            const response = await fetch(stylesheet.href, { method: 'HEAD' });
            const size = parseInt(response.headers.get('content-length') || '0');
            totalSize += size;
            chunks.push({ type: 'stylesheet', src: stylesheet.href, size });
          } catch (error) {
            console.warn('Failed to analyze stylesheet:', stylesheet.href);
          }
        }
      }
      
      return {
        size: totalSize,
        chunks,
        loadTime: performance.timing ? performance.timing.loadEventEnd - performance.timing.navigationStart : null,
        compression: await analyzeCompression()
      };
      
    } catch (error) {
      console.error('Failed to analyze bundle:', error);
      return null;
    }
  }, []);

  // Analyze cache performance
  const analyzeCache = useCallback(async () => {
    try {
      if ('caches' in window) {
        const cacheNames = await caches.keys();
        let totalSize = 0;
        let hitCount = 0;
        let missCount = 0;
        
        for (const cacheName of cacheNames) {
          const cache = await caches.open(cacheName);
          const keys = await cache.keys();
          totalSize += keys.length;
        }
        
        return {
          hitRate: hitCount / (hitCount + missCount) || 0,
          size: totalSize,
          efficiency: totalSize > 0 ? (hitCount / totalSize) * 100 : 0,
          invalidation: await analyzeCacheInvalidation()
        };
      }
      
      return null;
    } catch (error) {
      console.error('Failed to analyze cache:', error);
      return null;
    }
  }, []);

  // Analyze user experience
  const analyzeUserExperience = useCallback(async () => {
    try {
      const interactions = performance.getEntriesByType('measure').length;
      const errors = window.performance.getEntriesByType('resource')
        .filter(entry => entry.transferSize === 0 && entry.decodedBodySize === 0).length;
      
      return {
        interactions,
        errors,
        accessibility: await analyzeAccessibility(),
        responsiveness: await analyzeResponsiveness()
      };
    } catch (error) {
      console.error('Failed to analyze UX:', error);
      return null;
    }
  }, []);

  // Generate alerts and recommendations
  const generateAlertsAndRecommendations = useCallback(async (currentMetrics) => {
    const newAlerts = [];
    const newRecommendations = [];
    
    // Web Vitals alerts
    if (currentMetrics.webVitals.lcp > 2500) {
      newAlerts.push({
        type: 'warning',
        category: 'web-vitals',
        message: 'LCP is above 2.5s threshold',
        value: currentMetrics.webVitals.lcp,
        recommendation: 'Optimize images and reduce server response time'
      });
    }
    
    if (currentMetrics.webVitals.fid > 100) {
      newAlerts.push({
        type: 'error',
        category: 'web-vitals',
        message: 'FID is above 100ms threshold',
        value: currentMetrics.webVitals.fid,
        recommendation: 'Reduce JavaScript execution time'
      });
    }
    
    if (currentMetrics.webVitals.cls > 0.1) {
      newAlerts.push({
        type: 'warning',
        category: 'web-vitals',
        message: 'CLS is above 0.1 threshold',
        value: currentMetrics.webVitals.cls,
        recommendation: 'Avoid layout shifts and reserve space for dynamic content'
      });
    }
    
    // Memory alerts
    if (currentMetrics.performance.memory?.usage > 80) {
      newAlerts.push({
        type: 'warning',
        category: 'memory',
        message: 'High memory usage detected',
        value: currentMetrics.performance.memory.usage,
        recommendation: 'Check for memory leaks and optimize resource usage'
      });
    }
    
    // Bundle size alerts
    if (currentMetrics.bundle?.size > 1000000) { // 1MB
      newAlerts.push({
        type: 'warning',
        category: 'bundle',
        message: 'Large bundle size detected',
        value: currentMetrics.bundle.size,
        recommendation: 'Implement code splitting and lazy loading'
      });
    }
    
    // Generate recommendations
    if (currentMetrics.webVitals.lcp > 2000) {
      newRecommendations.push({
        priority: 'high',
        category: 'performance',
        title: 'Optimize Largest Contentful Paint',
        description: 'LCP is above 2s. Consider optimizing images, reducing server response time, and eliminating render-blocking resources.',
        actions: [
          'Optimize images with WebP format',
          'Implement lazy loading',
          'Reduce server response time',
          'Eliminate render-blocking resources'
        ]
      });
    }
    
    if (currentMetrics.bundle?.size > 500000) { // 500KB
      newRecommendations.push({
        priority: 'medium',
        category: 'bundle',
        title: 'Implement Code Splitting',
        description: 'Bundle size is large. Consider implementing code splitting to reduce initial load time.',
        actions: [
          'Implement route-based code splitting',
          'Use dynamic imports for heavy components',
          'Optimize vendor bundles',
          'Implement tree shaking'
        ]
      });
    }
    
    setAlerts(newAlerts);
    setRecommendations(newRecommendations);
  }, []);

  // Cleanup function
  const cleanup = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    if (performanceObserver.current) {
      performanceObserver.current.disconnect();
    }
    if (memoryObserver.current) {
      clearInterval(memoryObserver.current);
    }
  }, []);

  // Helper functions (simplified for brevity)
  const estimateBandwidth = async () => null;
  const analyzeCompression = async () => null;
  const analyzeCacheInvalidation = async () => null;
  const analyzeAccessibility = async () => null;
  const analyzeResponsiveness = async () => null;

  // Render performance metrics
  const renderWebVitals = () => (
    <div className="web-vitals-section">
      <h3>Core Web Vitals</h3>
      <div className="metrics-grid">
        {Object.entries(metrics.webVitals).map(([key, value]) => (
          <div key={key} className="metric-card">
            <div className="metric-label">{key.toUpperCase()}</div>
            <div className="metric-value">{value ? `${value}ms` : 'N/A'}</div>
            <div className="metric-status">
              {getWebVitalStatus(key, value)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const getWebVitalStatus = (metric, value) => {
    if (!value) return 'N/A';
    
    const thresholds = {
      lcp: { good: 2500, poor: 4000 },
      fid: { good: 100, poor: 300 },
      cls: { good: 0.1, poor: 0.25 },
      fcp: { good: 1800, poor: 3000 },
      ttfb: { good: 800, poor: 1800 }
    };
    
    const threshold = thresholds[metric];
    if (!threshold) return 'N/A';
    
    if (value <= threshold.good) return '✅ Good';
    if (value <= threshold.poor) return '⚠️ Needs Improvement';
    return '❌ Poor';
  };

  const renderAlerts = () => (
    <div className="alerts-section">
      <h3>Performance Alerts</h3>
      {alerts.length === 0 ? (
        <div className="no-alerts">✅ No performance issues detected</div>
      ) : (
        <div className="alerts-list">
          {alerts.map((alert, index) => (
            <div key={index} className={`alert alert-${alert.type}`}>
              <div className="alert-message">{alert.message}</div>
              <div className="alert-value">Value: {alert.value}</div>
              <div className="alert-recommendation">{alert.recommendation}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderRecommendations = () => (
    <div className="recommendations-section">
      <h3>Performance Recommendations</h3>
      {recommendations.length === 0 ? (
        <div className="no-recommendations">✅ No recommendations at this time</div>
      ) : (
        <div className="recommendations-list">
          {recommendations.map((rec, index) => (
            <div key={index} className={`recommendation recommendation-${rec.priority}`}>
              <div className="recommendation-title">{rec.title}</div>
              <div className="recommendation-description">{rec.description}</div>
              <div className="recommendation-actions">
                <h4>Recommended Actions:</h4>
                <ul>
                  {rec.actions.map((action, actionIndex) => (
                    <li key={actionIndex}>{action}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  if (isLoading) {
    return (
      <div className={`real-time-performance-dashboard loading ${className}`}>
        <div className="loading-spinner">Loading performance metrics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`real-time-performance-dashboard error ${className}`}>
        <div className="error-message">Failed to load performance metrics: {error}</div>
      </div>
    );
  }

  return (
    <div className={`real-time-performance-dashboard ${className}`} {...props}>
      <div className="dashboard-header">
        <h2>Real-Time Performance Dashboard</h2>
        <div className="dashboard-controls">
          <select 
            value={selectedTimeRange} 
            onChange={(e) => setSelectedTimeRange(e.target.value)}
          >
            <option value="1h">Last Hour</option>
            <option value="6h">Last 6 Hours</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
          </select>
          <button onClick={collectMetrics}>Refresh</button>
        </div>
      </div>

      <div className="dashboard-content">
        {renderWebVitals()}
        {showAlerts && renderAlerts()}
        {showRecommendations && renderRecommendations()}
      </div>

      <style jsx>{`
        .real-time-performance-dashboard {
          padding: 20px;
          background: #f8f9fa;
          border-radius: 8px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          padding-bottom: 10px;
          border-bottom: 1px solid #dee2e6;
        }
        
        .dashboard-controls {
          display: flex;
          gap: 10px;
          align-items: center;
        }
        
        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
          margin-bottom: 20px;
        }
        
        .metric-card {
          background: white;
          padding: 15px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          text-align: center;
        }
        
        .metric-label {
          font-size: 0.875rem;
          color: #6c757d;
          margin-bottom: 5px;
        }
        
        .metric-value {
          font-size: 1.5rem;
          font-weight: bold;
          color: #333;
          margin-bottom: 5px;
        }
        
        .metric-status {
          font-size: 0.875rem;
          font-weight: 500;
        }
        
        .alert {
          padding: 15px;
          border-radius: 8px;
          margin-bottom: 10px;
          border-left: 4px solid;
        }
        
        .alert-warning {
          background: #fff3cd;
          border-color: #ffc107;
          color: #856404;
        }
        
        .alert-error {
          background: #f8d7da;
          border-color: #dc3545;
          color: #721c24;
        }
        
        .recommendation {
          background: white;
          padding: 20px;
          border-radius: 8px;
          margin-bottom: 15px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .recommendation-high {
          border-left: 4px solid #dc3545;
        }
        
        .recommendation-medium {
          border-left: 4px solid #ffc107;
        }
        
        .recommendation-low {
          border-left: 4px solid #28a745;
        }
        
        .recommendation-title {
          font-size: 1.1rem;
          font-weight: bold;
          margin-bottom: 10px;
        }
        
        .recommendation-description {
          color: #6c757d;
          margin-bottom: 15px;
        }
        
        .recommendation-actions ul {
          margin: 0;
          padding-left: 20px;
        }
        
        .recommendation-actions li {
          margin-bottom: 5px;
        }
      `}</style>
    </div>
  );
});

RealTimePerformanceDashboard.displayName = 'RealTimePerformanceDashboard';

RealTimePerformanceDashboard.propTypes = {
  refreshInterval: PropTypes.number,
  showCharts: PropTypes.bool,
  showRecommendations: PropTypes.bool,
  showAlerts: PropTypes.bool,
  className: PropTypes.string
};

export default RealTimePerformanceDashboard;
