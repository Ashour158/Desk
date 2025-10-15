/**
 * Lazy Enhanced Lazy Image Component
 * Provides enhanced lazy loading with progressive image loading
 */

import React, { Suspense, lazy } from 'react';
import PropTypes from 'prop-types';

// Lazy load the enhanced lazy image component
const EnhancedLazyImage = lazy(() => import('./EnhancedLazyImage'));

/**
 * Lazy Enhanced Lazy Image Wrapper
 * Wraps the EnhancedLazyImage with Suspense for lazy loading
 */
const LazyEnhancedLazyImage = ({ 
  src, 
  alt, 
  className = '', 
  placeholder = null,
  fallback = null,
  ...props 
}) => {
  return (
    <Suspense fallback={fallback || placeholder || <div className="animate-pulse bg-gray-200 rounded" />}>
      <EnhancedLazyImage
        src={src}
        alt={alt}
        className={className}
        {...props}
      />
    </Suspense>
  );
};

LazyEnhancedLazyImage.propTypes = {
  src: PropTypes.string.isRequired,
  alt: PropTypes.string.isRequired,
  className: PropTypes.string,
  placeholder: PropTypes.node,
  fallback: PropTypes.node,
};

export default LazyEnhancedLazyImage;
