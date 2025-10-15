/**
 * Comprehensive form validation utilities
 * Provides real-time validation, error handling, and form state management
 */

/**
 * Validation rules for different field types
 */
export const validationRules = {
  email: [
    {
      type: 'required',
      message: 'Email is required',
      validate: (value) => value.trim() !== ''
    },
    {
      type: 'email',
      message: 'Please enter a valid email address',
      validate: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
    },
    {
      type: 'maxLength',
      message: 'Email is too long',
      validate: (value) => value.length <= 254
    }
  ],
  password: [
    {
      type: 'required',
      message: 'Password is required',
      validate: (value) => value !== ''
    },
    {
      type: 'minLength',
      message: 'Password must be at least 8 characters',
      validate: (value) => value.length >= 8
    },
    {
      type: 'pattern',
      message: 'Password must contain uppercase, lowercase, and number',
      validate: (value) => /(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)
    }
  ],
  phone: [
    {
      type: 'pattern',
      message: 'Please enter a valid phone number',
      validate: (value) => !value || /^\+?[\d\s\-\(\)]+$/.test(value)
    }
  ],
  subject: [
    {
      type: 'required',
      message: 'Subject is required',
      validate: (value) => value.trim() !== ''
    },
    {
      type: 'minLength',
      message: 'Subject must be at least 5 characters',
      validate: (value) => value.trim().length >= 5
    },
    {
      type: 'maxLength',
      message: 'Subject must be less than 200 characters',
      validate: (value) => value.length <= 200
    }
  ],
  description: [
    {
      type: 'required',
      message: 'Description is required',
      validate: (value) => value.trim() !== ''
    },
    {
      type: 'minLength',
      message: 'Description must be at least 10 characters',
      validate: (value) => value.trim().length >= 10
    }
  ],
  firstName: [
    {
      type: 'required',
      message: 'First name is required',
      validate: (value) => value.trim() !== ''
    },
    {
      type: 'pattern',
      message: 'First name can only contain letters and spaces',
      validate: (value) => /^[a-zA-Z\s]+$/.test(value)
    }
  ],
  lastName: [
    {
      type: 'required',
      message: 'Last name is required',
      validate: (value) => value.trim() !== ''
    },
    {
      type: 'pattern',
      message: 'Last name can only contain letters and spaces',
      validate: (value) => /^[a-zA-Z\s]+$/.test(value)
    }
  ]
};

/**
 * Validate a single field against its rules
 * @param {string} fieldName - Name of the field
 * @param {any} value - Value to validate
 * @param {Array} customRules - Custom validation rules
 * @returns {string} Error message or empty string
 */
export const validateField = (fieldName, value, customRules = []) => {
  const rules = customRules.length > 0 ? customRules : validationRules[fieldName] || [];
  
  for (const rule of rules) {
    if (!rule.validate(value)) {
      return rule.message;
    }
  }
  
  return '';
};

/**
 * Validate entire form data
 * @param {Object} formData - Form data to validate
 * @param {Object} customRules - Custom validation rules
 * @returns {Object} Validation errors
 */
export const validateForm = (formData, customRules = {}) => {
  const errors = {};
  
  Object.keys(formData).forEach(fieldName => {
    const fieldRules = customRules[fieldName] || validationRules[fieldName];
    if (fieldRules) {
      const error = validateField(fieldName, formData[fieldName], fieldRules);
      if (error) {
        errors[fieldName] = error;
      }
    }
  });
  
  return errors;
};

/**
 * Check if form is valid
 * @param {Object} formData - Form data to check
 * @param {Object} customRules - Custom validation rules
 * @returns {boolean} True if form is valid
 */
export const isFormValid = (formData, customRules = {}) => {
  const errors = validateForm(formData, customRules);
  return Object.keys(errors).length === 0;
};

/**
 * Get input constraints based on field type
 * @param {string} fieldName - Name of the field
 * @returns {Object} Input constraints
 */
export const getInputConstraints = (fieldName) => {
  const constraints = {
    email: {
      type: 'email',
      autoComplete: 'email',
      pattern: '[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}$'
    },
    password: {
      type: 'password',
      autoComplete: 'new-password',
      minLength: 8
    },
    phone: {
      type: 'tel',
      autoComplete: 'tel',
      pattern: '[0-9+\\-\\s()]+'
    },
    subject: {
      type: 'text',
      minLength: 5,
      maxLength: 200,
      pattern: '[a-zA-Z0-9\\s\\-_.,!?]+'
    },
    description: {
      type: 'textarea',
      minLength: 10
    },
    firstName: {
      type: 'text',
      autoComplete: 'given-name',
      pattern: '[a-zA-Z\\s]+'
    },
    lastName: {
      type: 'text',
      autoComplete: 'family-name',
      pattern: '[a-zA-Z\\s]+'
    },
    age: {
      type: 'number',
      min: 1,
      max: 120,
      step: 1
    },
    website: {
      type: 'url',
      autoComplete: 'url',
      pattern: 'https?://.+'
    },
    date: {
      type: 'date'
    }
  };
  
  return constraints[fieldName] || { type: 'text' };
};

