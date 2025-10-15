import React, { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';
import Logger from '../utils/logger';

/**
 * Optimized Authentication context with memoization to prevent unnecessary re-renders
 */
const AuthContext = createContext();

/**
 * Custom hook to use authentication context
 * @returns {Object} Authentication context value
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

/**
 * Optimized Authentication provider component with memoization
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    initializeAuth();
  }, []);

  /**
   * Initialize authentication state
   */
  const initializeAuth = useCallback(async () => {
    try {
      const token = localStorage.getItem('authToken');
      const userData = localStorage.getItem('user');

      if (token && userData) {
        // Verify token with backend
        const response = await fetch('/api/v1/auth/verify/', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const user = JSON.parse(userData);
          setUser(user);
          Logger.info('User authenticated from stored token', {
            userId: user.id,
            email: user.email
          });
        } else {
          // Token is invalid, clear storage
          localStorage.removeItem('authToken');
          localStorage.removeItem('user');
          Logger.warn('Invalid token found, clearing authentication');
        }
      }
    } catch (error) {
      Logger.error('Authentication initialization failed:', error);
      setError('Authentication initialization failed');
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Login function with memoization
   */
  const login = useCallback(async (email, password) => {
    try {
      setLoading(true);
      setError(null);

      Logger.apiRequest('POST', '/api/v1/auth/login/');

      const response = await fetch('/api/v1/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
      });

      Logger.apiResponse('POST', '/api/v1/auth/login/', response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Store authentication data
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      setUser(data.user);
      
      Logger.info('User logged in successfully', {
        userId: data.user.id,
        email: data.user.email
      });

      return data;
    } catch (error) {
      Logger.error('Login failed:', error, {
        email,
        status: error?.response?.status
      });
      setError('Login failed. Please check your credentials.');
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Logout function with memoization
   */
  const logout = useCallback(() => {
    try {
      // Clear local storage
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      
      // Clear user state
      setUser(null);
      setError(null);
      
      Logger.info('User logged out successfully');
    } catch (error) {
      Logger.error('Logout failed:', error);
    }
  }, []);

  /**
   * Update user profile with memoization
   */
  const updateProfile = useCallback(async (profileData) => {
    try {
      setLoading(true);
      setError(null);

      Logger.apiRequest('PUT', '/api/v1/profile/');

      const response = await fetch('/api/v1/profile/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify(profileData)
      });

      Logger.apiResponse('PUT', '/api/v1/profile/', response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Update user state
      setUser(prevUser => ({
        ...prevUser,
        ...data
      }));
      
      // Update stored user data
      localStorage.setItem('user', JSON.stringify(data));
      
      Logger.info('Profile updated successfully', {
        userId: data.id,
        email: data.email
      });

      return data;
    } catch (error) {
      Logger.error('Profile update failed:', error, {
        status: error?.response?.status
      });
      setError('Profile update failed');
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Memoized context value to prevent unnecessary re-renders
   */
  const contextValue = useMemo(() => ({
    user,
    loading,
    error,
    login,
    logout,
    updateProfile,
    isAuthenticated: !!user
  }), [user, loading, error, login, logout, updateProfile]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired
};

export default AuthProvider;
