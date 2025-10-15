import React, { useState, useEffect, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';
import { memo } from 'react';

/**
 * Performance Monitoring Dashboard Component
 * Provides real-time performance metrics and optimization recommendations
 */
const PerformanceDashboard = memo(({ 
  className = '',
  refreshInterval = 5000,
  showRecommendations = true,
  showMetrics = true,
  showCharts = true,
  ...props 
}) => {
  const [metrics, setMetrics] = useState({
    bundle: null,
    performance: null,
    cache: null,
    network: null
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  // Fetch performance metrics
  const fetchMetrics = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Fetch bundle analysis
      const bundleReport = await import('../utils/bundleAnalyzer').then(module => 
        module.getBundleReport()
      );

      // Fetch performance metrics
      const performanceMetrics = await import('../utils/bundleAnalyzer').then(module => 
        module.getPerformanceMetrics()
      );

      // Fetch cache metrics (if available)
      const cacheMetrics = await fetchCacheMetrics();

      // Fetch network metrics
      const networkMetrics = await fetchNetworkMetrics();

      setMetrics({
        bundle: bundleReport,
        performance: performanceMetrics,
        cache: cacheMetrics,
        network: networkMetrics
      });

      // Generate recommendations
      if (showRecommendations) {
        const recs = generateRecommendations(bundleReport, performanceMetrics, cacheMetrics);
        setRecommendations(recs);
      }

    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch performance metrics:', err);
    } finally {
      setIsLoading(false);
    }
  }, [showRecommendations]);

  // Fetch cache metrics
  const fetchCacheMetrics = async () => {
    try {
      const response = await fetch('/api/v1/performance/cache-metrics/');
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.warn('Failed to fetch cache metrics:', error);
    }
    return null;
  };

  // Fetch network metrics
  const fetchNetworkMetrics = async () => {
    try {
      const response = await fetch('/api/v1/performance/network-metrics/');
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.warn('Failed to fetch network metrics:', error);
    }
    return null;
  };

  // Generate recommendations
  const generateRecommendations = (bundle, performance, cache) => {
    const recs = [];

    // Bundle size recommendations
    if (bundle?.bundleData?.totalSize > 1000000) { // 1MB
      recs.push({
        type: 'error',
        title: 'Large Bundle Size',
        message: `Bundle size is ${(bundle.bundleData.totalSize / 1024 / 1024).toFixed(2)}MB`,
        suggestion: 'Consider implementing code splitting and tree shaking',
        priority: 'high'
      });
    }

    // Performance recommendations
    if (performance?.navigation?.totalTime > 3000) { // 3s
      recs.push({
        type: 'warning',
        title: 'Slow Page Load',
        message: `Page load time is ${(performance.navigation.totalTime / 1000).toFixed(2)}s`,
        suggestion: 'Optimize critical rendering path and reduce bundle size',
        priority: 'medium'
      });
    }

    // Cache recommendations
    if (cache?.hitRate < 0.8) { // 80%
      recs.push({
        type: 'info',
        title: 'Low Cache Hit Rate',
        message: `Cache hit rate is ${(cache.hitRate * 100).toFixed(1)}%`,
        suggestion: 'Review cache configuration and TTL settings',
        priority: 'low'
      });
    }

    // Resource recommendations
    if (performance?.resources > 50) {
      recs.push({
        type: 'warning',
        title: 'Too Many Resources',
        message: `${performance.resources} resources loaded`,
        suggestion: 'Consider combining resources and using sprites',
        priority: 'medium'
      });
    }

    return recs;
  };

  // Set up auto-refresh
  useEffect(() => {
    fetchMetrics();
    
    const interval = setInterval(fetchMetrics, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchMetrics, refreshInterval]);

  // Export metrics
  const exportMetrics = useCallback(() => {
    const data = {
      timestamp: new Date().toISOString(),
      metrics,
      recommendations
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `performance-metrics-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }, [metrics, recommendations]);

  if (isLoading) {
    return (
      <div className={`performance-dashboard-loading ${className}`} {...props}>
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>Loading performance metrics...</div>
          <div style={{ width: '40px', height: '40px', border: '4px solid #f3f4f6', borderTop: '4px solid #007bff', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto' }}></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`performance-dashboard-error ${className}`} {...props}>
        <div style={{ textAlign: 'center', padding: '2rem', color: '#dc3545' }}>
          <h3>Failed to load performance metrics</h3>
          <p>{error}</p>
          <button onClick={fetchMetrics} style={{ marginTop: '1rem', padding: '0.5rem 1rem', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`performance-dashboard ${className}`} {...props}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: '600' }}>Performance Dashboard</h2>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button onClick={fetchMetrics} style={{ padding: '0.5rem 1rem', background: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Refresh
          </button>
          <button onClick={exportMetrics} style={{ padding: '0.5rem 1rem', background: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Export
          </button>
        </div>
      </div>

      {showMetrics && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          {/* Bundle Metrics */}
          {metrics.bundle && (
            <MetricCard
              title="Bundle Analysis"
              metrics={[
                { label: 'Total Size', value: `${(metrics.bundle.bundleData.totalSize / 1024).toFixed(2)} KB` },
                { label: 'Resources', value: metrics.bundle.resourceAnalysis.totalResources },
                { label: 'Average Size', value: `${(metrics.bundle.resourceAnalysis.averageSize / 1024).toFixed(2)} KB` }
              ]}
              status={metrics.bundle.bundleData.totalSize > 1000000 ? 'warning' : 'good'}
            />
          )}

          {/* Performance Metrics */}
          {metrics.performance && (
            <MetricCard
              title="Performance"
              metrics={[
                { label: 'Load Time', value: `${(metrics.performance.navigation.totalTime / 1000).toFixed(2)}s` },
                { label: 'Resources', value: metrics.performance.resources },
                { label: 'Total Size', value: `${(metrics.performance.totalSize / 1024).toFixed(2)} KB` }
              ]}
              status={metrics.performance.navigation.totalTime > 3000 ? 'warning' : 'good'}
            />
          )}

          {/* Cache Metrics */}
          {metrics.cache && (
            <MetricCard
              title="Cache Performance"
              metrics={[
                { label: 'Hit Rate', value: `${(metrics.cache.hitRate * 100).toFixed(1)}%` },
                { label: 'Miss Rate', value: `${(metrics.cache.missRate * 100).toFixed(1)}%` },
                { label: 'Total Keys', value: metrics.cache.totalKeys }
              ]}
              status={metrics.cache.hitRate < 0.8 ? 'warning' : 'good'}
            />
          )}

          {/* Network Metrics */}
          {metrics.network && (
            <MetricCard
              title="Network"
              metrics={[
                { label: 'Requests', value: metrics.network.requests },
                { label: 'Avg Response', value: `${metrics.network.avgResponseTime}ms` },
                { label: 'Errors', value: metrics.network.errors }
              ]}
              status={metrics.network.errors > 0 ? 'error' : 'good'}
            />
          )}
        </div>
      )}

      {/* Recommendations */}
      {showRecommendations && recommendations.length > 0 && (
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ marginBottom: '1rem', fontSize: '1.2rem', fontWeight: '600' }}>Optimization Recommendations</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {recommendations.map((rec, index) => (
              <RecommendationCard key={index} recommendation={rec} />
            ))}
          </div>
        </div>
      )}

      {/* Charts */}
      {showCharts && (
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ marginBottom: '1rem', fontSize: '1.2rem', fontWeight: '600' }}>Performance Trends</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1rem' }}>
            <PerformanceChart title="Bundle Size Over Time" data={metrics.bundle?.resourceAnalysis} />
            <PerformanceChart title="Cache Hit Rate" data={metrics.cache} />
          </div>
        </div>
      )}
    </div>
  );
});

PerformanceDashboard.displayName = 'PerformanceDashboard';

PerformanceDashboard.propTypes = {
  className: PropTypes.string,
  refreshInterval: PropTypes.number,
  showRecommendations: PropTypes.bool,
  showMetrics: PropTypes.bool,
  showCharts: PropTypes.bool
};

/**
 * Metric Card Component
 */
const MetricCard = memo(({ title, metrics, status }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'good': return '#28a745';
      case 'warning': return '#ffc107';
      case 'error': return '#dc3545';
      default: return '#6c757d';
    }
  };

  return (
    <div style={{
      background: 'white',
      border: '1px solid #e9ecef',
      borderRadius: '8px',
      padding: '1rem',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: '600' }}>{title}</h4>
        <div style={{
          width: '12px',
          height: '12px',
          borderRadius: '50%',
          backgroundColor: getStatusColor(status)
        }} />
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {metrics.map((metric, index) => (
          <div key={index} style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#6c757d', fontSize: '0.875rem' }}>{metric.label}:</span>
            <span style={{ fontWeight: '500' }}>{metric.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
});

MetricCard.displayName = 'MetricCard';

MetricCard.propTypes = {
  title: PropTypes.string.isRequired,
  metrics: PropTypes.arrayOf(PropTypes.shape({
    label: PropTypes.string.isRequired,
    value: PropTypes.string.isRequired
  })).isRequired,
  status: PropTypes.oneOf(['good', 'warning', 'error']).isRequired
};

/**
 * Recommendation Card Component
 */
const RecommendationCard = memo(({ recommendation }) => {
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#dc3545';
      case 'medium': return '#ffc107';
      case 'low': return '#17a2b8';
      default: return '#6c757d';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'error': return '🚨';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      default: return '📝';
    }
  };

  return (
    <div style={{
      background: 'white',
      border: '1px solid #e9ecef',
      borderRadius: '8px',
      padding: '1rem',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      borderLeft: `4px solid ${getPriorityColor(recommendation.priority)}`
    }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
        <span style={{ marginRight: '0.5rem', fontSize: '1.2rem' }}>
          {getTypeIcon(recommendation.type)}
        </span>
        <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: '600' }}>{recommendation.title}</h4>
        <span style={{
          marginLeft: 'auto',
          padding: '0.25rem 0.5rem',
          background: getPriorityColor(recommendation.priority),
          color: 'white',
          borderRadius: '4px',
          fontSize: '0.75rem',
          fontWeight: '500'
        }}>
          {recommendation.priority.toUpperCase()}
        </span>
      </div>
      <p style={{ margin: '0 0 0.5rem 0', color: '#6c757d', fontSize: '0.875rem' }}>
        {recommendation.message}
      </p>
      <p style={{ margin: 0, fontSize: '0.875rem', fontWeight: '500' }}>
        💡 {recommendation.suggestion}
      </p>
    </div>
  );
});

RecommendationCard.displayName = 'RecommendationCard';

RecommendationCard.propTypes = {
  recommendation: PropTypes.shape({
    type: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    message: PropTypes.string.isRequired,
    suggestion: PropTypes.string.isRequired,
    priority: PropTypes.string.isRequired
  }).isRequired
};

/**
 * Performance Chart Component
 */
const PerformanceChart = memo(({ title, data }) => {
  if (!data) {
    return (
      <div style={{
        background: 'white',
        border: '1px solid #e9ecef',
        borderRadius: '8px',
        padding: '1rem',
        textAlign: 'center',
        color: '#6c757d'
      }}>
        <h4 style={{ margin: '0 0 1rem 0', fontSize: '1rem', fontWeight: '600' }}>{title}</h4>
        <p style={{ margin: 0 }}>No data available</p>
      </div>
    );
  }

  return (
    <div style={{
      background: 'white',
      border: '1px solid #e9ecef',
      borderRadius: '8px',
      padding: '1rem',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <h4 style={{ margin: '0 0 1rem 0', fontSize: '1rem', fontWeight: '600' }}>{title}</h4>
      <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6c757d' }}>
        <p>Chart visualization would go here</p>
      </div>
    </div>
  );
});

PerformanceChart.displayName = 'PerformanceChart';

PerformanceChart.propTypes = {
  title: PropTypes.string.isRequired,
  data: PropTypes.object
};

export default PerformanceDashboard;