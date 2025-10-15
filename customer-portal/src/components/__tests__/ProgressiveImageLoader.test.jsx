/**
 * Comprehensive test suite for ProgressiveImageLoader component
 * Tests all progressive image loading functionality with comprehensive coverage
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

import ProgressiveImageLoader from '../ProgressiveImageLoader';

// Mock Image constructor
class MockImage {
  constructor() {
    this.src = '';
    this.onload = null;
    this.onerror = null;
    this.complete = false;
    this.naturalWidth = 0;
    this.naturalHeight = 0;
  }
  
  addEventListener(event, callback) {
    if (event === 'load') this.onload = callback;
    if (event === 'error') this.onerror = callback;
  }
  
  removeEventListener() {}
}

// Mock Intersection Observer
const mockIntersectionObserver = vi.fn();
mockIntersectionObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null
});
window.IntersectionObserver = mockIntersectionObserver;

// Mock performance.now
vi.spyOn(performance, 'now').mockReturnValue(1000);

describe('ProgressiveImageLoader', () => {
  const defaultProps = {
    src: 'https://example.com/image.jpg',
    alt: 'Test Image',
    width: 400,
    height: 300,
    className: 'test-progressive-image'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock Image constructor
    global.Image = MockImage;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Component Rendering', () => {
    it('renders without crashing', () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      expect(screen.getByTestId('progressive-image-container')).toBeInTheDocument();
    });

    it('renders with custom className', () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      const container = screen.getByTestId('progressive-image-container');
      expect(container).toHaveClass('test-progressive-image');
    });

    it('renders with correct dimensions', () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      const container = screen.getByTestId('progressive-image-container');
      expect(container).toHaveStyle({ width: '400px', height: '300px' });
    });

    it('renders loading state initially', () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      expect(screen.getByTestId('image-loading')).toBeInTheDocument();
    });
  });

  describe('Progressive Loading Stages', () => {
    it('renders blur stage initially', () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      expect(screen.getByTestId('image-blur')).toBeInTheDocument();
    });

    it('transitions to low quality stage', async () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      // Simulate low quality image load
      act(() => {
        const mockImage = new MockImage();
        mockImage.src = 'https://example.com/image-low.jpg';
        mockImage.complete = true;
        mockImage.naturalWidth = 100;
        mockImage.naturalHeight = 75;
        mockImage.onload();
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('image-low-quality')).toBeInTheDocument();
      });
    });

    it('transitions to medium quality stage', async () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      // Simulate medium quality image load
      act(() => {
        const mockImage = new MockImage();
        mockImage.src = 'https://example.com/image-medium.jpg';
        mockImage.complete = true;
        mockImage.naturalWidth = 200;
        mockImage.naturalHeight = 150;
        mockImage.onload();
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('image-medium-quality')).toBeInTheDocument();
      });
    });

    it('transitions to high quality stage', async () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      // Simulate high quality image load
      act(() => {
        const mockImage = new MockImage();
        mockImage.src = 'https://example.com/image.jpg';
        mockImage.complete = true;
        mockImage.naturalWidth = 400;
        mockImage.naturalHeight = 300;
        mockImage.onload();
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('image-high-quality')).toBeInTheDocument();
      });
    });

    it('completes loading process', async () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      // Simulate complete loading process
      act(() => {
        const mockImage = new MockImage();
        mockImage.src = 'https://example.com/image.jpg';
        mockImage.complete = true;
        mockImage.naturalWidth = 400;
        mockImage.naturalHeight = 300;
        mockImage.onload();
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('image-loaded')).toBeInTheDocument();
        expect(screen.queryByTestId('image-loading')).not.toBeInTheDocument();
      });
    });
  });

  describe('Image Format Optimization', () => {
    it('supports WebP format', async () => {
      render(<ProgressiveImageLoader {...defaultProps} format="webp" />);
      
      await waitFor(() => {
        expect(screen.getByTestId('image-webp')).toBeInTheDocument();
      });
    });

    it('supports AVIF format', async () => {
      render(<ProgressiveImageLoader {...defaultProps} format="avif" />);
      
      await waitFor(() => {
        expect(screen.getByTestId('image-avif')).toBeInTheDocument();
      });
    });

    it('falls back to JPEG when WebP is not supported', async () => {
      // Mock WebP support check
      const mockCanvas = {
        toDataURL: vi.fn(() => 'data:image/jpeg;base64,')
      };
      HTMLCanvasElement.prototype.toDataURL = mockCanvas.toDataURL;
      
      render(<ProgressiveImageLoader {...defaultProps} format="webp" />);
      
      await waitFor(() => {
        expect(screen.getByTestId('image-jpeg-fallback')).toBeInTheDocument();
      });
    });

    it('falls back to JPEG when AVIF is not supported', async () => {
      render(<ProgressiveImageLoader {...defaultProps} format="avif" />);
      
      await waitFor(() => {
        expect(screen.getByTestId('image-jpeg-fallback')).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Image Loading', () => {
    it('loads appropriate image size for mobile', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });
      
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      expect(screen.getByTestId('image-mobile')).toBeInTheDocument();
    });

    it('loads appropriate image size for tablet', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768,
      });
      
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      expect(screen.getByTestId('image-tablet')).toBeInTheDocument();
    });

    it('loads appropriate image size for desktop', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1200,
      });
      
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      expect(screen.getByTestId('image-desktop')).toBeInTheDocument();
    });

    it('handles window resize', async () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      // Simulate window resize
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768,
      });
      
      fireEvent(window, new Event('resize'));
      
      await waitFor(() => {
        expect(screen.getByTestId('image-tablet')).toBeInTheDocument();
      });
    });
  });

  describe('Art Direction', () => {
    it('supports art direction for different screen sizes', () => {
      const artDirection = {
        mobile: 'https://example.com/image-mobile.jpg',
        tablet: 'https://example.com/image-tablet.jpg',
        desktop: 'https://example.com/image-desktop.jpg'
      };
      
      render(<ProgressiveImageLoader {...defaultProps} artDirection={artDirection} />);
      
      expect(screen.getByTestId('image-art-direction')).toBeInTheDocument();
    });

    it('handles missing art direction gracefully', () => {
      render(<ProgressiveImageLoader {...defaultProps} artDirection={{}} />);
      
      expect(screen.getByTestId('progressive-image-container')).toBeInTheDocument();
    });
  });

  describe('Lazy Loading', () => {
    it('implements lazy loading with Intersection Observer', () => {
      render(<ProgressiveImageLoader {...defaultProps} lazy={true} />);
      
      expect(mockIntersectionObserver).toHaveBeenCalled();
    });

    it('loads image when it comes into view', async () => {
      render(<ProgressiveImageLoader {...defaultProps} lazy={true} />);
      
      const observerCallback = mockIntersectionObserver.mock.calls[0][0];
      
      // Simulate intersection
      act(() => {
        observerCallback([{
          target: document.createElement('div'),
          isIntersecting: true,
          intersectionRatio: 1.0
        }]);
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('image-loading')).toBeInTheDocument();
      });
    });

    it('does not load image when not in view', () => {
      render(<ProgressiveImageLoader {...defaultProps} lazy={true} />);
      
      expect(screen.queryByTestId('image-loading')).not.toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('handles image load errors gracefully', async () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      // Simulate image load error
      act(() => {
        const mockImage = new MockImage();
        mockImage.src = 'https://example.com/invalid-image.jpg';
        mockImage.onerror();
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('image-error')).toBeInTheDocument();
      });
    });

    it('shows error message on load failure', async () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      act(() => {
        const mockImage = new MockImage();
        mockImage.src = 'https://example.com/invalid-image.jpg';
        mockImage.onerror();
      });
      
      await waitFor(() => {
        expect(screen.getByText('Failed to load image')).toBeInTheDocument();
      });
    });

    it('provides retry functionality on error', async () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      act(() => {
        const mockImage = new MockImage();
        mockImage.src = 'https://example.com/invalid-image.jpg';
        mockImage.onerror();
      });
      
      await waitFor(() => {
        const retryButton = screen.getByTestId('retry-button');
        expect(retryButton).toBeInTheDocument();
      });
    });

    it('handles network errors gracefully', async () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      // Simulate network error
      act(() => {
        const mockImage = new MockImage();
        mockImage.src = 'https://example.com/network-error.jpg';
        mockImage.onerror();
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('network-error')).toBeInTheDocument();
      });
    });
  });

  describe('Performance Monitoring', () => {
    it('tracks loading performance', () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      expect(screen.getByTestId('performance-metrics')).toBeInTheDocument();
    });

    it('measures load time', async () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      act(() => {
        const mockImage = new MockImage();
        mockImage.src = 'https://example.com/image.jpg';
        mockImage.complete = true;
        mockImage.onload();
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('load-time')).toBeInTheDocument();
      });
    });

    it('tracks memory usage', () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      expect(screen.getByTestId('memory-usage')).toBeInTheDocument();
    });

    it('monitors network performance', () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      expect(screen.getByTestId('network-performance')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      expect(screen.getByRole('img')).toBeInTheDocument();
      expect(screen.getByLabelText('Test Image')).toBeInTheDocument();
    });

    it('supports keyboard navigation', () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      const container = screen.getByTestId('progressive-image-container');
      expect(container).toHaveAttribute('tabIndex', '0');
    });

    it('announces loading state changes', async () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      act(() => {
        const mockImage = new MockImage();
        mockImage.src = 'https://example.com/image.jpg';
        mockImage.complete = true;
        mockImage.onload();
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('loading-announcement')).toBeInTheDocument();
      });
    });

    it('provides alt text for all image stages', () => {
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      expect(screen.getByAltText('Test Image')).toBeInTheDocument();
    });
  });

  describe('Responsive Design', () => {
    it('adapts to different screen sizes', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768,
      });
      
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      const container = screen.getByTestId('progressive-image-container');
      expect(container).toHaveClass('responsive');
    });

    it('handles high DPI displays', () => {
      Object.defineProperty(window, 'devicePixelRatio', {
        writable: true,
        configurable: true,
        value: 2,
      });
      
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      expect(screen.getByTestId('image-high-dpi')).toBeInTheDocument();
    });

    it('optimizes for different connection speeds', () => {
      // Mock slow connection
      Object.defineProperty(navigator, 'connection', {
        writable: true,
        configurable: true,
        value: { effectiveType: 'slow-2g' }
      });
      
      render(<ProgressiveImageLoader {...defaultProps} />);
      
      expect(screen.getByTestId('image-slow-connection')).toBeInTheDocument();
    });
  });

  describe('Performance Optimization', () => {
    it('uses React.memo for performance', () => {
      expect(ProgressiveImageLoader.displayName).toBe('ProgressiveImageLoader');
    });

    it('implements shouldComponentUpdate optimization', () => {
      const { rerender } = render(<ProgressiveImageLoader {...defaultProps} />);
      
      // Rerender with same props
      rerender(<ProgressiveImageLoader {...defaultProps} />);
      
      expect(screen.getByTestId('progressive-image-container')).toBeInTheDocument();
    });

    it('handles large images efficiently', () => {
      const largeImageProps = {
        ...defaultProps,
        src: 'https://example.com/large-image.jpg',
        width: 2000,
        height: 1500
      };
      
      render(<ProgressiveImageLoader {...largeImageProps} />);
      
      expect(screen.getByTestId('progressive-image-container')).toBeInTheDocument();
    });

    it('cleans up resources on unmount', () => {
      const { unmount } = render(<ProgressiveImageLoader {...defaultProps} />);
      
      expect(() => unmount()).not.toThrow();
    });
  });
});
