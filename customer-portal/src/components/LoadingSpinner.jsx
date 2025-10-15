import React, { memo } from 'react';
import PropTypes from 'prop-types';

/**
 * Loading spinner component for lazy loading fallbacks
 * Optimized with memo to prevent unnecessary re-renders
 */
const LoadingSpinner = memo(({ 
  size = 'medium', 
  color = 'primary', 
  text = 'Loading...',
  className = '',
  ...props 
}) => {
  const sizeClasses = {
    small: 'spinner-sm',
    medium: 'spinner-md',
    large: 'spinner-lg'
  };

  const colorClasses = {
    primary: 'spinner-primary',
    secondary: 'spinner-secondary',
    white: 'spinner-white'
  };

  return (
    <div 
      className={`loading-spinner ${sizeClasses[size]} ${colorClasses[color]} ${className}`}
      data-testid="loading-spinner"
      {...props}
    >
      <div className="spinner-container">
        <div className="spinner" />
        {text && <div className="spinner-text">{text}</div>}
      </div>
    </div>
  );
});

LoadingSpinner.propTypes = {
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  color: PropTypes.oneOf(['primary', 'secondary', 'white']),
  text: PropTypes.string,
  className: PropTypes.string
};

LoadingSpinner.displayName = 'LoadingSpinner';

export default LoadingSpinner;
