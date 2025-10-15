/**
 * Enhanced Logging System for React Frontend
 * Comprehensive logging with error tracking, performance monitoring, and user analytics
 */

import { errorReportingService } from './errorReporting';

/**
 * Enhanced logging configuration
 */
const LOGGING_CONFIG = {
  // Log levels
  LEVELS: {
    ERROR: 'error',
    WARN: 'warn',
    INFO: 'info',
    DEBUG: 'debug',
    TRACE: 'trace'
  },
  
  // Current log level based on environment
  currentLevel: process.env.NODE_ENV === 'production' ? 'error' : 'debug',
  
  // External service configuration
  externalServices: {
    sentry: process.env.REACT_APP_SENTRY_DSN,
    logrocket: process.env.REACT_APP_LOGROCKET_APP_ID,
    datadog: process.env.REACT_APP_DATADOG_API_KEY,
  },
  
  // Performance monitoring
  performance: {
    enabled: true,
    sampleRate: 1.0,
    slowThreshold: 1000, // 1 second
  },
  
  // User analytics
  analytics: {
    enabled: true,
    trackUserActions: true,
    trackPageViews: true,
    trackPerformance: true,
  },
  
  // Data sanitization
  sanitization: {
    enabled: true,
    sensitiveFields: ['password', 'token', 'secret', 'key', 'authorization', 'api_key'],
    redactPatterns: [
      /password["\']?\s*[:=]\s*["\']?[^"\']+["\']?/gi,
      /token["\']?\s*[:=]\s*["\']?[^"\']+["\']?/gi,
      /secret["\']?\s*[:=]\s*["\']?[^"\']+["\']?/gi,
      /key["\']?\s*[:=]\s*["\']?[^"\']+["\']?/gi,
      /authorization["\']?\s*[:=]\s*["\']?[^"\']+["\']?/gi,
      /api_key["\']?\s*[:=]\s*["\']?[^"\']+["\']?/gi,
    ]
  }
};

/**
 * Data sanitization utility
 */
class DataSanitizer {
  /**
   * Sanitize sensitive data from object
   * @param {any} data - Data to sanitize
   * @returns {any} Sanitized data
   */
  static sanitize(data) {
    if (!LOGGING_CONFIG.sanitization.enabled) {
      return data;
    }
    
    if (typeof data === 'string') {
      return this.sanitizeString(data);
    }
    
    if (typeof data === 'object' && data !== null) {
      return this.sanitizeObject(data);
    }
    
    return data;
  }
  
  /**
   * Sanitize string data
   * @param {string} str - String to sanitize
   * @returns {string} Sanitized string
   */
  static sanitizeString(str) {
    let sanitized = str;
    
    // Apply redaction patterns
    LOGGING_CONFIG.sanitization.redactPatterns.forEach(pattern => {
      sanitized = sanitized.replace(pattern, (match) => {
        const key = match.split(/[:=]/)[0];
        return `${key}=***REDACTED***`;
      });
    });
    
    return sanitized;
  }
  
  /**
   * Sanitize object data
   * @param {Object} obj - Object to sanitize
   * @returns {Object} Sanitized object
   */
  static sanitizeObject(obj) {
    const sanitized = { ...obj };
    
    // Recursively sanitize object properties
    Object.keys(sanitized).forEach(key => {
      if (LOGGING_CONFIG.sanitization.sensitiveFields.includes(key.toLowerCase())) {
        sanitized[key] = '***REDACTED***';
      } else if (typeof sanitized[key] === 'object' && sanitized[key] !== null) {
        sanitized[key] = this.sanitizeObject(sanitized[key]);
      } else if (typeof sanitized[key] === 'string') {
        sanitized[key] = this.sanitizeString(sanitized[key]);
      }
    });
    
    return sanitized;
  }
}

/**
 * Performance monitoring utility
 */
class PerformanceMonitor {
  constructor() {
    this.metrics = new Map();
    this.observers = [];
    this.isInitialized = false;
  }
  
  /**
   * Initialize performance monitoring
   */
  initialize() {
    if (this.isInitialized) return;
    
    // Monitor page load performance
    this.monitorPageLoad();
    
    // Monitor resource loading
    this.monitorResourceLoading();
    
    // Monitor user interactions
    this.monitorUserInteractions();
    
    this.isInitialized = true;
  }
  
  /**
   * Monitor page load performance
   */
  monitorPageLoad() {
    window.addEventListener('load', () => {
      const perfData = performance.getEntriesByType('navigation')[0];
      if (perfData) {
        this.recordMetric('page_load', {
          loadTime: perfData.loadEventEnd - perfData.loadEventStart,
          domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
          firstPaint: this.getFirstPaint(),
          firstContentfulPaint: this.getFirstContentfulPaint(),
          largestContentfulPaint: this.getLargestContentfulPaint(),
        });
      }
    });
  }
  
  /**
   * Monitor resource loading performance
   */
  monitorResourceLoading() {
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach(entry => {
        if (entry.duration > LOGGING_CONFIG.performance.slowThreshold) {
          this.recordMetric('slow_resource', {
            name: entry.name,
            duration: entry.duration,
            type: entry.entryType,
            size: entry.transferSize,
          });
        }
      });
    });
    
    observer.observe({ entryTypes: ['resource'] });
    this.observers.push(observer);
  }
  
  /**
   * Monitor user interactions
   */
  monitorUserInteractions() {
    // Monitor click events
    document.addEventListener('click', (event) => {
      this.recordMetric('user_interaction', {
        type: 'click',
        target: event.target.tagName,
        id: event.target.id,
        className: event.target.className,
        timestamp: Date.now(),
      });
    });
    
    // Monitor form submissions
    document.addEventListener('submit', (event) => {
      this.recordMetric('user_interaction', {
        type: 'form_submit',
        formId: event.target.id,
        formAction: event.target.action,
        timestamp: Date.now(),
      });
    });
  }
  
  /**
   * Record performance metric
   * @param {string} name - Metric name
   * @param {Object} data - Metric data
   */
  recordMetric(name, data) {
    const metric = {
      name,
      data,
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
    };
    
    this.metrics.set(`${name}_${Date.now()}`, metric);
    
    // Send to external service if enabled
    if (LOGGING_CONFIG.analytics.enabled) {
      this.sendToExternalService(metric);
    }
  }
  
  /**
   * Get first paint time
   * @returns {number} First paint time
   */
  getFirstPaint() {
    const paintEntries = performance.getEntriesByType('paint');
    const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
    return firstPaint ? firstPaint.startTime : 0;
  }
  
  /**
   * Get first contentful paint time
   * @returns {number} First contentful paint time
   */
  getFirstContentfulPaint() {
    const paintEntries = performance.getEntriesByType('paint');
    const firstContentfulPaint = paintEntries.find(entry => entry.name === 'first-contentful-paint');
    return firstContentfulPaint ? firstContentfulPaint.startTime : 0;
  }
  
  /**
   * Get largest contentful paint time
   * @returns {number} Largest contentful paint time
   */
  getLargestContentfulPaint() {
    const lcpEntries = performance.getEntriesByType('largest-contentful-paint');
    return lcpEntries.length > 0 ? lcpEntries[lcpEntries.length - 1].startTime : 0;
  }
  
  /**
   * Send metric to external service
   * @param {Object} metric - Metric to send
   */
  sendToExternalService(metric) {
    // Send to external analytics service
    if (LOGGING_CONFIG.externalServices.datadog) {
      this.sendToDataDog(metric);
    }
  }
  
  /**
   * Send metric to DataDog
   * @param {Object} metric - Metric to send
   */
  sendToDataDog(metric) {
    // Implementation for DataDog integration
    console.log('Sending metric to DataDog:', metric);
  }
  
  /**
   * Get performance metrics
   * @returns {Array} Performance metrics
   */
  getMetrics() {
    return Array.from(this.metrics.values());
  }
  
  /**
   * Clear metrics
   */
  clearMetrics() {
    this.metrics.clear();
  }
}

/**
 * User analytics utility
 */
class UserAnalytics {
  constructor() {
    this.sessionId = this.generateSessionId();
    this.userId = this.getUserId();
    this.pageViews = [];
    this.userActions = [];
    this.isInitialized = false;
  }
  
  /**
   * Initialize user analytics
   */
  initialize() {
    if (this.isInitialized) return;
    
    // Track page views
    this.trackPageView();
    
    // Track user session
    this.trackUserSession();
    
    // Track user interactions
    this.trackUserInteractions();
    
    this.isInitialized = true;
  }
  
  /**
   * Track page view
   * @param {string} page - Page name
   * @param {Object} context - Additional context
   */
  trackPageView(page = null, context = {}) {
    const pageView = {
      page: page || window.location.pathname,
      title: document.title,
      url: window.location.href,
      referrer: document.referrer,
      timestamp: Date.now(),
      sessionId: this.sessionId,
      userId: this.userId,
      context,
    };
    
    this.pageViews.push(pageView);
    
    // Send to external service
    if (LOGGING_CONFIG.analytics.enabled) {
      this.sendToExternalService('page_view', pageView);
    }
  }
  
  /**
   * Track user action
   * @param {string} action - Action name
   * @param {Object} context - Additional context
   */
  trackUserAction(action, context = {}) {
    const userAction = {
      action,
      timestamp: Date.now(),
      sessionId: this.sessionId,
      userId: this.userId,
      url: window.location.href,
      context,
    };
    
    this.userActions.push(userAction);
    
    // Send to external service
    if (LOGGING_CONFIG.analytics.enabled) {
      this.sendToExternalService('user_action', userAction);
    }
  }
  
  /**
   * Track user session
   */
  trackUserSession() {
    const session = {
      sessionId: this.sessionId,
      userId: this.userId,
      startTime: Date.now(),
      userAgent: navigator.userAgent,
      language: navigator.language,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      screenResolution: `${screen.width}x${screen.height}`,
      viewportSize: `${window.innerWidth}x${window.innerHeight}`,
    };
    
    // Send to external service
    if (LOGGING_CONFIG.analytics.enabled) {
      this.sendToExternalService('user_session', session);
    }
  }
  
  /**
   * Track user interactions
   */
  trackUserInteractions() {
    // Track clicks
    document.addEventListener('click', (event) => {
      this.trackUserAction('click', {
        target: event.target.tagName,
        id: event.target.id,
        className: event.target.className,
      });
    });
    
    // Track form interactions
    document.addEventListener('submit', (event) => {
      this.trackUserAction('form_submit', {
        formId: event.target.id,
        formAction: event.target.action,
      });
    });
    
    // Track navigation
    window.addEventListener('popstate', () => {
      this.trackPageView();
    });
  }
  
  /**
   * Send to external service
   * @param {string} type - Event type
   * @param {Object} data - Event data
   */
  sendToExternalService(type, data) {
    // Send to external analytics service
    if (LOGGING_CONFIG.externalServices.datadog) {
      this.sendToDataDog(type, data);
    }
  }
  
  /**
   * Send to DataDog
   * @param {string} type - Event type
   * @param {Object} data - Event data
   */
  sendToDataDog(type, data) {
    // Implementation for DataDog integration
    console.log('Sending analytics to DataDog:', { type, data });
  }
  
  /**
   * Generate session ID
   * @returns {string} Session ID
   */
  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  /**
   * Get user ID
   * @returns {string} User ID
   */
  getUserId() {
    const user = localStorage.getItem('user');
    if (user) {
      try {
        const userData = JSON.parse(user);
        return userData.id || 'anonymous';
      } catch (e) {
        return 'anonymous';
      }
    }
    return 'anonymous';
  }
  
  /**
   * Get analytics data
   * @returns {Object} Analytics data
   */
  getAnalyticsData() {
    return {
      sessionId: this.sessionId,
      userId: this.userId,
      pageViews: this.pageViews,
      userActions: this.userActions,
    };
  }
}

/**
 * Enhanced logger class
 */
class EnhancedLogger {
  constructor() {
    this.performanceMonitor = new PerformanceMonitor();
    this.userAnalytics = new UserAnalytics();
    this.isInitialized = false;
  }
  
  /**
   * Initialize enhanced logging
   */
  initialize() {
    if (this.isInitialized) return;
    
    // Initialize performance monitoring
    this.performanceMonitor.initialize();
    
    // Initialize user analytics
    this.userAnalytics.initialize();
    
    // Initialize error tracking
    this.initializeErrorTracking();
    
    this.isInitialized = true;
  }
  
  /**
   * Initialize error tracking
   */
  initializeErrorTracking() {
    // Track unhandled errors
    window.addEventListener('error', (event) => {
      this.error('Unhandled error', event.error, {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        type: 'unhandled_error',
      });
    });
    
    // Track unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.error('Unhandled promise rejection', event.reason, {
        type: 'unhandled_rejection',
      });
    });
  }
  
  /**
   * Check if log level should be output
   * @param {string} level - Log level
   * @returns {boolean} Whether to output
   */
  shouldLog(level) {
    const levels = Object.values(LOGGING_CONFIG.LEVELS);
    const currentIndex = levels.indexOf(LOGGING_CONFIG.currentLevel);
    const messageIndex = levels.indexOf(level);
    return messageIndex <= currentIndex;
  }
  
  /**
   * Format log message
   * @param {string} level - Log level
   * @param {string} message - Log message
   * @param {Object} context - Additional context
   * @returns {Object} Formatted log object
   */
  formatMessage(level, message, context = {}) {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      context: DataSanitizer.sanitize({
        ...context,
        userAgent: navigator.userAgent,
        url: window.location.href,
        userId: this.userAnalytics.userId,
        sessionId: this.userAnalytics.sessionId,
      }),
    };
  }
  
  /**
   * Send log to external service
   * @param {Object} logData - Log data
   */
  sendToExternalService(logData) {
    // Send to error reporting service
    if (errorReportingService && logData.level === 'error') {
      errorReportingService.reportError(new Error(logData.message), logData.context);
    }
    
    // Send to external logging service
    if (process.env.NODE_ENV === 'production') {
      fetch('/api/v1/logs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(logData)
      }).catch(err => {
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
  error(message, error = null, context = {}) {
    if (!this.shouldLog(LOGGING_CONFIG.LEVELS.ERROR)) return;
    
    const errorContext = {
      ...context,
      error: error ? {
        message: error.message,
        stack: error.stack,
        name: error.name
      } : null
    };
    
    const logData = this.formatMessage(LOGGING_CONFIG.LEVELS.ERROR, message, errorContext);
    
    if (process.env.NODE_ENV === 'development') {
      console.error(`[ERROR] ${message}`, error, context);
    }
    
    this.sendToExternalService(logData);
  }
  
  /**
   * Log warning message
   * @param {string} message - Warning message
   * @param {Object} context - Additional context
   */
  warn(message, context = {}) {
    if (!this.shouldLog(LOGGING_CONFIG.LEVELS.WARN)) return;
    
    const logData = this.formatMessage(LOGGING_CONFIG.LEVELS.WARN, message, context);
    
    if (process.env.NODE_ENV === 'development') {
      console.warn(`[WARN] ${message}`, context);
    }
    
    this.sendToExternalService(logData);
  }
  
  /**
   * Log info message
   * @param {string} message - Info message
   * @param {Object} context - Additional context
   */
  info(message, context = {}) {
    if (!this.shouldLog(LOGGING_CONFIG.LEVELS.INFO)) return;
    
    const logData = this.formatMessage(LOGGING_CONFIG.LEVELS.INFO, message, context);
    
    if (process.env.NODE_ENV === 'development') {
      console.info(`[INFO] ${message}`, context);
    }
    
    this.sendToExternalService(logData);
  }
  
  /**
   * Log debug message
   * @param {string} message - Debug message
   * @param {Object} context - Additional context
   */
  debug(message, context = {}) {
    if (!this.shouldLog(LOGGING_CONFIG.LEVELS.DEBUG)) return;
    
    const logData = this.formatMessage(LOGGING_CONFIG.LEVELS.DEBUG, message, context);
    
    if (process.env.NODE_ENV === 'development') {
      console.debug(`[DEBUG] ${message}`, context);
    }
    
    this.sendToExternalService(logData);
  }
  
  /**
   * Log performance metric
   * @param {string} operation - Operation name
   * @param {number} duration - Duration in milliseconds
   * @param {Object} context - Additional context
   */
  performance(operation, duration, context = {}) {
    this.performanceMonitor.recordMetric('performance', {
      operation,
      duration,
      context,
    });
    
    this.info(`Performance: ${operation} took ${duration}ms`, context);
  }
  
  /**
   * Log user action
   * @param {string} action - User action
   * @param {Object} context - Additional context
   */
  userAction(action, context = {}) {
    this.userAnalytics.trackUserAction(action, context);
    this.info(`User action: ${action}`, context);
  }
  
  /**
   * Log API request
   * @param {string} method - HTTP method
   * @param {string} url - Request URL
   * @param {Object} context - Additional context
   */
  apiRequest(method, url, context = {}) {
    this.info(`API Request: ${method} ${url}`, context);
  }
  
  /**
   * Log API response
   * @param {string} method - HTTP method
   * @param {string} url - Request URL
   * @param {Response} response - Response object
   */
  apiResponse(method, url, response) {
    this.info(`API Response: ${method} ${url} - ${response.status}`, {
      status: response.status,
      statusText: response.statusText,
      headers: Object.fromEntries(response.headers.entries()),
    });
  }
  
  /**
   * Get logging statistics
   * @returns {Object} Logging statistics
   */
  getStatistics() {
    return {
      isInitialized: this.isInitialized,
      performanceMetrics: this.performanceMonitor.getMetrics(),
      analyticsData: this.userAnalytics.getAnalyticsData(),
    };
  }
}

// Create enhanced logger instance
const enhancedLogger = new EnhancedLogger();

// Initialize enhanced logging
enhancedLogger.initialize();

export default enhancedLogger;
