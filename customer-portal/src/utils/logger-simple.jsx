/**
 * Simple logging service for the customer portal
 */

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
    return Logger.LEVELS.INFO;
  }

  /**
   * Check if should log at given level
   * @param {string} level - Log level
   * @returns {boolean} Should log
   */
  static shouldLog(level) {
    const levels = Object.values(Logger.LEVELS);
    const currentIndex = levels.indexOf(Logger.currentLevel);
    const levelIndex = levels.indexOf(level);
    return levelIndex <= currentIndex;
  }

  /**
   * Format log message
   * @param {string} level - Log level
   * @param {string} message - Message
   * @param {Object} context - Additional context
   * @returns {Object} Formatted log data
   */
  static formatMessage(level, message, context = {}) {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      context
    };
  }

  /**
   * Log error message
   * @param {string} message - Error message
   * @param {Error} error - Error object
   * @param {Object} context - Additional context
   */
  static error(message, error = null, context = {}) {
    if (!Logger.shouldLog(Logger.LEVELS.ERROR)) return;

    const logData = Logger.formatMessage(Logger.LEVELS.ERROR, message, context);
    
    console.error(`[ERROR] ${message}`, {
      ...logData,
      error: error?.stack || error
    });
  }

  /**
   * Log warning message
   * @param {string} message - Warning message
   * @param {Object} context - Additional context
   */
  static warn(message, context = {}) {
    if (!Logger.shouldLog(Logger.LEVELS.WARN)) return;

    const logData = Logger.formatMessage(Logger.LEVELS.WARN, message, context);
    
    console.warn(`[WARN] ${message}`, logData);
  }

  /**
   * Log info message
   * @param {string} message - Info message
   * @param {Object} context - Additional context
   */
  static info(message, context = {}) {
    if (!Logger.shouldLog(Logger.LEVELS.INFO)) return;

    const logData = Logger.formatMessage(Logger.LEVELS.INFO, message, context);
    
    console.log(`[INFO] ${message}`, logData);
  }

  /**
   * Log debug message
   * @param {string} message - Debug message
   * @param {Object} context - Additional context
   */
  static debug(message, context = {}) {
    if (!Logger.shouldLog(Logger.LEVELS.DEBUG)) return;

    const logData = Logger.formatMessage(Logger.LEVELS.DEBUG, message, context);
    
    console.log(`[DEBUG] ${message}`, logData);
  }

  /**
   * Log API request
   * @param {string} method - HTTP method
   * @param {string} url - Request URL
   * @param {Object} data - Request data
   */
  static apiRequest(method, url, data = null) {
    Logger.info(`API Request: ${method} ${url}`, {
      method,
      url,
      data: data ? 'Present' : 'None'
    });
  }

  /**
   * Log API response
   * @param {string} method - HTTP method
   * @param {string} url - Request URL
   * @param {Response} response - Response object
   */
  static apiResponse(method, url, response) {
    Logger.info(`API Response: ${method} ${url}`, {
      method,
      url,
      status: response.status,
      statusText: response.statusText
    });
  }

  /**
   * Log user action
   * @param {string} action - Action name
   * @param {Object} data - Action data
   */
  static userAction(action, data = {}) {
    Logger.info(`User Action: ${action}`, {
      action,
      ...data
    });
  }

  /**
   * Set log level
   * @param {string} level - Log level
   */
  static setLevel(level) {
    if (Object.values(Logger.LEVELS).includes(level)) {
      Logger.currentLevel = level;
    }
  }
}

export default Logger;
