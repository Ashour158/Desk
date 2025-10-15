import React, { memo } from 'react';
import PropTypes from 'prop-types';

/**
 * Empty state component for when there's no data to display
 * Provides helpful messaging and actions for users
 */
const EmptyState = memo(({
  icon,
  title,
  description,
  action,
  secondaryAction,
  image,
  className = '',
  size = 'medium',
  ...props
}) => {
  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return 'py-8';
      case 'large':
        return 'py-16';
      default:
        return 'py-12';
    }
  };

  const getIconSize = () => {
    switch (size) {
      case 'small':
        return 'w-12 h-12';
      case 'large':
        return 'w-20 h-20';
      default:
        return 'w-16 h-16';
    }
  };

  return (
    <div 
      className={`text-center ${getSizeStyles()} ${className}`}
      role="status"
      aria-live="polite"
      {...props}
    >
      <div className="max-w-md mx-auto">
        {/* Icon or Image */}
        {image ? (
          <img
            src={image}
            alt=""
            className={`mx-auto ${getIconSize()} mb-4`}
            aria-hidden="true"
          />
        ) : icon ? (
          <div className={`mx-auto ${getIconSize()} mb-4 text-gray-400`} aria-hidden="true">
            {icon}
          </div>
        ) : (
          <div className={`mx-auto ${getIconSize()} mb-4 text-gray-400`} aria-hidden="true">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        )}

        {/* Title */}
        {title && (
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {title}
          </h3>
        )}

        {/* Description */}
        {description && (
          <p className="text-gray-500 mb-6">
            {description}
          </p>
        )}

        {/* Actions */}
        {(action || secondaryAction) && (
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            {action && (
              <button
                onClick={action.onClick}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
                aria-label={action.ariaLabel || action.label}
              >
                {action.icon && (
                  <span className="mr-2" aria-hidden="true">
                    {action.icon}
                  </span>
                )}
                {action.label}
              </button>
            )}
            
            {secondaryAction && (
              <button
                onClick={secondaryAction.onClick}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
                aria-label={secondaryAction.ariaLabel || secondaryAction.label}
              >
                {secondaryAction.icon && (
                  <span className="mr-2" aria-hidden="true">
                    {secondaryAction.icon}
                  </span>
                )}
                {secondaryAction.label}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
});

/**
 * Empty state for no tickets
 */
export const EmptyTickets = memo(({ onCreateTicket, onRefresh, className = '' }) => (
  <EmptyState
    icon={
      <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
    }
    title="No tickets found"
    description="You don't have any support tickets yet. Create your first ticket to get started."
    action={{
      label: 'Create Ticket',
      onClick: onCreateTicket,
      icon: (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      )
    }}
    secondaryAction={{
      label: 'Refresh',
      onClick: onRefresh,
      icon: (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      )
    }}
    className={className}
  />
));

/**
 * Empty state for no search results
 */
export const EmptySearchResults = memo(({ query, onClearSearch, className = '' }) => (
  <EmptyState
    icon={
      <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    }
    title="No results found"
    description={`We couldn't find any results for "${query}". Try adjusting your search terms.`}
    action={{
      label: 'Clear Search',
      onClick: onClearSearch,
      icon: (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      )
    }}
    className={className}
  />
));

/**
 * Empty state for no knowledge base articles
 */
export const EmptyKnowledgeBase = memo(({ onRefresh, className = '' }) => (
  <EmptyState
    icon={
      <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 6.253v13m0-13C10.832 5.477 9.45 5.25 8 5.25c-1.45 0-2.832.227-4 1.253v13C5.168 18.477 6.55 18.75 8 18.75c1.45 0 2.832-.227 4-1.253v-13C10.832 5.477 9.45 5.25 8 5.25c-1.45 0-2.832.227-4 1.253v13C5.168 18.477 6.55 18.75 8 18.75c1.45 0 2.832-.227 4-1.253v-13z" />
      </svg>
    }
    title="No articles available"
    description="There are no knowledge base articles available at the moment. Check back later or contact support."
    action={{
      label: 'Contact Support',
      onClick: () => window.location.href = '/new-ticket',
      icon: (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      )
    }}
    secondaryAction={{
      label: 'Refresh',
      onClick: onRefresh,
      icon: (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      )
    }}
    className={className}
  />
));

/**
 * Empty state for error states
 */
export const EmptyError = memo(({ title, description, onRetry, onGoHome, className = '' }) => (
  <EmptyState
    icon={
      <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" className="text-red-400">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
    }
    title={title || "Something went wrong"}
    description={description || "We encountered an error while loading this page. Please try again."}
    action={{
      label: 'Try Again',
      onClick: onRetry,
      icon: (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      )
    }}
    secondaryAction={{
      label: 'Go Home',
      onClick: onGoHome,
      icon: (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      )
    }}
    className={className}
  />
));

EmptyState.propTypes = {
  icon: PropTypes.node,
  title: PropTypes.string,
  description: PropTypes.string,
  action: PropTypes.shape({
    label: PropTypes.string.isRequired,
    onClick: PropTypes.func.isRequired,
    icon: PropTypes.node,
    ariaLabel: PropTypes.string
  }),
  secondaryAction: PropTypes.shape({
    label: PropTypes.string.isRequired,
    onClick: PropTypes.func.isRequired,
    icon: PropTypes.node,
    ariaLabel: PropTypes.string
  }),
  image: PropTypes.string,
  className: PropTypes.string,
  size: PropTypes.oneOf(['small', 'medium', 'large'])
};

EmptyTickets.propTypes = {
  onCreateTicket: PropTypes.func.isRequired,
  onRefresh: PropTypes.func,
  className: PropTypes.string
};

EmptySearchResults.propTypes = {
  query: PropTypes.string.isRequired,
  onClearSearch: PropTypes.func.isRequired,
  className: PropTypes.string
};

EmptyKnowledgeBase.propTypes = {
  onRefresh: PropTypes.func,
  className: PropTypes.string
};

EmptyError.propTypes = {
  title: PropTypes.string,
  description: PropTypes.string,
  onRetry: PropTypes.func,
  onGoHome: PropTypes.func,
  className: PropTypes.string
};

export default EmptyState;
