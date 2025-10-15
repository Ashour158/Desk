import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import PropTypes from 'prop-types';
import { memo } from 'react';

/**
 * Progressive Image Component with Advanced Optimization
 * Provides progressive loading, blur-to-sharp transitions, and advanced caching
 */
const ProgressiveImage = memo(({
  src,
  alt,
  width,
  height,
  quality = 80,
  blurDataURL,
  placeholder = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMSIgaGVpZ2h0PSIxIiB2aWV3Qm94PSIwIDAgMSAxIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxIiBoZWlnaHQ9IjEiIGZpbGw9IiNmM2Y0ZjYiLz48L3N2Zz4=',
  className = '',
  style = {},
  onLoad,
  onError,
  lazy = true,
  progressive = true,
  blur = true,
  fade = true,
  cache = true,
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(!lazy);
  const [hasError, setHasError] = useState(false);
  const [currentSrc, setCurrentSrc] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadProgress, setLoadProgress] = useState(0);
  const imgRef = useRef(null);
  const observerRef = useRef(null);
  const xhrRef = useRef(null);

  // Generate optimized URLs for different quality levels
  const imageUrls = useMemo(() => {
    if (!src) return {};

    try {
      const baseUrl = new URL(src, window.location.origin);
      
      return {
        // Low quality for progressive loading
        low: (() => {
          const url = new URL(baseUrl);
          url.searchParams.set('w', Math.max(20, (width || 100) / 10).toString());
          url.searchParams.set('q', '20');
          url.searchParams.set('blur', '5');
          return url.toString();
        })(),
        
        // Medium quality
        medium: (() => {
          const url = new URL(baseUrl);
          url.searchParams.set('w', Math.max(50, (width || 100) / 2).toString());
          url.searchParams.set('q', '50');
          return url.toString();
        })(),
        
        // High quality
        high: (() => {
          const url = new URL(baseUrl);
          if (width) url.searchParams.set('w', width.toString());
          if (height) url.searchParams.set('h', height.toString());
          url.searchParams.set('q', quality.toString());
          url.searchParams.set('auto', 'format');
          return url.toString();
        })()
      };
    } catch (error) {
      console.warn('Failed to generate optimized URLs:', error);
      return { high: src };
    }
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
        rootMargin: '100px',
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

  // Progressive loading effect
  useEffect(() => {
    if (!isInView || !imageUrls.high) return;

    let currentStep = 0;
    const steps = ['low', 'medium', 'high'];
    
    const loadStep = async (step) => {
      try {
        setIsLoading(true);
        
        if (step === 'low' && blurDataURL) {
          setCurrentSrc(blurDataURL);
          await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        const img = new Image();
        
        return new Promise((resolve, reject) => {
          img.onload = () => {
            setCurrentSrc(imageUrls[step]);
            setLoadProgress((currentStep + 1) / steps.length * 100);
            resolve();
          };
          
          img.onerror = reject;
          img.src = imageUrls[step];
        });
      } catch (error) {
        console.warn(`Failed to load ${step} quality image:`, error);
        throw error;
      }
    };

    const loadProgressive = async () => {
      try {
        for (const step of steps) {
          if (imageUrls[step]) {
            await loadStep(step);
            currentStep++;
            
            // Add delay between steps for smooth transition
            if (step !== 'high') {
              await new Promise(resolve => setTimeout(resolve, 200));
            }
          }
        }
        
        setIsLoaded(true);
        setIsLoading(false);
        setLoadProgress(100);
        
        if (onLoad) onLoad();
      } catch (error) {
        setHasError(true);
        setIsLoading(false);
        if (onError) onError();
      }
    };

    loadProgressive();
  }, [isInView, imageUrls, blurDataURL, onLoad, onError]);

  // Handle image load
  const handleImageLoad = useCallback(() => {
    setIsLoaded(true);
    setIsLoading(false);
    setHasError(false);
    if (onLoad) onLoad();
  }, [onLoad]);

  // Handle image error
  const handleImageError = useCallback(() => {
    setHasError(true);
    setIsLoading(false);
    if (onError) onError();
  }, [onError]);

  // Progressive loading styles
  const progressiveStyles = useMemo(() => {
    const baseStyles = {
      width: width || '100%',
      height: height || 'auto',
      transition: fade ? 'opacity 0.5s ease-in-out, filter 0.3s ease-in-out' : 'none',
      opacity: isLoaded ? 1 : 0.7,
      filter: blur && !isLoaded ? 'blur(5px)' : 'none',
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
  }, [isLoaded, progressive, blur, fade, placeholder, style, width, height]);

  // Render loading state
  if (!isInView && lazy) {
    return (
      <div
        ref={imgRef}
        className={`progressive-image-placeholder ${className}`}
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
        className={`progressive-image-error ${className}`}
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

  // Render progressive image
  return (
    <div
      ref={imgRef}
      className={`progressive-image-container ${className}`}
      style={{ position: 'relative', ...style }}
      {...props}
    >
      {/* Progressive image */}
      <img
        src={currentSrc || imageUrls.high}
        alt={alt}
        width={width}
        height={height}
        className="progressive-image"
        style={progressiveStyles}
        onLoad={handleImageLoad}
        onError={handleImageError}
        loading={lazy ? 'lazy' : 'eager'}
        decoding="async"
      />
      
      {/* Loading progress indicator */}
      {isLoading && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            background: 'rgba(0, 0, 0, 0.7)',
            color: 'white',
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            fontSize: '0.875rem',
            zIndex: 10
          }}
        >
          Loading... {Math.round(loadProgress)}%
        </div>
      )}
      
      {/* Blur overlay for progressive effect */}
      {progressive && !isLoaded && currentSrc && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundImage: `url(${currentSrc})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            filter: 'blur(10px)',
            zIndex: 1
          }}
        />
      )}
    </div>
  );
});

ProgressiveImage.displayName = 'ProgressiveImage';

ProgressiveImage.propTypes = {
  src: PropTypes.string.isRequired,
  alt: PropTypes.string.isRequired,
  width: PropTypes.number,
  height: PropTypes.number,
  quality: PropTypes.number,
  blurDataURL: PropTypes.string,
  placeholder: PropTypes.string,
  className: PropTypes.string,
  style: PropTypes.object,
  onLoad: PropTypes.func,
  onError: PropTypes.func,
  lazy: PropTypes.bool,
  progressive: PropTypes.bool,
  blur: PropTypes.bool,
  fade: PropTypes.bool,
  cache: PropTypes.bool
};

/**
 * Image Gallery with Progressive Loading
 */
export const ProgressiveImageGallery = memo(({ 
  images = [], 
  columns = 3,
  gap = '1rem',
  ...props 
}) => {
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const handleImageClick = useCallback((index) => {
    setSelectedIndex(index);
    setIsFullscreen(true);
  }, []);

  const handleCloseFullscreen = useCallback(() => {
    setIsFullscreen(false);
    setSelectedIndex(null);
  }, []);

  const handleNext = useCallback(() => {
    setSelectedIndex((prev) => (prev + 1) % images.length);
  }, [images.length]);

  const handlePrev = useCallback(() => {
    setSelectedIndex((prev) => (prev - 1 + images.length) % images.length);
  }, [images.length]);

  const handleKeyDown = useCallback((event) => {
    if (!isFullscreen) return;
    
    switch (event.key) {
      case 'Escape':
        handleCloseFullscreen();
        break;
      case 'ArrowLeft':
        handlePrev();
        break;
      case 'ArrowRight':
        handleNext();
        break;
    }
  }, [isFullscreen, handleCloseFullscreen, handlePrev, handleNext]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div className="progressive-image-gallery" {...props}>
      <div 
        style={{ 
          display: 'grid', 
          gridTemplateColumns: `repeat(${columns}, 1fr)`,
          gap: gap
        }}
      >
        {images.map((image, index) => (
          <ProgressiveImage
            key={image.id || index}
            src={image.src}
            alt={image.alt}
            width={image.width}
            height={image.height}
            blurDataURL={image.blurDataURL}
            onClick={() => handleImageClick(index)}
            style={{ 
              cursor: 'pointer', 
              borderRadius: '8px',
              overflow: 'hidden'
            }}
            {...image}
          />
        ))}
      </div>

      {/* Fullscreen modal */}
      {isFullscreen && selectedIndex !== null && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.95)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '2rem'
          }}
          onClick={handleCloseFullscreen}
        >
          <div style={{ position: 'relative', maxWidth: '100%', maxHeight: '100%' }}>
            <ProgressiveImage
              src={images[selectedIndex]?.src}
              alt={images[selectedIndex]?.alt}
              blurDataURL={images[selectedIndex]?.blurDataURL}
              style={{ 
                maxWidth: '100%', 
                maxHeight: '100%', 
                objectFit: 'contain',
                borderRadius: '8px'
              }}
            />
            
            {/* Navigation */}
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
                    background: 'rgba(255, 255, 255, 0.9)',
                    border: 'none',
                    borderRadius: '50%',
                    width: '50px',
                    height: '50px',
                    cursor: 'pointer',
                    fontSize: '1.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
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
                    background: 'rgba(255, 255, 255, 0.9)',
                    border: 'none',
                    borderRadius: '50%',
                    width: '50px',
                    height: '50px',
                    cursor: 'pointer',
                    fontSize: '1.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
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
                background: 'rgba(255, 255, 255, 0.9)',
                border: 'none',
                borderRadius: '50%',
                width: '40px',
                height: '40px',
                cursor: 'pointer',
                fontSize: '1.2rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              ×
            </button>
            
            {/* Image counter */}
            <div
              style={{
                position: 'absolute',
                bottom: '20px',
                left: '50%',
                transform: 'translateX(-50%)',
                background: 'rgba(0, 0, 0, 0.7)',
                color: 'white',
                padding: '0.5rem 1rem',
                borderRadius: '20px',
                fontSize: '0.875rem'
              }}
            >
              {selectedIndex + 1} / {images.length}
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

ProgressiveImageGallery.displayName = 'ProgressiveImageGallery';

ProgressiveImageGallery.propTypes = {
  images: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    src: PropTypes.string.isRequired,
    alt: PropTypes.string.isRequired,
    width: PropTypes.number,
    height: PropTypes.number,
    blurDataURL: PropTypes.string
  })),
  columns: PropTypes.number,
  gap: PropTypes.string
};

export default ProgressiveImage;
