import React, { useState, useEffect, useCallback, useMemo, memo } from 'react';
import PropTypes from 'prop-types';
import { usePerformanceMonitoring } from '../utils/performanceMonitor';
import { useBundleAnalyzer } from '../utils/bundleAnalyzer';

/**
 * Real-time performance monitoring component
 * Displays live performance metrics and recommendations
 */
const RealTimePerformanceMonitor = memo(({ 
  isOpen = false, 
  onClose,
  refreshInterval = 1000,
  showRecommendations = true,
  showCharts = true,
  className = ''
}) => {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [performanceData, setPerformanceData] = useState([]);
  const [alerts, setAlerts] = useState([]);
  
  // Performance monitoring hook
  const { 
    startMonitoring, 
    stopMonitoring, 
    getMetrics 
  } = usePerformanceMonitoring('RealTimePerformanceMonitor');
  
  // Bundle analyzer hook
  const { 
    metrics: bundleMetrics, 
    startMonitoring: startBundleMonitoring,
    stopMonitoring: stopBundleMonitoring,
    getRecommendations 
  } = useBundleAnalyzer();

  // Start monitoring when component opens
  useEffect(() => {
    if (isOpen && !isMonitoring) {
      startMonitoring();
      startBundleMonitoring();
      setIsMonitoring(true);
    } else if (!isOpen && isMonitoring) {
      stopMonitoring();
      stopBundleMonitoring();
      setIsMonitoring(false);
    }
  }, [isOpen, isMonitoring, startMonitoring, stopMonitoring, startBundleMonitoring, stopBundleMonitoring]);

  // Update performance data periodically
  useEffect(() => {
    if (!isMonitoring) return;

    const interval = setInterval(() => {
      const currentMetrics = getMetrics();
      const bundleData = bundleMetrics;
      
      // Combine performance and bundle metrics
      const combinedMetrics = {
        ...currentMetrics,
        bundle: bundleData,
        timestamp: Date.now()
      };
      
      setPerformanceData(prev => [
        ...prev.slice(-19), // Keep last 20 data points
        combinedMetrics
      ]);
      
      // Check for performance alerts
      checkPerformanceAlerts(combinedMetrics);
      
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [isMonitoring, getMetrics, bundleMetrics, refreshInterval]);

  // Check for performance alerts
  const checkPerformanceAlerts = useCallback((metrics) => {
    const newAlerts = [];
    
    // Bundle size alert
    if (metrics.bundle?.bundleSize > 500000) {
      newAlerts.push({
        type: 'warning',
        message: 'Bundle size is large (>500KB)',
        timestamp: Date.now(),
        metric: 'bundleSize',
        value: metrics.bundle.bundleSize
      });
    }
    
    // Memory usage alert
    if (metrics.memoryUsage > 100) {
      newAlerts.push({
        type: 'error',
        message: 'High memory usage detected',
        timestamp: Date.now(),
        metric: 'memoryUsage',
        value: metrics.memoryUsage
      });
    }
    
    // Render time alert
    if (metrics.renderTime > 16) {
      newAlerts.push({
        type: 'warning',
        message: 'Slow render time detected',
        timestamp: Date.now(),
        metric: 'renderTime',
        value: metrics.renderTime
      });
    }
    
    if (newAlerts.length > 0) {
      setAlerts(prev => [...prev, ...newAlerts].slice(-10)); // Keep last 10 alerts
    }
  }, []);

  // Calculate performance score
  const performanceScore = useMemo(() => {
    const metrics = getMetrics();
    const bundle = bundleMetrics;
    
    let score = 100;
    
    // Deduct points for poor performance
    if (metrics.renderTime > 16) score -= 20;
    if (metrics.memoryUsage > 100) score -= 20;
    if (bundle.bundleSize > 500000) score -= 20;
    if (bundle.cacheHitRate < 70) score -= 20;
    if (metrics.apiCalls > 50) score -= 20;
    
    return Math.max(0, score);
  }, [getMetrics, bundleMetrics]);

  // Get performance recommendations
  const recommendations = useMemo(() => {
    return getRecommendations();
  }, [getRecommendations]);

  if (!isOpen) return null;

  return (
    <div className={`real-time-performance-monitor ${className}`}>
      <div className="monitor-header">
        <h3>Real-time Performance Monitor</h3>
        <div className="performance-score">
          <span className="score-label">Performance Score:</span>
          <span className={`score-value ${performanceScore >= 80 ? 'good' : performanceScore >= 60 ? 'warning' : 'error'}`}>
            {performanceScore}/100
          </span>
        </div>
        {onClose && (
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        )}
      </div>

      <div className="monitor-content">
        {/* Current Metrics */}
        <div className="metrics-section">
          <h4>Current Metrics</h4>
          <div className="metrics-grid">
            <div className="metric-item">
              <label>Render Time:</label>
              <span>{getMetrics().renderTime.toFixed(2)}ms</span>
            </div>
            <div className="metric-item">
              <label>Memory Usage:</label>
              <span>{getMetrics().memoryUsage.toFixed(2)}MB</span>
            </div>
            <div className="metric-item">
              <label>API Calls:</label>
              <span>{getMetrics().apiCalls}</span>
            </div>
            <div className="metric-item">
              <label>Bundle Size:</label>
              <span>{Math.round(bundleMetrics.bundleSize / 1024)}KB</span>
            </div>
            <div className="metric-item">
              <label>Cache Hit Rate:</label>
              <span>{bundleMetrics.cacheHitRate.toFixed(1)}%</span>
            </div>
            <div className="metric-item">
              <label>Compression:</label>
              <span>{bundleMetrics.compressionRatio.toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* Performance Charts */}
        {showCharts && (
          <div className="charts-section">
            <h4>Performance Trends</h4>
            <div className="chart-container">
              <div className="chart">
                <h5>Render Time Over Time</h5>
                <div className="chart-data">
                  {performanceData.slice(-10).map((data, index) => (
                    <div 
                      key={index}
                      className="chart-bar"
                      style={{ 
                        height: `${Math.min(data.renderTime * 2, 100)}px`,
                        backgroundColor: data.renderTime > 16 ? '#ff6b6b' : '#51cf66'
                      }}
                    />
                  ))}
                </div>
              </div>
              <div className="chart">
                <h5>Memory Usage Over Time</h5>
                <div className="chart-data">
                  {performanceData.slice(-10).map((data, index) => (
                    <div 
                      key={index}
                      className="chart-bar"
                      style={{ 
                        height: `${Math.min(data.memoryUsage * 2, 100)}px`,
                        backgroundColor: data.memoryUsage > 100 ? '#ff6b6b' : '#51cf66'
                      }}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Recommendations */}
        {showRecommendations && recommendations.length > 0 && (
          <div className="recommendations-section">
            <h4>Recommendations</h4>
            <div className="recommendations-list">
              {recommendations.map((rec, index) => (
                <div key={index} className={`recommendation ${rec.type}`}>
                  <span className="recommendation-type">{rec.type.toUpperCase()}</span>
                  <span className="recommendation-message">{rec.message}</span>
                  <span className="recommendation-impact">Impact: {rec.impact}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Alerts */}
        {alerts.length > 0 && (
          <div className="alerts-section">
            <h4>Performance Alerts</h4>
            <div className="alerts-list">
              {alerts.slice(-5).map((alert, index) => (
                <div key={index} className={`alert ${alert.type}`}>
                  <span className="alert-time">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="alert-message">{alert.message}</span>
                  <span className="alert-value">{alert.value}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

RealTimePerformanceMonitor.propTypes = {
  isOpen: PropTypes.bool,
  onClose: PropTypes.func,
  refreshInterval: PropTypes.number,
  showRecommendations: PropTypes.bool,
  showCharts: PropTypes.bool,
  className: PropTypes.string
};

RealTimePerformanceMonitor.displayName = 'RealTimePerformanceMonitor';

export default RealTimePerformanceMonitor;
