import React, { useState, useCallback, memo } from 'react';
import PropTypes from 'prop-types';
import { useDebouncedCallback } from '../hooks/useDebounce';

/**
 * Debounced search input component with advanced features
 * @param {Object} props - Component props
 */
const DebouncedSearchInput = memo(({
  onSearch,
  placeholder = 'Search...',
  delay = 300,
  minLength = 2,
  maxLength = 100,
  className = '',
  disabled = false,
  loading = false,
  clearable = true,
  showResultsCount = false,
  resultsCount = 0,
  ...props
}) => {
  const [value, setValue] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  // Advanced debounced search with options
  const debouncedSearch = useDebouncedCallback(
    async (searchValue) => {
      if (searchValue.length >= minLength) {
        setIsSearching(true);
        try {
          await onSearch(searchValue);
        } catch (error) {
          console.error('Search error:', error);
        } finally {
          setIsSearching(false);
        }
      }
    },
    delay,
    {
      leading: false,
      trailing: true,
      maxWait: 2000 // Maximum 2 seconds wait
    }
  );

  // Handle input change
  const handleChange = useCallback((e) => {
    const newValue = e.target.value;
    
    // Enforce max length
    if (newValue.length <= maxLength) {
      setValue(newValue);
      debouncedSearch(newValue);
    }
  }, [debouncedSearch, maxLength]);

  // Handle clear
  const handleClear = useCallback(() => {
    setValue('');
    onSearch('');
  }, [onSearch]);

  // Handle submit (Enter key)
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (value.length >= minLength) {
        debouncedSearch(value);
      }
    }
  }, [value, debouncedSearch, minLength]);

  return (
    <div className={`debounced-search-input ${className}`}>
      <div className="relative">
        <input
          type="text"
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          maxLength={maxLength}
          className={`
            w-full px-4 py-2 pr-20 border border-gray-300 rounded-lg
            focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            disabled:bg-gray-100 disabled:cursor-not-allowed
            ${isSearching || loading ? 'bg-blue-50' : ''}
          `}
          {...props}
        />
        
        {/* Search icon */}
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
          {isSearching || loading ? (
            <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          ) : (
            <svg className="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          )}
          
          {/* Clear button */}
          {clearable && value && (
            <button
              onClick={handleClear}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              type="button"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>
      
      {/* Results count */}
      {showResultsCount && value.length >= minLength && (
        <div className="mt-2 text-sm text-gray-500">
          {isSearching ? 'Searching...' : `${resultsCount} results found`}
        </div>
      )}
      
      {/* Character count */}
      {value.length > 0 && (
        <div className="mt-1 text-xs text-gray-400 text-right">
          {value.length}/{maxLength}
        </div>
      )}
    </div>
  );
});

DebouncedSearchInput.propTypes = {
  onSearch: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  delay: PropTypes.number,
  minLength: PropTypes.number,
  maxLength: PropTypes.number,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  loading: PropTypes.bool,
  clearable: PropTypes.bool,
  showResultsCount: PropTypes.bool,
  resultsCount: PropTypes.number
};

DebouncedSearchInput.displayName = 'DebouncedSearchInput';

export default DebouncedSearchInput;
