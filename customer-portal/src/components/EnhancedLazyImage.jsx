import React, { useState, useRef, useEffect, memo, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';

/**
 * Enhanced LazyImage component with AVIF support, progressive loading, and advanced optimization
 * @param {Object} props - Component props
 */
const EnhancedLazyImage = memo(({ 
  src, 
  alt, 
  className = '', 
  style = {}, 
  placeholder = null,
  threshold = 0.1,
  onLoad = null,
  onError = null,
  webp = true,
  avif = true,
  sizes = '100vw',
  quality = 80,
  progressive = true,
  compression = 'auto',
  ...props 
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [webpSupported, setWebpSupported] = useState(false);
  const [avifSupported, setAvifSupported] = useState(false);
  const [progressiveLoaded, setProgressiveLoaded] = useState(false);
  const [formatDetected, setFormatDetected] = useState(null);
  const imgRef = useRef(null);

  // Check format support
  useEffect(() => {
    const checkFormatSupport = async () => {
      // Check WebP support
      if (webp) {
        const webpSupported = await checkWebPSupport();
        setWebpSupported(webpSupported);
      }
      
      // Check AVIF support
      if (avif) {
        const avifSupported = await checkAVIFSupport();
        setAvifSupported(avifSupported);
      }
    };
    
    checkFormatSupport();
  }, [webp, avif]);

  // Check WebP support
  const checkWebPSupport = () => {
    return new Promise((resolve) => {
      const canvas = document.createElement('canvas');
      canvas.width = 1;
      canvas.height = 1;
      const webpSupported = canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
      resolve(webpSupported);
    });
  };

  // Check AVIF support
  const checkAVIFSupport = () => {
    return new Promise((resolve) => {
      const canvas = document.createElement('canvas');
      canvas.width = 1;
      canvas.height = 1;
      const avifSupported = canvas.toDataURL('image/avif').indexOf('data:image/avif') === 0;
      resolve(avifSupported);
    });
  };

  // Detect image format
  const detectImageFormat = useCallback(async (imageSrc) => {
    try {
      const response = await fetch(imageSrc, { method: 'HEAD' });
      const contentType = response.headers.get('content-type');
      
      if (contentType) {
        if (contentType.includes('image/avif')) return 'avif';
        if (contentType.includes('image/webp')) return 'webp';
        if (contentType.includes('image/jpeg')) return 'jpeg';
        if (contentType.includes('image/png')) return 'png';
        if (contentType.includes('image/gif')) return 'gif';
      }
      
      // Fallback to file extension
      const extension = imageSrc.split('.').pop().toLowerCase();
      return extension;
    } catch (error) {
      console.warn('Failed to detect image format:', error);
      return 'unknown';
    }
  }, []);

  // Generate optimized image URL
  const optimizedSrc = useMemo(() => {
    if (!src) return src;
    
    const url = new URL(src, window.location.origin);
    
    // Add quality parameter
    url.searchParams.set('q', quality.toString());
    
    // Add compression parameter
    if (compression !== 'auto') {
      url.searchParams.set('compression', compression);
    }
    
    // Add format parameter based on support
    if (avif && avifSupported) {
      url.searchParams.set('f', 'avif');
    } else if (webp && webpSupported) {
      url.searchParams.set('f', 'webp');
    }
    
    return url.toString();
  }, [src, webp, webpSupported, avif, avifSupported, quality, compression]);

  // Generate srcSet for responsive images
  const srcSet = useMemo(() => {
    if (!src) return '';
    
    const breakpoints = [320, 640, 768, 1024, 1280, 1920];
    return breakpoints
      .map(width => {
        const height = Math.round(width * 0.75); // 4:3 aspect ratio
        const url = new URL(src, window.location.origin);
        url.searchParams.set('w', width.toString());
        url.searchParams.set('h', height.toString());
        url.searchParams.set('q', quality.toString());
        
        if (compression !== 'auto') {
          url.searchParams.set('compression', compression);
        }
        
        // Add format parameter
        if (avif && avifSupported) {
          url.searchParams.set('f', 'avif');
        } else if (webp && webpSupported) {
          url.searchParams.set('f', 'webp');
        }
        
        return `${url.toString()} ${width}w`;
      })
      .join(', ');
  }, [src, webp, webpSupported, avif, avifSupported, quality, compression]);

  // Generate progressive srcSet
  const progressiveSrcSet = useMemo(() => {
    if (!progressive || !src) return '';
    
    const breakpoints = [320, 640, 768, 1024, 1280, 1920];
    return breakpoints
      .map(width => {
        const height = Math.round(width * 0.75);
        const url = new URL(src, window.location.origin);
        url.searchParams.set('w', width.toString());
        url.searchParams.set('h', height.toString());
        url.searchParams.set('q', '20'); // Low quality for progressive loading
        url.searchParams.set('progressive', 'true');
        
        if (compression !== 'auto') {
          url.searchParams.set('compression', compression);
        }
        
        return `${url.toString()} ${width}w`;
      })
      .join(', ');
  }, [src, progressive, compression]);

  // Intersection Observer for lazy loading
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { 
        threshold,
        rootMargin: '50px'
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [threshold]);

  // Progressive loading effect
  useEffect(() => {
    if (progressive && isInView && !isLoaded) {
      const timer = setTimeout(() => {
        setProgressiveLoaded(true);
      }, 100);
      
      return () => clearTimeout(timer);
    }
  }, [progressive, isInView, isLoaded]);

  // Handle image load
  const handleLoad = useCallback(() => {
    setIsLoaded(true);
    if (onLoad) {
      onLoad();
    }
  }, [onLoad]);

  // Handle image error
  const handleError = useCallback(() => {
    setHasError(true);
    if (onError) {
      onError();
    }
  }, [onError]);

  // Handle progressive load
  const handleProgressiveLoad = useCallback(() => {
    setProgressiveLoaded(true);
  }, []);

  return (
    <div 
      ref={imgRef} 
      className={`enhanced-lazy-image-container ${className}`}
      style={{ 
        position: 'relative',
        overflow: 'hidden',
        ...style 
      }}
      {...props}
    >
      {/* Placeholder while loading */}
      {!isLoaded && !hasError && (
        <div 
          className="enhanced-lazy-image-placeholder"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: '#f0f0f0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#666',
            fontSize: '14px'
          }}
        >
          {placeholder ? (
            <img 
              src={placeholder} 
              alt="Loading..." 
              style={{ 
                width: '100%', 
                height: '100%', 
                objectFit: 'cover',
                filter: 'blur(5px)'
              }} 
            />
          ) : (
            <div>Loading...</div>
          )}
        </div>
      )}

      {/* Error state */}
      {hasError && (
        <div 
          className="enhanced-lazy-image-error"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: '#f8f8f8',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#999',
            fontSize: '14px',
            border: '1px dashed #ddd'
          }}
        >
          <div>Failed to load image</div>
        </div>
      )}

      {/* Progressive loading image */}
      {progressive && isInView && !isLoaded && !hasError && (
        <picture>
          {avif && avifSupported && (
            <source 
              srcSet={progressiveSrcSet} 
              sizes={sizes} 
              type="image/avif" 
            />
          )}
          {webp && webpSupported && (
            <source 
              srcSet={progressiveSrcSet} 
              sizes={sizes} 
              type="image/webp" 
            />
          )}
          <img
            src={optimizedSrc}
            alt={alt}
            onLoad={handleProgressiveLoad}
            onError={handleError}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: progressiveLoaded ? 0.3 : 0,
              transition: 'opacity 0.3s ease-in-out'
            }}
            loading="lazy"
            decoding="async"
          />
        </picture>
      )}

      {/* Final high-quality image */}
      {isInView && !hasError && (
        <picture>
          {avif && avifSupported && (
            <source 
              srcSet={srcSet} 
              sizes={sizes} 
              type="image/avif" 
            />
          )}
          {webp && webpSupported && (
            <source 
              srcSet={srcSet} 
              sizes={sizes} 
              type="image/webp" 
            />
          )}
          <img
            src={optimizedSrc}
            alt={alt}
            onLoad={handleLoad}
            onError={handleError}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: isLoaded ? 1 : 0,
              transition: 'opacity 0.3s ease-in-out'
            }}
            loading="lazy"
            decoding="async"
          />
        </picture>
      )}
    </div>
  );
});

EnhancedLazyImage.propTypes = {
  src: PropTypes.string.isRequired,
  alt: PropTypes.string.isRequired,
  className: PropTypes.string,
  style: PropTypes.object,
  placeholder: PropTypes.string,
  threshold: PropTypes.number,
  onLoad: PropTypes.func,
  onError: PropTypes.func,
  webp: PropTypes.bool,
  avif: PropTypes.bool,
  sizes: PropTypes.string,
  quality: PropTypes.number,
  progressive: PropTypes.bool,
  compression: PropTypes.oneOf(['auto', 'lossless', 'lossy'])
};

EnhancedLazyImage.defaultProps = {
  className: '',
  style: {},
  placeholder: null,
  threshold: 0.1,
  onLoad: null,
  onError: null,
  webp: true,
  avif: true,
  sizes: '100vw',
  quality: 80,
  progressive: true,
  compression: 'auto'
};

EnhancedLazyImage.displayName = 'EnhancedLazyImage';

export default EnhancedLazyImage;
