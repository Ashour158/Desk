/**
 * Form analytics and tracking utilities
 * Provides comprehensive form interaction tracking and analytics
 */

/**
 * Form analytics configuration
 */
export const analyticsConfig = {
  // Analytics endpoints
  endpoints: {
    track: '/api/v1/analytics/form-events/',
    metrics: '/api/v1/analytics/form-metrics/',
    errors: '/api/v1/analytics/form-errors/'
  },
  
  // Tracking settings
  settings: {
    enableTracking: true,
    enableErrorTracking: true,
    enablePerformanceTracking: true,
    enableUserBehaviorTracking: true,
    batchSize: 10,
    flushInterval: 30000, // 30 seconds
    maxRetries: 3
  },
  
  // Event types
  eventTypes: {
    FORM_START: 'form_start',
    FORM_ABANDON: 'form_abandon',
    FORM_SUBMIT: 'form_submit',
    FORM_SUCCESS: 'form_success',
    FORM_ERROR: 'form_error',
    FIELD_FOCUS: 'field_focus',
    FIELD_BLUR: 'field_blur',
    FIELD_CHANGE: 'field_change',
    FIELD_ERROR: 'field_error',
    FIELD_VALIDATION: 'field_validation',
    FORM_RESET: 'form_reset',
    FORM_SAVE: 'form_save',
    FORM_LOAD: 'form_load'
  }
};

/**
 * Form analytics tracker
 */
