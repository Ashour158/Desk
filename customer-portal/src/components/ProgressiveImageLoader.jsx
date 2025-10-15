import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import PropTypes from 'prop-types';
import { memo } from 'react';

/**
 * Progressive Image Loader Component
 * Enhanced user experience with blur-to-sharp transitions and multiple quality levels
 */
const ProgressiveImageLoader = memo(({ 
  src,
  alt = '',
  width,
  height,
  quality = 80,
  webp = true,
  fallback = true,
  progressive = true,
  blurDataURL,
  placeholder = true,
  lazy = true,
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
  const [error, setError] = useState(null);
  const [isInView, setIsInView] = useState(!lazy);
  const [isIntersecting, setIsIntersecting] = useState(false);
  
  const imageRef = useRef(null);
  const intersectionObserver = useRef(null);
  const loadTimeout = useRef(null);
  const retryCount = useRef(0);
  const maxRetries = 3;

  // Check WebP support
  useEffect(() => {
    const checkWebPSupport = () => {
      const canvas = document.createElement('canvas');
      canvas.width = 1;
      canvas.height = 1;
      return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    };
    setWebpSupported(checkWebPSupport());
  }, []);

  // Generate optimized image URLs for different quality levels
  const imageUrls = useMemo(() => {
    if (!src) return {};
    
    try {
      const baseUrl = new URL(src, window.location.origin);
      
      return {
        // Low quality for initial blur
        low: (() => {
          const url = new URL(baseUrl);
          url.searchParams.set('w', Math.max(20, (width || 100) / 10).toString());
          url.searchParams.set('q', '20');
          url.searchParams.set('blur', '5');
          url.searchParams.set('auto', 'format');
          return url.toString();
        })(),
        
        // Medium quality for progressive loading
        medium: (() => {
          const url = new URL(baseUrl);
          url.searchParams.set('w', Math.max(50, (width || 100) / 2).toString());
          url.searchParams.set('q', '50');
          url.searchParams.set('auto', 'format');
          return url.toString();
        })(),
        
        // High quality for final image
        high: (() => {
          const url = new URL(baseUrl);
          if (width) url.searchParams.set('w', width.toString());
          if (height) url.searchParams.set('h', height.toString());
          url.searchParams.set('q', quality.toString());
          url.searchParams.set('auto', 'format');
          
          // Add WebP format if supported
          if (webp && webpSupported && !src.includes('.webp')) {
            const webpSrc = src.replace(/\.(jpg|jpeg|png)$/i, '.webp');
            if (webpSrc !== src) {
              const webpUrl = new URL(webpSrc, window.location.origin);
              if (width) webpUrl.searchParams.set('w', width.toString());
              if (height) webpUrl.searchParams.set('h', height.toString());
              webpUrl.searchParams.set('q', quality.toString());
              webpUrl.searchParams.set('auto', 'format');
              return webpUrl.toString();
            }
          }
          
          return url.toString();
        })()
      };
    } catch (error) {
      console.warn('Failed to generate optimized URLs:', error);
      return { low: src, medium: src, high: src };
    }
  }, [src, width, height, quality, webp, webpSupported]);

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
          rootMargin: '50px',
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

  // Progressive loading sequence
  useEffect(() => {
    if (!isInView || !src) return;

    let currentStage = 'placeholder';
    const loadSequence = progressive ? ['low', 'medium', 'high'] : ['high'];

    const loadImage = (url, stage) => {
      return new Promise((resolve, reject) => {
        const img = new Image();
        
        img.onload = () => {
          setCurrentSrc(url);
          setLoadStage(stage);
          setLoadProgress((loadSequence.indexOf(stage) + 1) / loadSequence.length * 100);
          resolve(url);
        };
        
        img.onerror = (error) => {
          console.warn(`Failed to load ${stage} quality image:`, error);
          reject(error);
        };
        
        // Add timeout for slow connections
        loadTimeout.current = setTimeout(() => {
          reject(new Error(`Timeout loading ${stage} quality image`));
        }, 10000);
        
        img.src = url;
      });
    };

    const progressiveLoad = async () => {
      try {
        setError(null);
        setLoadStage('loading');
        
        for (const stage of loadSequence) {
          try {
            await loadImage(imageUrls[stage], stage);
            
            // Add small delay between stages for smooth transition
            if (stage !== loadSequence[loadSequence.length - 1]) {
              await new Promise(resolve => setTimeout(resolve, 100));
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
  }, [isInView, src, imageUrls, progressive, onLoad, onError]);

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

  // Generate placeholder with blur effect
  const placeholderStyle = useMemo(() => {
    if (!placeholder || loadStage === 'loaded') return {};
    
    return {
      background: blurDataURL ? `url(${blurDataURL})` : 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)',
      backgroundSize: blurDataURL ? 'cover' : '200% 100%',
      backgroundPosition: blurDataURL ? 'center' : '0 0',
      filter: blurDataURL ? 'blur(5px)' : 'none',
      animation: blurDataURL ? 'none' : 'shimmer 1.5s infinite'
    };
  }, [placeholder, loadStage, blurDataURL]);

  // Generate container style
  const containerStyle = useMemo(() => ({
    position: 'relative',
    width: width ? `${width}px` : '100%',
    height: height ? `${height}px` : 'auto',
    overflow: 'hidden',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
    ...style
  }), [width, height, style]);

  // Generate image style
  const imageStyle = useMemo(() => ({
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    transition: 'opacity 0.3s ease, filter 0.3s ease',
    opacity: isLoaded ? 1 : 0.7,
    filter: loadStage === 'low' ? 'blur(2px)' : loadStage === 'medium' ? 'blur(1px)' : 'none'
  }), [isLoaded, loadStage]);

  return (
    <div
      ref={imageRef}
      className={`progressive-image-loader ${className}`}
      style={containerStyle}
      {...props}
    >
      {/* Placeholder/Background */}
      {loadStage !== 'loaded' && (
        <div
          className="progressive-image-placeholder"
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

      {/* Progressive Image */}
      {currentSrc && (
        <img
          src={currentSrc}
          alt={alt}
          style={imageStyle}
          onLoad={handleImageLoad}
          onError={handleImageError}
        />
      )}

      {/* Loading Progress Indicator */}
      {loadStage === 'loading' && (
        <div
          className="progressive-image-progress"
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            background: 'rgba(0, 0, 0, 0.7)',
            color: 'white',
            padding: '8px 16px',
            borderRadius: '20px',
            fontSize: '0.875rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <div
            style={{
              width: '20px',
              height: '20px',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              borderTop: '2px solid white',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }}
          />
          Loading {Math.round(loadProgress)}%
        </div>
      )}

      {/* Quality Indicator */}
      {loadStage === 'loaded' && progressive && (
        <div
          className="progressive-image-quality"
          style={{
            position: 'absolute',
            top: '8px',
            right: '8px',
            background: 'rgba(0, 0, 0, 0.7)',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '0.75rem',
            opacity: 0,
            transition: 'opacity 0.3s ease'
          }}
          onMouseEnter={(e) => e.target.style.opacity = '1'}
          onMouseLeave={(e) => e.target.style.opacity = '0'}
        >
          {webpSupported ? 'WebP' : 'JPEG'} • {quality}%
        </div>
      )}

      {/* Error State */}
      {error && (
        <div
          className="progressive-image-error"
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center',
            color: '#dc3545',
            fontSize: '0.875rem'
          }}
        >
          <div style={{ marginBottom: '8px' }}>⚠️</div>
          <div>Failed to load image</div>
          {retryCount.current < maxRetries && (
            <div style={{ fontSize: '0.75rem', marginTop: '4px' }}>
              Retrying... ({retryCount.current}/{maxRetries})
            </div>
          )}
        </div>
      )}

      {/* Performance Info (Development) */}
      {process.env.NODE_ENV === 'development' && (
        <div
          className="progressive-image-debug"
          style={{
            position: 'absolute',
            bottom: '8px',
            left: '8px',
            background: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '0.75rem',
            fontFamily: 'monospace'
          }}
        >
          Stage: {loadStage} | Progress: {Math.round(loadProgress)}% | 
          WebP: {webpSupported ? '✓' : '✗'} | 
          Retries: {retryCount.current}
        </div>
      )}

      {/* CSS Animations */}
      <style jsx>{`
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .progressive-image-loader:hover .progressive-image-quality {
          opacity: 1 !important;
        }
      `}</style>
    </div>
  );
});

ProgressiveImageLoader.displayName = 'ProgressiveImageLoader';

ProgressiveImageLoader.propTypes = {
  src: PropTypes.string.isRequired,
  alt: PropTypes.string,
  width: PropTypes.number,
  height: PropTypes.number,
  quality: PropTypes.number,
  webp: PropTypes.bool,
  fallback: PropTypes.bool,
  progressive: PropTypes.bool,
  blurDataURL: PropTypes.string,
  placeholder: PropTypes.bool,
  lazy: PropTypes.bool,
  onLoad: PropTypes.func,
  onError: PropTypes.func,
  className: PropTypes.string,
  style: PropTypes.object
};

export default ProgressiveImageLoader;
