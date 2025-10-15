import React, { useState, useEffect, useMemo, useCallback, memo } from 'react';
import PropTypes from 'prop-types';

/**
 * AVIF Image Component with Progressive Loading
 * Supports AVIF format with fallback to WebP and traditional formats
 */
const AVIFImage = memo(({ 
  src,
  alt,
  width,
  height,
  className = '',
  style = {},
  loading = 'lazy',
  placeholder = true,
  progressive = true,
  quality = 80,
  onLoad,
  onError,
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [currentSrc, setCurrentSrc] = useState(null);
  const [supportsAVIF, setSupportsAVIF] = useState(false);
  const [supportsWebP, setSupportsWebP] = useState(false);

  // Check format support
  useEffect(() => {
    const checkFormatSupport = async () => {
      // Check AVIF support
      const avifSupported = await checkAVIFSupport();
      setSupportsAVIF(avifSupported);

      // Check WebP support
      const webpSupported = await checkWebPSupport();
      setSupportsWebP(webpSupported);
    };

    checkFormatSupport();
  }, []);

  // Generate optimized image sources
  const imageSources = useMemo(() => {
    if (!src) return [];

    const baseSrc = src.replace(/\.[^/.]+$/, '');
    const sources = [];

    // AVIF format (best compression)
    if (supportsAVIF) {
      sources.push({
        srcset: `${baseSrc}.avif`,
        type: 'image/avif',
        quality: quality
      });
    }

    // WebP format (good compression)
    if (supportsWebP) {
      sources.push({
        srcset: `${baseSrc}.webp`,
        type: 'image/webp',
        quality: quality
      });
    }

    // Fallback to original format
    sources.push({
      srcset: src,
      type: getMimeType(src),
      quality: quality
    });

    return sources;
  }, [src, supportsAVIF, supportsWebP, quality]);

  // Get the best available source
  const bestSource = useMemo(() => {
    if (imageSources.length === 0) return src;
    
    // Return the first supported format
    return imageSources[0].srcset;
  }, [imageSources, src]);

  // Progressive loading
  const [progressiveSrc, setProgressiveSrc] = useState(null);
  const [isProgressiveLoaded, setIsProgressiveLoaded] = useState(false);

  useEffect(() => {
    if (progressive && bestSource) {
      // Load low-quality placeholder first
      const placeholderSrc = generatePlaceholder(bestSource, 10);
      setProgressiveSrc(placeholderSrc);
      
      // Then load full quality
      const img = new Image();
      img.onload = () => {
        setCurrentSrc(bestSource);
        setIsProgressiveLoaded(true);
      };
      img.src = bestSource;
    } else {
      setCurrentSrc(bestSource);
    }
  }, [bestSource, progressive]);

  // Handle image load
  const handleLoad = useCallback(() => {
    setIsLoaded(true);
    setHasError(false);
    if (onLoad) {
      onLoad();
    }
  }, [onLoad]);

  // Handle image error
  const handleError = useCallback(() => {
    setHasError(true);
    setIsLoaded(false);
    if (onError) {
      onError();
    }
  }, [onError]);

  // Generate responsive sizes
  const responsiveSizes = useMemo(() => {
    if (!width || !height) return '100vw';
    
    const sizes = [
      '(max-width: 768px) 100vw',
      '(max-width: 1024px) 50vw',
      '25vw'
    ];
    
    return sizes.join(', ');
  }, [width, height]);

  // Generate srcset for responsive images
  const generateSrcSet = useCallback((baseSrc, format) => {
    const sizes = [1, 2, 3]; // 1x, 2x, 3x densities
    return sizes.map(size => {
      const scaledWidth = width ? width * size : undefined;
      const scaledHeight = height ? height * size : undefined;
      return `${baseSrc}?w=${scaledWidth}&h=${scaledHeight}&q=${quality} ${size}x`;
    }).join(', ');
  }, [width, height, quality]);

  return (
    <div 
      className={`avif-image-container ${className}`}
      style={{ 
        position: 'relative',
        width: width || 'auto',
        height: height || 'auto',
        ...style 
      }}
      {...props}
    >
      {/* Progressive loading placeholder */}
      {progressive && progressiveSrc && !isProgressiveLoaded && (
        <img
          src={progressiveSrc}
          alt=""
          className="avif-image-placeholder"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            filter: 'blur(5px)',
            opacity: 0.7
          }}
        />
      )}

      {/* Main image */}
      {currentSrc && (
        <picture>
          {/* AVIF source */}
          {supportsAVIF && (
            <source
              srcSet={generateSrcSet(imageSources[0]?.srcset, 'avif')}
              type="image/avif"
              sizes={responsiveSizes}
            />
          )}
          
          {/* WebP source */}
          {supportsWebP && !supportsAVIF && (
            <source
              srcSet={generateSrcSet(imageSources[1]?.srcset, 'webp')}
              type="image/webp"
              sizes={responsiveSizes}
            />
          )}
          
          {/* Fallback image */}
          <img
            src={currentSrc}
            alt={alt}
            width={width}
            height={height}
            loading={loading}
            onLoad={handleLoad}
            onError={handleError}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: isLoaded ? 1 : 0,
              transition: 'opacity 0.3s ease-in-out'
            }}
            className="avif-image"
          />
        </picture>
      )}

      {/* Loading placeholder */}
      {placeholder && !isLoaded && !hasError && (
        <div className="avif-image-loading">
          <div className="loading-spinner" />
        </div>
      )}

      {/* Error state */}
      {hasError && (
        <div className="avif-image-error">
          <span>Failed to load image</span>
        </div>
      )}

      {/* Format indicator (development only) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="format-indicator">
          {supportsAVIF ? 'AVIF' : supportsWebP ? 'WebP' : 'JPEG/PNG'}
        </div>
      )}
    </div>
  );
});

// Helper functions
const checkAVIFSupport = async () => {
  try {
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    return canvas.toDataURL('image/avif').indexOf('data:image/avif') === 0;
  } catch (error) {
    return false;
  }
};

const checkWebPSupport = async () => {
  try {
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  } catch (error) {
    return false;
  }
};

const getMimeType = (src) => {
  const extension = src.split('.').pop().toLowerCase();
  const mimeTypes = {
    jpg: 'image/jpeg',
    jpeg: 'image/jpeg',
    png: 'image/png',
    gif: 'image/gif',
    webp: 'image/webp',
    avif: 'image/avif'
  };
  return mimeTypes[extension] || 'image/jpeg';
};

const generatePlaceholder = (src, quality) => {
  // Generate a low-quality placeholder
  return `${src}?q=${quality}&w=50&h=50&blur=5`;
};

AVIFImage.propTypes = {
  src: PropTypes.string.isRequired,
  alt: PropTypes.string.isRequired,
  width: PropTypes.number,
  height: PropTypes.number,
  className: PropTypes.string,
  style: PropTypes.object,
  loading: PropTypes.oneOf(['lazy', 'eager']),
  placeholder: PropTypes.bool,
  progressive: PropTypes.bool,
  quality: PropTypes.number,
  onLoad: PropTypes.func,
  onError: PropTypes.func
};

AVIFImage.defaultProps = {
  loading: 'lazy',
  placeholder: true,
  progressive: true,
  quality: 80
};

AVIFImage.displayName = 'AVIFImage';

export default AVIFImage;