class FormAnalyticsTracker {
  constructor() {
    this.events = [];
    this.sessionId = this.generateSessionId();
    this.formSessions = new Map();
    this.isOnline = navigator.onLine;
    
    // Setup online/offline listeners
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.flushEvents();
    });
    
    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
    
    // Setup periodic flush
    setInterval(() => {
      this.flushEvents();
    }, analyticsConfig.settings.flushInterval);
    
    // Setup beforeunload flush
    window.addEventListener('beforeunload', () => {
      this.flushEvents(true);
    });
  }

  /**
   * Generate unique session ID
   * @returns {string} Session ID
   */
  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Generate unique form session ID
   * @param {string} formId - Form ID
   * @returns {string} Form session ID
   */
  generateFormSessionId(formId) {
    return `form_${formId}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Track form event
   * @param {string} formId - Form ID
   * @param {string} eventType - Event type
   * @param {Object} data - Event data
   */
  track(formId, eventType, data = {}) {
    if (!analyticsConfig.settings.enableTracking) {
      return;
    }

    const event = {
      id: `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      sessionId: this.sessionId,
      formSessionId: this.getFormSessionId(formId),
      formId,
      eventType,
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      data: {
        ...data,
        formId,
        eventType
      }
    };

    this.events.push(event);
    
    // Update form session
    this.updateFormSession(formId, eventType, data);
    
    // Flush if batch size reached
    if (this.events.length >= analyticsConfig.settings.batchSize) {
      this.flushEvents();
    }
  }

  /**
   * Get or create form session ID
   * @param {string} formId - Form ID
   * @returns {string} Form session ID
   */
  getFormSessionId(formId) {
    if (!this.formSessions.has(formId)) {
      this.formSessions.set(formId, this.generateFormSessionId(formId));
    }
    return this.formSessions.get(formId);
  }

  /**
   * Update form session data
   * @param {string} formId - Form ID
   * @param {string} eventType - Event type
   * @param {Object} data - Event data
   */
  updateFormSession(formId, eventType, data) {
    const session = this.formSessions.get(formId) || {};
    const now = Date.now();
    
    if (!session.startTime) {
      session.startTime = now;
    }
    
    session.lastActivity = now;
    session.eventCount = (session.eventCount || 0) + 1;
    
    if (eventType === analyticsConfig.eventTypes.FORM_START) {
      session.startTime = now;
    } else if (eventType === analyticsConfig.eventTypes.FORM_SUBMIT) {
      session.submitTime = now;
    } else if (eventType === analyticsConfig.eventTypes.FORM_SUCCESS) {
      session.successTime = now;
      session.completed = true;
    } else if (eventType === analyticsConfig.eventTypes.FORM_ERROR) {
      session.errorCount = (session.errorCount || 0) + 1;
      session.lastError = now;
    }
    
    this.formSessions.set(formId, session);
  }

  /**
   * Track form start
   * @param {string} formId - Form ID
   * @param {Object} formData - Initial form data
   */
  trackFormStart(formId, formData = {}) {
    this.track(formId, analyticsConfig.eventTypes.FORM_START, {
      fieldCount: Object.keys(formData).length,
      hasInitialData: Object.keys(formData).length > 0
    });
  }

  /**
   * Track form abandon
   * @param {string} formId - Form ID
   * @param {Object} formData - Current form data
   * @param {string} reason - Abandon reason
   */
  trackFormAbandon(formId, formData = {}, reason = 'unknown') {
    const session = this.formSessions.get(formId);
    const timeSpent = session ? Date.now() - session.startTime : 0;
    
    this.track(formId, analyticsConfig.eventTypes.FORM_ABANDON, {
      reason,
      timeSpent,
      fieldCount: Object.keys(formData).length,
      completionPercentage: this.calculateCompletionPercentage(formData)
    });
  }

  /**
   * Track form submission
   * @param {string} formId - Form ID
   * @param {Object} formData - Form data
   * @param {boolean} isValid - Whether form is valid
   */
  trackFormSubmit(formId, formData, isValid) {
    const session = this.formSessions.get(formId);
    const timeSpent = session ? Date.now() - session.startTime : 0;
    
    this.track(formId, analyticsConfig.eventTypes.FORM_SUBMIT, {
      isValid,
      timeSpent,
      fieldCount: Object.keys(formData).length,
      completionPercentage: this.calculateCompletionPercentage(formData)
    });
  }

  /**
   * Track form success
   * @param {string} formId - Form ID
   * @param {Object} formData - Form data
   * @param {Object} response - Server response
   */
  trackFormSuccess(formId, formData, response = {}) {
    const session = this.formSessions.get(formId);
    const timeSpent = session ? Date.now() - session.startTime : 0;
    
    this.track(formId, analyticsConfig.eventTypes.FORM_SUCCESS, {
      timeSpent,
      fieldCount: Object.keys(formData).length,
      responseId: response.id,
      responseStatus: response.status
    });
  }

  /**
   * Track form error
   * @param {string} formId - Form ID
   * @param {Object} error - Error object
   * @param {Object} formData - Form data
   */
  trackFormError(formId, error, formData = {}) {
    this.track(formId, analyticsConfig.eventTypes.FORM_ERROR, {
      errorType: error.type || 'unknown',
      errorMessage: error.message || 'Unknown error',
      errorCode: error.code,
      fieldCount: Object.keys(formData).length,
      stack: error.stack
    });
  }

  /**
   * Track field interaction
   * @param {string} formId - Form ID
   * @param {string} fieldName - Field name
   * @param {string} eventType - Event type (focus, blur, change, error)
   * @param {any} value - Field value
   * @param {string} error - Field error
   */
  trackFieldInteraction(formId, fieldName, eventType, value, error = null) {
    this.track(formId, `field_${eventType}`, {
      fieldName,
      value: typeof value === 'string' ? value.substring(0, 100) : value, // Truncate long values
      hasError: !!error,
      errorMessage: error
    });
  }

  /**
   * Track field validation
   * @param {string} formId - Form ID
   * @param {string} fieldName - Field name
   * @param {boolean} isValid - Whether field is valid
   * @param {string} error - Validation error
   */
  trackFieldValidation(formId, fieldName, isValid, error = null) {
    this.track(formId, analyticsConfig.eventTypes.FIELD_VALIDATION, {
      fieldName,
      isValid,
      errorMessage: error
    });
  }

  /**
   * Calculate form completion percentage
   * @param {Object} formData - Form data
   * @returns {number} Completion percentage
   */
  calculateCompletionPercentage(formData) {
    const totalFields = Object.keys(formData).length;
    const filledFields = Object.values(formData).filter(value => 
      value !== '' && value !== null && value !== undefined
    ).length;
    
    return totalFields > 0 ? Math.round((filledFields / totalFields) * 100) : 0;
  }

  /**
   * Flush events to server
   * @param {boolean} sync - Whether to send synchronously
   */
  async flushEvents(sync = false) {
    if (this.events.length === 0 || !this.isOnline) {
      return;
    }

    const eventsToSend = [...this.events];
    this.events = [];

    try {
      const response = await fetch(analyticsConfig.endpoints.track, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          events: eventsToSend,
          sessionId: this.sessionId,
          timestamp: Date.now()
        })
      });

      if (!response.ok) {
        throw new Error(`Analytics tracking failed: ${response.status}`);
      }

      console.log(`Analytics: Sent ${eventsToSend.length} events`);
    } catch (error) {
      console.error('Analytics tracking error:', error);
      
      // Re-add events to queue for retry
      this.events.unshift(...eventsToSend);
      
      // Retry with exponential backoff
      setTimeout(() => {
        this.flushEvents();
      }, Math.min(1000 * Math.pow(2, this.retryCount || 0), 30000));
    }
  }

  /**
   * Get form metrics
   * @param {string} formId - Form ID
   * @returns {Object} Form metrics
   */
  getFormMetrics(formId) {
    const session = this.formSessions.get(formId);
    if (!session) {
      return null;
    }

    return {
      formId,
      sessionId: session.formSessionId,
      startTime: session.startTime,
      lastActivity: session.lastActivity,
      eventCount: session.eventCount,
      errorCount: session.errorCount || 0,
      completed: session.completed || false,
      timeSpent: session.lastActivity - session.startTime,
      completionTime: session.successTime ? session.successTime - session.startTime : null
    };
  }

  /**
   * Get all form metrics
   * @returns {Object} All form metrics
   */
  getAllMetrics() {
    const metrics = {};
    for (const [formId, session] of this.formSessions) {
      metrics[formId] = this.getFormMetrics(formId);
    }
    return metrics;
  }
}

