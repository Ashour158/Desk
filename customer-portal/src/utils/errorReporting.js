/**
 * Error reporting service for production error tracking
 * Integrates with external services like Sentry, LogRocket, etc.
 */

class ErrorReportingService {
  constructor() {
    this.isInitialized = false;
    this.service = null;
    this.config = {
      dsn: process.env.REACT_APP_SENTRY_DSN,
      environment: process.env.NODE_ENV,
      release: process.env.REACT_APP_VERSION || '1.0.0'
    };
  }

  /**
   * Initialize error reporting service
   */
  async initialize() {
    if (this.isInitialized) return;

    try {
      // Initialize Sentry if DSN is provided
      if (this.config.dsn) {
        const Sentry = await import('@sentry/react');
        
        Sentry.init({
          dsn: this.config.dsn,
          environment: this.config.environment,
          release: this.config.release,
          integrations: [
            new Sentry.BrowserTracing(),
            new Sentry.Replay()
          ],
          tracesSampleRate: 0.1,
          replaysSessionSampleRate: 0.1,
          replaysOnErrorSampleRate: 1.0,
        });

        this.service = Sentry;
        this.isInitialized = true;
        
        console.info('Error reporting service initialized');
      } else {
        console.warn('No error reporting DSN configured');
      }
    } catch (error) {
      console.error('Failed to initialize error reporting:', error);
    }
  }

  /**
   * Report an error to the error reporting service
   * @param {Error} error - Error object
   * @param {Object} context - Additional context
   * @param {string} level - Error level (error, warning, info)
   */
  reportError(error, context = {}, level = 'error') {
    if (!this.isInitialized || !this.service) {
      // Fallback to console in development
      console.error('Error (no reporting service):', error, context);
      return;
    }

    try {
      this.service.withScope((scope) => {
        // Add context
        Object.keys(context).forEach(key => {
          scope.setContext(key, context[key]);
        });

        // Set user context if available
        if (context.user) {
          scope.setUser(context.user);
        }

        // Set tags
        if (context.tags) {
          Object.keys(context.tags).forEach(key => {
            scope.setTag(key, context.tags[key]);
          });
        }

        // Capture the error
        this.service.captureException(error, {
          level,
          fingerprint: [error.message, context.component],
          extra: context
        });
      });
    } catch (reportingError) {
      console.error('Failed to report error:', reportingError);
    }
  }

  /**
   * Report a message (not an error)
   * @param {string} message - Message to report
   * @param {Object} context - Additional context
   * @param {string} level - Message level
   */
  reportMessage(message, context = {}, level = 'info') {
    if (!this.isInitialized || !this.service) {
      console.log(`Message (no reporting service): ${message}`, context);
      return;
    }

    try {
      this.service.withScope((scope) => {
        Object.keys(context).forEach(key => {
          scope.setContext(key, context[key]);
        });

        this.service.captureMessage(message, level);
      });
    } catch (reportingError) {
      console.error('Failed to report message:', reportingError);
    }
  }

  /**
   * Set user context for error reporting
   * @param {Object} user - User information
   */
  setUser(user) {
    if (!this.isInitialized || !this.service) return;

    try {
      this.service.setUser(user);
    } catch (error) {
      console.error('Failed to set user context:', error);
    }
  }

  /**
   * Set breadcrumb for error tracking
   * @param {string} message - Breadcrumb message
   * @param {string} category - Breadcrumb category
   * @param {string} level - Breadcrumb level
   */
  addBreadcrumb(message, category = 'user', level = 'info') {
    if (!this.isInitialized || !this.service) return;

    try {
      this.service.addBreadcrumb({
        message,
        category,
        level,
        timestamp: Date.now() / 1000
      });
    } catch (error) {
      console.error('Failed to add breadcrumb:', error);
    }
  }

  /**
   * Capture performance metrics
   * @param {string} operation - Operation name
   * @param {number} duration - Duration in milliseconds
   * @param {Object} context - Additional context
   */
  capturePerformance(operation, duration, context = {}) {
    if (!this.isInitialized || !this.service) return;

    try {
      this.service.addBreadcrumb({
        message: `Performance: ${operation}`,
        category: 'performance',
        level: 'info',
        data: {
          operation,
          duration,
          ...context
        }
      });
    } catch (error) {
      console.error('Failed to capture performance:', error);
    }
  }

  /**
   * Capture user action
   * @param {string} action - User action
   * @param {Object} context - Additional context
   */
  captureUserAction(action, context = {}) {
    if (!this.isInitialized || !this.service) return;

    try {
      this.service.addBreadcrumb({
        message: `User Action: ${action}`,
        category: 'user',
        level: 'info',
        data: context
      });
    } catch (error) {
      console.error('Failed to capture user action:', error);
    }
  }
}

// Create singleton instance
const errorReporting = new ErrorReportingService();

// Initialize on module load
errorReporting.initialize();

export default errorReporting;
