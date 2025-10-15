/**
 * Feature Flag Context for managing feature toggles across the application
 */

import React, { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';
import Logger from '../utils/logger-simple';

const FeatureFlagContext = createContext();

/**
 * Feature Flag Provider Component
 * Manages feature flags state and provides them to child components
 */
export const FeatureFlagProvider = ({ children }) => {
  const [featureFlags, setFeatureFlags] = useState({
    // Core Features
    TICKETS: true,
    KNOWLEDGE_BASE: true,
    LIVE_CHAT: true,
    NOTIFICATIONS: true,
    
    // Advanced Features
    AI_SUGGESTIONS: true,
    REAL_TIME_UPDATES: true,
    MOBILE_OPTIMIZATION: true,
    DARK_MODE: false,
    
    // Performance Features
    LAZY_LOADING: true,
    CODE_SPLITTING: true,
    SERVICE_WORKER: true,
    PERFORMANCE_MONITORING: true,
    
    // Communication Features
    VIDEO_CALLS: true,
    SCREEN_SHARING: true,
    FILE_SHARING: true,
    
    // Analytics Features
    USAGE_ANALYTICS: true,
    PERFORMANCE_ANALYTICS: true,
    ERROR_TRACKING: true,
    
    // Security Features
    TWO_FACTOR_AUTH: true,
    SESSION_TIMEOUT: true,
    SECURE_UPLOADS: true,
    
    // Experimental Features
    BETA_FEATURES: false,
    EXPERIMENTAL_UI: false,
    ADVANCED_SEARCH: true,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Fetch feature flags from backend API
   */
  const fetchFeatureFlags = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try to fetch from backend API
      const response = await fetch('/api/v1/features/flags/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setFeatureFlags(prevFlags => ({
          ...prevFlags,
          ...data.features,
        }));
        Logger.info('Feature flags loaded from backend:', data.features);
      } else {
        Logger.warn('Failed to fetch feature flags from backend, using defaults');
        // Use environment-specific defaults
        const envFlags = getEnvironmentFeatureFlags();
        setFeatureFlags(prevFlags => ({
          ...prevFlags,
          ...envFlags,
        }));
      }
    } catch (err) {
      Logger.error('Error fetching feature flags:', err);
      setError(err);
      // Use environment-specific defaults on error
      const envFlags = getEnvironmentFeatureFlags();
      setFeatureFlags(prevFlags => ({
        ...prevFlags,
        ...envFlags,
      }));
    } finally {
      setLoading(false);
    }
  };

  /**
   * Get environment-specific feature flags
   */
  const getEnvironmentFeatureFlags = () => {
    const env = process.env.NODE_ENV;
    
    switch (env) {
      case 'development':
        return {
          BETA_FEATURES: true,
          EXPERIMENTAL_UI: true,
          PERFORMANCE_MONITORING: true,
          DEBUG_MODE: true,
        };
      case 'staging':
        return {
          BETA_FEATURES: true,
          EXPERIMENTAL_UI: false,
          PERFORMANCE_MONITORING: true,
          DEBUG_MODE: false,
        };
      case 'production':
        return {
          BETA_FEATURES: false,
          EXPERIMENTAL_UI: false,
          PERFORMANCE_MONITORING: true,
          DEBUG_MODE: false,
        };
      default:
        return {};
    }
  };

  /**
   * Update a specific feature flag - Memoized to prevent unnecessary re-renders
   */
  const updateFeatureFlag = useCallback((flagName, value) => {
    setFeatureFlags(prevFlags => ({
      ...prevFlags,
      [flagName]: value,
    }));
    Logger.info(`Feature flag updated: ${flagName} = ${value}`);
  }, []);

  /**
   * Update multiple feature flags - Memoized to prevent unnecessary re-renders
   */
  const updateFeatureFlags = useCallback((flags) => {
    setFeatureFlags(prevFlags => ({
      ...prevFlags,
      ...flags,
    }));
    Logger.info('Multiple feature flags updated:', flags);
  }, []);

  /**
   * Reset feature flags to defaults - Memoized to prevent unnecessary re-renders
   */
  const resetFeatureFlags = useCallback(() => {
    const defaultFlags = {
      TICKETS: true,
      KNOWLEDGE_BASE: true,
      LIVE_CHAT: true,
      NOTIFICATIONS: true,
      AI_SUGGESTIONS: true,
      REAL_TIME_UPDATES: true,
      MOBILE_OPTIMIZATION: true,
      DARK_MODE: false,
      LAZY_LOADING: true,
      CODE_SPLITTING: true,
      SERVICE_WORKER: true,
      PERFORMANCE_MONITORING: true,
      VIDEO_CALLS: true,
      SCREEN_SHARING: true,
      FILE_SHARING: true,
      USAGE_ANALYTICS: true,
      PERFORMANCE_ANALYTICS: true,
      ERROR_TRACKING: true,
      TWO_FACTOR_AUTH: true,
      SESSION_TIMEOUT: true,
      SECURE_UPLOADS: true,
      BETA_FEATURES: false,
      EXPERIMENTAL_UI: false,
      ADVANCED_SEARCH: true,
    };
    
    setFeatureFlags(defaultFlags);
    Logger.info('Feature flags reset to defaults');
  }, []);

  /**
   * Get feature flag value - Memoized to prevent unnecessary re-renders
   */
  const getFeatureFlag = useCallback((flagName) => {
    return featureFlags[flagName] || false;
  }, [featureFlags]);

  /**
   * Check if feature is enabled - Memoized to prevent unnecessary re-renders
   */
  const isFeatureEnabled = useCallback((flagName) => {
    return Boolean(featureFlags[flagName]);
  }, [featureFlags]);

  /**
   * Get all feature flags - Memoized to prevent unnecessary re-renders
   */
  const getAllFeatureFlags = useCallback(() => {
    return { ...featureFlags };
  }, [featureFlags]);

  /**
   * Get feature flags by category - Memoized to prevent unnecessary re-renders
   */
  const getFeatureFlagsByCategory = useCallback((category) => {
    const categories = {
      core: ['TICKETS', 'KNOWLEDGE_BASE', 'LIVE_CHAT', 'NOTIFICATIONS'],
      advanced: ['AI_SUGGESTIONS', 'REAL_TIME_UPDATES', 'MOBILE_OPTIMIZATION'],
      performance: ['LAZY_LOADING', 'CODE_SPLITTING', 'SERVICE_WORKER', 'PERFORMANCE_MONITORING'],
      communication: ['VIDEO_CALLS', 'SCREEN_SHARING', 'FILE_SHARING'],
      analytics: ['USAGE_ANALYTICS', 'PERFORMANCE_ANALYTICS', 'ERROR_TRACKING'],
      security: ['TWO_FACTOR_AUTH', 'SESSION_TIMEOUT', 'SECURE_UPLOADS'],
      experimental: ['BETA_FEATURES', 'EXPERIMENTAL_UI', 'ADVANCED_SEARCH'],
    };

    const categoryFlags = categories[category] || [];
    return categoryFlags.reduce((acc, flag) => {
      acc[flag] = featureFlags[flag];
      return acc;
    }, {});
  }, [featureFlags]);

  // Load feature flags on mount
  useEffect(() => {
    fetchFeatureFlags();
  }, []);

  // Memoize the context value to prevent unnecessary re-renders
  const value = useMemo(() => ({
    featureFlags,
    loading,
    error,
    updateFeatureFlag,
    updateFeatureFlags,
    resetFeatureFlags,
    getFeatureFlag,
    isFeatureEnabled,
    getAllFeatureFlags,
    getFeatureFlagsByCategory,
    fetchFeatureFlags,
  }), [
    featureFlags,
    loading,
    error,
    updateFeatureFlag,
    updateFeatureFlags,
    resetFeatureFlags,
    getFeatureFlag,
    isFeatureEnabled,
    getAllFeatureFlags,
    getFeatureFlagsByCategory,
    fetchFeatureFlags
  ]);

  return (
    <FeatureFlagContext.Provider value={value}>
      {children}
    </FeatureFlagContext.Provider>
  );
};

