import React, { useState, useRef, useEffect, memo, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';

/**
 * Optimized LazyImage component with WebP support and responsive sizing
 * @param {Object} props - Component props
 * @param {string} props.src - Image source URL
 * @param {string} props.alt - Alt text for image
 * @param {string} props.className - CSS class name
 * @param {Object} props.style - Inline styles
 * @param {string} props.placeholder - Placeholder image URL
 * @param {number} props.threshold - Intersection observer threshold
 * @param {Function} props.onLoad - Callback when image loads
 * @param {Function} props.onError - Callback when image fails to load
 * @param {boolean} props.webp - Whether to use WebP format
 * @param {Object} props.sizes - Responsive image sizes
 * @param {string} props.quality - Image quality (1-100)
 */
const OptimizedLazyImage = memo(({ 
  src, 
  alt, 
  className = '', 
  style = {}, 
  placeholder = null,
  threshold = 0.1,
  onLoad = null,
  onError = null,
  webp = true,
  sizes = '100vw',
  quality = 80,
  ...props 
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [webpSupported, setWebpSupported] = useState(false);
  const imgRef = useRef(null);

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

  // Generate optimized image URL with WebP support and responsive sizing
  const optimizedSrc = useMemo(() => {
    if (!src) return src;
    
    // Add WebP support if available and requested
    if (webp && webpSupported && !src.includes('.webp')) {
      const webpSrc = src.replace(/\.(jpg|jpeg|png)$/i, '.webp');
      return webpSrc;
    }
    
    // Add responsive sizing parameters
    const url = new URL(src, window.location.origin);
    url.searchParams.set('w', '800');
    url.searchParams.set('h', '600');
    url.searchParams.set('fit', 'crop');
    url.searchParams.set('q', quality.toString());
    
    return url.toString();
  }, [src, webp, webpSupported, quality]);

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
        url.searchParams.set('fit', 'crop');
        url.searchParams.set('q', quality.toString());
        
        if (webp && webpSupported) {
          const webpUrl = new URL(url.toString());
          webpUrl.pathname = webpUrl.pathname.replace(/\.(jpg|jpeg|png)$/i, '.webp');
          return `${webpUrl.toString()} ${width}w`;
        }
        
        return `${url.toString()} ${width}w`;
      })
      .join(', ');
  }, [src, webp, webpSupported, quality]);

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
        rootMargin: '50px' // Start loading 50px before image comes into view
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [threshold]);

  const handleLoad = useCallback(() => {
    setIsLoaded(true);
    if (onLoad) {
      onLoad();
    }
  }, [onLoad]);

  const handleError = useCallback(() => {
    setHasError(true);
    if (onError) {
      onError();
    }
  }, [onError]);

  return (
    <div 
      ref={imgRef} 
      className={`optimized-lazy-image-container ${className}`}
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
          className="optimized-lazy-image-placeholder"
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
          className="optimized-lazy-image-error"
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

      {/* Actual image with WebP support */}
      {isInView && !hasError && (
        <picture>
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

OptimizedLazyImage.propTypes = {
  src: PropTypes.string.isRequired,
  alt: PropTypes.string.isRequired,
  className: PropTypes.string,
  style: PropTypes.object,
  placeholder: PropTypes.string,
  threshold: PropTypes.number,
  onLoad: PropTypes.func,
  onError: PropTypes.func,
  webp: PropTypes.bool,
  sizes: PropTypes.string,
  quality: PropTypes.number
};

OptimizedLazyImage.defaultProps = {
  className: '',
  style: {},
  placeholder: null,
  threshold: 0.1,
  onLoad: null,
  onError: null,
  webp: true,
  sizes: '100vw',
  quality: 80
};

OptimizedLazyImage.displayName = 'OptimizedLazyImage';

export default OptimizedLazyImage;
