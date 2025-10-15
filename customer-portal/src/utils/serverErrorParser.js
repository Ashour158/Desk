/**
 * Enhanced server error parsing and handling system
 * Provides comprehensive error parsing, categorization, and user-friendly messages
 */

/**
 * Server error parser configuration
 */
export const errorParserConfig = {
  // Error categories
  categories: {
    VALIDATION: 'validation',
    AUTHENTICATION: 'authentication',
    AUTHORIZATION: 'authorization',
    NETWORK: 'network',
    SERVER: 'server',
    CLIENT: 'client',
    UNKNOWN: 'unknown'
  },
  
  // Error severity levels
  severity: {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
    CRITICAL: 'critical'
  },
  
  // Error handling settings
  settings: {
    enableRetry: true,
    maxRetries: 3,
    retryDelay: 1000,
    enableLogging: true,
    enableAnalytics: true,
    enableUserFeedback: true
  },
  
  // Error message templates
  messageTemplates: {
    validation: {
      required: 'This field is required',
      email: 'Please enter a valid email address',
      minLength: 'Must be at least {min} characters',
      maxLength: 'Must be no more than {max} characters',
      pattern: 'Please enter a valid format',
      custom: '{message}'
    },
    authentication: {
      invalid_credentials: 'Invalid email or password',
      account_locked: 'Your account has been locked',
      session_expired: 'Your session has expired',
      two_factor_required: 'Two-factor authentication required'
    },
    authorization: {
      insufficient_permissions: 'You do not have permission to perform this action',
      access_denied: 'Access denied',
      resource_not_found: 'The requested resource was not found'
    },
    network: {
      connection_failed: 'Unable to connect to the server',
      timeout: 'Request timed out',
      offline: 'You appear to be offline'
    },
    server: {
      internal_error: 'An internal server error occurred',
      service_unavailable: 'The service is temporarily unavailable',
      maintenance: 'The system is under maintenance'
    }
  }
};

/**
 * Server error parser class
 */
class ServerErrorParser {
  constructor() {
    this.errorHistory = [];
    this.retryAttempts = new Map();
    this.errorAnalytics = new Map();
  }

  /**
   * Parse server error response
   * @param {Object} errorResponse - Server error response
   * @param {Object} context - Additional context
   * @returns {Object} Parsed error
   */
  parseError(errorResponse, context = {}) {
    const parsedError = {
      id: this.generateErrorId(),
      timestamp: Date.now(),
      category: this.categorizeError(errorResponse),
      severity: this.determineSeverity(errorResponse),
      message: this.extractMessage(errorResponse),
      details: this.extractDetails(errorResponse),
      fieldErrors: this.extractFieldErrors(errorResponse),
      suggestions: this.generateSuggestions(errorResponse),
      retryable: this.isRetryable(errorResponse),
      context: context,
      originalError: errorResponse
    };

    // Log error if enabled
    if (errorParserConfig.settings.enableLogging) {
      this.logError(parsedError);
    }

    // Track error for analytics
    if (errorParserConfig.settings.enableAnalytics) {
      this.trackError(parsedError);
    }

    return parsedError;
  }

  /**
   * Categorize error based on response
   * @param {Object} errorResponse - Error response
   * @returns {string} Error category
   */
  categorizeError(errorResponse) {
    const status = errorResponse.status || errorResponse.statusCode;
    const code = errorResponse.code || errorResponse.error_code;
    const message = errorResponse.message || errorResponse.error || '';

    // Network errors
    if (!navigator.onLine) {
      return errorParserConfig.categories.NETWORK;
    }

    // HTTP status code based categorization
    if (status) {
      if (status >= 400 && status < 500) {
        if (status === 401) {
          return errorParserConfig.categories.AUTHENTICATION;
        } else if (status === 403) {
          return errorParserConfig.categories.AUTHORIZATION;
        } else if (status === 422) {
          return errorParserConfig.categories.VALIDATION;
        } else {
          return errorParserConfig.categories.CLIENT;
        }
      } else if (status >= 500) {
        return errorParserConfig.categories.SERVER;
      }
    }

    // Error code based categorization
    if (code) {
      const codeStr = code.toString().toLowerCase();
      if (codeStr.includes('validation') || codeStr.includes('invalid')) {
        return errorParserConfig.categories.VALIDATION;
      } else if (codeStr.includes('auth') || codeStr.includes('login')) {
        return errorParserConfig.categories.AUTHENTICATION;
      } else if (codeStr.includes('permission') || codeStr.includes('access')) {
        return errorParserConfig.categories.AUTHORIZATION;
      }
    }

    // Message based categorization
    const messageStr = message.toLowerCase();
    if (messageStr.includes('validation') || messageStr.includes('invalid')) {
      return errorParserConfig.categories.VALIDATION;
    } else if (messageStr.includes('auth') || messageStr.includes('login')) {
      return errorParserConfig.categories.AUTHENTICATION;
    } else if (messageStr.includes('permission') || messageStr.includes('access')) {
      return errorParserConfig.categories.AUTHORIZATION;
    } else if (messageStr.includes('network') || messageStr.includes('connection')) {
      return errorParserConfig.categories.NETWORK;
    }

    return errorParserConfig.categories.UNKNOWN;
  }

