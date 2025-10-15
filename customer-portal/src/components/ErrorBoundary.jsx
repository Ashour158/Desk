import React from 'react';
import PropTypes from 'prop-types';
import Logger from '../utils/logger';

/**
 * Error Boundary Component for React Error Handling
 * Catches JavaScript errors anywhere in the child component tree
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Generate unique error ID
    const errorId = `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Update state with error details
    this.setState({
      error,
      errorInfo,
      errorId
    });

    // Log error details
    Logger.error('Error Boundary caught an error:', {
      error: error.toString(),
      errorInfo,
      errorId,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString()
    });

    // Report error to external service
    this.reportError(error, errorInfo, errorId);
  }

  reportError = (error, errorInfo, errorId) => {
    try {
      const errorReport = {
        errorId,
        message: error.toString(),
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        userId: this.getCurrentUserId(),
        sessionId: this.getSessionId(),
        severity: this.getErrorSeverity(error),
        tags: this.getErrorTags(error, errorInfo)
      };

      // Log to console for development
      console.error('Error Report:', errorReport);

      // Send to external service
      this.sendToErrorReportingService(errorReport);
      
    } catch (reportingError) {
      Logger.error('Failed to report error:', reportingError);
    }
  };

  getErrorSeverity = (error) => {
    // Determine error severity based on error type
    if (error.name === 'ChunkLoadError' || error.name === 'Loading chunk failed') {
      return 'warning'; // Network issues, not critical
    }
    if (error.message.includes('Network Error') || error.message.includes('fetch')) {
      return 'error'; // Network errors
    }
    if (error.message.includes('TypeError') || error.message.includes('ReferenceError')) {
      return 'fatal'; // Code errors are critical
    }
    return 'error'; // Default to error
  };

  getErrorTags = (error, errorInfo) => {
    return {
      errorType: error.name,
      component: this.getComponentName(errorInfo),
      environment: process.env.NODE_ENV,
      version: process.env.REACT_APP_VERSION || 'unknown'
    };
  };

  getComponentName = (errorInfo) => {
    // Extract component name from component stack
    const stack = errorInfo.componentStack;
    const match = stack.match(/in\s+(\w+)/);
    return match ? match[1] : 'Unknown';
  };

  sendToErrorReportingService = async (errorReport) => {
    try {
      // Check if Sentry is available
      if (window.Sentry) {
        window.Sentry.captureException(new Error(errorReport.message), {
          extra: errorReport,
          tags: errorReport.tags,
          level: errorReport.severity
        });
        return;
      }

      // Fallback: Send to custom error reporting endpoint
      if (process.env.REACT_APP_ERROR_REPORTING_URL) {
        await fetch(process.env.REACT_APP_ERROR_REPORTING_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.getAuthToken()}`
          },
          body: JSON.stringify(errorReport)
        });
        return;
      }

      // Final fallback: Store in localStorage for later retrieval
      this.storeErrorLocally(errorReport);
      
    } catch (serviceError) {
      Logger.error('Failed to send error to reporting service:', serviceError);
      // Store locally as backup
      this.storeErrorLocally(errorReport);
    }
  };

  getAuthToken = () => {
    try {
      return localStorage.getItem('authToken');
    } catch {
      return null;
    }
  };

  storeErrorLocally = (errorReport) => {
    try {
      const storedErrors = JSON.parse(localStorage.getItem('errorReports') || '[]');
      storedErrors.push(errorReport);
      
      // Keep only last 10 errors
      if (storedErrors.length > 10) {
        storedErrors.splice(0, storedErrors.length - 10);
      }
      
      localStorage.setItem('errorReports', JSON.stringify(storedErrors));
    } catch (storageError) {
      Logger.error('Failed to store error locally:', storageError);
    }
  };

  getCurrentUserId = () => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      return user.id || 'anonymous';
    } catch {
      return 'anonymous';
    }
  };

  getSessionId = () => {
    try {
      return localStorage.getItem('sessionId') || 'unknown';
    } catch {
      return 'unknown';
    }
  };

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.handleRetry);
      }

      // Default fallback UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
            <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full mb-4">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            
            <div className="text-center">
              <h1 className="text-lg font-medium text-gray-900 mb-2">
                Something went wrong
              </h1>
              <p className="text-sm text-gray-500 mb-4">
                We're sorry, but something unexpected happened. Our team has been notified.
              </p>
              
              {process.env.NODE_ENV === 'development' && (
                <details className="mb-4 text-left">
                  <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-800">
                    Error Details (Development)
                  </summary>
                  <div className="mt-2 p-3 bg-gray-100 rounded text-xs font-mono">
                    <div><strong>Error ID:</strong> {this.state.errorId}</div>
                    <div><strong>Error:</strong> {this.state.error?.toString()}</div>
                    <div><strong>Stack:</strong></div>
                    <pre className="whitespace-pre-wrap text-xs">
                      {this.state.error?.stack}
                    </pre>
                    <div><strong>Component Stack:</strong></div>
                    <pre className="whitespace-pre-wrap text-xs">
                      {this.state.errorInfo?.componentStack}
                    </pre>
                  </div>
                </details>
              )}
              
              <div className="flex space-x-3">
                <button
                  onClick={this.handleRetry}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Try Again
                </button>
                <button
                  onClick={this.handleReload}
                  className="flex-1 bg-gray-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  Reload Page
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired,
  fallback: PropTypes.func
};

export default ErrorBoundary;