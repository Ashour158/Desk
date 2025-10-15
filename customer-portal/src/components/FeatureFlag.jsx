/**
 * Feature Flag Components for conditional rendering
 */

import React from 'react';
import { useFeatureFlag, useFeatureFlags } from '../contexts/FeatureFlagContext';

/**
 * Feature Flag Wrapper Component
 * Conditionally renders children based on feature flag
 */
export const FeatureFlag = ({ 
  flag, 
  children, 
  fallback = null, 
  inverse = false,
  loading = null,
  error = null 
}) => {
  const { isEnabled, value } = useFeatureFlag(flag);

  // Show loading state
  if (loading !== null) {
    return loading;
  }

  // Show error state
  if (error !== null) {
    return error;
  }

  // Check if feature should be shown
  const shouldShow = inverse ? !isEnabled : isEnabled;

  return shouldShow ? children : fallback;
};

/**
 * Multiple Feature Flag Wrapper
 * Shows content only if ALL specified flags are enabled
 */
export const AllFeatureFlags = ({ 
  flags, 
  children, 
  fallback = null,
  inverse = false 
}) => {
  const { flags: flagStates } = useFeatureFlags(flags);
  
  const allEnabled = flags.every(flag => flagStates[flag]?.isEnabled);
  const shouldShow = inverse ? !allEnabled : allEnabled;

  return shouldShow ? children : fallback;
};

/**
 * Any Feature Flag Wrapper
 * Shows content if ANY of the specified flags are enabled
 */
export const AnyFeatureFlag = ({ 
  flags, 
  children, 
  fallback = null,
  inverse = false 
}) => {
  const { flags: flagStates } = useFeatureFlags(flags);
  
  const anyEnabled = flags.some(flag => flagStates[flag]?.isEnabled);
  const shouldShow = inverse ? !anyEnabled : anyEnabled;

  return shouldShow ? children : fallback;
};

/**
 * Feature Flag Toggle Component
 * Renders different content based on feature flag state
 */
export const FeatureFlagToggle = ({ 
  flag, 
  enabled, 
  disabled, 
  loading = null,
  error = null 
}) => {
  const { isEnabled } = useFeatureFlag(flag);

  if (loading !== null) {
    return loading;
  }

  if (error !== null) {
    return error;
  }

  return isEnabled ? enabled : disabled;
};

/**
 * Feature Flag Debug Component
 * Shows feature flag information for debugging
 */
export const FeatureFlagDebug = ({ flag, showValue = true, showType = true }) => {
  const { isEnabled, value } = useFeatureFlag(flag);

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div className="feature-flag-debug" style={{
      position: 'fixed',
      bottom: '10px',
      right: '10px',
      background: 'rgba(0,0,0,0.8)',
      color: 'white',
      padding: '8px',
      borderRadius: '4px',
      fontSize: '12px',
      zIndex: 9999,
    }}>
      <div><strong>Flag:</strong> {flag}</div>
      <div><strong>Enabled:</strong> {isEnabled ? 'Yes' : 'No'}</div>
      {showValue && <div><strong>Value:</strong> {String(value)}</div>}
      {showType && <div><strong>Type:</strong> {typeof value}</div>}
    </div>
  );
};

/**
 * Feature Flag Status Component
 * Shows the status of a feature flag
 */
export const FeatureFlagStatus = ({ flag, showLabel = true }) => {
  const { isEnabled } = useFeatureFlag(flag);

  return (
    <span className={`feature-flag-status ${isEnabled ? 'enabled' : 'disabled'}`}>
      {showLabel && `${flag}: `}
      <span className={`status-indicator ${isEnabled ? 'enabled' : 'disabled'}`}>
        {isEnabled ? '✓' : '✗'}
      </span>
    </span>
  );
};

/**
 * Feature Flag List Component
 * Shows a list of feature flags and their status
 */
export const FeatureFlagList = ({ flags = [], showValues = false }) => {
  const { flags: flagStates, loading, error } = useFeatureFlags(flags);

  if (loading) {
    return <div>Loading feature flags...</div>;
  }

  if (error) {
    return <div>Error loading feature flags: {error.message}</div>;
  }

  return (
    <div className="feature-flag-list">
      {flags.map(flag => (
        <div key={flag} className="feature-flag-item">
          <FeatureFlagStatus flag={flag} />
          {showValues && (
            <span className="feature-flag-value">
              (Value: {String(flagStates[flag]?.value)})
            </span>
          )}
        </div>
      ))}
    </div>
  );
};

export default FeatureFlag;