  /**
   * Determine error severity
   * @param {Object} errorResponse - Error response
   * @returns {string} Error severity
   */
  determineSeverity(errorResponse) {
    const status = errorResponse.status || errorResponse.statusCode;
    const category = this.categorizeError(errorResponse);

    // Critical errors
    if (status >= 500 || category === errorParserConfig.categories.SERVER) {
      return errorParserConfig.severity.CRITICAL;
    }

    // High severity errors
    if (status === 401 || status === 403 || category === errorParserConfig.categories.AUTHENTICATION) {
      return errorParserConfig.severity.HIGH;
    }

    // Medium severity errors
    if (status === 422 || category === errorParserConfig.categories.VALIDATION) {
      return errorParserConfig.severity.MEDIUM;
    }

    // Low severity errors
    if (status === 404 || category === errorParserConfig.categories.CLIENT) {
      return errorParserConfig.severity.LOW;
    }

    return errorParserConfig.severity.MEDIUM;
  }

  /**
   * Extract user-friendly error message
   * @param {Object} errorResponse - Error response
   * @returns {string} Error message
   */
  extractMessage(errorResponse) {
    const category = this.categorizeError(errorResponse);
    const status = errorResponse.status || errorResponse.statusCode;
    const code = errorResponse.code || errorResponse.error_code;
    const message = errorResponse.message || errorResponse.error || errorResponse.detail;

    // Try to get message from templates
    const templates = errorParserConfig.messageTemplates[category];
    if (templates && code && templates[code]) {
      return templates[code];
    }

    // Use specific status code messages
    if (status) {
      switch (status) {
        case 400:
          return 'Bad request. Please check your input.';
        case 401:
          return 'Authentication required. Please log in.';
        case 403:
          return 'Access denied. You do not have permission.';
        case 404:
          return 'The requested resource was not found.';
        case 422:
          return 'Please correct the validation errors below.';
        case 429:
          return 'Too many requests. Please try again later.';
        case 500:
          return 'Internal server error. Please try again later.';
        case 502:
          return 'Service temporarily unavailable.';
        case 503:
          return 'Service under maintenance.';
        default:
          break;
      }
    }

    // Use provided message or default
    return message || 'An unexpected error occurred. Please try again.';
  }

  /**
   * Extract error details
   * @param {Object} errorResponse - Error response
   * @returns {Object} Error details
   */
  extractDetails(errorResponse) {
    const details = {
      status: errorResponse.status || errorResponse.statusCode,
      code: errorResponse.code || errorResponse.error_code,
      type: errorResponse.type || errorResponse.error_type,
      timestamp: errorResponse.timestamp || Date.now(),
      requestId: errorResponse.request_id || errorResponse.requestId,
      traceId: errorResponse.trace_id || errorResponse.traceId
    };

    // Remove undefined values
    return Object.fromEntries(
      Object.entries(details).filter(([_, value]) => value !== undefined)
    );
  }

  /**
   * Extract field-specific errors
   * @param {Object} errorResponse - Error response
   * @returns {Object} Field errors
   */
  extractFieldErrors(errorResponse) {
    const fieldErrors = {};

    // Check for field_errors
    if (errorResponse.field_errors) {
      Object.assign(fieldErrors, errorResponse.field_errors);
    }

    // Check for errors object
    if (errorResponse.errors) {
      Object.assign(fieldErrors, errorResponse.errors);
    }

    // Check for validation errors
    if (errorResponse.validation_errors) {
      Object.assign(fieldErrors, errorResponse.validation_errors);
    }

    // Check for non_field_errors
    if (errorResponse.non_field_errors) {
      fieldErrors.general = Array.isArray(errorResponse.non_field_errors)
        ? errorResponse.non_field_errors[0]
        : errorResponse.non_field_errors;
    }

    return fieldErrors;
  }

