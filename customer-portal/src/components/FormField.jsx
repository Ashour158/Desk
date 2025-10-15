import React, { memo, forwardRef } from 'react';
import PropTypes from 'prop-types';

/**
 * Enhanced form field component with validation and accessibility
 */
const FormField = memo(forwardRef(({
  name,
  label,
  type = 'text',
  value,
  onChange,
  onBlur,
  error,
  required = false,
  placeholder,
  className = '',
  inputClassName = '',
  labelClassName = '',
  errorClassName = '',
  helpText,
  disabled = false,
  autoComplete,
  ...props
}, ref) => {
  const fieldId = `field-${name}`;
  const errorId = `${name}-error`;
  const helpId = `${name}-help`;

  const getInputClasses = () => {
    const baseClasses = 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm';
    const errorClasses = error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : '';
    const disabledClasses = disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : '';
    
    return `${baseClasses} ${errorClasses} ${disabledClasses} ${inputClassName}`.trim();
  };

  const getLabelClasses = () => {
    const baseClasses = 'block text-sm font-medium text-gray-700';
    const errorClasses = error ? 'text-red-700' : '';
    
    return `${baseClasses} ${errorClasses} ${labelClassName}`.trim();
  };

  const getErrorClasses = () => {
    const baseClasses = 'mt-1 text-sm text-red-600';
    return `${baseClasses} ${errorClassName}`.trim();
  };

  const renderInput = () => {
    const commonProps = {
      id: fieldId,
      name,
      value: value || '',
      onChange,
      onBlur,
      disabled,
      required,
      placeholder,
      autoComplete,
      'aria-invalid': error ? 'true' : 'false',
      'aria-describedby': [
        error ? errorId : null,
        helpText ? helpId : null
      ].filter(Boolean).join(' ') || undefined,
      className: getInputClasses(),
      ...props
    };

    switch (type) {
      case 'textarea':
        return (
          <textarea
            ref={ref}
            {...commonProps}
            rows={props.rows || 4}
          />
        );
      
      case 'select':
        return (
          <select
            ref={ref}
            {...commonProps}
          >
            {props.options?.map(option => (
              <option key={option.value} value={option.value} disabled={option.disabled}>
                {option.label}
              </option>
            ))}
          </select>
        );
      
      case 'checkbox':
        return (
          <div className="flex items-center">
            <input
              ref={ref}
              type="checkbox"
              id={fieldId}
              name={name}
              checked={value || false}
              onChange={onChange}
              onBlur={onBlur}
              disabled={disabled}
              required={required}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              aria-invalid={error ? 'true' : 'false'}
              aria-describedby={error ? errorId : undefined}
            />
            {label && (
              <label htmlFor={fieldId} className="ml-2 block text-sm text-gray-900">
                {label}
                {required && <span className="text-red-500 ml-1">*</span>}
              </label>
            )}
          </div>
        );
      
      case 'radio':
        return (
          <div className="space-y-2">
            {props.options?.map(option => (
              <div key={option.value} className="flex items-center">
                <input
                  type="radio"
                  id={`${fieldId}-${option.value}`}
                  name={name}
                  value={option.value}
                  checked={value === option.value}
                  onChange={onChange}
                  onBlur={onBlur}
                  disabled={disabled}
                  required={required}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  aria-invalid={error ? 'true' : 'false'}
                  aria-describedby={error ? errorId : undefined}
                />
                <label htmlFor={`${fieldId}-${option.value}`} className="ml-2 block text-sm text-gray-900">
                  {option.label}
                </label>
              </div>
            ))}
          </div>
        );
      
      default:
        return (
          <input
            ref={ref}
            type={type}
            {...commonProps}
          />
        );
    }
  };

  // For checkbox and radio, render differently
  if (type === 'checkbox' || type === 'radio') {
    return (
      <div className={`form-field ${className}`}>
        {renderInput()}
        {error && (
          <p id={errorId} className={getErrorClasses()} role="alert">
            {error}
          </p>
        )}
        {helpText && !error && (
          <p id={helpId} className="mt-1 text-sm text-gray-500">
            {helpText}
          </p>
        )}
      </div>
    );
  }

  return (
    <div className={`form-field ${className}`}>
      {label && (
        <label htmlFor={fieldId} className={getLabelClasses()}>
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      {renderInput()}
      
      {error && (
        <p id={errorId} className={getErrorClasses()} role="alert">
          <svg className="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </p>
      )}
      
      {helpText && !error && (
        <p id={helpId} className="mt-1 text-sm text-gray-500">
          {helpText}
        </p>
      )}
    </div>
  );
}));

FormField.propTypes = {
  name: PropTypes.string.isRequired,
  label: PropTypes.string,
  type: PropTypes.oneOf([
    'text', 'email', 'password', 'tel', 'url', 'number', 'date', 'time', 'datetime-local',
    'textarea', 'select', 'checkbox', 'radio'
  ]),
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number, PropTypes.bool]),
  onChange: PropTypes.func,
  onBlur: PropTypes.func,
  error: PropTypes.string,
  required: PropTypes.bool,
  placeholder: PropTypes.string,
  className: PropTypes.string,
  inputClassName: PropTypes.string,
  labelClassName: PropTypes.string,
  errorClassName: PropTypes.string,
  helpText: PropTypes.string,
  disabled: PropTypes.bool,
  autoComplete: PropTypes.string,
  options: PropTypes.arrayOf(PropTypes.shape({
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    label: PropTypes.string,
    disabled: PropTypes.bool
  })),
  rows: PropTypes.number
};

FormField.displayName = 'FormField';

export default FormField;
