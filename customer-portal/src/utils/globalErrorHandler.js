/**
 * Global Error Handler for comprehensive error management
 * Handles unhandled errors, promise rejections, and provides centralized error reporting
 */

import Logger from './logger';
import errorReportingService from './errorReporting';

/**
 * Global error handler configuration
 */
const ERROR_HANDLER_CONFIG = {
  // Error reporting settings
  enableErrorReporting: true,
  enableConsoleLogging: process.env.NODE_ENV === 'development',
  enableUserNotifications: true,
  
  // Retry settings
  maxRetryAttempts: 3,
  retryDelay: 1000,
  
  // Error categorization
  errorCategories: {
    NETWORK: 'network',
    VALIDATION: 'validation',
    AUTHENTICATION: 'authentication',
    AUTHORIZATION: 'authorization',
    SERVER: 'server',
    CLIENT: 'client',
    UNKNOWN: 'unknown'
  },
  
  // Error severity levels
  severityLevels: {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
    CRITICAL: 'critical'
  }
};

/**
 * Error categorization utility
 */
class ErrorCategorizer {
  /**
   * Categorize error based on type and context
   * @param {Error} error - The error to categorize
   * @param {Object} context - Additional context
   * @returns {Object} Error category and severity
   */
  static categorize(error, context = {}) {
    let category = ERROR_HANDLER_CONFIG.errorCategories.UNKNOWN;
    let severity = ERROR_HANDLER_CONFIG.severityLevels.MEDIUM;
    
    // Network errors
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      category = ERROR_HANDLER_CONFIG.errorCategories.NETWORK;
      severity = ERROR_HANDLER_CONFIG.severityLevels.MEDIUM;
    }
    
    // HTTP errors
    if (error.message.includes('HTTP error')) {
      const statusCode = this.extractStatusCode(error.message);
      if (statusCode >= 400 && statusCode < 500) {
        category = ERROR_HANDLER_CONFIG.errorCategories.CLIENT;
        severity = ERROR_HANDLER_CONFIG.severityLevels.MEDIUM;
      } else if (statusCode >= 500) {
        category = ERROR_HANDLER_CONFIG.errorCategories.SERVER;
        severity = ERROR_HANDLER_CONFIG.severityLevels.HIGH;
      }
    }
    
    // Authentication errors
    if (error.message.includes('401') || error.message.includes('Unauthorized')) {
      category = ERROR_HANDLER_CONFIG.errorCategories.AUTHENTICATION;
      severity = ERROR_HANDLER_CONFIG.severityLevels.HIGH;
    }
    
    // Authorization errors
    if (error.message.includes('403') || error.message.includes('Forbidden')) {
      category = ERROR_HANDLER_CONFIG.errorCategories.AUTHORIZATION;
      severity = ERROR_HANDLER_CONFIG.severityLevels.HIGH;
    }
    
    // Validation errors
    if (error.message.includes('validation') || error.message.includes('ValidationError')) {
      category = ERROR_HANDLER_CONFIG.errorCategories.VALIDATION;
      severity = ERROR_HANDLER_CONFIG.severityLevels.LOW;
    }
    
    // Critical errors
    if (error.name === 'ReferenceError' || error.name === 'TypeError') {
      severity = ERROR_HANDLER_CONFIG.severityLevels.CRITICAL;
    }
    
    return { category, severity };
  }
  
  /**
   * Extract status code from error message
   * @param {string} message - Error message
   * @returns {number|null} Status code
   */
  static extractStatusCode(message) {
    const match = message.match(/status: (\d+)/);
    return match ? parseInt(match[1]) : null;
  }
}

/**
 * Error recovery strategies
 */
class ErrorRecoveryStrategies {
  /**
   * Network error recovery
   * @param {Error} error - The error
   * @param {Object} context - Error context
   * @returns {Promise<boolean>} Recovery success
   */
  static async handleNetworkError(error, context) {
    try {
      // Check if online
      if (!navigator.onLine) {
        Logger.warn('Network error: Device is offline');
        return false;
      }
      
      // Try to reconnect
      const response = await fetch('/api/health/', { method: 'HEAD' });
      if (response.ok) {
        Logger.info('Network recovery: Connection restored');
        return true;
      }
      
      return false;
    } catch (recoveryError) {
      Logger.error('Network recovery failed:', recoveryError);
      return false;
    }
  }
  
  /**
   * Authentication error recovery
   * @param {Error} error - The error
   * @param {Object} context - Error context
   * @returns {Promise<boolean>} Recovery success
   */
  static async handleAuthenticationError(error, context) {
    try {
      // Clear invalid tokens
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      
      // Redirect to login
      window.location.href = '/login';
      
      Logger.info('Authentication error: Redirected to login');
      return true;
    } catch (recoveryError) {
      Logger.error('Authentication recovery failed:', recoveryError);
      return false;
    }
  }
  
