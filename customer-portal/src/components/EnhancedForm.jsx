import React, { memo, useCallback, useEffect } from 'react';
import PropTypes from 'prop-types';
import useFormValidation from '../hooks/useFormValidation';
import { useNotifications } from './NotificationSystem';
import { useFormStatePersistence } from '../utils/formStatePersistence';
import { parseServerError } from '../utils/serverErrorParser';
import { useFormAnalytics } from '../utils/formAnalytics';

/**
 * Enhanced form component with comprehensive validation and state management
 */
const EnhancedForm = memo(({
  formId,
  initialData = {},
  validationRules = {},
  onSubmit,
  onReset,
  children,
  className = '',
  options = {},
  ...props
}) => {
  const { showSuccess, showError, showWarning } = useNotifications();
  
  // Enhanced form features
  const formAnalytics = useFormAnalytics(formId);
  const {
    saveState,
    loadState,
    restoreState,
    setupAutoSave,
    clearAutoSave,
    deleteState,
    hasSavedState
  } = useFormStatePersistence(formId, initialData, {
    enableAutoSave: options.enableAutoSave !== false,
    enableRecovery: options.enableRecovery !== false,
    onStateSaved: (formData) => {
      console.log(`Form state auto-saved for ${formId}`);
    },
    onStateRestored: () => {
      showSuccess('Form state restored from draft', {
        title: 'Draft Restored',
        message: 'Your previous form data has been restored.'
      });
    }
  });
  
  const {
    formData,
    errors,
    loading,
    isDirty,
    hasUnsavedChanges,
    lastSaved,
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
    validateFormData,
    checkFormValidity,
    getInputProps,
    getFieldError,
    hasFieldError,
    getFormStats
  } = useFormValidation(initialData, validationRules, {
    formId,
    enableAutoSave: true,
    enableUnsavedChangesWarning: true,
    enableAnalytics: true,
    ...options
  });

  /**
   * Handle form submission with enhanced error handling
   */
  const handleFormSubmit = useCallback(async (e) => {
    e.preventDefault();
    
    // Track form submission attempt
    formAnalytics.trackFormSubmit(formData, checkFormValidity());
    
    const result = await handleSubmit(async (formData) => {
      try {
        const response = await onSubmit(formData);
        
        // Parse server errors if present
        if (!response.success && response.errors) {
          const parsedError = parseServerError(response, {
            formId,
            formData,
            timestamp: Date.now()
          });
          
          // Track form error
          formAnalytics.trackFormError(parsedError, formData);
          
          return {
            success: false,
            errors: parsedError.fieldErrors,
            general: parsedError.message,
            suggestions: parsedError.suggestions
          };
        }
        
        return response;
      } catch (error) {
        // Parse and track error
        const parsedError = parseServerError(error, {
          formId,
          formData,
          timestamp: Date.now()
        });
        
        formAnalytics.trackFormError(parsedError, formData);
        
        return {
          success: false,
          errors: parsedError.fieldErrors,
          general: parsedError.message,
          suggestions: parsedError.suggestions
        };
      }
    });
    
    if (result.success) {
      // Track successful submission
      formAnalytics.trackFormSuccess(formData, result.data);
      
      // Clear saved state on successful submission
      await deleteState();
      
      showSuccess('Form submitted successfully!', {
        title: 'Success',
        message: 'Your form has been submitted successfully.'
      });
      
      if (onReset) {
        onReset();
      }
    } else {
      const errorCount = Object.keys(result.errors).length;
      if (errorCount > 0) {
        showError(`Please fix ${errorCount} error${errorCount > 1 ? 's' : ''} before submitting.`, {
          title: 'Validation Errors',
          message: 'Please review the highlighted fields and correct the errors.'
        });
      } else {
        showError(result.general || 'Form submission failed. Please try again.', {
          title: 'Submission Error',
          message: result.suggestions ? result.suggestions.join(' ') : 'There was an error submitting your form. Please try again.'
        });
      }
    }
  }, [handleSubmit, onSubmit, onReset, showSuccess, showError, formData, checkFormValidity, formAnalytics, deleteState]);

  /**
   * Handle form reset with confirmation
   */
  const handleFormReset = useCallback(() => {
    if (isDirty) {
      if (confirm('Are you sure you want to reset the form? All unsaved changes will be lost.')) {
        resetForm();
        if (onReset) {
          onReset();
        }
        showWarning('Form has been reset.', {
          title: 'Form Reset',
          message: 'All form data has been cleared.'
        });
      }
    } else {
      resetForm();
      if (onReset) {
        onReset();
      }
    }
  }, [isDirty, resetForm, onReset, showWarning]);

  /**
   * Handle navigation warning
   */
  const handleNavigationWarning = useCallback((e) => {
    if (hasUnsavedChanges) {
      e.preventDefault();
      if (confirm('You have unsaved changes. Are you sure you want to leave?')) {
        // Allow navigation
        return true;
      }
      return false;
    }
    return true;
  }, [hasUnsavedChanges]);

  // Setup enhanced form features
  useEffect(() => {
    // Track form start
    formAnalytics.trackFormStart(formData);
    
    // Setup auto-save
    setupAutoSave(() => formData);
    
    // Check for saved state and offer to restore
    const checkSavedState = async () => {
      const hasSaved = await hasSavedState();
      if (hasSaved) {
        const shouldRestore = await restoreState((restoredData) => {
          // This will be handled by the form validation hook
          console.log('Form state restored:', restoredData);
        });
      }
    };
    
    checkSavedState();
    
    // Setup navigation warning
    const handleBeforeUnload = (e) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
        return 'You have unsaved changes. Are you sure you want to leave?';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      clearAutoSave();
    };
  }, [formAnalytics, setupAutoSave, hasSavedState, restoreState, hasUnsavedChanges, clearAutoSave, formData]);

  return (
    <div className={`enhanced-form ${className}`} {...props}>
      {/* Form Header with Stats */}
      <div className="form-header mb-4">
        <div className="flex justify-between items-center">
          <div className="form-stats">
            {isDirty && (
              <span className="text-sm text-amber-600 flex items-center">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Unsaved changes
              </span>
            )}
            {lastSaved && (
              <span className="text-sm text-green-600 ml-4">
                Last saved: {new Date(lastSaved).toLocaleTimeString()}
              </span>
            )}
          </div>
          
          <div className="form-actions">
            <button
              type="button"
              onClick={handleFormReset}
              disabled={loading}
              className="btn btn-secondary mr-2"
            >
              Reset Form
            </button>
          </div>
        </div>
      </div>

      {/* Form Content */}
      <form onSubmit={handleFormSubmit} className="space-y-6">
        {/* General Errors */}
        {errors.general && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md" role="alert">
            <div className="flex">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div>
                <h4 className="font-medium">Form Submission Error</h4>
                <p className="text-sm">{errors.general}</p>
              </div>
            </div>
          </div>
        )}

        {/* Form Fields */}
        {children && typeof children === 'function' 
          ? children({
              formData,
              errors,
              loading,
              isDirty,
              hasUnsavedChanges,
              handleChange,
              handleBlur,
              getInputProps,
              getFieldError,
              hasFieldError,
              validateFormData,
              checkFormValidity
            })
          : children
        }

        {/* Form Footer */}
        <div className="form-footer flex justify-between items-center pt-4 border-t border-gray-200">
          <div className="form-status">
            {loading && (
              <span className="text-sm text-blue-600 flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Submitting...
              </span>
            )}
            {!loading && hasUnsavedChanges && (
              <span className="text-sm text-amber-600">
                You have unsaved changes
              </span>
            )}
            {!loading && !hasUnsavedChanges && !checkFormValidity() && (
              <span className="text-sm text-red-600">
                Please fix validation errors
              </span>
            )}
          </div>

          <div className="form-submit">
            <button
              type="submit"
              disabled={loading || !checkFormValidity()}
              className="btn btn-primary"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Submitting...
                </>
              ) : (
                'Submit'
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
});

EnhancedForm.propTypes = {
  formId: PropTypes.string.isRequired,
  initialData: PropTypes.object,
  validationRules: PropTypes.object,
  onSubmit: PropTypes.func.isRequired,
  onReset: PropTypes.func,
  children: PropTypes.oneOfType([PropTypes.node, PropTypes.func]),
  className: PropTypes.string,
  options: PropTypes.object
};

export default EnhancedForm;
