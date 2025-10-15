/**
 * Centralized logging service for the customer portal
 * Replaces console.log statements with proper logging
 */

// import errorReporting from './errorReporting';

class Logger {
  /**
   * Log levels
   */
  static get LEVELS() {
    return {
      ERROR: 'error',
      WARN: 'warn',
      INFO: 'info',
      DEBUG: 'debug'
    };
  }

  /**
   * Current log level
   */
  static get currentLevel() {
    return process.env.NODE_ENV === 'production' ? Logger.LEVELS.ERROR : Logger.LEVELS.DEBUG;
  }

  /**
   * Check if a log level should be output
   * @param {string} level - Log level to check
   * @returns {boolean} Whether to output the log
   */
  static shouldLog(level) {
    const levels = Object.values(Logger.LEVELS);
    const currentIndex = levels.indexOf(Logger.currentLevel);
    const messageIndex = levels.indexOf(level);
    return messageIndex <= currentIndex;
  }

  /**
   * Format log message with timestamp and context
   * @param {string} level - Log level
   * @param {string} message - Log message
   * @param {Object} context - Additional context
   * @returns {Object} Formatted log object
   */
  static formatMessage(level, message, context = {}) {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      context: {
        ...context,
        userAgent: navigator.userAgent,
        url: window.location.href,
        userId: context.userId || 'anonymous'
      }
    };
  }

  /**
   * Send log to external service (in production)
   * @param {Object} logData - Formatted log data
   */
  static sendToLogService(logData) {
    // TODO: Implement actual logging service integration
    // Examples: Sentry, LogRocket, DataDog, etc.
    
    if (process.env.NODE_ENV === 'production') {
      // Send to production logging service
      fetch('/api/v1/logs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(logData)
      }).catch(err => {
        // Fallback to console if logging service fails
        console.error('Failed to send log to service:', err);
      });
    }
  }

  /**
   * Log error message
   * @param {string} message - Error message
   * @param {Error|Object} error - Error object or additional context
   * @param {Object} context - Additional context
   */
  static error(message, error = null, context = {}) {
    if (!Logger.shouldLog(Logger.LEVELS.ERROR)) return;

    const errorContext = {
      ...context,
      error: error ? {
        message: error.message,
        stack: error.stack,
        name: error.name
      } : null
    };

    const logData = Logger.formatMessage(Logger.LEVELS.ERROR, message, errorContext);

    if (process.env.NODE_ENV === 'development') {
      console.error(`[ERROR] ${message}`, error, context);
    } else {
      Logger.sendToLogService(logData);
    }

    // Report to error reporting service (commented out for now)
    // if (error instanceof Error) {
    //   errorReporting.reportError(error, {
    //     ...context,
    //     loggerMessage: message
    //   });
    // } else {
    //   errorReporting.reportMessage(message, {
    //     ...context,
    //     error: error
    //   }, 'error');
    // }
  }

  /**
   * Log warning message
   * @param {string} message - Warning message
   * @param {Object} context - Additional context
   */
  static warn(message, context = {}) {
    if (!Logger.shouldLog(Logger.LEVELS.WARN)) return;

    const logData = Logger.formatMessage(Logger.LEVELS.WARN, message, context);

    if (process.env.NODE_ENV === 'development') {
      console.warn(`[WARN] ${message}`, context);
    } else {
      Logger.sendToLogService(logData);
    }
  }

  /**
   * Log info message
   * @param {string} message - Info message
   * @param {Object} context - Additional context
   */
  static info(message, context = {}) {
    if (!Logger.shouldLog(Logger.LEVELS.INFO)) return;

    const logData = Logger.formatMessage(Logger.LEVELS.INFO, message, context);

    if (process.env.NODE_ENV === 'development') {
      console.info(`[INFO] ${message}`, context);
    } else {
      Logger.sendToLogService(logData);
    }
  }

  /**
   * Log debug message
   * @param {string} message - Debug message
   * @param {Object} context - Additional context
   */
  static debug(message, context = {}) {
    if (!Logger.shouldLog(Logger.LEVELS.DEBUG)) return;

    const logData = Logger.formatMessage(Logger.LEVELS.DEBUG, message, context);

    if (process.env.NODE_ENV === 'development') {
      console.debug(`[DEBUG] ${message}`, context);
    } else {
      Logger.sendToLogService(logData);
    }
  }

  /**
   * Log API request
   * @param {string} method - HTTP method
   * @param {string} url - Request URL
   * @param {Object} options - Request options
   */
  static apiRequest(method, url, options = {}) {
    Logger.debug(`API Request: ${method} ${url}`, {
      method,
      url,
      options: {
        headers: options.headers,
        body: options.body ? 'Present' : 'None'
      }
    });
  }

  /**
   * Log API response
   * @param {string} method - HTTP method
   * @param {string} url - Request URL
   * @param {Response} response - Response object
   * @param {Object} context - Additional context
   */
  static apiResponse(method, url, response, context = {}) {
    const level = response.ok ? Logger.LEVELS.INFO : Logger.LEVELS.ERROR;
    const message = `API Response: ${method} ${url} - ${response.status}`;
    
    const logContext = {
      ...context,
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    };

    if (level === Logger.LEVELS.ERROR) {
      Logger.error(message, null, logContext);
    } else {
      Logger.info(message, logContext);
    }
  }

  /**
   * Log user action
   * @param {string} action - User action
   * @param {Object} context - Additional context
   */
  static userAction(action, context = {}) {
    Logger.info(`User Action: ${action}`, {
      ...context,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log performance metrics
   * @param {string} operation - Operation name
   * @param {number} duration - Duration in milliseconds
   * @param {Object} context - Additional context
   */
  static performance(operation, duration, context = {}) {
    Logger.info(`Performance: ${operation} took ${duration}ms`, {
      ...context,
      duration,
      operation
    });
  }
}

export default Logger;
