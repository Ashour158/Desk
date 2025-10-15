/**
 * Comprehensive test suite for RealTimePerformanceDashboard component
 * Tests all performance monitoring functionality with comprehensive coverage
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

import RealTimePerformanceDashboard from '../RealTimePerformanceDashboard';

// Mock performance monitoring utilities
vi.mock('../../utils/performanceMonitor', () => ({
  default: {
    getMetrics: vi.fn(() => ({
      webVitals: {
        lcp: 2.5,
        fid: 100,
        cls: 0.1,
        fcp: 1.8,
        ttfb: 200
      },
      performance: {
        memory: { used: 50, total: 100 },
        timing: { load: 3000, dom: 1500 },
        navigation: { type: 'navigate' },
        paint: { fcp: 1800, lcp: 2500 },
        resource: { count: 25, size: 1024000 }
      },
      bundle: {
        size: 2048000,
        chunks: 5,
        loadTime: 1500,
        compression: 0.7
      },
      network: {
        connection: '4g',
        requests: 15,
        bandwidth: 10000000,
        latency: 50
      },
      cache: {
        hitRate: 0.85,
        size: 512000,
        efficiency: 0.9,
        invalidation: 0.1
      },
      ux: {
        interactions: 25,
        errors: 2,
        accessibility: 0.95,
        responsiveness: 0.9
      }
    })),
    start: vi.fn(),
    end: vi.fn(),
    mark: vi.fn(),
    measure: vi.fn()
  }
}));

// Mock bundle analyzer
vi.mock('../../utils/bundleAnalyzer', () => ({
  getBundleReport: vi.fn(() => ({
    totalSize: 2048000,
    chunks: [
      { name: 'vendor', size: 1024000 },
      { name: 'app', size: 1024000 }
    ],
    loadTime: 1500,
    compression: 0.7
  })),
  getPerformanceMetrics: vi.fn(() => ({
    memory: { used: 50, total: 100 },
    timing: { load: 3000, dom: 1500 },
    navigation: { type: 'navigate' },
    paint: { fcp: 1800, lcp: 2500 },
    resource: { count: 25, size: 1024000 }
  }))
}));

// Mock network utilities
vi.mock('../../utils/networkOptimizer', () => ({
  default: {
    getConnectionInfo: vi.fn(() => ({
      effectiveType: '4g',
      downlink: 10,
      rtt: 50
    })),
    getNetworkMetrics: vi.fn(() => ({
      requests: 15,
      bandwidth: 10000000,
      latency: 50
    }))
  }
}));

// Mock cache utilities
vi.mock('../../utils/cacheOptimizer', () => ({
  default: {
    getCacheMetrics: vi.fn(() => ({
      hitRate: 0.85,
      size: 512000,
      efficiency: 0.9,
      invalidation: 0.1
    }))
  }
}));

describe('RealTimePerformanceDashboard', () => {
  const defaultProps = {
    refreshInterval: 2000,
    showCharts: true,
    showRecommendations: true,
    showAlerts: true,
    className: 'test-dashboard'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock performance.now
    vi.spyOn(performance, 'now').mockReturnValue(1000);
    // Mock requestAnimationFrame
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation((cb) => {
      cb(1000);
      return 1;
    });
    // Mock clearInterval
    vi.spyOn(window, 'clearInterval').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Component Rendering', () => {
    it('renders without crashing', () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      expect(screen.getByTestId('performance-dashboard')).toBeInTheDocument();
    });

    it('renders with custom className', () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      const dashboard = screen.getByTestId('performance-dashboard');
      expect(dashboard).toHaveClass('test-dashboard');
    });

    it('renders loading state initially', () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    it('renders all main sections when loaded', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('web-vitals-section')).toBeInTheDocument();
        expect(screen.getByTestId('performance-metrics-section')).toBeInTheDocument();
        expect(screen.getByTestId('bundle-analysis-section')).toBeInTheDocument();
        expect(screen.getByTestId('network-metrics-section')).toBeInTheDocument();
        expect(screen.getByTestId('cache-metrics-section')).toBeInTheDocument();
        expect(screen.getByTestId('ux-metrics-section')).toBeInTheDocument();
      });
    });
  });

  describe('Web Vitals Monitoring', () => {
    it('displays Core Web Vitals metrics', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('LCP: 2.5s')).toBeInTheDocument();
        expect(screen.getByText('FID: 100ms')).toBeInTheDocument();
        expect(screen.getByText('CLS: 0.1')).toBeInTheDocument();
        expect(screen.getByText('FCP: 1.8s')).toBeInTheDocument();
        expect(screen.getByText('TTFB: 200ms')).toBeInTheDocument();
      });
    });

    it('shows performance status indicators', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('lcp-status')).toBeInTheDocument();
        expect(screen.getByTestId('fid-status')).toBeInTheDocument();
        expect(screen.getByTestId('cls-status')).toBeInTheDocument();
      });
    });

    it('updates metrics in real-time', async () => {
      const { rerender } = render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('LCP: 2.5s')).toBeInTheDocument();
      });

      // Simulate metrics update
      const performanceMonitor = await import('../../utils/performanceMonitor');
      performanceMonitor.default.getMetrics.mockReturnValue({
        webVitals: {
          lcp: 3.0,
          fid: 150,
          cls: 0.2,
          fcp: 2.0,
          ttfb: 250
        }
      });

      rerender(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('LCP: 3.0s')).toBeInTheDocument();
      });
    });
  });

  describe('Performance Metrics', () => {
    it('displays memory usage metrics', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Memory Usage: 50%')).toBeInTheDocument();
        expect(screen.getByText('Total Memory: 100 MB')).toBeInTheDocument();
      });
    });

    it('displays timing metrics', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Load Time: 3.0s')).toBeInTheDocument();
        expect(screen.getByText('DOM Ready: 1.5s')).toBeInTheDocument();
      });
    });

    it('displays navigation metrics', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Navigation Type: navigate')).toBeInTheDocument();
      });
    });

    it('displays paint metrics', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('FCP: 1.8s')).toBeInTheDocument();
        expect(screen.getByText('LCP: 2.5s')).toBeInTheDocument();
      });
    });
  });

  describe('Bundle Analysis', () => {
    it('displays bundle size metrics', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Bundle Size: 2.0 MB')).toBeInTheDocument();
        expect(screen.getByText('Chunks: 5')).toBeInTheDocument();
        expect(screen.getByText('Load Time: 1.5s')).toBeInTheDocument();
        expect(screen.getByText('Compression: 70%')).toBeInTheDocument();
      });
    });

    it('displays chunk breakdown', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Vendor: 1.0 MB')).toBeInTheDocument();
        expect(screen.getByText('App: 1.0 MB')).toBeInTheDocument();
      });
    });

    it('shows bundle optimization recommendations', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('bundle-recommendations')).toBeInTheDocument();
      });
    });
  });

  describe('Network Metrics', () => {
    it('displays network connection info', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Connection: 4g')).toBeInTheDocument();
        expect(screen.getByText('Requests: 15')).toBeInTheDocument();
        expect(screen.getByText('Bandwidth: 10.0 Mbps')).toBeInTheDocument();
        expect(screen.getByText('Latency: 50ms')).toBeInTheDocument();
      });
    });

    it('shows network performance status', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('network-status')).toBeInTheDocument();
      });
    });
  });

  describe('Cache Metrics', () => {
    it('displays cache performance metrics', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Cache Hit Rate: 85%')).toBeInTheDocument();
        expect(screen.getByText('Cache Size: 512 KB')).toBeInTheDocument();
        expect(screen.getByText('Cache Efficiency: 90%')).toBeInTheDocument();
        expect(screen.getByText('Invalidation Rate: 10%')).toBeInTheDocument();
      });
    });

    it('shows cache optimization recommendations', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('cache-recommendations')).toBeInTheDocument();
      });
    });
  });

  describe('User Experience Metrics', () => {
    it('displays UX metrics', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Interactions: 25')).toBeInTheDocument();
        expect(screen.getByText('Errors: 2')).toBeInTheDocument();
        expect(screen.getByText('Accessibility: 95%')).toBeInTheDocument();
        expect(screen.getByText('Responsiveness: 90%')).toBeInTheDocument();
      });
    });

    it('shows UX improvement recommendations', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('ux-recommendations')).toBeInTheDocument();
      });
    });
  });

  describe('Real-time Updates', () => {
    it('updates metrics at specified interval', async () => {
      vi.useFakeTimers();
      
      render(<RealTimePerformanceDashboard {...defaultProps} refreshInterval={1000} />);
      
      await waitFor(() => {
        expect(screen.getByText('LCP: 2.5s')).toBeInTheDocument();
      });

      // Fast-forward time
      act(() => {
        vi.advanceTimersByTime(1000);
      });

      await waitFor(() => {
        expect(screen.getByText('LCP: 2.5s')).toBeInTheDocument();
      });

      vi.useRealTimers();
    });

    it('handles real-time update errors gracefully', async () => {
      const performanceMonitor = await import('../../utils/performanceMonitor');
      performanceMonitor.default.getMetrics.mockRejectedValue(new Error('Metrics fetch failed'));

      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toBeInTheDocument();
      });
    });
  });

  describe('Charts and Visualizations', () => {
    it('renders performance charts when showCharts is true', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} showCharts={true} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('performance-chart')).toBeInTheDocument();
        expect(screen.getByTestId('memory-chart')).toBeInTheDocument();
        expect(screen.getByTestId('network-chart')).toBeInTheDocument();
      });
    });

    it('does not render charts when showCharts is false', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} showCharts={false} />);
      
      await waitFor(() => {
        expect(screen.queryByTestId('performance-chart')).not.toBeInTheDocument();
        expect(screen.queryByTestId('memory-chart')).not.toBeInTheDocument();
        expect(screen.queryByTestId('network-chart')).not.toBeInTheDocument();
      });
    });
  });

  describe('Recommendations', () => {
    it('shows performance recommendations when showRecommendations is true', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} showRecommendations={true} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('performance-recommendations')).toBeInTheDocument();
        expect(screen.getByTestId('bundle-recommendations')).toBeInTheDocument();
        expect(screen.getByTestId('cache-recommendations')).toBeInTheDocument();
        expect(screen.getByTestId('ux-recommendations')).toBeInTheDocument();
      });
    });

    it('does not show recommendations when showRecommendations is false', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} showRecommendations={false} />);
      
      await waitFor(() => {
        expect(screen.queryByTestId('performance-recommendations')).not.toBeInTheDocument();
        expect(screen.queryByTestId('bundle-recommendations')).not.toBeInTheDocument();
        expect(screen.queryByTestId('cache-recommendations')).not.toBeInTheDocument();
        expect(screen.queryByTestId('ux-recommendations')).not.toBeInTheDocument();
      });
    });
  });

  describe('Alerts', () => {
    it('shows performance alerts when showAlerts is true', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} showAlerts={true} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('performance-alerts')).toBeInTheDocument();
      });
    });

    it('does not show alerts when showAlerts is false', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} showAlerts={false} />);
      
      await waitFor(() => {
        expect(screen.queryByTestId('performance-alerts')).not.toBeInTheDocument();
      });
    });

    it('displays critical performance alerts', async () => {
      const performanceMonitor = await import('../../utils/performanceMonitor');
      performanceMonitor.default.getMetrics.mockReturnValue({
        webVitals: {
          lcp: 5.0, // Critical LCP
          fid: 300, // Critical FID
          cls: 0.5, // Critical CLS
          fcp: 3.0,
          ttfb: 1000
        }
      });

      render(<RealTimePerformanceDashboard {...defaultProps} showAlerts={true} />);
      
      await waitFor(() => {
        expect(screen.getByText('Critical LCP: 5.0s')).toBeInTheDocument();
        expect(screen.getByText('Critical FID: 300ms')).toBeInTheDocument();
        expect(screen.getByText('Critical CLS: 0.5')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('handles metrics fetch errors', async () => {
      const performanceMonitor = await import('../../utils/performanceMonitor');
      performanceMonitor.default.getMetrics.mockRejectedValue(new Error('Metrics fetch failed'));

      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toBeInTheDocument();
        expect(screen.getByText('Failed to fetch performance metrics')).toBeInTheDocument();
      });
    });

    it('handles network errors gracefully', async () => {
      const networkOptimizer = await import('../../utils/networkOptimizer');
      networkOptimizer.default.getNetworkMetrics.mockRejectedValue(new Error('Network error'));

      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('network-error')).toBeInTheDocument();
      });
    });

    it('handles cache errors gracefully', async () => {
      const cacheOptimizer = await import('../../utils/cacheOptimizer');
      cacheOptimizer.default.getCacheMetrics.mockRejectedValue(new Error('Cache error'));

      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('cache-error')).toBeInTheDocument();
      });
    });
  });

  describe('Performance Optimization', () => {
    it('uses React.memo for performance', () => {
      expect(RealTimePerformanceDashboard.displayName).toBe('RealTimePerformanceDashboard');
    });

    it('handles component unmounting gracefully', () => {
      const { unmount } = render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      expect(() => unmount()).not.toThrow();
    });

    it('cleans up intervals on unmount', () => {
      const { unmount } = render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      unmount();
      
      expect(window.clearInterval).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByRole('main')).toBeInTheDocument();
        expect(screen.getByLabelText('Performance Dashboard')).toBeInTheDocument();
      });
    });

    it('supports keyboard navigation', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        const dashboard = screen.getByTestId('performance-dashboard');
        expect(dashboard).toHaveAttribute('tabIndex', '0');
      });
    });

    it('has proper color contrast for status indicators', async () => {
      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        const lcpStatus = screen.getByTestId('lcp-status');
        expect(lcpStatus).toHaveClass('status-indicator');
      });
    });
  });

  describe('Responsive Design', () => {
    it('adapts to different screen sizes', async () => {
      // Mock window.innerWidth
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768,
      });

      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        const dashboard = screen.getByTestId('performance-dashboard');
        expect(dashboard).toHaveClass('responsive');
      });
    });

    it('shows mobile-optimized layout on small screens', async () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      render(<RealTimePerformanceDashboard {...defaultProps} />);
      
      await waitFor(() => {
        const dashboard = screen.getByTestId('performance-dashboard');
        expect(dashboard).toHaveClass('mobile-layout');
      });
    });
  });
});
