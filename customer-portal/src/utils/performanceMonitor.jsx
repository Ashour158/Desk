/**
 * Advanced performance monitoring system for React components and API calls.
 */

import React from 'react';
import Logger from './logger';

class PerformanceMonitor {
  constructor() {
    this.metrics = new Map();
    this.observers = new Map();
    this.isEnabled = process.env.NODE_ENV === 'production' || 
                    localStorage.getItem('performance_monitoring') === 'true';
    
    if (this.isEnabled) {
      this.initializeWebVitals();
      this.initializeResourceTiming();
    }
  }

  /**
   * Initialize Web Vitals monitoring
   */
  initializeWebVitals() {
    if (typeof window === 'undefined') return;

    // Import web-vitals dynamically
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(this.handleWebVital.bind(this, 'CLS'));
      getFID(this.handleWebVital.bind(this, 'FID'));
      getFCP(this.handleWebVital.bind(this, 'FCP'));
      getLCP(this.handleWebVital.bind(this, 'LCP'));
      getTTFB(this.handleWebVital.bind(this, 'TTFB'));
    }).catch(error => {
      Logger.warn('Web Vitals not available:', error);
    });
  }

  /**
   * Initialize Resource Timing monitoring
   */
  initializeResourceTiming() {
    if (typeof window === 'undefined') return;

    // Monitor resource loading performance
    if ('performance' in window && 'getEntriesByType' in window.performance) {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.handleResourceTiming(entry);
        }
      });

      try {
        observer.observe({ entryTypes: ['resource', 'navigation'] });
        this.observers.set('resource', observer);
      } catch (error) {
        Logger.warn('Resource timing observer not supported:', error);
      }
    }
  }

  /**
   * Handle Web Vitals metrics
   */
  handleWebVital(name, metric) {
    const data = {
      name,
      value: metric.value,
      delta: metric.delta,
      id: metric.id,
      navigationType: metric.navigationType,
      rating: metric.rating
    };

    Logger.performance(`Web Vital: ${name}`, metric.value, data);
    
    // Send to analytics service
    this.sendToAnalytics('web-vital', data);
  }

  /**
   * Handle Resource Timing metrics
   */
  handleResourceTiming(entry) {
    const data = {
      name: entry.name,
      entryType: entry.entryType,
      duration: entry.duration,
      startTime: entry.startTime,
      transferSize: entry.transferSize,
      encodedBodySize: entry.encodedBodySize,
      decodedBodySize: entry.decodedBodySize
    };

    // Only log significant resources
    if (entry.duration > 100) { // More than 100ms
      Logger.performance(`Resource: ${entry.name}`, entry.duration, data);
    }
  }

  /**
   * Start measuring a performance metric
   */
  start(name) {
    if (!this.isEnabled) return;

    const startTime = performance.now();
    this.metrics.set(name, {
      startTime,
      marks: [{ name: `${name}_start`, timestamp: startTime }]
    });

    Logger.debug(`Performance metric '${name}' started`);
  }

  /**
   * Record a mark within a performance metric
   */
  mark(name, markName) {
    if (!this.isEnabled) return;

    const metric = this.metrics.get(name);
    if (!metric) return;

    const timestamp = performance.now();
    metric.marks.push({ name: markName, timestamp });

    Logger.debug(`Performance mark '${markName}' recorded for '${name}'`);
  }

  /**
   * End measuring a performance metric
   */
  end(name, context = {}) {
    if (!this.isEnabled) return;

    const metric = this.metrics.get(name);
    if (!metric) return;

    const endTime = performance.now();
    const duration = endTime - metric.startTime;

    metric.marks.push({ name: `${name}_end`, timestamp: endTime });

    const data = {
      duration,
      marks: metric.marks.map(mark => ({
        name: mark.name,
        relativeTime: (mark.timestamp - metric.startTime).toFixed(2)
      })),
      ...context
    };

    Logger.performance(name, duration, data);

    // Send to analytics
    this.sendToAnalytics('performance', { name, ...data });

    // Clean up
    this.metrics.delete(name);
  }

  /**
   * Measure a React component render
   */
  measureRender(componentName, renderFn) {
    if (!this.isEnabled) return renderFn();

    this.start(`render_${componentName}`);
    try {
      const result = renderFn();
      return result;
    } finally {
      this.end(`render_${componentName}`, { component: componentName });
    }
  }

  /**
   * Measure an API call
   */
  async measureAPI(endpoint, apiCall) {
    if (!this.isEnabled) return apiCall();

    this.start(`api_${endpoint}`);
    try {
      const result = await apiCall();
      this.end(`api_${endpoint}`, { endpoint, success: true });
      return result;
    } catch (error) {
      this.end(`api_${endpoint}`, { endpoint, success: false, error: error.message });
      throw error;
    }
  }

  /**
   * Measure a function execution
   */
  async measure(name, fn, context = {}) {
    if (!this.isEnabled) return fn();

    this.start(name);
    try {
      const result = await fn();
      this.end(name, { ...context, success: true });
      return result;
    } catch (error) {
      this.end(name, { ...context, success: false, error: error.message });
      throw error;
    }
  }

  /**
   * Get current performance metrics
   */
  getMetrics() {
    return {
      activeMetrics: Array.from(this.metrics.keys()),
      observers: Array.from(this.observers.keys()),
      isEnabled: this.isEnabled
    };
  }

  /**
   * Send metrics to analytics service
   */
  sendToAnalytics(type, data) {
    if (!this.isEnabled) return;

    try {
      // Send to your analytics service
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', 'performance_metric', {
          event_category: 'Performance',
          event_label: type,
          value: data.duration || data.value,
          custom_map: data
        });
      }

      // Send to custom analytics endpoint
      fetch('/api/analytics/performance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type,
          data,
          timestamp: new Date().toISOString(),
          url: window.location.href,
          userAgent: navigator.userAgent
        })
      }).catch(error => {
        Logger.warn('Failed to send performance metrics:', error);
      });
    } catch (error) {
      Logger.warn('Error sending performance metrics:', error);
    }
  }

  /**
   * Clean up observers
   */
  cleanup() {
    this.observers.forEach(observer => {
      if (observer.disconnect) {
        observer.disconnect();
      }
    });
    this.observers.clear();
    this.metrics.clear();
  }
}

