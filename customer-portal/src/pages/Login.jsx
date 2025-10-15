import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import Logger from '../utils/logger';
import EnhancedForm from '../components/EnhancedForm';
import FormField from '../components/FormField';
import { validationRules } from '../utils/formValidation';

/**
 * Login page component
 * @param {Object} props - Component props
 */
const Login = ({ onLogin }) => {
  const navigate = useNavigate();
  const [initialData] = useState({
    email: '',
    password: '',
    remember: false
  });

  /**
   * Handle form submission
   * @param {Object} formData - Form data
   * @returns {Object} Submission result
   */
  const handleSubmit = async (formData) => {
    try {
      Logger.apiRequest('POST', '/api/v1/auth/login/', { body: 'Present' });

      const response = await fetch('/api/v1/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      Logger.apiResponse('POST', '/api/v1/auth/login/', response);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Store authentication data
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      Logger.info('User logged in successfully', {
        userId: data.user.id,
        email: data.user.email
      });
      
      Logger.userAction('login', {
        userId: data.user.id,
        email: data.user.email
      });

      // Call login callback if provided
      if (onLogin) {
        onLogin(data.user);
      }

      // Navigate to dashboard
      navigate('/dashboard');
      
      return { success: true, data };
      
    } catch (error) {
      Logger.error('Login failed:', error, {
        email: formData.email,
        status: error?.response?.status
      });
      
      return { 
        success: false, 
        errors: { 
          general: error.message || 'Invalid email or password. Please try again.' 
        } 
      };
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link to="/register" className="font-medium text-blue-600 hover:text-blue-500">
              create a new account
            </Link>
          </p>
        </div>
        
        <EnhancedForm
          formId="login-form"
          initialData={initialData}
          validationRules={{
            email: validationRules.email,
            password: validationRules.password
          }}
          onSubmit={handleSubmit}
          className="mt-8 space-y-6"
        >
          {({ formData, errors, loading, getInputProps, getFieldError }) => (
            <>
              <div className="space-y-4">
                <FormField
                  name="email"
                  label="Email address"
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
                  placeholder="Enter your password"
                  {...getInputProps('password')}
                  error={getFieldError('password')}
                />

                <div className="flex items-center justify-between">
                  <FormField
                    name="remember"
                    label="Remember me"
                    type="checkbox"
                    {...getInputProps('remember')}
                    error={getFieldError('remember')}
                  />

                  <div className="text-sm">
                    <Link to="/forgot-password" className="font-medium text-blue-600 hover:text-blue-500">
                      Forgot your password?
                    </Link>
                  </div>
                </div>
              </div>
            </>
          )}
        </EnhancedForm>
      </div>
    </div>
  );
};

Login.propTypes = {
  onLogin: PropTypes.func,
};

Login.defaultProps = {
  onLogin: null,
};

export default Login;
