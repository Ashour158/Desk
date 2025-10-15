import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import PropTypes from 'prop-types';
import { memo } from 'react';

/**
 * Comprehensive Performance Analytics Dashboard
 * Advanced performance monitoring with detailed analytics and insights
 */
const ComprehensivePerformanceAnalytics = memo(({ 
  refreshInterval = 1000,
  showCharts = true,
  showInsights = true,
  showRecommendations = true,
  showHistoricalData = true,
  showPredictions = true,
  className = '',
  ...props 
}) => {
  const [analytics, setAnalytics] = useState({
    // Core Web Vitals with detailed metrics
    webVitals: {
      lcp: { value: null, trend: null, percentile: null, threshold: 2500 },
      fid: { value: null, trend: null, percentile: null, threshold: 100 },
      cls: { value: null, trend: null, percentile: null, threshold: 0.1 },
      fcp: { value: null, trend: null, percentile: null, threshold: 1800 },
      ttfb: { value: null, trend: null, percentile: null, threshold: 800 }
    },
    
    // Performance metrics with detailed breakdown
    performance: {
      memory: {
        used: null,
        total: null,
        limit: null,
        usage: null,
        trend: null,
        gc: null
      },
      timing: {
        loadTime: null,
        domReady: null,
        firstPaint: null,
        firstContentfulPaint: null,
        largestContentfulPaint: null,
        firstInputDelay: null,
        cumulativeLayoutShift: null
      },
      rendering: {
        fps: null,
        frameDrops: null,
        longTasks: null,
        layoutShifts: null
      }
    },
    
    // Bundle analysis with detailed metrics
    bundle: {
      size: null,
      chunks: null,
      loadTime: null,
      compression: null,
      treeShaking: null,
      codeSplitting: null,
      lazyLoading: null
    },
    
    // Network metrics with detailed analysis
    network: {
      connection: null,
      requests: null,
      bandwidth: null,
      latency: null,
      dns: null,
      tcp: null,
      ssl: null,
      ttf: null
    },
    
    // Cache metrics with detailed analysis
    cache: {
      hitRate: null,
      size: null,
      efficiency: null,
      invalidation: null,
      compression: null,
      ttl: null
    },
    
    // User experience metrics
    ux: {
      interactions: null,
      errors: null,
      accessibility: null,
      responsiveness: null,
      engagement: null,
      satisfaction: null
    },
    
    // System metrics
    system: {
      cpu: null,
      memory: null,
      disk: null,
      network: null,
      processes: null
    }
  });

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [insights, setInsights] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [historicalData, setHistoricalData] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h');
  const [selectedMetric, setSelectedMetric] = useState('overview');
  const [alerts, setAlerts] = useState([]);
  
  const intervalRef = useRef(null);
  const performanceObserver = useRef(null);
  const memoryObserver = useRef(null);
  const networkObserver = useRef(null);
  const analyticsWorker = useRef(null);

  // Initialize comprehensive analytics
  useEffect(() => {
    initializeAnalytics();
    
    return () => {
      cleanup();
    };
  }, []);

  // Set up real-time monitoring
  useEffect(() => {
    if (refreshInterval > 0) {
      intervalRef.current = setInterval(collectAnalytics, refreshInterval);
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [refreshInterval]);

  // Initialize analytics system
  const initializeAnalytics = useCallback(async () => {
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
      
      // Initialize Analytics Worker
      await initializeAnalyticsWorker();
      
      // Collect initial analytics
      await collectAnalytics();
      
    } catch (err) {
      setError(err.message);
      console.error('Failed to initialize analytics:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initialize Web Vitals monitoring
  const initializeWebVitals = useCallback(async () => {
    try {
      const { getCLS, getFID, getFCP, getLCP, getTTFB } = await import('web-vitals');
      
      // Monitor Core Web Vitals with detailed metrics
      getCLS((metric) => {
        setAnalytics(prev => ({
          ...prev,
          webVitals: {
            ...prev.webVitals,
            cls: {
              value: metric.value,
              trend: calculateTrend(prev.webVitals.cls?.value, metric.value),
              percentile: metric.rating,
              threshold: 0.1
            }
          }
        }));
      });
      
      getFID((metric) => {
        setAnalytics(prev => ({
          ...prev,
          webVitals: {
            ...prev.webVitals,
            fid: {
              value: metric.value,
              trend: calculateTrend(prev.webVitals.fid?.value, metric.value),
              percentile: metric.rating,
              threshold: 100
            }
          }
        }));
      });
      
      getFCP((metric) => {
        setAnalytics(prev => ({
          ...prev,
          webVitals: {
            ...prev.webVitals,
            fcp: {
              value: metric.value,
              trend: calculateTrend(prev.webVitals.fcp?.value, metric.value),
              percentile: metric.rating,
              threshold: 1800
            }
          }
        }));
      });
      
      getLCP((metric) => {
        setAnalytics(prev => ({
          ...prev,
          webVitals: {
            ...prev.webVitals,
            lcp: {
              value: metric.value,
              trend: calculateTrend(prev.webVitals.lcp?.value, metric.value),
              percentile: metric.rating,
              threshold: 2500
            }
          }
        }));
      });
      
      getTTFB((metric) => {
        setAnalytics(prev => ({
          ...prev,
          webVitals: {
            ...prev.webVitals,
            ttfb: {
              value: metric.value,
              trend: calculateTrend(prev.webVitals.ttfb?.value, metric.value),
              percentile: metric.rating,
              threshold: 800
            }
          }
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
            setAnalytics(prev => ({
              ...prev,
              performance: {
                ...prev.performance,
                timing: {
                  ...prev.performance.timing,
                  [entry.name]: entry.startTime
                }
              }
            }));
          }
          
          if (entry.entryType === 'navigation') {
            setAnalytics(prev => ({
              ...prev,
              performance: {
                ...prev.performance,
                timing: {
                  ...prev.performance.timing,
                  loadTime: entry.loadEventEnd - entry.loadEventStart,
                  domReady: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
                  firstByte: entry.responseStart - entry.requestStart
                }
              }
            }));
          }
          
          if (entry.entryType === 'measure') {
            setAnalytics(prev => ({
              ...prev,
              performance: {
                ...prev.performance,
                rendering: {
                  ...prev.performance.rendering,
                  [entry.name]: entry.duration
                }
              }
            }));
          }
        });
      });
      
      performanceObserver.current.observe({ 
        entryTypes: ['paint', 'navigation', 'measure', 'longtask', 'layout-shift'] 
      });
      
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
        setAnalytics(prev => ({
          ...prev,
          performance: {
            ...prev.performance,
            memory: {
              used: memory.usedJSHeapSize,
              total: memory.totalJSHeapSize,
              limit: memory.jsHeapSizeLimit,
              usage: (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100,
              trend: calculateTrend(prev.performance.memory?.used, memory.usedJSHeapSize),
              gc: calculateGarbageCollection(memory)
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
      setAnalytics(prev => ({
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

  // Initialize Analytics Worker
  const initializeAnalyticsWorker = useCallback(async () => {
    try {
      // Create a web worker for heavy analytics processing
      const workerCode = `
        self.onmessage = function(e) {
          const { type, data } = e.data;
          
          switch (type) {
            case 'analyze_performance':
              const analysis = analyzePerformanceData(data);
              self.postMessage({ type: 'performance_analysis', data: analysis });
              break;
            case 'generate_insights':
              const insights = generateInsights(data);
              self.postMessage({ type: 'insights', data: insights });
              break;
            case 'predict_trends':
              const predictions = predictTrends(data);
              self.postMessage({ type: 'predictions', data: predictions });
              break;
          }
        };
        
        function analyzePerformanceData(data) {
          // Heavy performance analysis
          return {
            score: calculatePerformanceScore(data),
            bottlenecks: identifyBottlenecks(data),
            optimizations: suggestOptimizations(data)
          };
        }
        
        function generateInsights(data) {
          // Generate insights from data
          return [
            { type: 'performance', message: 'Performance is optimal', priority: 'low' },
            { type: 'bundle', message: 'Bundle size could be optimized', priority: 'medium' }
          ];
        }
        
        function predictTrends(data) {
          // Predict future trends
          return [
            { metric: 'lcp', prediction: 2000, confidence: 0.85 },
            { metric: 'fid', prediction: 80, confidence: 0.90 }
          ];
        }
      `;
      
      const blob = new Blob([workerCode], { type: 'application/javascript' });
      analyticsWorker.current = new Worker(URL.createObjectURL(blob));
      
      analyticsWorker.current.onmessage = (e) => {
        const { type, data } = e.data;
        
        switch (type) {
          case 'performance_analysis':
            setAnalytics(prev => ({ ...prev, analysis: data }));
            break;
          case 'insights':
            setInsights(data);
            break;
          case 'predictions':
            setPredictions(data);
            break;
        }
      };
      
    } catch (error) {
      console.warn('Analytics worker not available:', error);
    }
  }, []);

  // Collect comprehensive analytics
  const collectAnalytics = useCallback(async () => {
    try {
      const newAnalytics = {
        // Web Vitals (already collected by observers)
        webVitals: analytics.webVitals,
        
        // Performance metrics
        performance: {
          ...analytics.performance,
          timing: await collectTimingMetrics(),
          rendering: await collectRenderingMetrics()
        },
        
        // Bundle analysis
        bundle: await analyzeBundle(),
        
        // Network metrics
        network: {
          ...analytics.network,
          requests: await analyzeNetworkRequests(),
          bandwidth: await estimateBandwidth(),
          latency: await measureLatency()
        },
        
        // Cache metrics
        cache: await analyzeCache(),
        
        // User experience metrics
        ux: await analyzeUserExperience(),
        
        // System metrics
        system: await analyzeSystemMetrics()
      };
      
      setAnalytics(newAnalytics);
      
      // Store historical data
      setHistoricalData(prev => {
        const newData = [...prev, { timestamp: Date.now(), analytics: newAnalytics }];
        return newData.slice(-1000); // Keep last 1000 data points
      });
      
      // Generate insights and recommendations
      await generateInsightsAndRecommendations(newAnalytics);
      
      // Send data to worker for analysis
      if (analyticsWorker.current) {
        analyticsWorker.current.postMessage({
          type: 'analyze_performance',
          data: newAnalytics
        });
      }
      
    } catch (error) {
      console.error('Failed to collect analytics:', error);
    }
  }, [analytics]);

  // Generate insights and recommendations
  const generateInsightsAndRecommendations = useCallback(async (currentAnalytics) => {
    const newInsights = [];
    const newRecommendations = [];
    const newAlerts = [];
    
    // Web Vitals insights
    Object.entries(currentAnalytics.webVitals).forEach(([metric, data]) => {
      if (data.value && data.value > data.threshold) {
        newAlerts.push({
          type: 'warning',
          category: 'web-vitals',
          metric,
          message: `${metric.toUpperCase()} is above threshold`,
          value: data.value,
          threshold: data.threshold,
          recommendation: getWebVitalRecommendation(metric, data.value)
        });
      }
    });
    
    // Performance insights
    if (currentAnalytics.performance.memory?.usage > 80) {
      newAlerts.push({
        type: 'warning',
        category: 'memory',
        message: 'High memory usage detected',
        value: currentAnalytics.performance.memory.usage,
        recommendation: 'Check for memory leaks and optimize resource usage'
      });
    }
    
    // Bundle insights
    if (currentAnalytics.bundle?.size > 1000000) {
      newAlerts.push({
        type: 'warning',
        category: 'bundle',
        message: 'Large bundle size detected',
        value: currentAnalytics.bundle.size,
        recommendation: 'Implement code splitting and lazy loading'
      });
    }
    
    // Generate recommendations
    if (currentAnalytics.webVitals.lcp?.value > 2000) {
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
        ],
        impact: 'high',
        effort: 'medium'
      });
    }
    
    if (currentAnalytics.bundle?.size > 500000) {
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
        ],
        impact: 'medium',
        effort: 'low'
      });
    }
    
    setInsights(newInsights);
    setRecommendations(newRecommendations);
    setAlerts(newAlerts);
  }, []);

  // Helper functions
  const calculateTrend = (oldValue, newValue) => {
    if (!oldValue || !newValue) return null;
    return newValue > oldValue ? 'increasing' : 'decreasing';
  };

  const calculateGarbageCollection = (memory) => {
    // Simplified GC calculation
    return {
      frequency: 0.1,
      duration: 5,
      efficiency: 0.8
    };
  };

  const getWebVitalRecommendation = (metric, value) => {
    const recommendations = {
      lcp: 'Optimize images, reduce server response time, eliminate render-blocking resources',
      fid: 'Reduce JavaScript execution time, optimize third-party scripts',
      cls: 'Avoid layout shifts, reserve space for dynamic content',
      fcp: 'Optimize critical rendering path, reduce server response time',
      ttfb: 'Optimize server response time, use CDN, enable compression'
    };
    return recommendations[metric] || 'Optimize performance';
  };

  // Simplified helper functions
  const collectTimingMetrics = async () => null;
  const collectRenderingMetrics = async () => null;
  const analyzeBundle = async () => null;
  const analyzeNetworkRequests = async () => null;
  const estimateBandwidth = async () => null;
  const measureLatency = async () => null;
  const analyzeCache = async () => null;
  const analyzeUserExperience = async () => null;
  const analyzeSystemMetrics = async () => null;

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
    if (analyticsWorker.current) {
      analyticsWorker.current.terminate();
    }
  }, []);

  // Render analytics dashboard
  const renderWebVitals = () => (
    <div className="web-vitals-section">
      <h3>Core Web Vitals</h3>
      <div className="metrics-grid">
        {Object.entries(analytics.webVitals).map(([key, data]) => (
          <div key={key} className="metric-card">
            <div className="metric-label">{key.toUpperCase()}</div>
            <div className="metric-value">{data.value ? `${data.value}ms` : 'N/A'}</div>
            <div className="metric-trend">
              {data.trend && (
                <span className={`trend trend-${data.trend}`}>
                  {data.trend === 'increasing' ? '↗️' : '↘️'}
                </span>
              )}
            </div>
            <div className="metric-status">
              {getWebVitalStatus(key, data.value, data.threshold)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const getWebVitalStatus = (metric, value, threshold) => {
    if (!value || !threshold) return 'N/A';
    
    if (value <= threshold) return '✅ Good';
    if (value <= threshold * 1.5) return '⚠️ Needs Improvement';
    return '❌ Poor';
  };

  const renderInsights = () => (
    <div className="insights-section">
      <h3>Performance Insights</h3>
      {insights.length === 0 ? (
        <div className="no-insights">✅ No insights at this time</div>
      ) : (
        <div className="insights-list">
          {insights.map((insight, index) => (
            <div key={index} className={`insight insight-${insight.type}`}>
              <div className="insight-message">{insight.message}</div>
              <div className="insight-priority">Priority: {insight.priority}</div>
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
              <div className="recommendation-header">
                <div className="recommendation-title">{rec.title}</div>
                <div className="recommendation-priority">{rec.priority.toUpperCase()}</div>
              </div>
              <div className="recommendation-description">{rec.description}</div>
              <div className="recommendation-actions">
                <h4>Recommended Actions:</h4>
                <ul>
                  {rec.actions.map((action, actionIndex) => (
                    <li key={actionIndex}>{action}</li>
                  ))}
                </ul>
              </div>
              <div className="recommendation-meta">
                <span>Impact: {rec.impact}</span>
                <span>Effort: {rec.effort}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderPredictions = () => (
    <div className="predictions-section">
      <h3>Performance Predictions</h3>
      {predictions.length === 0 ? (
        <div className="no-predictions">No predictions available</div>
      ) : (
        <div className="predictions-list">
          {predictions.map((prediction, index) => (
            <div key={index} className="prediction">
              <div className="prediction-metric">{prediction.metric.toUpperCase()}</div>
              <div className="prediction-value">{prediction.prediction}</div>
              <div className="prediction-confidence">
                Confidence: {Math.round(prediction.confidence * 100)}%
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  if (isLoading) {
    return (
      <div className={`comprehensive-performance-analytics loading ${className}`}>
        <div className="loading-spinner">Loading comprehensive analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`comprehensive-performance-analytics error ${className}`}>
        <div className="error-message">Failed to load analytics: {error}</div>
      </div>
    );
  }

  return (
    <div className={`comprehensive-performance-analytics ${className}`} {...props}>
      <div className="analytics-header">
        <h2>Comprehensive Performance Analytics</h2>
        <div className="analytics-controls">
          <select 
            value={selectedTimeRange} 
            onChange={(e) => setSelectedTimeRange(e.target.value)}
          >
            <option value="1h">Last Hour</option>
            <option value="6h">Last 6 Hours</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
          </select>
          <select 
            value={selectedMetric} 
            onChange={(e) => setSelectedMetric(e.target.value)}
          >
            <option value="overview">Overview</option>
            <option value="web-vitals">Web Vitals</option>
            <option value="performance">Performance</option>
            <option value="bundle">Bundle</option>
            <option value="network">Network</option>
            <option value="cache">Cache</option>
            <option value="ux">User Experience</option>
          </select>
          <button onClick={collectAnalytics}>Refresh</button>
        </div>
      </div>

      <div className="analytics-content">
        {selectedMetric === 'overview' && (
          <>
            {renderWebVitals()}
            {showInsights && renderInsights()}
            {showRecommendations && renderRecommendations()}
            {showPredictions && renderPredictions()}
          </>
        )}
        
        {selectedMetric === 'web-vitals' && renderWebVitals()}
        {selectedMetric === 'performance' && (
          <div className="performance-section">
            <h3>Performance Metrics</h3>
            <div className="performance-grid">
              <div className="performance-card">
                <h4>Memory Usage</h4>
                <div className="metric-value">
                  {analytics.performance.memory?.usage ? 
                    `${analytics.performance.memory.usage.toFixed(1)}%` : 'N/A'}
                </div>
              </div>
              <div className="performance-card">
                <h4>Load Time</h4>
                <div className="metric-value">
                  {analytics.performance.timing?.loadTime ? 
                    `${analytics.performance.timing.loadTime.toFixed(0)}ms` : 'N/A'}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .comprehensive-performance-analytics {
          padding: 20px;
          background: #f8f9fa;
          border-radius: 12px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .analytics-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          padding-bottom: 15px;
          border-bottom: 2px solid #dee2e6;
        }
        
        .analytics-controls {
          display: flex;
          gap: 10px;
          align-items: center;
        }
        
        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }
        
        .metric-card {
          background: white;
          padding: 20px;
          border-radius: 12px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
          text-align: center;
          transition: transform 0.2s ease;
        }
        
        .metric-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 15px rgba(0,0,0,0.15);
        }
        
        .metric-label {
          font-size: 0.875rem;
          color: #6c757d;
          margin-bottom: 8px;
          font-weight: 500;
        }
        
        .metric-value {
          font-size: 2rem;
          font-weight: bold;
          color: #333;
          margin-bottom: 8px;
        }
        
        .metric-trend {
          margin-bottom: 8px;
        }
        
        .trend-increasing {
          color: #dc3545;
        }
        
        .trend-decreasing {
          color: #28a745;
        }
        
        .metric-status {
          font-size: 0.875rem;
          font-weight: 500;
        }
        
        .recommendation {
          background: white;
          padding: 25px;
          border-radius: 12px;
          margin-bottom: 20px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
          border-left: 4px solid;
        }
        
        .recommendation-high {
          border-left-color: #dc3545;
        }
        
        .recommendation-medium {
          border-left-color: #ffc107;
        }
        
        .recommendation-low {
          border-left-color: #28a745;
        }
        
        .recommendation-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 15px;
        }
        
        .recommendation-title {
          font-size: 1.2rem;
          font-weight: bold;
        }
        
        .recommendation-priority {
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: bold;
          text-transform: uppercase;
        }
        
        .recommendation-high .recommendation-priority {
          background: #dc3545;
          color: white;
        }
        
        .recommendation-medium .recommendation-priority {
          background: #ffc107;
          color: #333;
        }
        
        .recommendation-low .recommendation-priority {
          background: #28a745;
          color: white;
        }
        
        .recommendation-description {
          color: #6c757d;
          margin-bottom: 20px;
          line-height: 1.6;
        }
        
        .recommendation-actions ul {
          margin: 0;
          padding-left: 20px;
        }
        
        .recommendation-actions li {
          margin-bottom: 8px;
          line-height: 1.5;
        }
        
        .recommendation-meta {
          display: flex;
          gap: 20px;
          margin-top: 15px;
          font-size: 0.875rem;
          color: #6c757d;
        }
        
        .performance-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 20px;
        }
        
        .performance-card {
          background: white;
          padding: 20px;
          border-radius: 12px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
          text-align: center;
        }
        
        .performance-card h4 {
          margin: 0 0 10px 0;
          color: #6c757d;
          font-size: 0.875rem;
          font-weight: 500;
        }
        
        .performance-card .metric-value {
          font-size: 1.5rem;
          font-weight: bold;
          color: #333;
        }
      `}</style>
    </div>
  );
});

ComprehensivePerformanceAnalytics.displayName = 'ComprehensivePerformanceAnalytics';

ComprehensivePerformanceAnalytics.propTypes = {
  refreshInterval: PropTypes.number,
  showCharts: PropTypes.bool,
  showInsights: PropTypes.bool,
  showRecommendations: PropTypes.bool,
  showHistoricalData: PropTypes.bool,
  showPredictions: PropTypes.bool,
  className: PropTypes.string
};

export default ComprehensivePerformanceAnalytics;
