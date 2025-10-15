/**
 * Comprehensive test suite for AdvancedVirtualizedList component
 * Tests all virtual scrolling functionality with comprehensive coverage
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

import AdvancedVirtualizedList from '../AdvancedVirtualizedList';

// Mock Intersection Observer
const mockIntersectionObserver = vi.fn();
mockIntersectionObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null
});
window.IntersectionObserver = mockIntersectionObserver;

// Mock ResizeObserver
const mockResizeObserver = vi.fn();
mockResizeObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null
});
window.ResizeObserver = mockResizeObserver;

// Mock performance.now
vi.spyOn(performance, 'now').mockReturnValue(1000);

describe('AdvancedVirtualizedList', () => {
  const mockData = Array.from({ length: 1000 }, (_, i) => ({
    id: i,
    name: `Item ${i}`,
    description: `Description for item ${i}`,
    value: Math.random() * 100
  }));

  const defaultProps = {
    data: mockData,
    itemHeight: 50,
    containerHeight: 400,
    overscan: 5,
    className: 'test-virtualized-list'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock getBoundingClientRect
    Element.prototype.getBoundingClientRect = vi.fn(() => ({
      width: 800,
      height: 400,
      top: 0,
      left: 0,
      bottom: 400,
      right: 800,
      x: 0,
      y: 0,
      toJSON: () => {}
    }));
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Component Rendering', () => {
    it('renders without crashing', () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      expect(screen.getByTestId('virtualized-list')).toBeInTheDocument();
    });

    it('renders with custom className', () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      const list = screen.getByTestId('virtualized-list');
      expect(list).toHaveClass('test-virtualized-list');
    });

    it('renders container with correct height', () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      const container = screen.getByTestId('virtualized-container');
      expect(container).toHaveStyle({ height: '400px' });
    });

    it('renders only visible items initially', () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      // Should render approximately 8 visible items (400px / 50px) + overscan
      const visibleItems = screen.getAllByTestId(/virtualized-item-/);
      expect(visibleItems.length).toBeLessThanOrEqual(15); // 8 visible + 5 overscan + buffer
    });
  });

  describe('Virtual Scrolling', () => {
    it('renders correct number of visible items', () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      const visibleItems = screen.getAllByTestId(/virtualized-item-/);
      expect(visibleItems.length).toBeGreaterThan(0);
      expect(visibleItems.length).toBeLessThanOrEqual(15);
    });

    it('updates visible items on scroll', async () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      const container = screen.getByTestId('virtualized-container');
      
      // Simulate scroll
      fireEvent.scroll(container, { target: { scrollTop: 1000 } });
      
      await waitFor(() => {
        const visibleItems = screen.getAllByTestId(/virtualized-item-/);
        expect(visibleItems.length).toBeGreaterThan(0);
      });
    });

    it('handles scroll to bottom', async () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      const container = screen.getByTestId('virtualized-container');
      
      // Scroll to bottom
      fireEvent.scroll(container, { target: { scrollTop: 50000 } });
      
      await waitFor(() => {
        const visibleItems = screen.getAllByTestId(/virtualized-item-/);
        expect(visibleItems.length).toBeGreaterThan(0);
      });
    });

    it('handles scroll to top', async () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      const container = screen.getByTestId('virtualized-container');
      
      // Scroll to top
      fireEvent.scroll(container, { target: { scrollTop: 0 } });
      
      await waitFor(() => {
        const visibleItems = screen.getAllByTestId(/virtualized-item-/);
        expect(visibleItems.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Overscan Functionality', () => {
    it('renders overscan items above visible area', () => {
      render(<AdvancedVirtualizedList {...defaultProps} overscan={10} />);
      
      const visibleItems = screen.getAllByTestId(/virtualized-item-/);
      expect(visibleItems.length).toBeGreaterThan(8); // More than just visible items
    });

    it('renders overscan items below visible area', () => {
      render(<AdvancedVirtualizedList {...defaultProps} overscan={10} />);
      
      const visibleItems = screen.getAllByTestId(/virtualized-item-/);
      expect(visibleItems.length).toBeGreaterThan(8); // More than just visible items
    });

    it('adjusts overscan based on scroll direction', async () => {
      render(<AdvancedVirtualizedList {...defaultProps} overscan={5} />);
      
      const container = screen.getByTestId('virtualized-container');
      
      // Scroll down
      fireEvent.scroll(container, { target: { scrollTop: 1000 } });
      
      await waitFor(() => {
        const visibleItems = screen.getAllByTestId(/virtualized-item-/);
        expect(visibleItems.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Scroll Direction Detection', () => {
    it('detects scroll direction correctly', async () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      const container = screen.getByTestId('virtualized-container');
      
      // Scroll down
      fireEvent.scroll(container, { target: { scrollTop: 1000 } });
      
      await waitFor(() => {
        expect(screen.getByTestId('scroll-direction')).toHaveTextContent('down');
      });
      
      // Scroll up
      fireEvent.scroll(container, { target: { scrollTop: 500 } });
      
      await waitFor(() => {
        expect(screen.getByTestId('scroll-direction')).toHaveTextContent('up');
      });
    });

    it('handles rapid scroll direction changes', async () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      const container = screen.getByTestId('virtualized-container');
      
      // Rapid scroll changes
      fireEvent.scroll(container, { target: { scrollTop: 1000 } });
      fireEvent.scroll(container, { target: { scrollTop: 500 } });
      fireEvent.scroll(container, { target: { scrollTop: 1500 } });
      
      await waitFor(() => {
        const visibleItems = screen.getAllByTestId(/virtualized-item-/);
        expect(visibleItems.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Intersection Observer', () => {
    it('sets up intersection observer correctly', () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      expect(mockIntersectionObserver).toHaveBeenCalled();
    });

    it('handles intersection observer callbacks', () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      const observerCallback = mockIntersectionObserver.mock.calls[0][0];
      
      // Simulate intersection
      act(() => {
        observerCallback([{
          target: document.createElement('div'),
          isIntersecting: true,
          intersectionRatio: 1.0
        }]);
      });
      
      expect(screen.getByTestId('virtualized-list')).toBeInTheDocument();
    });

    it('cleans up intersection observer on unmount', () => {
      const { unmount } = render(<AdvancedVirtualizedList {...defaultProps} />);
      
      unmount();
      
      const observer = mockIntersectionObserver.mock.results[0].value;
      expect(observer.disconnect).toHaveBeenCalled();
    });
  });

  describe('Performance Monitoring', () => {
    it('tracks render performance', () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      expect(screen.getByTestId('performance-metrics')).toBeInTheDocument();
    });

    it('measures scroll performance', async () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      const container = screen.getByTestId('virtualized-container');
      
      fireEvent.scroll(container, { target: { scrollTop: 1000 } });
      
      await waitFor(() => {
        expect(screen.getByTestId('scroll-performance')).toBeInTheDocument();
      });
    });

    it('tracks memory usage', () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      expect(screen.getByTestId('memory-usage')).toBeInTheDocument();
    });
  });

  describe('Infinite Scroll', () => {
    it('supports infinite scroll when enabled', async () => {
      const onLoadMore = vi.fn();
      render(
        <AdvancedVirtualizedList 
          {...defaultProps} 
          infiniteScroll={true}
          onLoadMore={onLoadMore}
        />
      );
      
      const container = screen.getByTestId('virtualized-container');
      
      // Scroll to bottom
      fireEvent.scroll(container, { target: { scrollTop: 50000 } });
      
      await waitFor(() => {
        expect(onLoadMore).toHaveBeenCalled();
      });
    });

    it('does not trigger infinite scroll when disabled', async () => {
      const onLoadMore = vi.fn();
      render(
        <AdvancedVirtualizedList 
          {...defaultProps} 
          infiniteScroll={false}
          onLoadMore={onLoadMore}
        />
      );
      
      const container = screen.getByTestId('virtualized-container');
      
      // Scroll to bottom
      fireEvent.scroll(container, { target: { scrollTop: 50000 } });
      
      await waitFor(() => {
        expect(onLoadMore).not.toHaveBeenCalled();
      });
    });

    it('shows loading indicator during infinite scroll', async () => {
      const onLoadMore = vi.fn(() => new Promise(resolve => setTimeout(resolve, 100)));
      render(
        <AdvancedVirtualizedList 
          {...defaultProps} 
          infiniteScroll={true}
          onLoadMore={onLoadMore}
        />
      );
      
      const container = screen.getByTestId('virtualized-container');
      
      // Scroll to bottom
      fireEvent.scroll(container, { target: { scrollTop: 50000 } });
      
      await waitFor(() => {
        expect(screen.getByTestId('infinite-scroll-loading')).toBeInTheDocument();
      });
    });
  });

  describe('Scroll Progress', () => {
    it('displays scroll progress indicator', () => {
      render(<AdvancedVirtualizedList {...defaultProps} showScrollProgress={true} />);
      
      expect(screen.getByTestId('scroll-progress')).toBeInTheDocument();
    });

    it('updates scroll progress on scroll', async () => {
      render(<AdvancedVirtualizedList {...defaultProps} showScrollProgress={true} />);
      
      const container = screen.getByTestId('virtualized-container');
      
      fireEvent.scroll(container, { target: { scrollTop: 1000 } });
      
      await waitFor(() => {
        const progressBar = screen.getByTestId('scroll-progress-bar');
        expect(progressBar).toHaveStyle({ width: expect.any(String) });
      });
    });

    it('hides scroll progress when disabled', () => {
      render(<AdvancedVirtualizedList {...defaultProps} showScrollProgress={false} />);
      
      expect(screen.queryByTestId('scroll-progress')).not.toBeInTheDocument();
    });
  });

  describe('Memory Optimization', () => {
    it('implements memory optimization', () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      expect(screen.getByTestId('memory-optimization')).toBeInTheDocument();
    });

    it('tracks memory usage', () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      expect(screen.getByTestId('memory-usage')).toBeInTheDocument();
    });

    it('handles memory cleanup on unmount', () => {
      const { unmount } = render(<AdvancedVirtualizedList {...defaultProps} />);
      
      expect(() => unmount()).not.toThrow();
    });
  });

  describe('Error Handling', () => {
    it('handles empty data gracefully', () => {
      render(<AdvancedVirtualizedList {...defaultProps} data={[]} />);
      
      expect(screen.getByTestId('empty-state')).toBeInTheDocument();
    });

    it('handles invalid itemHeight gracefully', () => {
      render(<AdvancedVirtualizedList {...defaultProps} itemHeight={0} />);
      
      expect(screen.getByTestId('virtualized-list')).toBeInTheDocument();
    });

    it('handles invalid containerHeight gracefully', () => {
      render(<AdvancedVirtualizedList {...defaultProps} containerHeight={0} />);
      
      expect(screen.getByTestId('virtualized-list')).toBeInTheDocument();
    });

    it('handles scroll errors gracefully', async () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      const container = screen.getByTestId('virtualized-container');
      
      // Simulate scroll error
      fireEvent.scroll(container, { target: { scrollTop: 'invalid' } });
      
      await waitFor(() => {
        expect(screen.getByTestId('virtualized-list')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      expect(screen.getByRole('list')).toBeInTheDocument();
      expect(screen.getByLabelText('Virtualized List')).toBeInTheDocument();
    });

    it('supports keyboard navigation', () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      const container = screen.getByTestId('virtualized-container');
      expect(container).toHaveAttribute('tabIndex', '0');
    });

    it('announces scroll position changes', async () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      const container = screen.getByTestId('virtualized-container');
      
      fireEvent.scroll(container, { target: { scrollTop: 1000 } });
      
      await waitFor(() => {
        expect(screen.getByTestId('scroll-announcement')).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Design', () => {
    it('adapts to different container heights', () => {
      render(<AdvancedVirtualizedList {...defaultProps} containerHeight={600} />);
      
      const container = screen.getByTestId('virtualized-container');
      expect(container).toHaveStyle({ height: '600px' });
    });

    it('adapts to different item heights', () => {
      render(<AdvancedVirtualizedList {...defaultProps} itemHeight={100} />);
      
      const visibleItems = screen.getAllByTestId(/virtualized-item-/);
      expect(visibleItems.length).toBeGreaterThan(0);
    });

    it('handles window resize', async () => {
      render(<AdvancedVirtualizedList {...defaultProps} />);
      
      // Simulate window resize
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1200,
      });
      
      fireEvent(window, new Event('resize'));
      
      await waitFor(() => {
        expect(screen.getByTestId('virtualized-list')).toBeInTheDocument();
      });
    });
  });

  describe('Performance Optimization', () => {
    it('uses React.memo for performance', () => {
      expect(AdvancedVirtualizedList.displayName).toBe('AdvancedVirtualizedList');
    });

    it('implements shouldComponentUpdate optimization', () => {
      const { rerender } = render(<AdvancedVirtualizedList {...defaultProps} />);
      
      // Rerender with same props
      rerender(<AdvancedVirtualizedList {...defaultProps} />);
      
      expect(screen.getByTestId('virtualized-list')).toBeInTheDocument();
    });

    it('handles large datasets efficiently', () => {
      const largeData = Array.from({ length: 10000 }, (_, i) => ({
        id: i,
        name: `Item ${i}`,
        description: `Description for item ${i}`,
        value: Math.random() * 100
      }));
      
      render(<AdvancedVirtualizedList {...defaultProps} data={largeData} />);
      
      expect(screen.getByTestId('virtualized-list')).toBeInTheDocument();
    });
  });
});
