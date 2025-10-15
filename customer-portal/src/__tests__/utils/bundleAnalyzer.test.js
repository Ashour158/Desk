import { BundleAnalyzer, bundleAnalyzer, useBundleAnalyzer } from '../../utils/bundleAnalyzer';

// Mock React for the hook
jest.mock('react', () => ({
  useState: jest.fn(),
  useEffect: jest.fn(),
  useCallback: jest.fn()
}));

describe('BundleAnalyzer', () => {
  let analyzer;

  beforeEach(() => {
    analyzer = new BundleAnalyzer();
    // Mock performance API
    global.performance = {
      getEntriesByType: jest.fn(() => [
        {
          name: 'http://localhost:3000/static/js/main.js',
          transferSize: 100000,
          decodedBodySize: 200000,
          responseEnd: 1000,
          startTime: 500
        },
        {
          name: 'http://localhost:3000/static/css/main.css',
          transferSize: 50000,
          decodedBodySize: 100000,
          responseEnd: 800,
          startTime: 400
        }
      ])
    };
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('analyzeBundleSize', () => {
    it('calculates total bundle size correctly', () => {
      analyzer.analyzeBundleSize();
      
      expect(analyzer.metrics.bundleSize).toBe(150000); // 100000 + 50000
    });

    it('calculates chunk sizes correctly', () => {
      analyzer.analyzeBundleSize();
      
      expect(analyzer.metrics.chunkSizes).toHaveProperty('main');
      expect(analyzer.metrics.chunkSizes.main).toBe(100000);
    });

    it('calculates compression ratio correctly', () => {
      analyzer.analyzeBundleSize();
      
      // (300000 - 150000) / 300000 * 100 = 50%
      expect(analyzer.metrics.compressionRatio).toBe(50);
    });
  });

  describe('monitorLoadTimes', () => {
    it('tracks load times for different resource types', () => {
      analyzer.monitorLoadTimes();
      
      expect(analyzer.metrics.loadTimes.javascript).toBeDefined();
      expect(analyzer.metrics.loadTimes.css).toBeDefined();
      expect(analyzer.metrics.loadTimes.javascript[0]).toBe(500); // 1000 - 500
    });
  });

  describe('calculateCacheHitRate', () => {
    it('calculates cache hit rate correctly', () => {
      // Mock resources with different cache states
      global.performance.getEntriesByType = jest.fn(() => [
        { transferSize: 0, decodedBodySize: 100000 }, // Cache hit
        { transferSize: 50000, decodedBodySize: 100000 } // Cache miss
      ]);

      analyzer.calculateCacheHitRate();
      
      expect(analyzer.metrics.cacheHitRate).toBe(50); // 1 hit out of 2 requests
    });
  });

  describe('getRecommendations', () => {
    it('recommends code splitting for large bundles', () => {
      analyzer.metrics.bundleSize = 600000; // 600KB
      
      const recommendations = analyzer.getRecommendations();
      
      expect(recommendations).toContainEqual({
        type: 'warning',
        message: 'Bundle size is large (>500KB). Consider code splitting.',
        impact: 'high'
      });
    });

    it('recommends compression for low compression ratio', () => {
      analyzer.metrics.compressionRatio = 30;
      
      const recommendations = analyzer.getRecommendations();
      
      expect(recommendations).toContainEqual({
        type: 'info',
        message: 'Compression ratio is low. Enable gzip compression.',
        impact: 'medium'
      });
    });

    it('recommends caching optimization for low cache hit rate', () => {
      analyzer.metrics.cacheHitRate = 50;
      
      const recommendations = analyzer.getRecommendations();
      
      expect(recommendations).toContainEqual({
        type: 'warning',
        message: 'Cache hit rate is low. Optimize caching strategy.',
        impact: 'medium'
      });
    });
  });

  describe('observer pattern', () => {
    it('notifies observers when metrics update', () => {
      const mockObserver = jest.fn();
      analyzer.addObserver(mockObserver);
      
      analyzer.analyzeBundleSize();
      
      expect(mockObserver).toHaveBeenCalledWith(analyzer.getMetrics());
    });

    it('removes observers correctly', () => {
      const mockObserver = jest.fn();
      analyzer.addObserver(mockObserver);
      analyzer.removeObserver(mockObserver);
      
      analyzer.analyzeBundleSize();
      
      expect(mockObserver).not.toHaveBeenCalled();
    });
  });

  describe('monitoring lifecycle', () => {
    it('starts monitoring correctly', () => {
      const analyzeSpy = jest.spyOn(analyzer, 'analyzeBundleSize');
      const monitorSpy = jest.spyOn(analyzer, 'monitorLoadTimes');
      const cacheSpy = jest.spyOn(analyzer, 'calculateCacheHitRate');
      
      analyzer.startMonitoring();
      
      expect(analyzeSpy).toHaveBeenCalled();
      expect(monitorSpy).toHaveBeenCalled();
      expect(cacheSpy).toHaveBeenCalled();
    });

    it('stops monitoring correctly', () => {
      analyzer.startMonitoring();
      analyzer.stopMonitoring();
      
      expect(analyzer.monitoringInterval).toBeNull();
    });
  });
});

describe('bundleAnalyzer instance', () => {
  it('is a singleton instance', () => {
    expect(bundleAnalyzer).toBeInstanceOf(BundleAnalyzer);
  });
});

describe('useBundleAnalyzer hook', () => {
  it('returns metrics and methods', () => {
    const mockSetState = jest.fn();
    const mockUseEffect = jest.fn();
    
    require('react').useState.mockReturnValue([{}, mockSetState]);
    require('react').useEffect.mockImplementation(mockUseEffect);
    
    const result = useBundleAnalyzer();
    
    expect(result).toHaveProperty('metrics');
    expect(result).toHaveProperty('startMonitoring');
    expect(result).toHaveProperty('stopMonitoring');
    expect(result).toHaveProperty('getRecommendations');
  });
});