  /**
   * Generate error suggestions
   * @param {Object} errorResponse - Error response
   * @returns {Array} Error suggestions
   */
  generateSuggestions(errorResponse) {
    const category = this.categorizeError(errorResponse);
    const status = errorResponse.status || errorResponse.statusCode;
    const suggestions = [];

    switch (category) {
      case errorParserConfig.categories.VALIDATION:
        suggestions.push('Please check all required fields');
        suggestions.push('Ensure all fields meet the minimum requirements');
        break;

      case errorParserConfig.categories.AUTHENTICATION:
        suggestions.push('Please check your email and password');
        suggestions.push('Try logging out and logging back in');
        break;

      case errorParserConfig.categories.AUTHORIZATION:
        suggestions.push('Contact your administrator for access');
        suggestions.push('Check if you have the required permissions');
        break;

      case errorParserConfig.categories.NETWORK:
        suggestions.push('Check your internet connection');
        suggestions.push('Try refreshing the page');
        break;

      case errorParserConfig.categories.SERVER:
        suggestions.push('Try again in a few minutes');
        suggestions.push('Contact support if the problem persists');
        break;
    }

    // Status-specific suggestions
    if (status === 429) {
      suggestions.push('Wait a moment before trying again');
    } else if (status === 503) {
      suggestions.push('The system is under maintenance');
    }

    return suggestions;
  }

  /**
   * Check if error is retryable
   * @param {Object} errorResponse - Error response
   * @returns {boolean} Whether error is retryable
   */
  isRetryable(errorResponse) {
    const status = errorResponse.status || errorResponse.statusCode;
    const category = this.categorizeError(errorResponse);

    // Network errors are usually retryable
    if (category === errorParserConfig.categories.NETWORK) {
      return true;
    }

    // Server errors are usually retryable
    if (category === errorParserConfig.categories.SERVER) {
      return true;
    }

    // Specific status codes that are retryable
    if (status && [408, 429, 500, 502, 503, 504].includes(status)) {
      return true;
    }

    return false;
  }

  /**
   * Generate unique error ID
   * @returns {string} Error ID
   */
  generateErrorId() {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Log error for debugging
   * @param {Object} parsedError - Parsed error
   */
  logError(parsedError) {
    console.group(`🚨 Error: ${parsedError.category.toUpperCase()}`);
    console.error('Message:', parsedError.message);
    console.error('Details:', parsedError.details);
    console.error('Field Errors:', parsedError.fieldErrors);
    console.error('Suggestions:', parsedError.suggestions);
    console.error('Original Error:', parsedError.originalError);
    console.groupEnd();

    // Add to error history
    this.errorHistory.push(parsedError);
    
    // Keep only last 100 errors
    if (this.errorHistory.length > 100) {
      this.errorHistory = this.errorHistory.slice(-100);
    }
  }

  /**
   * Track error for analytics
   * @param {Object} parsedError - Parsed error
   */
  trackError(parsedError) {
    const key = `${parsedError.category}_${parsedError.severity}`;
    const count = this.errorAnalytics.get(key) || 0;
    this.errorAnalytics.set(key, count + 1);

    // Send to analytics service
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'form_error', {
        error_category: parsedError.category,
        error_severity: parsedError.severity,
        error_message: parsedError.message
      });
    }
  }

  /**
   * Get error analytics
   * @returns {Object} Error analytics
   */
  getErrorAnalytics() {
    return {
      totalErrors: this.errorHistory.length,
      errorCounts: Object.fromEntries(this.errorAnalytics),
      recentErrors: this.errorHistory.slice(-10),
      errorTrends: this.calculateErrorTrends()
    };
  }

  /**
   * Calculate error trends
   * @returns {Object} Error trends
   */
  calculateErrorTrends() {
    const now = Date.now();
    const oneHour = 60 * 60 * 1000;
    const oneDay = 24 * oneHour;

    const lastHour = this.errorHistory.filter(e => now - e.timestamp < oneHour).length;
    const lastDay = this.errorHistory.filter(e => now - e.timestamp < oneDay).length;

    return {
      lastHour,
      lastDay,
      trend: lastHour > 5 ? 'increasing' : lastHour < 2 ? 'decreasing' : 'stable'
    };
  }

  /**
   * Clear error history
   */
  clearErrorHistory() {
    this.errorHistory = [];
    this.errorAnalytics.clear();
  }
}

/**
 * Create server error parser instance
 */
const serverErrorParser = new ServerErrorParser();

/**
 * Parse server error with enhanced features
 * @param {Object} errorResponse - Server error response
 * @param {Object} context - Additional context
 * @returns {Object} Parsed error
 */
export const parseServerError = (errorResponse, context = {}) => {
  return serverErrorParser.parseError(errorResponse, context);
};

/**
 * Get error analytics
 * @returns {Object} Error analytics
 */
export const getErrorAnalytics = () => {
  return serverErrorParser.getErrorAnalytics();
};

/**
 * Clear error history
 */
export const clearErrorHistory = () => {
  serverErrorParser.clearErrorHistory();
};

export default serverErrorParser;
