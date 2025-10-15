/**
 * Comprehensive Performance Dashboard Tests
 * Tests critical performance monitoring and memory optimization functionality.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PerformanceDashboard from '../../components/PerformanceDashboard';

// Mock performance API
const mockPerformance = {
  now: jest.fn(() => Date.now()),
  getEntriesByType: jest.fn(() => []),
  getEntriesByName: jest.fn(() => []),
  mark: jest.fn(),
  measure: jest.fn(),
  clearMarks: jest.fn(),
  clearMeasures: jest.fn()
};

// Mock memory API
const mockMemory = {
  usedJSHeapSize: 1000000,
  totalJSHeapSize: 2000000,
  jsHeapSizeLimit: 4000000
};

// Mock navigator API
const mockNavigator = {
  connection: {
    effectiveType: '4g',
    downlink: 10,
    rtt: 50
  }
};

// Mock ResizeObserver
const mockResizeObserver = jest.fn(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn()
}));

// Setup mocks
beforeAll(() => {
  global.performance = mockPerformance;
  global.memory = mockMemory;
  global.navigator = mockNavigator;
  global.ResizeObserver = mockResizeObserver;
});

beforeEach(() => {
  jest.clearAllMocks();
});

describe('Performance Dashboard', () => {
  describe('Rendering and Basic Functionality', () => {
    it('should render performance dashboard without crashing', () => {
      render(<PerformanceDashboard />);
      
      expect(screen.getByTestId('performance-dashboard')).toBeInTheDocument();
    });

    it('should display performance metrics', () => {
      render(<PerformanceDashboard />);
      
      expect(screen.getByText('Performance Metrics')).toBeInTheDocument();
      expect(screen.getByText('Memory Usage')).toBeInTheDocument();
      expect(screen.getByText('Network Performance')).toBeInTheDocument();
    });

    it('should display real-time performance data', async () => {
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('memory-usage')).toBeInTheDocument();
        expect(screen.getByTestId('cpu-usage')).toBeInTheDocument();
        expect(screen.getByTestId('network-performance')).toBeInTheDocument();
      });
    });
  });

  describe('Memory Monitoring', () => {
    it('should display memory usage correctly', async () => {
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        const memoryUsage = screen.getByTestId('memory-usage');
        expect(memoryUsage).toBeInTheDocument();
        expect(memoryUsage).toHaveTextContent('50%'); // 1MB / 2MB * 100
      });
    });

    it('should detect memory leaks', async () => {
      // Simulate memory leak by increasing used memory
      mockMemory.usedJSHeapSize = 3500000; // 3.5MB (close to limit)
      
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('memory-leak-warning')).toBeInTheDocument();
        expect(screen.getByText('Memory usage is high')).toBeInTheDocument();
      });
    });

    it('should trigger garbage collection when memory is high', async () => {
      mockMemory.usedJSHeapSize = 3500000;
      
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('gc-trigger')).toBeInTheDocument();
      });
    });

    it('should display memory optimization recommendations', async () => {
      mockMemory.usedJSHeapSize = 3000000;
      
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('memory-optimization-tips')).toBeInTheDocument();
        expect(screen.getByText('Consider reducing image sizes')).toBeInTheDocument();
      });
    });
  });

  describe('CPU Monitoring', () => {
    it('should display CPU usage correctly', async () => {
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        const cpuUsage = screen.getByTestId('cpu-usage');
        expect(cpuUsage).toBeInTheDocument();
      });
    });

    it('should detect high CPU usage', async () => {
      // Mock high CPU usage
      mockPerformance.now.mockReturnValueOnce(1000).mockReturnValueOnce(2000);
      
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('cpu-warning')).toBeInTheDocument();
        expect(screen.getByText('CPU usage is high')).toBeInTheDocument();
      });
    });

    it('should suggest performance optimizations for high CPU usage', async () => {
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('cpu-optimization-tips')).toBeInTheDocument();
        expect(screen.getByText('Consider using Web Workers')).toBeInTheDocument();
      });
    });
  });

  describe('Network Performance Monitoring', () => {
    it('should display network performance metrics', async () => {
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        const networkPerf = screen.getByTestId('network-performance');
        expect(networkPerf).toBeInTheDocument();
        expect(networkPerf).toHaveTextContent('4g');
        expect(networkPerf).toHaveTextContent('10 Mbps');
      });
    });

    it('should detect slow network connections', async () => {
      // Mock slow connection
      mockNavigator.connection.effectiveType = '2g';
      mockNavigator.connection.downlink = 1;
      
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('network-warning')).toBeInTheDocument();
        expect(screen.getByText('Slow network connection detected')).toBeInTheDocument();
      });
    });

    it('should suggest network optimizations for slow connections', async () => {
      mockNavigator.connection.effectiveType = '2g';
      
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('network-optimization-tips')).toBeInTheDocument();
        expect(screen.getByText('Consider enabling data compression')).toBeInTheDocument();
      });
    });
  });

  describe('Performance Metrics Collection', () => {
    it('should collect performance metrics automatically', async () => {
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(mockPerformance.getEntriesByType).toHaveBeenCalledWith('navigation');
        expect(mockPerformance.getEntriesByType).toHaveBeenCalledWith('resource');
      });
    });

    it('should track page load performance', async () => {
      mockPerformance.getEntriesByType.mockReturnValue([
        {
          name: 'navigation',
          loadEventEnd: 1000,
          loadEventStart: 500,
          domContentLoadedEventEnd: 800,
          domContentLoadedEventStart: 600
        }
      ]);
      
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('page-load-time')).toBeInTheDocument();
        expect(screen.getByText('500ms')).toBeInTheDocument();
      });
    });

    it('should track resource loading performance', async () => {
      mockPerformance.getEntriesByType.mockReturnValue([
        {
          name: 'https://example.com/image.jpg',
          duration: 200,
          transferSize: 50000,
          decodedBodySize: 48000
        }
      ]);
      
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('resource-load-times')).toBeInTheDocument();
        expect(screen.getByText('200ms')).toBeInTheDocument();
      });
    });
  });

  describe('Performance Alerts and Warnings', () => {
    it('should display performance alerts', async () => {
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('performance-alerts')).toBeInTheDocument();
      });
    });

    it('should show critical performance warnings', async () => {
      // Mock critical performance issues
      mockMemory.usedJSHeapSize = 3800000; // Very high memory usage
      mockNavigator.connection.effectiveType = '2g';
      
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('critical-performance-warning')).toBeInTheDocument();
        expect(screen.getByText('Critical performance issues detected')).toBeInTheDocument();
      });
    });

    it('should provide performance improvement suggestions', async () => {
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('performance-suggestions')).toBeInTheDocument();
        expect(screen.getByText('Enable code splitting')).toBeInTheDocument();
        expect(screen.getByText('Optimize images')).toBeInTheDocument();
      });
    });
  });

  describe('Performance History and Trends', () => {
    it('should display performance history chart', async () => {
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('performance-history-chart')).toBeInTheDocument();
      });
    });

    it('should show performance trends over time', async () => {
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('performance-trends')).toBeInTheDocument();
        expect(screen.getByText('Performance Trends')).toBeInTheDocument();
      });
    });

    it('should allow filtering performance data by time range', async () => {
      render(<PerformanceDashboard />);
      
      const timeRangeFilter = screen.getByTestId('time-range-filter');
      fireEvent.change(timeRangeFilter, { target: { value: '1h' } });
      
      await waitFor(() => {
        expect(screen.getByText('Last 1 hour')).toBeInTheDocument();
      });
    });
  });

  describe('Performance Optimization Features', () => {
    it('should provide memory optimization tools', async () => {
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('memory-optimization-tools')).toBeInTheDocument();
        expect(screen.getByText('Clear Cache')).toBeInTheDocument();
        expect(screen.getByText('Force Garbage Collection')).toBeInTheDocument();
      });
    });

    it('should allow manual garbage collection', async () => {
      render(<PerformanceDashboard />);
      
      const gcButton = screen.getByText('Force Garbage Collection');
      fireEvent.click(gcButton);
      
      await waitFor(() => {
        expect(screen.getByText('Garbage collection triggered')).toBeInTheDocument();
      });
    });

    it('should provide cache management tools', async () => {
      render(<PerformanceDashboard />);
      
      const clearCacheButton = screen.getByText('Clear Cache');
      fireEvent.click(clearCacheButton);
      
      await waitFor(() => {
        expect(screen.getByText('Cache cleared successfully')).toBeInTheDocument();
      });
    });
  });

  describe('Performance Monitoring Controls', () => {
    it('should allow starting and stopping performance monitoring', async () => {
      render(<PerformanceDashboard />);
      
      const startButton = screen.getByText('Start Monitoring');
      fireEvent.click(startButton);
      
      await waitFor(() => {
        expect(screen.getByText('Monitoring Started')).toBeInTheDocument();
      });
      
      const stopButton = screen.getByText('Stop Monitoring');
      fireEvent.click(stopButton);
      
      await waitFor(() => {
        expect(screen.getByText('Monitoring Stopped')).toBeInTheDocument();
      });
    });

    it('should allow configuring monitoring intervals', async () => {
      render(<PerformanceDashboard />);
      
      const intervalInput = screen.getByTestId('monitoring-interval');
      fireEvent.change(intervalInput, { target: { value: '5000' } });
      
      await waitFor(() => {
        expect(screen.getByText('Monitoring interval set to 5000ms')).toBeInTheDocument();
      });
    });

    it('should allow enabling/disabling specific metrics', async () => {
      render(<PerformanceDashboard />);
      
      const memoryToggle = screen.getByTestId('memory-monitoring-toggle');
      fireEvent.click(memoryToggle);
      
      await waitFor(() => {
        expect(screen.getByText('Memory monitoring disabled')).toBeInTheDocument();
      });
    });
  });

  describe('Performance Data Export', () => {
    it('should allow exporting performance data', async () => {
      render(<PerformanceDashboard />);
      
      const exportButton = screen.getByText('Export Data');
      fireEvent.click(exportButton);
      
      await waitFor(() => {
        expect(screen.getByText('Performance data exported')).toBeInTheDocument();
      });
    });

    it('should support different export formats', async () => {
      render(<PerformanceDashboard />);
      
      const formatSelect = screen.getByTestId('export-format');
      fireEvent.change(formatSelect, { target: { value: 'csv' } });
      
      const exportButton = screen.getByText('Export Data');
      fireEvent.click(exportButton);
      
      await waitFor(() => {
        expect(screen.getByText('Performance data exported as CSV')).toBeInTheDocument();
      });
    });
  });

  describe('Performance Dashboard Responsiveness', () => {
    it('should be responsive on different screen sizes', async () => {
      // Mock small screen
      Object.defineProperty(window, 'innerWidth', { value: 320 });
      Object.defineProperty(window, 'innerHeight', { value: 568 });
      
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('performance-dashboard')).toHaveClass('mobile-layout');
      });
    });

    it('should adapt layout for tablet screens', async () => {
      // Mock tablet screen
      Object.defineProperty(window, 'innerWidth', { value: 768 });
      Object.defineProperty(window, 'innerHeight', { value: 1024 });
      
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('performance-dashboard')).toHaveClass('tablet-layout');
      });
    });

    it('should optimize for desktop screens', async () => {
      // Mock desktop screen
      Object.defineProperty(window, 'innerWidth', { value: 1920 });
      Object.defineProperty(window, 'innerHeight', { value: 1080 });
      
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByTestId('performance-dashboard')).toHaveClass('desktop-layout');
      });
    });
  });

  describe('Performance Dashboard Error Handling', () => {
    it('should handle performance API errors gracefully', async () => {
      // Mock performance API error
      mockPerformance.getEntriesByType.mockImplementation(() => {
        throw new Error('Performance API not available');
      });
      
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('Performance monitoring unavailable')).toBeInTheDocument();
      });
    });

    it('should handle memory API errors gracefully', async () => {
      // Mock memory API error
      delete global.memory;
      
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('Memory monitoring unavailable')).toBeInTheDocument();
      });
    });

    it('should handle network API errors gracefully', async () => {
      // Mock network API error
      delete global.navigator.connection;
      
      render(<PerformanceDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('Network monitoring unavailable')).toBeInTheDocument();
      });
    });
  });

  describe('Performance Dashboard Accessibility', () => {
    it('should be accessible with keyboard navigation', async () => {
      render(<PerformanceDashboard />);
      
      const dashboard = screen.getByTestId('performance-dashboard');
      fireEvent.keyDown(dashboard, { key: 'Tab' });
      
      await waitFor(() => {
        expect(document.activeElement).toBeInTheDocument();
      });
    });

    it('should have proper ARIA labels', async () => {
      render(<PerformanceDashboard />);
      
      expect(screen.getByTestId('performance-dashboard')).toHaveAttribute('aria-label', 'Performance Dashboard');
      expect(screen.getByTestId('memory-usage')).toHaveAttribute('aria-label', 'Memory Usage');
      expect(screen.getByTestId('cpu-usage')).toHaveAttribute('aria-label', 'CPU Usage');
    });

    it('should support screen readers', async () => {
      render(<PerformanceDashboard />);
      
      expect(screen.getByTestId('performance-dashboard')).toHaveAttribute('role', 'main');
      expect(screen.getByTestId('performance-metrics')).toHaveAttribute('role', 'region');
    });
  });
});
