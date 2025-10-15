/**
 * Memory optimization utilities for React applications
 */

import { useEffect, useCallback, useMemo, useRef } from 'react';

/**
 * Memory usage tracker
 */
class MemoryTracker {
  constructor() {
    this.measurements = [];
    this.isTracking = false;
    this.intervalId = null;
  }

  /**
   * Start tracking memory usage
   * @param {number} interval - Measurement interval in milliseconds
   */
  startTracking(interval = 5000) {
    if (this.isTracking) return;
    
    this.isTracking = true;
    this.intervalId = setInterval(() => {
      this.measureMemory();
    }, interval);
  }

  /**
   * Stop tracking memory usage
   */
  stopTracking() {
    if (!this.isTracking) return;
    
    this.isTracking = false;
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  /**
   * Measure current memory usage
   */
  measureMemory() {
    if ('memory' in performance) {
      const memory = performance.memory;
      const measurement = {
        timestamp: Date.now(),
        usedJSHeapSize: memory.usedJSHeapSize,
        totalJSHeapSize: memory.totalJSHeapSize,
        jsHeapSizeLimit: memory.jsHeapSizeLimit,
        usedPercentage: (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100
      };
      
      this.measurements.push(measurement);
      
      // Keep only last 100 measurements
      if (this.measurements.length > 100) {
        this.measurements = this.measurements.slice(-100);
      }
      
      return measurement;
    }
    return null;
  }

  /**
   * Get memory usage statistics
   * @returns {Object} Memory statistics
   */
  getStatistics() {
    if (this.measurements.length === 0) return null;
    
    const usedSizes = this.measurements.map(m => m.usedJSHeapSize);
    const totalSizes = this.measurements.map(m => m.totalJSHeapSize);
    const percentages = this.measurements.map(m => m.usedPercentage);
    
    return {
      current: this.measurements[this.measurements.length - 1],
      average: {
        usedJSHeapSize: usedSizes.reduce((a, b) => a + b, 0) / usedSizes.length,
        totalJSHeapSize: totalSizes.reduce((a, b) => a + b, 0) / totalSizes.length,
        usedPercentage: percentages.reduce((a, b) => a + b, 0) / percentages.length
      },
      peak: {
        usedJSHeapSize: Math.max(...usedSizes),
        totalJSHeapSize: Math.max(...totalSizes),
        usedPercentage: Math.max(...percentages)
      },
      trend: this.calculateTrend()
    };
  }

  /**
   * Calculate memory usage trend
   * @returns {string} Trend direction
   */
  calculateTrend() {
    if (this.measurements.length < 2) return 'stable';
    
    const recent = this.measurements.slice(-10);
    const older = this.measurements.slice(-20, -10);
    
    if (recent.length === 0 || older.length === 0) return 'stable';
    
    const recentAvg = recent.reduce((a, b) => a + b.usedJSHeapSize, 0) / recent.length;
    const olderAvg = older.reduce((a, b) => a + b.usedJSHeapSize, 0) / older.length;
    
    const change = ((recentAvg - olderAvg) / olderAvg) * 100;
    
    if (change > 10) return 'increasing';
    if (change < -10) return 'decreasing';
    return 'stable';
  }

  /**
   * Clear measurements
   */
  clearMeasurements() {
    this.measurements = [];
  }
}

// Global memory tracker instance
const memoryTracker = new MemoryTracker();

/**
 * Memory leak detector
 */
class MemoryLeakDetector {
  constructor() {
    this.observers = new Map();
    this.cleanupFunctions = new Set();
  }

  /**
   * Observe object for memory leaks
   * @param {string} name - Object name
   * @param {Object} obj - Object to observe
   * @param {Function} cleanup - Cleanup function
   */
  observe(name, obj, cleanup) {
    if (this.observers.has(name)) {
      console.warn(`Object ${name} is already being observed`);
      return;
    }
    
    this.observers.set(name, {
      object: obj,
      cleanup,
      createdAt: Date.now(),
      lastAccessed: Date.now()
    });
    
    if (cleanup) {
      this.cleanupFunctions.add(cleanup);
    }
  }

  /**
   * Stop observing object
   * @param {string} name - Object name
   */
  stopObserving(name) {
    const observer = this.observers.get(name);
    if (observer) {
      if (observer.cleanup) {
        observer.cleanup();
        this.cleanupFunctions.delete(observer.cleanup);
      }
      this.observers.delete(name);
    }
  }

  /**
   * Get memory leak report
   * @returns {Object} Memory leak report
   */
  getReport() {
    const now = Date.now();
    const report = {
      totalObservers: this.observers.size,
      potentialLeaks: [],
      recommendations: []
    };
    
    this.observers.forEach((observer, name) => {
      const age = now - observer.createdAt;
      const lastAccessed = now - observer.lastAccessed;
      
      if (age > 300000 && lastAccessed > 60000) { // 5 minutes old and not accessed in 1 minute
        report.potentialLeaks.push({
          name,
          age: Math.round(age / 1000),
          lastAccessed: Math.round(lastAccessed / 1000)
        });
      }
    });
    
    if (report.potentialLeaks.length > 0) {
      report.recommendations.push('Consider cleaning up unused objects');
      report.recommendations.push('Review object lifecycle management');
    }
    
    return report;
  }

  /**
   * Cleanup all observed objects
   */
  cleanupAll() {
    this.cleanupFunctions.forEach(cleanup => {
      try {
        cleanup();
      } catch (error) {
        console.error('Error during cleanup:', error);
      }
    });
    
    this.cleanupFunctions.clear();
    this.observers.clear();
  }
}

// Global memory leak detector instance
const memoryLeakDetector = new MemoryLeakDetector();

/**
 * Optimize large data structures
 * @param {Array} data - Data to optimize
 * @param {Object} options - Optimization options
 * @returns {Array} Optimized data
 */
export const optimizeLargeDataStructures = (data, options = {}) => {
  const {
    maxSize = 1000,
    chunkSize = 100,
    enableVirtualization = true,
    enableMemoization = true
  } = options;
  
  if (!Array.isArray(data)) return data;
  
  // If data is small, return as is
  if (data.length <= maxSize) return data;
  
  // For large datasets, implement virtualization
  if (enableVirtualization) {
    return {
      data: data,
      virtualized: true,
      chunkSize,
      totalItems: data.length,
      getChunk: (startIndex, endIndex) => data.slice(startIndex, endIndex)
    };
  }
  
  // For medium datasets, implement chunking
  const chunks = [];
  for (let i = 0; i < data.length; i += chunkSize) {
    chunks.push(data.slice(i, i + chunkSize));
  }
  
  return {
    chunks,
    totalItems: data.length,
    chunkSize
  };
};

/**
 * Implement cleanup in useEffect
 * @param {Function} cleanup - Cleanup function
 * @param {Array} dependencies - Dependencies array
 * @returns {Function} Optimized useEffect
 */
export const useOptimizedEffect = (cleanup, dependencies = []) => {
  return (effect, deps) => {
    const cleanupRef = useRef();
    
    useEffect(() => {
      cleanupRef.current = effect();
      
      return () => {
        if (cleanupRef.current) {
          cleanupRef.current();
        }
      };
    }, deps);
  };
};

/**
 * Memory-efficient component wrapper
 * @param {React.Component} Component - Component to wrap
 * @param {Object} options - Optimization options
 * @returns {React.Component} Optimized component
 */
export const withMemoryOptimization = (Component, options = {}) => {
  const {
    enableCleanup = true,
    enableLeakDetection = true,
    maxRenderCount = 1000
  } = options;
  
  return React.memo((props) => {
    const renderCountRef = useRef(0);
    const cleanupRef = useRef();
    
    // Track render count
    renderCountRef.current += 1;
    
    // Memory leak detection
    if (enableLeakDetection && renderCountRef.current > maxRenderCount) {
      console.warn(`Component ${Component.displayName || Component.name} has rendered ${renderCountRef.current} times`);
    }
    
    // Setup cleanup
    useEffect(() => {
      if (enableCleanup) {
        cleanupRef.current = () => {
          // Component cleanup logic
          renderCountRef.current = 0;
        };
      }
      
      return () => {
        if (cleanupRef.current) {
          cleanupRef.current();
        }
      };
    }, []);
    
    return <Component {...props} />;
  });
};

/**
 * Garbage collection monitoring
 * @param {Object} options - Monitoring options
 * @returns {Object} Monitoring controls
 */
export const monitorGarbageCollection = (options = {}) => {
  const {
    interval = 10000, // 10 seconds
    threshold = 0.8, // 80% memory usage
    enableLogging = true
  } = options;
  
  let monitoringInterval = null;
  let isMonitoring = false;
  
  const startMonitoring = () => {
    if (isMonitoring) return;
    
    isMonitoring = true;
    monitoringInterval = setInterval(() => {
      const memory = performance.memory;
      const usage = memory.usedJSHeapSize / memory.jsHeapSizeLimit;
      
      if (usage > threshold) {
        if (enableLogging) {
          console.warn(`High memory usage detected: ${(usage * 100).toFixed(1)}%`);
        }
        
        // Trigger garbage collection if available
        if (window.gc) {
          window.gc();
        }
      }
    }, interval);
  };
  
  const stopMonitoring = () => {
    if (!isMonitoring) return;
    
    isMonitoring = false;
    if (monitoringInterval) {
      clearInterval(monitoringInterval);
      monitoringInterval = null;
    }
  };
  
  return {
    startMonitoring,
    stopMonitoring,
    isMonitoring: () => isMonitoring
  };
};

/**
 * Memory optimization utilities
 */
export const memoryOptimizer = {
  /**
   * Start memory tracking
   * @param {number} interval - Measurement interval
   */
  startTracking: (interval) => memoryTracker.startTracking(interval),
  
  /**
   * Stop memory tracking
   */
  stopTracking: () => memoryTracker.stopTracking(),
  
  /**
   * Get memory statistics
   * @returns {Object} Memory statistics
   */
  getStatistics: () => memoryTracker.getStatistics(),
  
  /**
   * Clear memory measurements
   */
  clearMeasurements: () => memoryTracker.clearMeasurements(),
  
  /**
   * Observe object for leaks
   * @param {string} name - Object name
   * @param {Object} obj - Object to observe
   * @param {Function} cleanup - Cleanup function
   */
  observeObject: (name, obj, cleanup) => memoryLeakDetector.observe(name, obj, cleanup),
  
  /**
   * Stop observing object
   * @param {string} name - Object name
   */
  stopObserving: (name) => memoryLeakDetector.stopObserving(name),
  
  /**
   * Get memory leak report
   * @returns {Object} Memory leak report
   */
  getLeakReport: () => memoryLeakDetector.getReport(),
  
  /**
   * Cleanup all observed objects
   */
  cleanupAll: () => memoryLeakDetector.cleanupAll(),
  
  /**
   * Optimize data structures
   * @param {Array} data - Data to optimize
   * @param {Object} options - Optimization options
   * @returns {Array} Optimized data
   */
  optimizeData: optimizeLargeDataStructures,
  
  /**
   * Monitor garbage collection
   * @param {Object} options - Monitoring options
   * @returns {Object} Monitoring controls
   */
  monitorGC: monitorGarbageCollection
};

export default memoryOptimizer;