/**
 * Parse server validation errors
 * @param {Object} errorResponse - Server error response
 * @returns {Object} Parsed errors
 */
export const parseServerErrors = (errorResponse) => {
  const errors = {};
  
  if (errorResponse.field_errors) {
    Object.entries(errorResponse.field_errors).forEach(([field, messages]) => {
      errors[field] = Array.isArray(messages) ? messages[0] : messages;
    });
  }
  
  if (errorResponse.non_field_errors) {
    errors.general = Array.isArray(errorResponse.non_field_errors) 
      ? errorResponse.non_field_errors[0] 
      : errorResponse.non_field_errors;
  }
  
  if (errorResponse.detail) {
    errors.general = errorResponse.detail;
  }
  
  return errors;
};

/**
 * Form state management utilities
 */
export const formStateManager = {
  /**
   * Save form state to localStorage
   * @param {string} formId - Unique form identifier
   * @param {Object} formData - Form data to save
   */
  saveFormState: (formId, formData) => {
    try {
      localStorage.setItem(`form_${formId}`, JSON.stringify({
        data: formData,
        timestamp: Date.now()
      }));
    } catch (error) {
      console.warn('Failed to save form state:', error);
    }
  },
  
  /**
   * Load form state from localStorage
   * @param {string} formId - Unique form identifier
   * @returns {Object|null} Saved form data or null
   */
  loadFormState: (formId) => {
    try {
      const saved = localStorage.getItem(`form_${formId}`);
      if (saved) {
        const parsed = JSON.parse(saved);
        // Check if data is not too old (24 hours)
        if (Date.now() - parsed.timestamp < 24 * 60 * 60 * 1000) {
          return parsed.data;
        }
      }
    } catch (error) {
      console.warn('Failed to load form state:', error);
    }
    return null;
  },
  
  /**
   * Clear form state from localStorage
   * @param {string} formId - Unique form identifier
   */
  clearFormState: (formId) => {
    try {
      localStorage.removeItem(`form_${formId}`);
    } catch (error) {
      console.warn('Failed to clear form state:', error);
    }
  }
};

/**
 * Unsaved changes detection utilities
 */
export const unsavedChangesManager = {
  /**
   * Check if form has unsaved changes
   * @param {Object} currentData - Current form data
   * @param {Object} initialData - Initial form data
   * @returns {boolean} True if there are unsaved changes
   */
  hasUnsavedChanges: (currentData, initialData) => {
    return JSON.stringify(currentData) !== JSON.stringify(initialData);
  },
  
  /**
   * Setup beforeunload warning
   * @param {boolean} hasChanges - Whether form has unsaved changes
   */
  setupBeforeUnloadWarning: (hasChanges) => {
    const handleBeforeUnload = (e) => {
      if (hasChanges) {
        e.preventDefault();
        e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
        return 'You have unsaved changes. Are you sure you want to leave?';
      }
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  },
  
  /**
   * Setup navigation warning for React Router
   * @param {boolean} hasChanges - Whether form has unsaved changes
   * @param {Function} onConfirm - Callback when user confirms navigation
   */
  setupNavigationWarning: (hasChanges, onConfirm) => {
    return (e) => {
      if (hasChanges) {
        e.preventDefault();
        if (confirm('You have unsaved changes. Are you sure you want to leave?')) {
          onConfirm();
        }
      }
    };
  }
};

/**
 * Form analytics utilities
 */
export const formAnalytics = {
  /**
   * Track form event
   * @param {string} formId - Form identifier
   * @param {string} event - Event type
   * @param {Object} data - Event data
   */
  trackEvent: (formId, event, data = {}) => {
    try {
      // In a real application, you would send this to your analytics service
      console.log('Form Analytics:', {
        formId,
        event,
        data,
        timestamp: Date.now()
      });
    } catch (error) {
      console.warn('Failed to track form event:', error);
    }
  },
  
  /**
   * Track form validation errors
   * @param {string} formId - Form identifier
   * @param {Object} errors - Validation errors
   */
  trackValidationErrors: (formId, errors) => {
    formAnalytics.trackEvent(formId, 'validation_errors', {
      errorCount: Object.keys(errors).length,
      errors: Object.keys(errors)
    });
  },
  
  /**
   * Track form submission
   * @param {string} formId - Form identifier
   * @param {boolean} success - Whether submission was successful
   * @param {Object} data - Form data
   */
  trackSubmission: (formId, success, data = {}) => {
    formAnalytics.trackEvent(formId, 'form_submission', {
      success,
      fieldCount: Object.keys(data).length,
      hasErrors: !success
    });
  }
};

export default {
  validateField,
  validateForm,
  isFormValid,
  getInputConstraints,
  parseServerErrors,
  formStateManager,
  unsavedChangesManager,
  formAnalytics,
  validationRules
};
