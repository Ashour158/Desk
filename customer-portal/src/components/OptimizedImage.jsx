import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import PropTypes from 'prop-types';
import { memo } from 'react';

/**
 * Optimized Image Component with WebP Support
 * Provides automatic WebP format detection, lazy loading, and progressive loading
 */
const OptimizedImage = memo(({
  src,
  alt,
  width,
  height,
  quality = 80,
  lazy = true,
  progressive = true,
  webp = true,
  fallback = true,
  className = '',
  style = {},
  onLoad,
  onError,
  placeholder = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMSIgaGVpZ2h0PSIxIiB2aWV3Qm94PSIwIDAgMSAxIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxIiBoZWlnaHQ9IjEiIGZpbGw9IiNmM2Y0ZjYiLz48L3N2Zz4=',
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(!lazy);
  const [hasError, setHasError] = useState(false);
  const [currentSrc, setCurrentSrc] = useState(null);
  const [webpSupported, setWebpSupported] = useState(false);
  const imgRef = useRef(null);
  const observerRef = useRef(null);

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

  // Generate optimized image URL
  const optimizedSrc = useMemo(() => {
    if (!src) return src;

    try {
      const url = new URL(src, window.location.origin);
      
      // Add WebP format if supported
      if (webp && webpSupported && !src.includes('.webp')) {
        const webpSrc = src.replace(/\.(jpg|jpeg|png)$/i, '.webp');
        if (webpSrc !== src) {
          return webpSrc;
        }
      }

      // Add optimization parameters
      if (width) url.searchParams.set('w', width.toString());
      if (height) url.searchParams.set('h', height.toString());
      if (quality) url.searchParams.set('q', quality.toString());
      url.searchParams.set('fit', 'crop');
      url.searchParams.set('auto', 'format');

      return url.toString();
    } catch (error) {
      console.warn('Failed to optimize image URL:', error);
      return src;
    }
  }, [src, webp, webpSupported, width, height, quality]);

  // Generate srcSet for responsive images
  const srcSet = useMemo(() => {
    if (!src || !width) return undefined;

    const sizes = [1, 2, 3]; // 1x, 2x, 3x
    return sizes.map(scale => {
      const w = width * scale;
      const h = height ? height * scale : undefined;
      
      const url = new URL(src, window.location.origin);
      url.searchParams.set('w', w.toString());
      if (h) url.searchParams.set('h', h.toString());
      url.searchParams.set('q', quality.toString());
      url.searchParams.set('fit', 'crop');
      url.searchParams.set('auto', 'format');
      
      return `${url.toString()} ${scale}x`;
    }).join(', ');
  }, [src, width, height, quality]);

  // Set up intersection observer for lazy loading
  useEffect(() => {
    if (!lazy || isInView) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      {
        rootMargin: '50px',
        threshold: 0.1
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
      observerRef.current = observer;
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [lazy, isInView]);

  // Load image
  useEffect(() => {
    if (!isInView || !optimizedSrc) return;

    const img = new Image();
    
    const handleLoad = () => {
      setCurrentSrc(optimizedSrc);
      setIsLoaded(true);
      setHasError(false);
      if (onLoad) onLoad();
    };

    const handleError = () => {
      setHasError(true);
      if (fallback && optimizedSrc !== src) {
        // Try fallback to original
        const fallbackImg = new Image();
        fallbackImg.onload = () => {
          setCurrentSrc(src);
          setIsLoaded(true);
          setHasError(false);
          if (onLoad) onLoad();
        };
        fallbackImg.onerror = () => {
          if (onError) onError();
        };
        fallbackImg.src = src;
      } else {
        if (onError) onError();
      }
    };

    img.onload = handleLoad;
    img.onerror = handleError;
    img.src = optimizedSrc;

    return () => {
      img.onload = null;
      img.onerror = null;
    };
  }, [isInView, optimizedSrc, src, fallback, onLoad, onError]);

  // Handle image load
  const handleImageLoad = useCallback(() => {
    setIsLoaded(true);
    setHasError(false);
    if (onLoad) onLoad();
  }, [onLoad]);

  // Handle image error
  const handleImageError = useCallback(() => {
    setHasError(true);
    if (onError) onError();
  }, [onError]);

  // Progressive loading styles
  const progressiveStyles = useMemo(() => {
    const baseStyles = {
      transition: 'opacity 0.3s ease-in-out',
      opacity: isLoaded ? 1 : 0,
      ...style
    };

    if (progressive && !isLoaded) {
      return {
        ...baseStyles,
        backgroundImage: `url(${placeholder})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      };
    }

    return baseStyles;
  }, [isLoaded, progressive, placeholder, style]);

  // Render loading placeholder
  if (!isInView && lazy) {
    return (
      <div
        ref={imgRef}
        className={`optimized-image-placeholder ${className}`}
        style={{
          width: width || '100%',
          height: height || '200px',
          backgroundColor: '#f3f4f6',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          ...style
        }}
        {...props}
      >
        <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>
          Loading...
        </div>
      </div>
    );
  }

  // Render error state
  if (hasError) {
    return (
      <div
        className={`optimized-image-error ${className}`}
        style={{
          width: width || '100%',
          height: height || '200px',
          backgroundColor: '#f3f4f6',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#6b7280',
          fontSize: '0.875rem',
          ...style
        }}
        {...props}
      >
        <div>Failed to load image</div>
      </div>
    );
  }

  // Render optimized image
  return (
    <img
      ref={imgRef}
      src={currentSrc || optimizedSrc}
      alt={alt}
      width={width}
      height={height}
      srcSet={srcSet}
      sizes={width ? `${width}px` : undefined}
      className={`optimized-image ${className}`}
      style={progressiveStyles}
      onLoad={handleImageLoad}
      onError={handleImageError}
      loading={lazy ? 'lazy' : 'eager'}
      decoding="async"
      {...props}
    />
  );
});

OptimizedImage.displayName = 'OptimizedImage';

OptimizedImage.propTypes = {
  src: PropTypes.string.isRequired,
  alt: PropTypes.string.isRequired,
  width: PropTypes.number,
  height: PropTypes.number,
  quality: PropTypes.number,
  lazy: PropTypes.bool,
  progressive: PropTypes.bool,
  webp: PropTypes.bool,
  fallback: PropTypes.bool,
  className: PropTypes.string,
  style: PropTypes.object,
  onLoad: PropTypes.func,
  onError: PropTypes.func,
  placeholder: PropTypes.string
};

/**
 * Image Gallery Component with WebP Support
 */
export const OptimizedImageGallery = memo(({ images = [], ...props }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const handleImageClick = useCallback((index) => {
    setCurrentIndex(index);
    setIsFullscreen(true);
  }, []);

  const handleCloseFullscreen = useCallback(() => {
    setIsFullscreen(false);
  }, []);

  const handleNext = useCallback(() => {
    setCurrentIndex((prev) => (prev + 1) % images.length);
  }, [images.length]);

  const handlePrev = useCallback(() => {
    setCurrentIndex((prev) => (prev - 1 + images.length) % images.length);
  }, [images.length]);

  return (
    <div className="optimized-image-gallery" {...props}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
        {images.map((image, index) => (
          <OptimizedImage
            key={image.id || index}
            src={image.src}
            alt={image.alt}
            width={200}
            height={200}
            onClick={() => handleImageClick(index)}
            style={{ cursor: 'pointer', borderRadius: '8px' }}
            {...image}
          />
        ))}
      </div>

      {/* Fullscreen modal */}
      {isFullscreen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.9)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}
          onClick={handleCloseFullscreen}
        >
          <div style={{ position: 'relative', maxWidth: '90vw', maxHeight: '90vh' }}>
            <OptimizedImage
              src={images[currentIndex]?.src}
              alt={images[currentIndex]?.alt}
              style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
            />
            
            {/* Navigation buttons */}
            {images.length > 1 && (
              <>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handlePrev();
                  }}
                  style={{
                    position: 'absolute',
                    left: '20px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'rgba(255, 255, 255, 0.8)',
                    border: 'none',
                    borderRadius: '50%',
                    width: '50px',
                    height: '50px',
                    cursor: 'pointer',
                    fontSize: '1.5rem'
                  }}
                >
                  ‹
                </button>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleNext();
                  }}
                  style={{
                    position: 'absolute',
                    right: '20px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'rgba(255, 255, 255, 0.8)',
                    border: 'none',
                    borderRadius: '50%',
                    width: '50px',
                    height: '50px',
                    cursor: 'pointer',
                    fontSize: '1.5rem'
                  }}
                >
                  ›
                </button>
              </>
            )}
            
            {/* Close button */}
            <button
              onClick={handleCloseFullscreen}
              style={{
                position: 'absolute',
                top: '20px',
                right: '20px',
                background: 'rgba(255, 255, 255, 0.8)',
                border: 'none',
                borderRadius: '50%',
                width: '40px',
                height: '40px',
                cursor: 'pointer',
                fontSize: '1.2rem'
              }}
            >
              ×
            </button>
          </div>
        </div>
      )}
    </div>
  );
});

OptimizedImageGallery.displayName = 'OptimizedImageGallery';

OptimizedImageGallery.propTypes = {
  images: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    src: PropTypes.string.isRequired,
    alt: PropTypes.string.isRequired
  }))
};

export default OptimizedImage;