/**
 * Create form analytics tracker instance
 */
const formAnalytics = new FormAnalyticsTracker();

/**
 * Form analytics hooks for React components
 */
export const useFormAnalytics = (formId) => {
  const track = (eventType, data) => {
    formAnalytics.track(formId, eventType, data);
  };

  const trackFormStart = (formData) => {
    formAnalytics.trackFormStart(formId, formData);
  };

  const trackFormAbandon = (formData, reason) => {
    formAnalytics.trackFormAbandon(formId, formData, reason);
  };

  const trackFormSubmit = (formData, isValid) => {
    formAnalytics.trackFormSubmit(formId, formData, isValid);
  };

  const trackFormSuccess = (formData, response) => {
    formAnalytics.trackFormSuccess(formId, formData, response);
  };

  const trackFormError = (error, formData) => {
    formAnalytics.trackFormError(formId, error, formData);
  };

  const trackFieldInteraction = (fieldName, eventType, value, error) => {
    formAnalytics.trackFieldInteraction(formId, fieldName, eventType, value, error);
  };

  const trackFieldValidation = (fieldName, isValid, error) => {
    formAnalytics.trackFieldValidation(formId, fieldName, isValid, error);
  };

  const getMetrics = () => {
    return formAnalytics.getFormMetrics(formId);
  };

  return {
    track,
    trackFormStart,
    trackFormAbandon,
    trackFormSubmit,
    trackFormSuccess,
    trackFormError,
    trackFieldInteraction,
    trackFieldValidation,
    getMetrics
  };
};

/**
 * Form analytics dashboard data
 */
export const getAnalyticsDashboard = () => {
  const metrics = formAnalytics.getAllMetrics();
  const totalForms = Object.keys(metrics).length;
  const completedForms = Object.values(metrics).filter(m => m.completed).length;
  const totalErrors = Object.values(metrics).reduce((sum, m) => sum + (m.errorCount || 0), 0);
  const avgTimeSpent = Object.values(metrics)
    .filter(m => m.timeSpent)
    .reduce((sum, m) => sum + m.timeSpent, 0) / completedForms;

  return {
    totalForms,
    completedForms,
    completionRate: totalForms > 0 ? (completedForms / totalForms) * 100 : 0,
    totalErrors,
    avgTimeSpent,
    metrics
  };
};

export default formAnalytics;
