import React, { memo } from 'react';
import PropTypes from 'prop-types';

/**
 * Skeleton loader component for loading states
 * Provides visual feedback while content is loading
 */
const SkeletonLoader = memo(({ 
  variant = 'text', 
  width, 
  height, 
  className = '',
  animation = 'pulse',
  ...props 
}) => {
  const getSkeletonStyles = () => {
    const baseStyles = 'bg-gray-200 rounded';
    const animationStyles = {
      pulse: 'animate-pulse',
      wave: 'animate-wave',
      shimmer: 'animate-shimmer'
    };
    
    return `${baseStyles} ${animationStyles[animation] || animationStyles.pulse}`;
  };

  const getVariantStyles = () => {
    switch (variant) {
      case 'text':
        return 'h-4 w-full';
      case 'title':
        return 'h-6 w-3/4';
      case 'subtitle':
        return 'h-5 w-1/2';
      case 'avatar':
        return 'rounded-full w-10 h-10';
      case 'button':
        return 'h-10 w-24';
      case 'card':
        return 'h-32 w-full';
      case 'image':
        return 'h-48 w-full';
      case 'table':
        return 'h-12 w-full';
      case 'list':
        return 'h-16 w-full';
      default:
        return 'h-4 w-full';
    }
  };

  const style = {
    width: width || undefined,
    height: height || undefined
  };

  return (
    <div
      className={`${getSkeletonStyles()} ${getVariantStyles()} ${className}`}
      style={style}
      aria-hidden="true"
      {...props}
    />
  );
});

/**
 * Skeleton card component for card layouts
 */
export const SkeletonCard = memo(({ className = '', ...props }) => (
  <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`} {...props}>
    <div className="flex items-center space-x-4 mb-4">
      <SkeletonLoader variant="avatar" />
      <div className="flex-1">
        <SkeletonLoader variant="title" className="mb-2" />
        <SkeletonLoader variant="subtitle" />
      </div>
    </div>
    <SkeletonLoader variant="text" className="mb-2" />
    <SkeletonLoader variant="text" className="w-3/4" />
  </div>
));

/**
 * Skeleton table component for table layouts
 */
export const SkeletonTable = memo(({ rows = 5, columns = 4, className = '', ...props }) => (
  <div className={`bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden ${className}`} {...props}>
    {/* Table header */}
    <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
      <div className="flex space-x-4">
        {Array.from({ length: columns }).map((_, index) => (
          <SkeletonLoader key={index} variant="text" className="flex-1" />
        ))}
      </div>
    </div>
    
    {/* Table rows */}
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <div key={rowIndex} className="px-6 py-4 border-b border-gray-100 last:border-b-0">
        <div className="flex space-x-4">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <SkeletonLoader key={colIndex} variant="text" className="flex-1" />
          ))}
        </div>
      </div>
    ))}
  </div>
));

/**
 * Skeleton list component for list layouts
 */
export const SkeletonList = memo(({ items = 5, className = '', ...props }) => (
  <div className={`space-y-4 ${className}`} {...props}>
    {Array.from({ length: items }).map((_, index) => (
      <div key={index} className="flex items-center space-x-4 p-4 bg-white rounded-lg shadow-sm border border-gray-200">
        <SkeletonLoader variant="avatar" />
        <div className="flex-1">
          <SkeletonLoader variant="title" className="mb-2" />
          <SkeletonLoader variant="text" className="w-2/3" />
        </div>
        <SkeletonLoader variant="button" />
      </div>
    ))}
  </div>
));

/**
 * Skeleton form component for form layouts
 */
export const SkeletonForm = memo(({ fields = 4, className = '', ...props }) => (
  <div className={`space-y-6 ${className}`} {...props}>
    {Array.from({ length: fields }).map((_, index) => (
      <div key={index} className="space-y-2">
        <SkeletonLoader variant="text" className="w-1/4" />
        <SkeletonLoader variant="text" className="w-full h-10" />
      </div>
    ))}
    <div className="flex space-x-4">
      <SkeletonLoader variant="button" className="w-24" />
      <SkeletonLoader variant="button" className="w-24" />
    </div>
  </div>
));

/**
 * Skeleton dashboard component for dashboard layouts
 */
export const SkeletonDashboard = memo(({ className = '', ...props }) => (
  <div className={`space-y-6 ${className}`} {...props}>
    {/* Header */}
    <div className="flex items-center justify-between">
      <SkeletonLoader variant="title" className="w-64" />
      <SkeletonLoader variant="button" className="w-32" />
    </div>
    
    {/* Stats cards */}
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {Array.from({ length: 4 }).map((_, index) => (
        <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <SkeletonLoader variant="text" className="w-1/2 mb-2" />
          <SkeletonLoader variant="title" className="w-3/4" />
        </div>
      ))}
    </div>
    
    {/* Main content */}
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <SkeletonCard />
      <SkeletonCard />
    </div>
  </div>
));

SkeletonLoader.propTypes = {
  variant: PropTypes.oneOf([
    'text', 'title', 'subtitle', 'avatar', 'button', 'card', 'image', 'table', 'list'
  ]),
  width: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  height: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  className: PropTypes.string,
  animation: PropTypes.oneOf(['pulse', 'wave', 'shimmer'])
};

SkeletonCard.propTypes = {
  className: PropTypes.string
};

SkeletonTable.propTypes = {
  rows: PropTypes.number,
  columns: PropTypes.number,
  className: PropTypes.string
};

SkeletonList.propTypes = {
  items: PropTypes.number,
  className: PropTypes.string
};

SkeletonForm.propTypes = {
  fields: PropTypes.number,
  className: PropTypes.string
};

SkeletonDashboard.propTypes = {
  className: PropTypes.string
};

export default SkeletonLoader;
