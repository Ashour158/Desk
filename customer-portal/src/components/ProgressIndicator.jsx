import React, { memo, useEffect, useState } from 'react';
import PropTypes from 'prop-types';

/**
 * Progress indicator component for showing loading progress
 * Supports linear, circular, and step-based progress indicators
 */
const ProgressIndicator = memo(({
  type = 'linear',
  progress = 0,
  total = 100,
  size = 'medium',
  color = 'blue',
  showPercentage = true,
  showLabel = false,
  label,
  animated = true,
  className = '',
  ...props
}) => {
  const [displayProgress, setDisplayProgress] = useState(0);

  // Animate progress value
  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => {
        setDisplayProgress(progress);
      }, 100);
      return () => clearTimeout(timer);
    } else {
      setDisplayProgress(progress);
    }
  }, [progress, animated]);

  const percentage = Math.round((displayProgress / total) * 100);
  const clampedPercentage = Math.min(Math.max(percentage, 0), 100);

  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return type === 'circular' ? 'w-8 h-8' : 'h-2';
      case 'large':
        return type === 'circular' ? 'w-16 h-16' : 'h-4';
      default:
        return type === 'circular' ? 'w-12 h-12' : 'h-3';
    }
  };

  const getColorStyles = () => {
    const colorMap = {
      blue: 'bg-blue-600',
      green: 'bg-green-600',
      red: 'bg-red-600',
      yellow: 'bg-yellow-600',
      purple: 'bg-purple-600',
      gray: 'bg-gray-600'
    };
    return colorMap[color] || colorMap.blue;
  };

  const getTextSize = () => {
    switch (size) {
      case 'small':
        return 'text-xs';
      case 'large':
        return 'text-lg';
      default:
        return 'text-sm';
    }
  };

  if (type === 'circular') {
    const radius = size === 'small' ? 16 : size === 'large' ? 32 : 24;
    const circumference = 2 * Math.PI * radius;
    const strokeDasharray = circumference;
    const strokeDashoffset = circumference - (clampedPercentage / 100) * circumference;

    return (
      <div className={`relative ${getSizeStyles()} ${className}`} {...props}>
        <svg
          className="w-full h-full transform -rotate-90"
          viewBox={`0 0 ${radius * 2} ${radius * 2}`}
        >
          {/* Background circle */}
          <circle
            cx={radius}
            cy={radius}
            r={radius - 2}
            stroke="currentColor"
            strokeWidth="4"
            fill="none"
            className="text-gray-200"
          />
          {/* Progress circle */}
          <circle
            cx={radius}
            cy={radius}
            r={radius - 2}
            stroke="currentColor"
            strokeWidth="4"
            fill="none"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            className={`${getColorStyles().replace('bg-', 'text-')} transition-all duration-300 ease-out`}
            strokeLinecap="round"
          />
        </svg>
        
        {/* Percentage text */}
        {showPercentage && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`font-medium ${getTextSize()} text-gray-700`}>
              {clampedPercentage}%
            </span>
          </div>
        )}
        
        {/* Label */}
        {showLabel && label && (
          <div className="mt-2 text-center">
            <span className={`${getTextSize()} text-gray-600`}>
              {label}
            </span>
          </div>
        )}
      </div>
    );
  }

  // Linear progress bar
  return (
    <div className={`w-full ${className}`} {...props}>
      {/* Progress bar container */}
      <div className={`bg-gray-200 rounded-full overflow-hidden ${getSizeStyles()}`}>
        <div
          className={`h-full ${getColorStyles()} transition-all duration-300 ease-out`}
          style={{ width: `${clampedPercentage}%` }}
          role="progressbar"
          aria-valuenow={displayProgress}
          aria-valuemin={0}
          aria-valuemax={total}
          aria-label={label || `Progress: ${clampedPercentage}%`}
        />
      </div>
      
      {/* Label and percentage */}
      {(showLabel || showPercentage) && (
        <div className="flex justify-between items-center mt-2">
          {showLabel && label && (
            <span className={`${getTextSize()} text-gray-600`}>
              {label}
            </span>
          )}
          {showPercentage && (
            <span className={`${getTextSize()} font-medium text-gray-700`}>
              {clampedPercentage}%
            </span>
          )}
        </div>
      )}
    </div>
  );
});

/**
 * Step progress indicator for multi-step processes
 */
