/**
 * Feature Flag Analytics Dashboard Component
 */

import React, { useState, useEffect } from 'react';
import { useFeatureFlags } from '../contexts/FeatureFlagContext';
import Logger from '../utils/logger-simple';

const FeatureFlagAnalytics = () => {
  const { flags, loading, error } = useFeatureFlags();
  const [analytics, setAnalytics] = useState({
    totalFlags: 0,
    enabledFlags: 0,
    disabledFlags: 0,
    categories: {},
    usage: {},
    health: {},
  });
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [timeRange, setTimeRange] = useState('7d');

  useEffect(() => {
    if (!loading && !error) {
      calculateAnalytics();
    }
  }, [flags, loading, error]);

  const calculateAnalytics = () => {
    const totalFlags = Object.keys(flags).length;
    const enabledFlags = Object.values(flags).filter(flag => flag.isEnabled).length;
    const disabledFlags = totalFlags - enabledFlags;

    // Categorize flags
    const categories = {
      core: ['TICKETS', 'KNOWLEDGE_BASE', 'LIVE_CHAT', 'NOTIFICATIONS'],
      advanced: ['AI_SUGGESTIONS', 'REAL_TIME_UPDATES', 'MOBILE_OPTIMIZATION'],
      performance: ['LAZY_LOADING', 'CODE_SPLITTING', 'SERVICE_WORKER', 'PERFORMANCE_MONITORING'],
      communication: ['VIDEO_CALLS', 'SCREEN_SHARING', 'FILE_SHARING'],
      analytics: ['USAGE_ANALYTICS', 'PERFORMANCE_ANALYTICS', 'ERROR_TRACKING'],
      security: ['TWO_FACTOR_AUTH', 'SESSION_TIMEOUT', 'SECURE_UPLOADS'],
      experimental: ['BETA_FEATURES', 'EXPERIMENTAL_UI', 'ADVANCED_SEARCH'],
    };

    const categoryStats = {};
    Object.keys(categories).forEach(category => {
      const categoryFlags = categories[category];
      const enabled = categoryFlags.filter(flag => flags[flag]?.isEnabled).length;
      categoryStats[category] = {
        total: categoryFlags.length,
        enabled,
        disabled: categoryFlags.length - enabled,
        percentage: categoryFlags.length > 0 ? (enabled / categoryFlags.length) * 100 : 0,
      };
    });

    setAnalytics({
      totalFlags,
      enabledFlags,
      disabledFlags,
      categories: categoryStats,
      usage: calculateUsageStats(),
      health: calculateHealthStats(),
    });
  };

  const calculateUsageStats = () => {
    // Simulate usage data (in real implementation, this would come from API)
    return {
      mostUsed: ['TICKETS', 'KNOWLEDGE_BASE', 'LIVE_CHAT'],
      leastUsed: ['BETA_FEATURES', 'EXPERIMENTAL_UI', 'ADVANCED_SEARCH'],
      totalUsage: 1250,
      averageUsage: 45.2,
    };
  };

  const calculateHealthStats = () => {
    // Simulate health data (in real implementation, this would come from API)
    return {
      healthy: 15,
      degraded: 2,
      unhealthy: 1,
      unknown: 0,
    };
  };

  const getFilteredFlags = () => {
    if (selectedCategory === 'all') {
      return Object.entries(flags);
    }

    const categories = {
      core: ['TICKETS', 'KNOWLEDGE_BASE', 'LIVE_CHAT', 'NOTIFICATIONS'],
      advanced: ['AI_SUGGESTIONS', 'REAL_TIME_UPDATES', 'MOBILE_OPTIMIZATION'],
      performance: ['LAZY_LOADING', 'CODE_SPLITTING', 'SERVICE_WORKER', 'PERFORMANCE_MONITORING'],
      communication: ['VIDEO_CALLS', 'SCREEN_SHARING', 'FILE_SHARING'],
      analytics: ['USAGE_ANALYTICS', 'PERFORMANCE_ANALYTICS', 'ERROR_TRACKING'],
      security: ['TWO_FACTOR_AUTH', 'SESSION_TIMEOUT', 'SECURE_UPLOADS'],
      experimental: ['BETA_FEATURES', 'EXPERIMENTAL_UI', 'ADVANCED_SEARCH'],
    };

    const categoryFlags = categories[selectedCategory] || [];
    return Object.entries(flags).filter(([flagName]) => categoryFlags.includes(flagName));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading feature flag analytics...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error loading analytics</h3>
            <div className="mt-2 text-sm text-red-700">
              {error.message || 'An error occurred while loading feature flag analytics.'}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="feature-flag-analytics">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Feature Flag Analytics</h2>
        <p className="text-gray-600">Monitor and analyze feature flag usage and performance</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Flags</p>
              <p className="text-2xl font-semibold text-gray-900">{analytics.totalFlags}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Enabled</p>
              <p className="text-2xl font-semibold text-green-600">{analytics.enabledFlags}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Disabled</p>
              <p className="text-2xl font-semibold text-red-600">{analytics.disabledFlags}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <svg className="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Health Score</p>
              <p className="text-2xl font-semibold text-yellow-600">
                {analytics.health.healthy + analytics.health.degraded + analytics.health.unhealthy > 0 
                  ? Math.round((analytics.health.healthy / (analytics.health.healthy + analytics.health.degraded + analytics.health.unhealthy)) * 100)
                  : 0}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Categories</option>
            <option value="core">Core Features</option>
            <option value="advanced">Advanced Features</option>
            <option value="performance">Performance</option>
            <option value="communication">Communication</option>
            <option value="analytics">Analytics</option>
            <option value="security">Security</option>
            <option value="experimental">Experimental</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Time Range</label>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="1d">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
        </div>
      </div>

      {/* Category Statistics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Category Breakdown</h3>
          <div className="space-y-4">
            {Object.entries(analytics.categories).map(([category, stats]) => (
              <div key={category} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
                  <span className="text-sm font-medium text-gray-700 capitalize">{category}</span>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-500">{stats.enabled}/{stats.total}</span>
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${stats.percentage}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900">{Math.round(stats.percentage)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Health Status</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm font-medium text-gray-700">Healthy</span>
              </div>
              <span className="text-sm font-medium text-gray-900">{analytics.health.healthy}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-yellow-500 rounded-full mr-3"></div>
                <span className="text-sm font-medium text-gray-700">Degraded</span>
              </div>
              <span className="text-sm font-medium text-gray-900">{analytics.health.degraded}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-red-500 rounded-full mr-3"></div>
                <span className="text-sm font-medium text-gray-700">Unhealthy</span>
              </div>
              <span className="text-sm font-medium text-gray-900">{analytics.health.unhealthy}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Feature Flag List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Feature Flags</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {getFilteredFlags().map(([flagName, flag]) => (
            <div key={flagName} className="px-6 py-4 flex items-center justify-between">
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full mr-3 ${flag.isEnabled ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{flagName}</p>
                  <p className="text-sm text-gray-500">Feature flag for {flagName.toLowerCase().replace(/_/g, ' ')}</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  flag.isEnabled 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {flag.isEnabled ? 'Enabled' : 'Disabled'}
                </span>
                <button
                  onClick={() => flag.update(!flag.isEnabled)}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  Toggle
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FeatureFlagAnalytics;
