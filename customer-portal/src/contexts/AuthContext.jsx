import React, { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';
import Logger from '../utils/logger';

/**
 * Authentication context for managing user authentication state
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
 * Authentication provider component
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
  const initializeAuth = async () => {
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
      setError('Failed to initialize authentication');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Login user - Memoized to prevent unnecessary re-renders
   * @param {Object} userData - User data from login
   * @param {string} token - Authentication token
   */
  const login = useCallback((userData, token) => {
    setUser(userData);
    localStorage.setItem('authToken', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setError(null);
    
    Logger.info('User logged in successfully', {
      userId: userData.id,
      email: userData.email
    });
    
    Logger.userAction('login', {
      userId: userData.id,
      email: userData.email
    });
  }, []);

  /**
   * Logout user - Memoized to prevent unnecessary re-renders
   */
  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    setError(null);
    
    Logger.info('User logged out');
    Logger.userAction('logout', {});
  }, []);

  /**
   * Update user data - Memoized to prevent unnecessary re-renders
   * @param {Object} userData - Updated user data
   */
  const updateUser = useCallback((userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
    
    Logger.info('User data updated', {
      userId: userData.id,
      email: userData.email
    });
  }, []);

  /**
   * Set authentication error - Memoized to prevent unnecessary re-renders
   * @param {string} errorMessage - Error message
   */
  const setAuthError = useCallback((errorMessage) => {
    setError(errorMessage);
    Logger.error('Authentication error:', new Error(errorMessage));
  }, []);

  /**
   * Clear authentication error - Memoized to prevent unnecessary re-renders
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Memoize the context value to prevent unnecessary re-renders
  const value = useMemo(() => ({
    user,
    loading,
    error,
    login,
    logout,
    updateUser,
    setAuthError,
    clearError,
    isAuthenticated: !!user
  }), [user, loading, error, login, logout, updateUser, setAuthError, clearError]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export default AuthContext;