export const StepProgress = memo(({
  steps,
  currentStep = 0,
  orientation = 'horizontal',
  size = 'medium',
  className = '',
  ...props
}) => {
  const getStepSize = () => {
    switch (size) {
      case 'small':
        return 'w-6 h-6 text-xs';
      case 'large':
        return 'w-10 h-10 text-lg';
      default:
        return 'w-8 h-8 text-sm';
    }
  };

  const getStepStyles = (index) => {
    if (index < currentStep) {
      return 'bg-green-600 text-white border-green-600';
    } else if (index === currentStep) {
      return 'bg-blue-600 text-white border-blue-600';
    } else {
      return 'bg-white text-gray-400 border-gray-300';
    }
  };

  const getConnectorStyles = (index) => {
    if (index < currentStep) {
      return 'bg-green-600';
    } else {
      return 'bg-gray-300';
    }
  };

  if (orientation === 'vertical') {
    return (
      <div className={`space-y-4 ${className}`} {...props}>
        {steps.map((step, index) => (
          <div key={index} className="flex items-start">
            <div className="flex flex-col items-center">
              <div className={`${getStepSize()} rounded-full border-2 flex items-center justify-center font-medium ${getStepStyles(index)}`}>
                {index < currentStep ? (
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  index + 1
                )}
              </div>
              {index < steps.length - 1 && (
                <div className={`w-0.5 h-8 mt-2 ${getConnectorStyles(index)}`} />
              )}
            </div>
            <div className="ml-4 flex-1">
              <h3 className={`font-medium ${index <= currentStep ? 'text-gray-900' : 'text-gray-400'}`}>
                {step.title}
              </h3>
              {step.description && (
                <p className={`text-sm ${index <= currentStep ? 'text-gray-600' : 'text-gray-400'}`}>
                  {step.description}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Horizontal orientation
  return (
    <div className={`flex items-center ${className}`} {...props}>
      {steps.map((step, index) => (
        <React.Fragment key={index}>
          <div className="flex flex-col items-center">
            <div className={`${getStepSize()} rounded-full border-2 flex items-center justify-center font-medium ${getStepStyles(index)}`}>
              {index < currentStep ? (
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              ) : (
                index + 1
              )}
            </div>
            <div className="mt-2 text-center">
              <h3 className={`font-medium text-sm ${index <= currentStep ? 'text-gray-900' : 'text-gray-400'}`}>
                {step.title}
              </h3>
              {step.description && (
                <p className={`text-xs ${index <= currentStep ? 'text-gray-600' : 'text-gray-400'}`}>
                  {step.description}
                </p>
              )}
            </div>
          </div>
          {index < steps.length - 1 && (
            <div className={`flex-1 h-0.5 mx-4 ${getConnectorStyles(index)}`} />
          )}
        </React.Fragment>
      ))}
    </div>
  );
});

/**
 * Loading spinner with progress
 */
export const LoadingSpinner = memo(({
  size = 'medium',
  color = 'blue',
  text,
  className = '',
  ...props
}) => {
  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return 'w-4 h-4';
      case 'large':
        return 'w-8 h-8';
      default:
        return 'w-6 h-6';
    }
  };

  const getColorStyles = () => {
    const colorMap = {
      blue: 'text-blue-600',
      green: 'text-green-600',
      red: 'text-red-600',
      yellow: 'text-yellow-600',
      purple: 'text-purple-600',
      gray: 'text-gray-600'
    };
    return colorMap[color] || colorMap.blue;
  };

  return (
    <div className={`flex items-center space-x-3 ${className}`} {...props}>
      <div className={`${getSizeStyles()} ${getColorStyles()}`}>
        <svg className="animate-spin" fill="none" viewBox="0 0 24 24">
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      </div>
      {text && (
        <span className="text-sm text-gray-600">
          {text}
        </span>
      )}
    </div>
  );
});

ProgressIndicator.propTypes = {
  type: PropTypes.oneOf(['linear', 'circular']),
  progress: PropTypes.number,
  total: PropTypes.number,
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  color: PropTypes.oneOf(['blue', 'green', 'red', 'yellow', 'purple', 'gray']),
  showPercentage: PropTypes.bool,
  showLabel: PropTypes.bool,
  label: PropTypes.string,
  animated: PropTypes.bool,
  className: PropTypes.string
};

StepProgress.propTypes = {
  steps: PropTypes.arrayOf(PropTypes.shape({
    title: PropTypes.string.isRequired,
    description: PropTypes.string
  })).isRequired,
  currentStep: PropTypes.number,
  orientation: PropTypes.oneOf(['horizontal', 'vertical']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  className: PropTypes.string
};

LoadingSpinner.propTypes = {
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  color: PropTypes.oneOf(['blue', 'green', 'red', 'yellow', 'purple', 'gray']),
  text: PropTypes.string,
  className: PropTypes.string
};

export default ProgressIndicator;