// Create global instance
const performanceMonitor = new PerformanceMonitor();

// React Profiler integration
export const Profiler = ({ id, children }) => {
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

    Logger.performance(`React Profiler: ${id}`, actualDuration, data);
    performanceMonitor.sendToAnalytics('react_profiler', data);
  };

  return (
    <React.Profiler id={id} onRender={onRenderCallback}>
      {children}
    </React.Profiler>
  );
};

// HOC for automatic performance monitoring
export const withPerformanceMonitoring = (WrappedComponent, componentName) => {
  return React.memo((props) => {
    return performanceMonitor.measureRender(componentName, () => (
      <WrappedComponent {...props} />
    ));
  });
};

// Hook for performance monitoring
export const usePerformanceMonitoring = (componentName) => {
  const startTime = React.useRef(null);
  const [isMonitoring, setIsMonitoring] = React.useState(false);

  const startMonitoring = React.useCallback(() => {
    startTime.current = performance.now();
    performanceMonitor.start(`component_${componentName}`);
    setIsMonitoring(true);
  }, [componentName]);

  const stopMonitoring = React.useCallback(() => {
    if (startTime.current) {
      const duration = performance.now() - startTime.current;
      performanceMonitor.end(`component_${componentName}`, { 
        component: componentName,
        duration 
      });
    }
    setIsMonitoring(false);
  }, [componentName]);

  const getMetrics = React.useCallback(() => {
    return performanceMonitor.getMetrics();
  }, []);

  React.useEffect(() => {
    return () => {
      if (startTime.current) {
        const duration = performance.now() - startTime.current;
        performanceMonitor.end(`component_${componentName}`, { 
          component: componentName,
          duration 
        });
      }
    };
  }, [componentName]);

  return {
    startMonitoring,
    stopMonitoring,
    getMetrics,
    isMonitoring,
    start: (name) => performanceMonitor.start(`${componentName}_${name}`),
    end: (name, context) => performanceMonitor.end(`${componentName}_${name}`, context),
    mark: (name, markName) => performanceMonitor.mark(`${componentName}_${name}`, markName)
  };
};

export default performanceMonitor;