  /**
   * Generic error recovery
   * @param {Error} error - The error
   * @param {Object} context - Error context
   * @returns {Promise<boolean>} Recovery success
   */
  static async handleGenericError(error, context) {
    try {
      // Show user-friendly message
      if (ERROR_HANDLER_CONFIG.enableUserNotifications) {
        this.showUserNotification(error, context);
      }
      
      return false; // Generic errors typically can't be auto-recovered
    } catch (recoveryError) {
      Logger.error('Generic recovery failed:', recoveryError);
      return false;
    }
  }
  
  /**
   * Show user notification for error
   * @param {Error} error - The error
   * @param {Object} context - Error context
   */
  static showUserNotification(error, context) {
    // Import notification system
    import('../components/NotificationSystem').then(({ useNotifications }) => {
      // This would need to be called from a component context
      // For now, we'll use a simple alert
      const message = this.getUserFriendlyMessage(error, context);
      alert(message);
    });
  }
  
  /**
   * Get user-friendly error message
   * @param {Error} error - The error
   * @param {Object} context - Error context
   * @returns {string} User-friendly message
   */
  static getUserFriendlyMessage(error, context) {
    const { category } = ErrorCategorizer.categorize(error, context);
    
    switch (category) {
      case ERROR_HANDLER_CONFIG.errorCategories.NETWORK:
        return 'Network connection issue. Please check your internet connection and try again.';
      case ERROR_HANDLER_CONFIG.errorCategories.AUTHENTICATION:
        return 'Your session has expired. Please log in again.';
      case ERROR_HANDLER_CONFIG.errorCategories.AUTHORIZATION:
        return 'You do not have permission to perform this action.';
      case ERROR_HANDLER_CONFIG.errorCategories.VALIDATION:
        return 'Please check your input and try again.';
      case ERROR_HANDLER_CONFIG.errorCategories.SERVER:
        return 'Server error occurred. Please try again later.';
      default:
        return 'An unexpected error occurred. Please try again.';
    }
  }
}

/**
 * Global error handler class
 */
class GlobalErrorHandler {
  constructor() {
    this.errorCount = 0;
    this.maxErrors = 10; // Max errors before showing critical error
    this.errorHistory = [];
    this.isInitialized = false;
  }
  
  /**
   * Initialize global error handling
   */
  initialize() {
    if (this.isInitialized) {
      return;
    }
    
    // Handle uncaught errors
    window.addEventListener('error', this.handleError.bind(this));
    
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', this.handlePromiseRejection.bind(this));
    
    // Handle resource loading errors
    window.addEventListener('error', this.handleResourceError.bind(this), true);
    
    // Handle network errors
    window.addEventListener('offline', this.handleOffline.bind(this));
    window.addEventListener('online', this.handleOnline.bind(this));
    
    this.isInitialized = true;
    Logger.info('Global error handler initialized');
  }
  
  /**
   * Handle JavaScript errors
   * @param {ErrorEvent} event - Error event
   */
  async handleError(event) {
    const error = event.error || new Error(event.message);
    const context = {
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      type: 'javascript_error',
      timestamp: new Date().toISOString()
    };
    
    await this.processError(error, context);
  }
  
  /**
   * Handle unhandled promise rejections
   * @param {PromiseRejectionEvent} event - Promise rejection event
   */
  async handlePromiseRejection(event) {
    const error = event.reason instanceof Error ? event.reason : new Error(String(event.reason));
    const context = {
      type: 'promise_rejection',
      timestamp: new Date().toISOString()
    };
    
    await this.processError(error, context);
  }
  
  /**
   * Handle resource loading errors
   * @param {ErrorEvent} event - Error event
   */
  async handleResourceError(event) {
    if (event.target !== window) {
      const error = new Error(`Resource loading error: ${event.target.src || event.target.href}`);
      const context = {
        type: 'resource_error',
        element: event.target.tagName,
        src: event.target.src || event.target.href,
        timestamp: new Date().toISOString()
      };
      
      await this.processError(error, context);
    }
  }
  
  /**
   * Handle offline event
   * @param {Event} event - Offline event
   */
  handleOffline(event) {
    Logger.warn('Device went offline');
    
    // Show offline notification
    if (ERROR_HANDLER_CONFIG.enableUserNotifications) {
      this.showOfflineNotification();
    }
  }
  
  /**
   * Handle online event
   * @param {Event} event - Online event
   */
  handleOnline(event) {
    Logger.info('Device came back online');
    
    // Hide offline notification
    this.hideOfflineNotification();
    
    // Retry failed requests
    this.retryFailedRequests();
  }
  
  /**
   * Process error with categorization and recovery
   * @param {Error} error - The error
   * @param {Object} context - Error context
   */
  async processError(error, context) {
    try {
      // Categorize error
      const { category, severity } = ErrorCategorizer.categorize(error, context);
      
      // Add to error history
      this.errorHistory.push({
        error,
        context,
        category,
        severity,
        timestamp: new Date().toISOString()
      });
      
      // Limit error history
      if (this.errorHistory.length > 100) {
        this.errorHistory = this.errorHistory.slice(-50);
      }
      
      // Increment error count
      this.errorCount++;
      
      // Log error
      if (ERROR_HANDLER_CONFIG.enableConsoleLogging) {
        Logger.error('Global error caught:', error, context);
      }
      
      // Report error
      if (ERROR_HANDLER_CONFIG.enableErrorReporting) {
        await this.reportError(error, context, category, severity);
      }
      
      // Attempt recovery
      const recovered = await this.attemptRecovery(error, context, category);
      
      if (!recovered) {
        // Show user notification
        if (ERROR_HANDLER_CONFIG.enableUserNotifications) {
          this.showErrorNotification(error, context, category);
        }
      }
      
      // Check for critical error threshold
      if (this.errorCount >= this.maxErrors) {
        this.handleCriticalErrorThreshold();
      }
      
    } catch (processingError) {
      Logger.error('Error processing failed:', processingError);
    }
  }
  