/**
 * Hook to use feature flags
 */
export const useFeatureFlag = (flagName) => {
  const context = useContext(FeatureFlagContext);
  
  if (!context) {
    throw new Error('useFeatureFlag must be used within a FeatureFlagProvider');
  }

  return {
    isEnabled: context.isFeatureEnabled(flagName),
    value: context.getFeatureFlag(flagName),
    update: (value) => context.updateFeatureFlag(flagName, value),
  };
};

/**
 * Hook to use multiple feature flags
 */
export const useFeatureFlags = (flagNames = []) => {
  const context = useContext(FeatureFlagContext);
  
  if (!context) {
    throw new Error('useFeatureFlags must be used within a FeatureFlagProvider');
  }

  if (flagNames.length === 0) {
    return {
      flags: context.getAllFeatureFlags(),
      loading: context.loading,
      error: context.error,
      update: context.updateFeatureFlags,
      reset: context.resetFeatureFlags,
    };
  }

  const flags = flagNames.reduce((acc, flagName) => {
    acc[flagName] = {
      isEnabled: context.isFeatureEnabled(flagName),
      value: context.getFeatureFlag(flagName),
      update: (value) => context.updateFeatureFlag(flagName, value),
    };
    return acc;
  }, {});

  return {
    flags,
    loading: context.loading,
    error: context.error,
  };
};

/**
 * Hook to use feature flags by category
 */
export const useFeatureFlagsByCategory = (category) => {
  const context = useContext(FeatureFlagContext);
  
  if (!context) {
    throw new Error('useFeatureFlagsByCategory must be used within a FeatureFlagProvider');
  }

  return {
    flags: context.getFeatureFlagsByCategory(category),
    loading: context.loading,
    error: context.error,
  };
};

export default FeatureFlagContext;
