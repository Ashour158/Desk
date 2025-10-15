import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import Logger from '../utils/logger';
import EnhancedForm from '../components/EnhancedForm';
import FormField from '../components/FormField';
import { validationRules } from '../utils/formValidation';

/**
 * Registration page component
 * @param {Object} props - Component props
 */
const Register = ({ onRegister }) => {
  const navigate = useNavigate();
  const [initialData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    company: '',
    phone: '',
    agreeToTerms: false
  });

  /**
   * Custom validation rules for registration
   */
  const customValidationRules = {
    ...validationRules,
    confirmPassword: [
      {
        type: 'required',
        message: 'Password confirmation is required',
        validate: (value) => value !== ''
      },
      {
        type: 'custom',
        message: 'Passwords do not match',
        validate: (value, allData) => value === allData.password
      }
    ],
    agreeToTerms: [
      {
        type: 'required',
        message: 'You must agree to the terms and conditions',
        validate: (value) => value === true
      }
    ]
  };

  /**
   * Handle form submission
   * @param {Object} formData - Form data
   * @returns {Object} Submission result
   */
  const handleSubmit = async (formData) => {
    try {
      Logger.apiRequest('POST', '/api/v1/auth/register/', { body: 'Present' });

      const response = await fetch('/api/v1/auth/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: formData.firstName,
          last_name: formData.lastName,
          email: formData.email,
          password: formData.password,
          company: formData.company,
          phone: formData.phone
        })
      });

      Logger.apiResponse('POST', '/api/v1/auth/register/', response);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Registration failed');
      }

      const data = await response.json();
      
      Logger.info('User registered successfully', {
        userId: data.user.id,
        email: data.user.email
      });
      
      Logger.userAction('register', {
        userId: data.user.id,
        email: data.user.email
      });

      // Call register callback if provided
      if (onRegister) {
        onRegister(data.user);
      }

      // Navigate to login page
      navigate('/login?registered=true');
      
      return { success: true, data };
      
    } catch (error) {
      Logger.error('Registration failed:', error, {
        email: formData.email,
        status: error?.response?.status
      });
      
      return { 
        success: false, 
        errors: { 
          general: error.message || 'Registration failed. Please try again.' 
        } 
      };
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
              sign in to your existing account
            </Link>
          </p>
        </div>
        
        <EnhancedForm
          formId="register-form"
          initialData={initialData}
          validationRules={customValidationRules}
          onSubmit={handleSubmit}
          className="mt-8 space-y-6"
        >
          {({ formData, errors, loading, getInputProps, getFieldError }) => (
            <>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    name="firstName"
                    label="First Name"
                    type="text"
                    required
                    placeholder="First name"
                    {...getInputProps('firstName')}
                    error={getFieldError('firstName')}
                  />

                  <FormField
                    name="lastName"
                    label="Last Name"
                    type="text"
                    required
                    placeholder="Last name"
                    {...getInputProps('lastName')}
                    error={getFieldError('lastName')}
                  />
                </div>

                <FormField
                  name="email"
                  label="Email Address"
                  type="email"
                  required
                  placeholder="Enter your email"
                  {...getInputProps('email')}
                  error={getFieldError('email')}
                />

                <FormField
                  name="password"
                  label="Password"
                  type="password"
                  required
                  placeholder="Create a password"
                  helpText="Password must be at least 8 characters with uppercase, lowercase, and number"
                  {...getInputProps('password')}
                  error={getFieldError('password')}
                />

                <FormField
                  name="confirmPassword"
                  label="Confirm Password"
                  type="password"
                  required
                  placeholder="Confirm your password"
                  {...getInputProps('confirmPassword')}
                  error={getFieldError('confirmPassword')}
                />

                <FormField
                  name="company"
                  label="Company (Optional)"
                  type="text"
                  placeholder="Your company name"
                  {...getInputProps('company')}
                  error={getFieldError('company')}
                />

                <FormField
                  name="phone"
                  label="Phone Number (Optional)"
                  type="tel"
                  placeholder="Your phone number"
                  {...getInputProps('phone')}
                  error={getFieldError('phone')}
                />

                <FormField
                  name="agreeToTerms"
                  label={
                    <span>
                      I agree to the{' '}
                      <Link to="/terms" className="text-blue-600 hover:text-blue-500">
                        Terms and Conditions
                      </Link>{' '}
                      and{' '}
                      <Link to="/privacy" className="text-blue-600 hover:text-blue-500">
                        Privacy Policy
                      </Link>
                    </span>
                  }
                  type="checkbox"
                  required
                  {...getInputProps('agreeToTerms')}
                  error={getFieldError('agreeToTerms')}
                />
              </div>
            </>
          )}
        </EnhancedForm>
      </div>
    </div>
  );
};

Register.propTypes = {
  onRegister: PropTypes.func,
};

Register.defaultProps = {
  onRegister: null,
};

export default Register;