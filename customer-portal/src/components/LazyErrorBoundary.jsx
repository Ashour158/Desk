/**
 * Lazy Error Boundary Component
 * Provides error boundary functionality with lazy loading
 */

import React, { Suspense, lazy } from 'react';
import PropTypes from 'prop-types';

// Lazy load the main ErrorBoundary component
const ErrorBoundary = lazy(() => import('./ErrorBoundary'));

/**
 * Lazy Error Boundary Wrapper
 * Wraps the ErrorBoundary with Suspense for lazy loading
 */
const LazyErrorBoundary = ({ children, fallback = null, ...props }) => {
  return (
    <Suspense fallback={fallback || <div>Loading error boundary...</div>}>
      <ErrorBoundary {...props}>
        {children}
      </ErrorBoundary>
    </Suspense>
  );
};

LazyErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired,
  fallback: PropTypes.node,
};

export default LazyErrorBoundary;
