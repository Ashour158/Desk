import { useState, useCallback, useEffect, useRef } from 'react';
import { 
  validateField, 
  validateForm, 
  isFormValid, 
  getInputConstraints,
  parseServerErrors,
  formStateManager,
  unsavedChangesManager,
  formAnalytics
} from '../utils/formValidation';

/**
 * Custom hook for comprehensive form validation and management
 * @param {Object} initialData - Initial form data
 * @param {Object} validationRules - Custom validation rules
 * @param {Object} options - Form options
 * @returns {Object} Form state and methods
 */
export const useFormValidation = (initialData = {}, validationRules = {}, options = {}) => {
  const {
    formId = 'default-form',
    enableAutoSave = false,
    enableUnsavedChangesWarning = true,
    enableAnalytics = true,
    autoSaveInterval = 30000, // 30 seconds
    validateOnChange = true,
    validateOnBlur = true
  } = options;

  const [formData, setFormData] = useState(initialData);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [lastSaved, setLastSaved] = useState(null);
  
  const autoSaveTimeoutRef = useRef(null);
  const beforeUnloadCleanupRef = useRef(null);

  /**
   * Initialize form state
   */
  useEffect(() => {
    // Load saved form state if available
    const savedData = formStateManager.loadFormState(formId);
    if (savedData) {
      setFormData(savedData);
      setIsDirty(true);
    }

    // Setup beforeunload warning
    if (enableUnsavedChangesWarning) {
      beforeUnloadCleanupRef.current = unsavedChangesManager.setupBeforeUnloadWarning(hasUnsavedChanges);
    }

    // Track form start
    if (enableAnalytics) {
      formAnalytics.trackEvent(formId, 'form_started', { fieldCount: Object.keys(initialData).length });
    }

    return () => {
      if (beforeUnloadCleanupRef.current) {
        beforeUnloadCleanupRef.current();
      }
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, [formId, enableUnsavedChangesWarning, enableAnalytics, hasUnsavedChanges]);

  /**
   * Update unsaved changes state
   */
  useEffect(() => {
    const hasChanges = unsavedChangesManager.hasUnsavedChanges(formData, initialData);
    setHasUnsavedChanges(hasChanges);
    setIsDirty(hasChanges);
  }, [formData, initialData]);

  /**
   * Auto-save functionality
   */
  useEffect(() => {
    if (enableAutoSave && isDirty && !loading) {
      autoSaveTimeoutRef.current = setTimeout(() => {
        handleAutoSave();
      }, autoSaveInterval);
    }

    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, [formData, isDirty, loading, enableAutoSave, autoSaveInterval]);

  /**
   * Handle field change with real-time validation
   */
  const handleChange = useCallback((e) => {
    const { name, value, type, checked } = e.target;
    const fieldValue = type === 'checkbox' ? checked : value;
    
    setFormData(prev => ({
      ...prev,
      [name]: fieldValue
    }));

    // Clear field error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }

    // Real-time validation
    if (validateOnChange) {
      const fieldError = validateField(name, fieldValue, validationRules[name]);
      if (fieldError) {
        setErrors(prev => ({
          ...prev,
          [name]: fieldError
        }));
      }
    }

    // Track field interaction
    if (enableAnalytics) {
      formAnalytics.trackEvent(formId, 'field_changed', { field: name, hasError: !!errors[name] });
    }
  }, [errors, validateOnChange, validationRules, formId, enableAnalytics]);

  /**
   * Handle field blur with validation
   */
  const handleBlur = useCallback((e) => {
    const { name, value } = e.target;
    
    if (validateOnBlur) {
      const fieldError = validateField(name, value, validationRules[name]);
      setErrors(prev => ({
        ...prev,
        [name]: fieldError
      }));
    }
  }, [validateOnBlur, validationRules]);

  /**
   * Validate entire form
   */
  const validateFormData = useCallback(() => {
    const formErrors = validateForm(formData, validationRules);
    setErrors(formErrors);
    
    if (enableAnalytics && Object.keys(formErrors).length > 0) {
      formAnalytics.trackValidationErrors(formId, formErrors);
    }
    
    return formErrors;
  }, [formData, validationRules, formId, enableAnalytics]);

  /**
   * Check if form is valid
   */
  const checkFormValidity = useCallback(() => {
    return isFormValid(formData, validationRules);
  }, [formData, validationRules]);

  /**
   * Handle form submission
   */
  const handleSubmit = useCallback(async (submitFunction) => {
    setLoading(true);
    
    // Validate form before submission
    const formErrors = validateFormData();
    if (Object.keys(formErrors).length > 0) {
      setLoading(false);
      return { success: false, errors: formErrors };
    }

    try {
      const result = await submitFunction(formData);
      
      // Clear form state on successful submission
      if (result.success) {
        setFormData(initialData);
        setErrors({});
        setIsDirty(false);
        setHasUnsavedChanges(false);
        formStateManager.clearFormState(formId);
        
        if (enableAnalytics) {
          formAnalytics.trackSubmission(formId, true, formData);
        }
      }
      
      return result;
    } catch (error) {
      // Handle server errors
      const serverErrors = parseServerErrors(error.response?.data || {});
      setErrors(serverErrors);
      
      if (enableAnalytics) {
        formAnalytics.trackSubmission(formId, false, formData);
      }
      
      return { success: false, errors: serverErrors };
    } finally {
      setLoading(false);
    }
  }, [formData, validateFormData, initialData, formId, enableAnalytics]);

  /**
   * Reset form to initial state
   */
  const resetForm = useCallback(() => {
    setFormData(initialData);
    setErrors({});
    setLoading(false);
    setIsDirty(false);
    setHasUnsavedChanges(false);
    formStateManager.clearFormState(formId);
    
    if (enableAnalytics) {
      formAnalytics.trackEvent(formId, 'form_reset');
    }
  }, [initialData, formId, enableAnalytics]);

  /**
   * Auto-save form data
   */
  const handleAutoSave = useCallback(() => {
    if (isDirty && !loading) {
      formStateManager.saveFormState(formId, formData);
      setLastSaved(Date.now());
      
      if (enableAnalytics) {
        formAnalytics.trackEvent(formId, 'auto_save', { fieldCount: Object.keys(formData).length });
      }
    }
  }, [formId, formData, isDirty, loading, enableAnalytics]);

  /**
   * Get input props for a field
   */
  const getInputProps = useCallback((fieldName, customProps = {}) => {
    const constraints = getInputConstraints(fieldName);
    const fieldError = errors[fieldName];
    
    return {
      name: fieldName,
      value: formData[fieldName] || '',
      onChange: handleChange,
      onBlur: handleBlur,
      ...constraints,
      ...customProps,
      className: `${customProps.className || ''} ${fieldError ? 'border-red-500' : ''}`.trim(),
      'aria-invalid': fieldError ? 'true' : 'false',
      'aria-describedby': fieldError ? `${fieldName}-error` : undefined
    };
  }, [formData, errors, handleChange, handleBlur]);

  /**
   * Get error message for a field
   */
  const getFieldError = useCallback((fieldName) => {
    return errors[fieldName] || '';
  }, [errors]);

  /**
   * Check if field has error
   */
  const hasFieldError = useCallback((fieldName) => {
    return !!errors[fieldName];
  }, [errors]);

  /**
   * Get form statistics
   */
  const getFormStats = useCallback(() => {
    return {
      fieldCount: Object.keys(formData).length,
      errorCount: Object.keys(errors).length,
      isDirty,
      hasUnsavedChanges,
      isValid: checkFormValidity(),
      lastSaved: lastSaved ? new Date(lastSaved).toLocaleString() : null
    };
  }, [formData, errors, isDirty, hasUnsavedChanges, checkFormValidity, lastSaved]);

  return {
    // Form state
    formData,
    errors,
    loading,
    isDirty,
    hasUnsavedChanges,
    lastSaved,
    
    // Form methods
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
    validateFormData,
    checkFormValidity,
    
    // Field utilities
    getInputProps,
    getFieldError,
    hasFieldError,
    
    // Form utilities
    getFormStats,
    setFormData,
    setErrors,
    setLoading
  };
};

export default useFormValidation;
