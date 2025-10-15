/**
 * Feature Flag Management Component
 * Allows administrators to manage feature flags
 */

import React, { useState, useEffect } from 'react';
import { useFeatureFlags } from '../contexts/FeatureFlagContext';
import Logger from '../utils/logger-simple';

const FeatureFlagManagement = () => {
  const { flags, loading, error, updateFeatureFlag, updateFeatureFlags, resetFeatureFlags } = useFeatureFlags();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [bulkActions, setBulkActions] = useState({
    selected: [],
    action: '',
  });

  const categories = {
    core: ['TICKETS', 'KNOWLEDGE_BASE', 'LIVE_CHAT', 'NOTIFICATIONS'],
    advanced: ['AI_SUGGESTIONS', 'REAL_TIME_UPDATES', 'MOBILE_OPTIMIZATION'],
    performance: ['LAZY_LOADING', 'CODE_SPLITTING', 'SERVICE_WORKER', 'PERFORMANCE_MONITORING'],
    communication: ['VIDEO_CALLS', 'SCREEN_SHARING', 'FILE_SHARING'],
    analytics: ['USAGE_ANALYTICS', 'PERFORMANCE_ANALYTICS', 'ERROR_TRACKING'],
    security: ['TWO_FACTOR_AUTH', 'SESSION_TIMEOUT', 'SECURE_UPLOADS'],
    experimental: ['BETA_FEATURES', 'EXPERIMENTAL_UI', 'ADVANCED_SEARCH'],
  };

  const getFilteredFlags = () => {
    let filtered = Object.entries(flags);

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(([flagName]) =>
        flagName.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      const categoryFlags = categories[selectedCategory] || [];
      filtered = filtered.filter(([flagName]) => categoryFlags.includes(flagName));
    }

    return filtered;
  };

  const handleToggleFlag = async (flagName, currentValue) => {
    try {
      await updateFeatureFlag(flagName, !currentValue);
      Logger.info(`Feature flag ${flagName} toggled to ${!currentValue}`);
    } catch (err) {
      Logger.error(`Error toggling feature flag ${flagName}:`, err);
    }
  };

  const handleBulkAction = async () => {
    if (bulkActions.selected.length === 0 || !bulkActions.action) {
      return;
    }

    try {
      const updates = {};
      bulkActions.selected.forEach(flagName => {
        updates[flagName] = bulkActions.action === 'enable';
      });

      await updateFeatureFlags(updates);
      Logger.info(`Bulk ${bulkActions.action} applied to ${bulkActions.selected.length} flags`);
      
      setBulkActions({ selected: [], action: '' });
    } catch (err) {
      Logger.error('Error applying bulk action:', err);
    }
  };

  const handleSelectAll = () => {
    const filteredFlags = getFilteredFlags();
    const allSelected = filteredFlags.every(([flagName]) => bulkActions.selected.includes(flagName));
    
    if (allSelected) {
      setBulkActions(prev => ({ ...prev, selected: [] }));
    } else {
      setBulkActions(prev => ({
        ...prev,
        selected: filteredFlags.map(([flagName]) => flagName),
      }));
    }
  };

  const handleSelectFlag = (flagName) => {
    setBulkActions(prev => ({
      ...prev,
      selected: prev.selected.includes(flagName)
        ? prev.selected.filter(name => name !== flagName)
        : [...prev.selected, flagName],
    }));
  };

  const handleResetFlags = async () => {
    if (window.confirm('Are you sure you want to reset all feature flags to their default values?')) {
      try {
        await resetFeatureFlags();
        Logger.info('All feature flags reset to defaults');
      } catch (err) {
        Logger.error('Error resetting feature flags:', err);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading feature flags...</span>
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
            <h3 className="text-sm font-medium text-red-800">Error loading feature flags</h3>
            <div className="mt-2 text-sm text-red-700">
              {error.message || 'An error occurred while loading feature flags.'}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const filteredFlags = getFilteredFlags();

  return (
    <div className="feature-flag-management">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Feature Flag Management</h2>
        <p className="text-gray-600">Manage and configure feature flags for your application</p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search feature flags..."
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              {Object.keys(categories).map(category => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)} Features
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Bulk Actions</label>
            <div className="flex space-x-2">
              <select
                value={bulkActions.action}
                onChange={(e) => setBulkActions(prev => ({ ...prev, action: e.target.value }))}
                className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Action</option>
                <option value="enable">Enable Selected</option>
                <option value="disable">Disable Selected</option>
              </select>
              <button
                onClick={handleBulkAction}
                disabled={bulkActions.selected.length === 0 || !bulkActions.action}
                className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Apply
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Actions</label>
            <div className="flex space-x-2">
              <button
                onClick={handleResetFlags}
                className="px-4 py-2 bg-red-600 text-white rounded-md text-sm font-medium hover:bg-red-700"
              >
                Reset All
              </button>
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="px-4 py-2 bg-gray-600 text-white rounded-md text-sm font-medium hover:bg-gray-700"
              >
                {showAdvanced ? 'Hide' : 'Show'} Advanced
              </button>
            </div>
          </div>
        </div>

        {/* Bulk Selection */}
        {bulkActions.selected.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-blue-800">
                {bulkActions.selected.length} flag(s) selected
              </span>
              <button
                onClick={() => setBulkActions({ selected: [], action: '' })}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Clear Selection
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Feature Flags Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              Feature Flags ({filteredFlags.length})
            </h3>
            <button
              onClick={handleSelectAll}
              className="text-sm font-medium text-blue-600 hover:text-blue-800"
            >
              {filteredFlags.every(([flagName]) => bulkActions.selected.includes(flagName)) ? 'Deselect All' : 'Select All'}
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <input
                    type="checkbox"
                    checked={filteredFlags.length > 0 && filteredFlags.every(([flagName]) => bulkActions.selected.includes(flagName))}
                    onChange={handleSelectAll}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Flag Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredFlags.map(([flagName, flag]) => {
                const category = Object.keys(categories).find(cat => 
                  categories[cat].includes(flagName)
                ) || 'other';

                return (
                  <tr key={flagName} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        checked={bulkActions.selected.includes(flagName)}
                        onChange={() => handleSelectFlag(flagName)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{flagName}</div>
                        <div className="text-sm text-gray-500">
                          {flagName.toLowerCase().replace(/_/g, ' ')}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        flag.isEnabled 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {flag.isEnabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {category.charAt(0).toUpperCase() + category.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleToggleFlag(flagName, flag.isEnabled)}
                        className={`${
                          flag.isEnabled 
                            ? 'text-red-600 hover:text-red-800' 
                            : 'text-green-600 hover:text-green-800'
                        }`}
                      >
                        {flag.isEnabled ? 'Disable' : 'Enable'}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {filteredFlags.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No feature flags found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search or filter criteria.
            </p>
          </div>
        )}
      </div>

      {/* Advanced Settings */}
      {showAdvanced && (
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Advanced Settings</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Environment</label>
              <select className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="development">Development</option>
                <option value="staging">Staging</option>
                <option value="production">Production</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Cache TTL (seconds)</label>
              <input
                type="number"
                defaultValue="300"
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FeatureFlagManagement;
