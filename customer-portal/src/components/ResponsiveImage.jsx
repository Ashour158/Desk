import React, { useState, useCallback, memo } from 'react';
import PropTypes from 'prop-types';

/**
 * Responsive Image component with accessibility features
 * Supports multiple formats (AVIF, WebP, JPEG) and responsive sizing
 */
const ResponsiveImage = memo(({
  src,
  alt,
  width,
  height,
  className = '',
  loading = 'lazy',
  sizes = '(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw',
  quality = 80,
  placeholder = 'blur',
  onLoad,
  onError,
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isInView, setIsInView] = useState(loading === 'eager');

  /**
   * Generate responsive srcSet for different screen sizes
   */
  const generateSrcSet = useCallback((baseSrc, format = '') => {
    const breakpoints = [320, 640, 768, 1024, 1280, 1920];
    const formatExtension = format ? `.${format}` : '';
    
    return breakpoints
      .map(width => {
        const height = Math.round(width * (height / width));
        const url = new URL(baseSrc, window.location.origin);
        url.searchParams.set('w', width.toString());
        url.searchParams.set('h', height.toString());
        url.searchParams.set('q', quality.toString());
        url.searchParams.set('fit', 'crop');
        
        if (format) {
          url.pathname = url.pathname.replace(/\.(jpg|jpeg|png)$/i, formatExtension);
        }
        
        return `${url.toString()} ${width}w`;
      })
      .join(', ');
  }, [quality, height, width]);

  /**
   * Handle image load
   */
  const handleLoad = useCallback(() => {
    setIsLoaded(true);
    setHasError(false);
    if (onLoad) {
      onLoad();
    }
  }, [onLoad]);

  /**
   * Handle image error
   */
  const handleError = useCallback(() => {
    setHasError(true);
    setIsLoaded(false);
    if (onError) {
      onError();
    }
  }, [onError]);

  /**
   * Intersection Observer for lazy loading
   */
  React.useEffect(() => {
    if (loading === 'lazy' && !isInView) {
      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observer.disconnect();
          }
        },
        { 
          threshold: 0.1,
          rootMargin: '50px'
        }
      );

      const imgElement = document.querySelector(`[data-src="${src}"]`);
      if (imgElement) {
        observer.observe(imgElement);
      }

      return () => observer.disconnect();
    }
  }, [loading, isInView, src]);

  // Generate srcSet for different formats
  const avifSrcSet = generateSrcSet(src, 'avif');
  const webpSrcSet = generateSrcSet(src, 'webp');
  const jpegSrcSet = generateSrcSet(src, 'jpg');

  // Don't render if lazy loading and not in view
  if (loading === 'lazy' && !isInView) {
    return (
      <div 
        className={`bg-gray-200 animate-pulse ${className}`}
        style={{ width, height }}
        data-src={src}
        aria-hidden="true"
      />
    );
  }

  return (
    <picture className={className}>
      {/* AVIF source for modern browsers */}
      <source
        type="image/avif"
        srcSet={avifSrcSet}
        sizes={sizes}
      />
      
      {/* WebP source for good browser support */}
      <source
        type="image/webp"
        srcSet={webpSrcSet}
        sizes={sizes}
      />
      
      {/* Fallback JPEG */}
      <img
        src={src}
        srcSet={jpegSrcSet}
        sizes={sizes}
        alt={alt}
        width={width}
        height={height}
        loading={loading}
        onLoad={handleLoad}
        onError={handleError}
        className={`transition-opacity duration-300 ${
          isLoaded ? 'opacity-100' : 'opacity-0'
        } ${hasError ? 'opacity-50' : ''}`}
        style={{
          aspectRatio: width && height ? `${width}/${height}` : undefined
        }}
        {...props}
      />
      
      {/* Loading placeholder */}
      {!isLoaded && !hasError && (
        <div 
          className="absolute inset-0 bg-gray-200 animate-pulse flex items-center justify-center"
          aria-hidden="true"
        >
          <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
          </svg>
        </div>
      )}
      
      {/* Error state */}
      {hasError && (
        <div 
          className="absolute inset-0 bg-gray-100 flex items-center justify-center"
          role="img"
          aria-label="Image failed to load"
        >
          <div className="text-center text-gray-500">
            <svg className="w-8 h-8 mx-auto mb-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
            </svg>
            <p className="text-sm">Image unavailable</p>
          </div>
        </div>
      )}
    </picture>
  );
});

ResponsiveImage.propTypes = {
  src: PropTypes.string.isRequired,
  alt: PropTypes.string.isRequired,
  width: PropTypes.number,
  height: PropTypes.number,
  className: PropTypes.string,
  loading: PropTypes.oneOf(['lazy', 'eager']),
  sizes: PropTypes.string,
  quality: PropTypes.number,
  placeholder: PropTypes.oneOf(['blur', 'empty']),
  onLoad: PropTypes.func,
  onError: PropTypes.func
};

ResponsiveImage.displayName = 'ResponsiveImage';

export default ResponsiveImage;
