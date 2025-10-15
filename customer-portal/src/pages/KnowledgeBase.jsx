import React, { useState, useEffect, memo, useCallback, useMemo } from 'react';
import PropTypes from 'prop-types';
import Logger from '../utils/logger';
import { useDebounce, useDebouncedCallback } from '../hooks/useDebounce';
import DebouncedSearchInput from '../components/DebouncedSearchInput';

/**
 * Knowledge base page component
 * @param {Object} props - Component props
 */
const KnowledgeBase = ({ user }) => {
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  
  // Debounce search query to prevent excessive API calls
  const debouncedSearchQuery = useDebounce(searchQuery, 300);
  
  // Advanced debounced search callback
  const debouncedSearch = useDebouncedCallback(
    async (query) => {
      if (query.trim()) {
        await handleSearch(query);
      } else {
        // Reset to all articles if search is empty
        fetchKnowledgeBase();
      }
    },
    300,
    {
      leading: false,
      trailing: true,
      maxWait: 2000
    }
  );

  useEffect(() => {
    fetchKnowledgeBase();
  }, []);

  /**
   * Fetch knowledge base data
   */
  const fetchKnowledgeBase = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      Logger.apiRequest('GET', '/api/v1/knowledge-base/');
      
      const response = await fetch('/api/v1/knowledge-base/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      Logger.apiResponse('GET', '/api/v1/knowledge-base/', response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setArticles(data.articles || []);
      setCategories(data.categories || []);
      
      Logger.info('Knowledge base loaded successfully', {
        articlesCount: data.articles?.length || 0,
        categoriesCount: data.categories?.length || 0
      });
      
    } catch (error) {
      Logger.error('Failed to load knowledge base:', error, {
        status: error?.response?.status
      });
      setError('Failed to load knowledge base');
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Handle search with debouncing
   */
  const handleSearch = useCallback(async (query) => {
    if (!query.trim()) return;

    try {
      setLoading(true);
      
      Logger.apiRequest('GET', `/api/v1/knowledge-base/search/?q=${encodeURIComponent(query)}`);
      
      const response = await fetch(`/api/v1/knowledge-base/search/?q=${encodeURIComponent(query)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      Logger.apiResponse('GET', `/api/v1/knowledge-base/search/?q=${encodeURIComponent(query)}`, response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setArticles(data.results || []);
      
      Logger.info('Knowledge base search completed', {
        query: query,
        resultsCount: data.results?.length || 0
      });
      
      Logger.userAction('knowledge_base_search', {
        query: query,
        resultsCount: data.results?.length || 0
      });
      
    } catch (error) {
      Logger.error('Knowledge base search failed:', error, {
        query: query,
        status: error?.response?.status
      });
      setError('Search failed');
    } finally {
      setLoading(false);
    }
  }, []);

  // Trigger search when debounced query changes
  useEffect(() => {
    if (debouncedSearchQuery.trim()) {
      handleSearch(debouncedSearchQuery);
    }
  }, [debouncedSearchQuery, handleSearch]);

  /**
   * Filter articles by category - memoized for performance
   */
  const filteredArticles = useMemo(() => {
    return articles.filter(article => {
      if (selectedCategory && article.category !== selectedCategory) {
        return false;
      }
      return true;
    });
  }, [articles, selectedCategory]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">
          <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Knowledge Base</h3>
        <p className="text-gray-500 mb-4">{error}</p>
        <button
          onClick={fetchKnowledgeBase}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Knowledge Base
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Find answers to common questions and solutions
          </p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <form className="space-y-4">
            <div className="flex space-x-4">
              <div className="flex-1">
                <DebouncedSearchInput
                  onSearch={debouncedSearch}
                  placeholder="Search articles..."
                  delay={300}
                  minLength={2}
                  maxLength={100}
                  showResultsCount={true}
                  resultsCount={filteredArticles.length}
                  className="w-full"
                />
              </div>
            </div>
          </form>

          {/* Category Filter */}
          {categories.length > 0 && (
            <div className="mt-4">
              <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Category
              </label>
              <select
                id="category"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
              >
                <option value="">All Categories</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Articles List */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {searchQuery ? `Search Results for "${searchQuery}"` : 'All Articles'}
          </h3>
          
          {filteredArticles.length === 0 ? (
            <div className="text-center py-8">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No articles found</h3>
              <p className="mt-1 text-sm text-gray-500">
                {searchQuery ? 'Try a different search term.' : 'No articles are available yet.'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredArticles.map((article) => (
                <div key={article.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="text-lg font-medium text-gray-900 mb-2">
                        {article.title}
                      </h4>
                      <p className="text-gray-600 mb-3">
                        {article.summary || article.content?.substring(0, 150) + '...'}
                      </p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>Category: {article.category?.name || 'Uncategorized'}</span>
                        <span>Views: {article.view_count || 0}</span>
                        <span>Updated: {new Date(article.updated_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="ml-4 flex-shrink-0">
                      <button className="text-blue-600 hover:text-blue-500 font-medium">
                        Read More
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

KnowledgeBase.propTypes = {
  user: PropTypes.shape({
    id: PropTypes.number,
    first_name: PropTypes.string,
    last_name: PropTypes.string,
    email: PropTypes.string,
  }),
};

KnowledgeBase.defaultProps = {
  user: null,
};

KnowledgeBase.displayName = 'KnowledgeBase';

export default memo(KnowledgeBase);
