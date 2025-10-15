import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import PropTypes from 'prop-types';
import { memo } from 'react';

/**
 * Advanced Image Optimizer Component
 * Progressive loading with blur-to-sharp transitions and intelligent optimization
 */
const AdvancedImageOptimizer = memo(({ 
  src,
  alt = '',
  width,
  height,
  quality = 80,
  webp = true,
  avif = true,
  progressive = true,
  blurDataURL,
  placeholder = true,
  lazy = true,
  responsive = true,
  artDirection = false,
  onLoad,
  onError,
  className = '',
  style = {},
  ...props 
}) => {
  const [currentSrc, setCurrentSrc] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [loadProgress, setLoadProgress] = useState(0);
  const [loadStage, setLoadStage] = useState('placeholder');
  const [webpSupported, setWebpSupported] = useState(false);
  const [avifSupported, setAvifSupported] = useState(false);
  const [error, setError] = useState(null);
  const [isInView, setIsInView] = useState(!lazy);
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [devicePixelRatio, setDevicePixelRatio] = useState(1);
  const [connectionType, setConnectionType] = useState('4g');
  
  const imageRef = useRef(null);
  const intersectionObserver = useRef(null);
  const loadTimeout = useRef(null);
  const retryCount = useRef(0);
  const maxRetries = 3;
  const imageLoadPromises = useRef(new Map());

  // Check format support and device capabilities
  useEffect(() => {
    const checkFormatSupport = async () => {
      // Check WebP support
      const webpSupported = await checkWebPSupport();
      setWebpSupported(webpSupported);
      
      // Check AVIF support
      const avifSupported = await checkAVIFSupport();
      setAvifSupported(avifSupported);
      
      // Get device pixel ratio
      setDevicePixelRatio(window.devicePixelRatio || 1);
      
      // Get connection type
      if ('connection' in navigator) {
        setConnectionType(navigator.connection.effectiveType || '4g');
      }
    };
    
    checkFormatSupport();
  }, []);

  // Check WebP support
  const checkWebPSupport = useCallback(async () => {
    try {
      const canvas = document.createElement('canvas');
      canvas.width = 1;
      canvas.height = 1;
      return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    } catch {
      return false;
    }
  }, []);

  // Check AVIF support
  const checkAVIFSupport = useCallback(async () => {
    try {
      const canvas = document.createElement('canvas');
      canvas.width = 1;
      canvas.height = 1;
      return canvas.toDataURL('image/avif').indexOf('data:image/avif') === 0;
    } catch {
      return false;
    }
  }, []);

  // Generate optimized image URLs with intelligent format selection
  const imageUrls = useMemo(() => {
    if (!src) return {};
    
    try {
      const baseUrl = new URL(src, window.location.origin);
      const format = getOptimalFormat();
      const dimensions = getOptimalDimensions();
      
      return {
        // Ultra-low quality for instant blur
        blur: (() => {
          const url = new URL(baseUrl);
          url.searchParams.set('w', Math.max(10, (dimensions.width || 100) / 20).toString());
          url.searchParams.set('q', '10');
          url.searchParams.set('blur', '10');
          url.searchParams.set('auto', 'format');
          if (format !== 'original') url.searchParams.set('f', format);
          return url.toString();
        })(),
        
        // Low quality for initial load
        low: (() => {
          const url = new URL(baseUrl);
          url.searchParams.set('w', Math.max(20, (dimensions.width || 100) / 10).toString());
          url.searchParams.set('q', '20');
          url.searchParams.set('blur', '5');
          url.searchParams.set('auto', 'format');
          if (format !== 'original') url.searchParams.set('f', format);
          return url.toString();
        })(),
        
        // Medium quality for progressive loading
        medium: (() => {
          const url = new URL(baseUrl);
          url.searchParams.set('w', Math.max(50, (dimensions.width || 100) / 2).toString());
          url.searchParams.set('q', '50');
          url.searchParams.set('blur', '2');
          url.searchParams.set('auto', 'format');
          if (format !== 'original') url.searchParams.set('f', format);
          return url.toString();
        })(),
        
        // High quality for final image
        high: (() => {
          const url = new URL(baseUrl);
          if (dimensions.width) url.searchParams.set('w', dimensions.width.toString());
          if (dimensions.height) url.searchParams.set('h', dimensions.height.toString());
          url.searchParams.set('q', quality.toString());
          url.searchParams.set('auto', 'format');
          if (format !== 'original') url.searchParams.set('f', format);
          return url.toString();
        })()
      };
    } catch (error) {
      console.warn('Failed to generate optimized URLs:', error);
      return { blur: src, low: src, medium: src, high: src };
    }
  }, [src, width, height, quality, webp, avif, devicePixelRatio, connectionType]);

  // Get optimal format based on support and connection
  const getOptimalFormat = useCallback(() => {
    if (avif && avifSupported) return 'avif';
    if (webp && webpSupported) return 'webp';
    return 'original';
  }, [avif, avifSupported, webp, webpSupported]);

  // Get optimal dimensions based on device and connection
  const getOptimalDimensions = useCallback(() => {
    const baseWidth = width || 400;
    const baseHeight = height || 300;
    
    // Adjust for device pixel ratio
    const adjustedWidth = Math.ceil(baseWidth * devicePixelRatio);
    const adjustedHeight = Math.ceil(baseHeight * devicePixelRatio);
    
    // Adjust for connection type
    const connectionMultiplier = {
      'slow-2g': 0.5,
      '2g': 0.7,
      '3g': 0.8,
      '4g': 1.0
    }[connectionType] || 1.0;
    
    return {
      width: Math.ceil(adjustedWidth * connectionMultiplier),
      height: Math.ceil(adjustedHeight * connectionMultiplier)
    };
  }, [width, height, devicePixelRatio, connectionType]);

  // Set up intersection observer for lazy loading
  useEffect(() => {
    if (lazy && imageRef.current) {
      intersectionObserver.current = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            setIsIntersecting(true);
            if (intersectionObserver.current) {
              intersectionObserver.current.disconnect();
            }
          }
        },
        {
          rootMargin: '100px',
          threshold: 0.1
        }
      );
      
      intersectionObserver.current.observe(imageRef.current);
    }

    return () => {
      if (intersectionObserver.current) {
        intersectionObserver.current.disconnect();
      }
    };
  }, [lazy]);

  // Progressive loading with intelligent sequencing
  useEffect(() => {
    if (!isInView || !src) return;

    const loadImage = async (url, stage) => {
      // Check if already loading this URL
      if (imageLoadPromises.current.has(url)) {
        return imageLoadPromises.current.get(url);
      }

      const promise = new Promise((resolve, reject) => {
        const img = new Image();
        
        img.onload = () => {
          setCurrentSrc(url);
          setLoadStage(stage);
          setLoadProgress((['blur', 'low', 'medium', 'high'].indexOf(stage) + 1) / 4 * 100);
          resolve(url);
        };
        
        img.onerror = (error) => {
          console.warn(`Failed to load ${stage} quality image:`, error);
          reject(error);
        };
        
        // Add timeout for slow connections
        loadTimeout.current = setTimeout(() => {
          reject(new Error(`Timeout loading ${stage} quality image`));
        }, 15000);
        
        img.src = url;
      });

      imageLoadPromises.current.set(url, promise);
      return promise;
    };

    const progressiveLoad = async () => {
      try {
        setError(null);
        setLoadStage('loading');
        
        const loadSequence = progressive ? ['blur', 'low', 'medium', 'high'] : ['high'];
        
        for (const stage of loadSequence) {
          try {
            await loadImage(imageUrls[stage], stage);
            
            // Add intelligent delay between stages
            if (stage !== loadSequence[loadSequence.length - 1]) {
              const delay = getIntelligentDelay(stage, connectionType);
              await new Promise(resolve => setTimeout(resolve, delay));
            }
          } catch (error) {
            console.warn(`Failed to load ${stage} quality, trying next stage:`, error);
            if (stage === loadSequence[loadSequence.length - 1]) {
              throw error;
            }
          }
        }
        
        setIsLoaded(true);
        setLoadStage('loaded');
        onLoad?.(imageUrls.high);
        
      } catch (error) {
        console.error('Progressive loading failed:', error);
        setError(error);
        setLoadStage('error');
        
        // Retry with exponential backoff
        if (retryCount.current < maxRetries) {
          retryCount.current++;
          const delay = Math.pow(2, retryCount.current) * 1000;
          setTimeout(() => {
            progressiveLoad();
          }, delay);
        } else {
          onError?.(error);
        }
      }
    };

    progressiveLoad();

    return () => {
      if (loadTimeout.current) {
        clearTimeout(loadTimeout.current);
      }
    };
  }, [isInView, src, imageUrls, progressive, connectionType, onLoad, onError]);

  // Get intelligent delay based on stage and connection
  const getIntelligentDelay = useCallback((stage, connection) => {
    const baseDelays = {
      blur: 0,
      low: 100,
      medium: 200,
      high: 300
    };
    
    const connectionMultipliers = {
      'slow-2g': 3,
      '2g': 2,
      '3g': 1.5,
      '4g': 1
    };
    
    return baseDelays[stage] * (connectionMultipliers[connection] || 1);
  }, []);

  // Handle image load events
  const handleImageLoad = useCallback(() => {
    setIsLoaded(true);
    setLoadStage('loaded');
    onLoad?.(currentSrc);
  }, [currentSrc, onLoad]);

  const handleImageError = useCallback((error) => {
    setError(error);
    setLoadStage('error');
    onError?.(error);
  }, [onError]);

  // Generate responsive srcSet
  const generateSrcSet = useCallback(() => {
    if (!responsive) return null;
    
    const breakpoints = [320, 640, 768, 1024, 1280, 1536];
    const format = getOptimalFormat();
    
    return breakpoints
      .filter(bp => bp <= (width || 1024) * 2)
      .map(bp => {
        const url = new URL(src, window.location.origin);
        url.searchParams.set('w', bp.toString());
        url.searchParams.set('q', quality.toString());
        url.searchParams.set('auto', 'format');
        if (format !== 'original') url.searchParams.set('f', format);
        return `${url.toString()} ${bp}w`;
      })
      .join(', ');
  }, [src, width, quality, responsive, getOptimalFormat]);

  // Generate art direction sizes
  const generateSizes = useCallback(() => {
    if (!artDirection) return null;
    
    return '(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw';
  }, [artDirection]);

  // Generate placeholder with enhanced blur effect
  const placeholderStyle = useMemo(() => {
    if (!placeholder || loadStage === 'loaded') return {};
    
    return {
      background: blurDataURL ? `url(${blurDataURL})` : 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)',
      backgroundSize: blurDataURL ? 'cover' : '200% 100%',
      backgroundPosition: blurDataURL ? 'center' : '0 0',
      filter: blurDataURL ? 'blur(8px)' : 'none',
      animation: blurDataURL ? 'none' : 'shimmer 2s infinite',
      transform: 'scale(1.1)',
      transition: 'all 0.3s ease'
    };
  }, [placeholder, loadStage, blurDataURL]);

  // Generate container style with enhanced animations
  const containerStyle = useMemo(() => ({
    position: 'relative',
    width: width ? `${width}px` : '100%',
    height: height ? `${height}px` : 'auto',
    overflow: 'hidden',
    backgroundColor: '#f8f9fa',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    transition: 'all 0.3s ease',
    ...style
  }), [width, height, style]);

  // Generate image style with enhanced transitions
  const imageStyle = useMemo(() => ({
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
    opacity: isLoaded ? 1 : 0.8,
    filter: getImageFilter(),
    transform: getImageTransform()
  }), [isLoaded, loadStage]);

  // Get image filter based on load stage
  const getImageFilter = useCallback(() => {
    switch (loadStage) {
      case 'blur': return 'blur(8px) brightness(0.8)';
      case 'low': return 'blur(4px) brightness(0.9)';
      case 'medium': return 'blur(1px) brightness(0.95)';
      case 'high': return 'none';
      default: return 'blur(2px)';
    }
  }, [loadStage]);

  // Get image transform based on load stage
  const getImageTransform = useCallback(() => {
    switch (loadStage) {
      case 'blur': return 'scale(1.05)';
      case 'low': return 'scale(1.02)';
      case 'medium': return 'scale(1.01)';
      case 'high': return 'scale(1)';
      default: return 'scale(1.02)';
    }
  }, [loadStage]);

  return (
    <div
      ref={imageRef}
      className={`advanced-image-optimizer ${className}`}
      style={containerStyle}
      {...props}
    >
      {/* Enhanced Placeholder/Background */}
      {loadStage !== 'loaded' && (
        <div
          className="advanced-image-placeholder"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            ...placeholderStyle
          }}
        />
      )}

      {/* Progressive Image with Enhanced Attributes */}
      {currentSrc && (
        <img
          src={currentSrc}
          alt={alt}
          style={imageStyle}
          srcSet={generateSrcSet()}
          sizes={generateSizes()}
          onLoad={handleImageLoad}
          onError={handleImageError}
          loading={lazy ? 'lazy' : 'eager'}
          decoding="async"
        />
      )}

      {/* Enhanced Loading Progress Indicator */}
      {loadStage === 'loading' && (
        <div
          className="advanced-image-progress"
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            background: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            padding: '12px 20px',
            borderRadius: '25px',
            fontSize: '0.875rem',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
          }}
        >
          <div
            style={{
              width: '24px',
              height: '24px',
              border: '3px solid rgba(255, 255, 255, 0.3)',
              borderTop: '3px solid white',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }}
          />
          <div>
            <div>Loading {Math.round(loadProgress)}%</div>
            <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>
              {loadStage === 'blur' && 'Ultra-low quality...'}
              {loadStage === 'low' && 'Low quality...'}
              {loadStage === 'medium' && 'Medium quality...'}
              {loadStage === 'high' && 'High quality...'}
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Quality and Format Indicator */}
      {loadStage === 'loaded' && (
        <div
          className="advanced-image-info"
          style={{
            position: 'absolute',
            top: '8px',
            right: '8px',
            background: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            padding: '6px 12px',
            borderRadius: '20px',
            fontSize: '0.75rem',
            opacity: 0,
            transition: 'opacity 0.3s ease',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
          onMouseEnter={(e) => e.target.style.opacity = '1'}
          onMouseLeave={(e) => e.target.style.opacity = '0'}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>{getOptimalFormat().toUpperCase()}</span>
            <span>•</span>
            <span>{quality}%</span>
            <span>•</span>
            <span>{devicePixelRatio}x</span>
          </div>
        </div>
      )}

      {/* Enhanced Error State */}
      {error && (
        <div
          className="advanced-image-error"
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center',
            color: '#dc3545',
            fontSize: '0.875rem',
            background: 'rgba(255, 255, 255, 0.9)',
            padding: '20px',
            borderRadius: '12px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
          }}
        >
          <div style={{ fontSize: '2rem', marginBottom: '8px' }}>⚠️</div>
          <div style={{ fontWeight: '500', marginBottom: '4px' }}>Failed to load image</div>
          <div style={{ fontSize: '0.75rem', color: '#6c757d' }}>
            {retryCount.current < maxRetries ? (
              <>Retrying... ({retryCount.current}/{maxRetries})</>
            ) : (
              <>Unable to load image after {maxRetries} attempts</>
            )}
          </div>
        </div>
      )}

      {/* Enhanced Performance Info (Development) */}
      {process.env.NODE_ENV === 'development' && (
        <div
          className="advanced-image-debug"
          style={{
            position: 'absolute',
            bottom: '8px',
            left: '8px',
            background: 'rgba(0, 0, 0, 0.9)',
            color: 'white',
            padding: '8px 12px',
            borderRadius: '8px',
            fontSize: '0.75rem',
            fontFamily: 'monospace',
            backdropFilter: 'blur(10px)',
            maxWidth: '200px',
            lineHeight: '1.4'
          }}
        >
          <div>Stage: {loadStage}</div>
          <div>Progress: {Math.round(loadProgress)}%</div>
          <div>Format: {getOptimalFormat()}</div>
          <div>WebP: {webpSupported ? '✓' : '✗'}</div>
          <div>AVIF: {avifSupported ? '✓' : '✗'}</div>
          <div>DPR: {devicePixelRatio}x</div>
          <div>Connection: {connectionType}</div>
          <div>Retries: {retryCount.current}</div>
        </div>
      )}

      {/* Enhanced CSS Animations */}
      <style jsx>{`
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .advanced-image-optimizer:hover .advanced-image-info {
          opacity: 1 !important;
        }
        
        .advanced-image-optimizer:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
      `}</style>
    </div>
  );
});

AdvancedImageOptimizer.displayName = 'AdvancedImageOptimizer';

AdvancedImageOptimizer.propTypes = {
  src: PropTypes.string.isRequired,
  alt: PropTypes.string,
  width: PropTypes.number,
  height: PropTypes.number,
  quality: PropTypes.number,
  webp: PropTypes.bool,
  avif: PropTypes.bool,
  progressive: PropTypes.bool,
  blurDataURL: PropTypes.string,
  placeholder: PropTypes.bool,
  lazy: PropTypes.bool,
  responsive: PropTypes.bool,
  artDirection: PropTypes.bool,
  onLoad: PropTypes.func,
  onError: PropTypes.func,
  className: PropTypes.string,
  style: PropTypes.object
};

export default AdvancedImageOptimizer;