  /**
   * Attempt error recovery
   * @param {Error} error - The error
   * @param {Object} context - Error context
   * @param {string} category - Error category
   * @returns {Promise<boolean>} Recovery success
   */
  async attemptRecovery(error, context, category) {
    try {
      switch (category) {
        case ERROR_HANDLER_CONFIG.errorCategories.NETWORK:
          return await ErrorRecoveryStrategies.handleNetworkError(error, context);
        case ERROR_HANDLER_CONFIG.errorCategories.AUTHENTICATION:
          return await ErrorRecoveryStrategies.handleAuthenticationError(error, context);
        default:
          return await ErrorRecoveryStrategies.handleGenericError(error, context);
      }
    } catch (recoveryError) {
      Logger.error('Recovery attempt failed:', recoveryError);
      return false;
    }
  }
  
  /**
   * Report error to external service
   * @param {Error} error - The error
   * @param {Object} context - Error context
   * @param {string} category - Error category
   * @param {string} severity - Error severity
   */
  async reportError(error, context, category, severity) {
    try {
      const errorReport = {
        message: error.message,
        stack: error.stack,
        category,
        severity,
        context,
        userAgent: navigator.userAgent,
        url: window.location.href,
        timestamp: new Date().toISOString()
      };
      
      // Report to error service
      if (errorReportingService) {
        await errorReportingService.reportError(errorReport);
      }
      
    } catch (reportingError) {
      Logger.error('Error reporting failed:', reportingError);
    }
  }
  
  /**
   * Show error notification to user
   * @param {Error} error - The error
   * @param {Object} context - Error context
   * @param {string} category - Error category
   */
  showErrorNotification(error, context, category) {
    const message = ErrorRecoveryStrategies.getUserFriendlyMessage(error, context);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'global-error-notification';
    notification.innerHTML = `
      <div class="error-notification-content">
        <i class="fas fa-exclamation-triangle"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
    `;
    
    // Add styles
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #f8d7da;
      color: #721c24;
      padding: 15px;
      border-radius: 5px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
      z-index: 10000;
      max-width: 400px;
    `;
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 5000);
  }
  
  /**
   * Show offline notification
   */
  showOfflineNotification() {
    const notification = document.createElement('div');
    notification.id = 'offline-notification';
    notification.innerHTML = `
      <div class="offline-notification-content">
        <i class="fas fa-wifi"></i>
        <span>You are offline. Some features may not work.</span>
      </div>
    `;
    
    notification.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      background: #ffc107;
      color: #856404;
      padding: 10px;
      text-align: center;
      z-index: 10001;
    `;
    
    document.body.appendChild(notification);
  }
  
  /**
   * Hide offline notification
   */
  hideOfflineNotification() {
    const notification = document.getElementById('offline-notification');
    if (notification) {
      notification.remove();
    }
  }
  
  /**
   * Retry failed requests
   */
  retryFailedRequests() {
    // This would integrate with the network optimizer
    Logger.info('Retrying failed requests...');
    // Implementation would depend on the request queue system
  }
  
  /**
   * Handle critical error threshold
   */
  handleCriticalErrorThreshold() {
    Logger.error('Critical error threshold reached');
    
    // Show critical error modal
    const modal = document.createElement('div');
    modal.className = 'critical-error-modal';
    modal.innerHTML = `
      <div class="modal-content">
        <h2>Critical Error</h2>
        <p>Too many errors have occurred. Please refresh the page.</p>
        <button onclick="window.location.reload()">Refresh Page</button>
      </div>
    `;
    
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.8);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10002;
    `;
    
    document.body.appendChild(modal);
  }
  
  /**
   * Get error statistics
   * @returns {Object} Error statistics
   */
  getErrorStatistics() {
    return {
      totalErrors: this.errorCount,
      errorHistory: this.errorHistory,
      isInitialized: this.isInitialized,
      maxErrors: this.maxErrors
    };
  }
  
  /**
   * Reset error count
   */
  resetErrorCount() {
    this.errorCount = 0;
    this.errorHistory = [];
    Logger.info('Error count reset');
  }
}

// Create global instance
const globalErrorHandler = new GlobalErrorHandler();

// Export for use in other modules
export { globalErrorHandler, ErrorCategorizer, ErrorRecoveryStrategies };

// Auto-initialize when module is loaded
if (typeof window !== 'undefined') {
  globalErrorHandler.initialize();
}

export default globalErrorHandler;
