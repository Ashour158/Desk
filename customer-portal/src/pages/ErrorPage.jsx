import React from 'react';
import { useRouteError } from 'react-router-dom';

/**
 * Error page component for handling application errors
 */
const ErrorPage = () => {
  const error = useRouteError();

  return (
    <div className="error-page" data-testid="error-page">
      <div className="error-content">
        <h1>Oops! Something went wrong</h1>
        <p>We're sorry, but something unexpected happened.</p>
        {error && (
          <details>
            <summary>Error Details</summary>
            <pre>{error.message || error}</pre>
          </details>
        )}
        <button onClick={() => window.location.reload()}>
          Try Again
        </button>
      </div>
    </div>
  );
};

export default ErrorPage;
