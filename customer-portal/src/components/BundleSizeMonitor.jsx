import React, { useState, useEffect, useMemo, useCallback, memo } from 'react';
import PropTypes from 'prop-types';
import { useBundleAnalyzer } from '../utils/bundleAnalyzer';

/**
 * Bundle Size Monitor Component
 * Displays real-time bundle size metrics and recommendations
 */
const BundleSizeMonitor = memo(({ 
  isOpen = false,
  onClose,
  refreshInterval = 30000,
  showCharts = true,
  showRecommendations = true,
  className = ''
}) => {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [bundleData, setBundleData] = useState([]);
  const [alerts, setAlerts] = useState([]);
  
  const { 
    metrics, 
    startMonitoring, 
    stopMonitoring, 
    getRecommendations 
  } = useBundleAnalyzer();

  // Start monitoring when component opens
  useEffect(() => {
    if (isOpen && !isMonitoring) {
      startMonitoring();
      setIsMonitoring(true);
    } else if (!isOpen && isMonitoring) {
      stopMonitoring();
      setIsMonitoring(false);
    }
  }, [isOpen, isMonitoring, startMonitoring, stopMonitoring]);

  // Update bundle data periodically
  useEffect(() => {
    if (!isMonitoring) return;

    const interval = setInterval(() => {
      const currentMetrics = metrics;
      
      setBundleData(prev => [
        ...prev.slice(-19), // Keep last 20 data points
        {
          ...currentMetrics,
          timestamp: Date.now()
        }
      ]);
      
      // Check for bundle size alerts
      checkBundleAlerts(currentMetrics);
      
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [isMonitoring, metrics, refreshInterval]);

  // Check for bundle size alerts
  const checkBundleAlerts = useCallback((metrics) => {
    const newAlerts = [];
    
    // Bundle size alert
    if (metrics.bundleSize > 500000) { // 500KB
      newAlerts.push({
        type: 'warning',
        message: 'Bundle size exceeds 500KB',
        timestamp: Date.now(),
        metric: 'bundleSize',
        value: metrics.bundleSize
      });
    }
    
    // Compression ratio alert
    if (metrics.compressionRatio < 60) {
      newAlerts.push({
        type: 'info',
        message: 'Low compression ratio detected',
        timestamp: Date.now(),
        metric: 'compressionRatio',
        value: metrics.compressionRatio
      });
    }
    
    // Cache hit rate alert
    if (metrics.cacheHitRate < 70) {
      newAlerts.push({
        type: 'warning',
        message: 'Low cache hit rate detected',
        timestamp: Date.now(),
        metric: 'cacheHitRate',
        value: metrics.cacheHitRate
      });
    }
    
    if (newAlerts.length > 0) {
      setAlerts(prev => [...prev, ...newAlerts].slice(-10)); // Keep last 10 alerts
    }
  }, []);

  // Calculate bundle health score
  const bundleHealthScore = useMemo(() => {
    let score = 100;
    
    // Deduct points for poor metrics
    if (metrics.bundleSize > 500000) score -= 30;
    if (metrics.compressionRatio < 60) score -= 20;
    if (metrics.cacheHitRate < 70) score -= 20;
    if (metrics.pendingRequests > 5) score -= 15;
    if (metrics.cachedRequests < 10) score -= 15;
    
    return Math.max(0, score);
  }, [metrics]);

  // Get recommendations
  const recommendations = useMemo(() => {
    return getRecommendations();
  }, [getRecommendations]);

  // Format file size
  const formatFileSize = useCallback((bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }, []);

  if (!isOpen) return null;

  return (
    <div className={`bundle-size-monitor ${className}`}>
      <div className="monitor-header">
        <h3>Bundle Size Monitor</h3>
        <div className="health-score">
          <span className="score-label">Bundle Health:</span>
          <span className={`score-value ${bundleHealthScore >= 80 ? 'good' : bundleHealthScore >= 60 ? 'warning' : 'error'}`}>
            {bundleHealthScore}/100
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
              <label>Total Bundle Size:</label>
              <span>{formatFileSize(metrics.bundleSize)}</span>
            </div>
            <div className="metric-item">
              <label>Compression Ratio:</label>
              <span>{metrics.compressionRatio.toFixed(1)}%</span>
            </div>
            <div className="metric-item">
              <label>Cache Hit Rate:</label>
              <span>{metrics.cacheHitRate.toFixed(1)}%</span>
            </div>
            <div className="metric-item">
              <label>Pending Requests:</label>
              <span>{metrics.pendingRequests}</span>
            </div>
            <div className="metric-item">
              <label>Cached Requests:</label>
              <span>{metrics.cachedRequests}</span>
            </div>
            <div className="metric-item">
              <label>Cache Timeout:</label>
              <span>{metrics.cacheTimeout}ms</span>
            </div>
          </div>
        </div>

        {/* Chunk Sizes */}
        {Object.keys(metrics.chunkSizes || {}).length > 0 && (
          <div className="chunks-section">
            <h4>Chunk Sizes</h4>
            <div className="chunks-list">
              {Object.entries(metrics.chunkSizes).map(([chunkName, size]) => (
                <div key={chunkName} className="chunk-item">
                  <span className="chunk-name">{chunkName}</span>
                  <span className="chunk-size">{formatFileSize(size)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Performance Charts */}
        {showCharts && bundleData.length > 0 && (
          <div className="charts-section">
            <h4>Bundle Size Trends</h4>
            <div className="chart-container">
              <div className="chart">
                <h5>Bundle Size Over Time</h5>
                <div className="chart-data">
                  {bundleData.slice(-10).map((data, index) => (
                    <div 
                      key={index}
                      className="chart-bar"
                      style={{ 
                        height: `${Math.min((data.bundleSize / 1000000) * 100, 100)}px`,
                        backgroundColor: data.bundleSize > 500000 ? '#ff6b6b' : '#51cf66'
                      }}
                    />
                  ))}
                </div>
              </div>
              <div className="chart">
                <h5>Compression Ratio Over Time</h5>
                <div className="chart-data">
                  {bundleData.slice(-10).map((data, index) => (
                    <div 
                      key={index}
                      className="chart-bar"
                      style={{ 
                        height: `${Math.min(data.compressionRatio, 100)}px`,
                        backgroundColor: data.compressionRatio < 60 ? '#ff6b6b' : '#51cf66'
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
            <h4>Optimization Recommendations</h4>
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
            <h4>Bundle Alerts</h4>
            <div className="alerts-list">
              {alerts.slice(-5).map((alert, index) => (
                <div key={index} className={`alert ${alert.type}`}>
                  <span className="alert-time">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="alert-message">{alert.message}</span>
                  <span className="alert-value">{formatFileSize(alert.value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="actions-section">
          <button 
            className="action-button"
            onClick={() => {
              // Clear cache
              if (window.caches) {
                caches.keys().then(names => {
                  names.forEach(name => caches.delete(name));
                });
              }
            }}
          >
            Clear Cache
          </button>
          <button 
            className="action-button"
            onClick={() => {
              // Refresh bundle analysis
              window.location.reload();
            }}
          >
            Refresh Analysis
          </button>
        </div>
      </div>
    </div>
  );
});

BundleSizeMonitor.propTypes = {
  isOpen: PropTypes.bool,
  onClose: PropTypes.func,
  refreshInterval: PropTypes.number,
  showCharts: PropTypes.bool,
  showRecommendations: PropTypes.bool,
  className: PropTypes.string
};

BundleSizeMonitor.displayName = 'BundleSizeMonitor';

export default BundleSizeMonitor;
