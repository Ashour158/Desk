import React, { useState, useCallback, useEffect } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import PropTypes from 'prop-types';
import Logger from '../utils/logger';

/**
 * Enhanced Layout component with accessibility, mobile navigation, and keyboard support
 * @param {Object} props - Component props
 */
const Layout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [focusedElement, setFocusedElement] = useState(null);

  /**
   * Handle logout action with accessibility
   */
  const handleLogout = useCallback(() => {
    Logger.userAction('logout', {});
    // Clear authentication data
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    // Redirect to login
    navigate('/login');
  }, [navigate]);

  /**
   * Handle keyboard navigation
   */
  const handleKeyDown = useCallback((e) => {
    switch (e.key) {
      case 'Enter':
      case ' ':
        if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A') {
          e.target.click();
        }
        break;
      case 'Escape':
        if (isMobileMenuOpen) {
          setIsMobileMenuOpen(false);
          // Return focus to menu button
          const menuButton = document.querySelector('[aria-controls="mobile-menu"]');
          if (menuButton) menuButton.focus();
        }
        break;
      case 'Tab':
        // Handle tab navigation within mobile menu
        if (isMobileMenuOpen) {
          const menuItems = document.querySelectorAll('#mobile-menu a, #mobile-menu button');
          const firstItem = menuItems[0];
          const lastItem = menuItems[menuItems.length - 1];
          
          if (e.shiftKey && document.activeElement === firstItem) {
            e.preventDefault();
            lastItem.focus();
          } else if (!e.shiftKey && document.activeElement === lastItem) {
            e.preventDefault();
            firstItem.focus();
          }
        }
        break;
    }
  }, [isMobileMenuOpen]);

  /**
   * Toggle mobile menu with accessibility
   */
  const toggleMobileMenu = useCallback(() => {
    setIsMobileMenuOpen(prev => !prev);
  }, []);

  /**
   * Close mobile menu
   */
  const closeMobileMenu = useCallback(() => {
    setIsMobileMenuOpen(false);
  }, []);

  /**
   * Handle focus management
   */
  useEffect(() => {
    if (isMobileMenuOpen) {
      // Focus first menu item when menu opens
      const firstMenuItem = document.querySelector('#mobile-menu a, #mobile-menu button');
      if (firstMenuItem) {
        firstMenuItem.focus();
      }
    }
  }, [isMobileMenuOpen]);

  /**
   * Close mobile menu when route changes
   */
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  /**
   * Handle escape key globally
   */
  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Skip to main content link */}
      <a 
        href="#main-content" 
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-blue-600 text-white px-4 py-2 rounded z-50"
        onFocus={() => setFocusedElement('skip-link')}
      >
        Skip to main content
      </a>

      {/* Navigation Header */}
      <nav 
        className="bg-white shadow-sm border-b" 
        role="navigation" 
        aria-label="Main navigation"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Logo and Desktop Navigation */}
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Link 
                  to="/dashboard" 
                  className="text-xl font-bold text-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
                  aria-label="HelpDesk Portal - Go to Dashboard"
                >
                  HelpDesk Portal
                </Link>
              </div>
              
              {/* Desktop Navigation */}
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8" role="menubar">
                <Link
                  to="/dashboard"
                  className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
                  role="menuitem"
                  aria-current={location.pathname === '/dashboard' ? 'page' : undefined}
                >
                  Dashboard
                </Link>
                <Link
                  to="/tickets"
                  className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
                  role="menuitem"
                  aria-current={location.pathname === '/tickets' ? 'page' : undefined}
                >
                  My Tickets
                </Link>
                <Link
                  to="/knowledge-base"
                  className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
                  role="menuitem"
                  aria-current={location.pathname === '/knowledge-base' ? 'page' : undefined}
                >
                  Knowledge Base
                </Link>
              </div>
            </div>

            {/* Mobile menu button and user actions */}
            <div className="flex items-center">
              {/* Mobile menu button */}
              <button
                className="sm:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
                aria-expanded={isMobileMenuOpen}
                aria-controls="mobile-menu"
                aria-label={isMobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
                onClick={toggleMobileMenu}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleMobileMenu();
                  }
                }}
              >
                <span className="sr-only">Open main menu</span>
                {isMobileMenuOpen ? (
                  <svg className="block h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                ) : (
                  <svg className="block h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                )}
              </button>

              {/* Logout button */}
              <div className="flex-shrink-0 ml-2">
                <button
                  onClick={handleLogout}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      handleLogout();
                    }
                  }}
                  className="bg-white p-2 rounded-full text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 min-h-[44px] min-w-[44px] flex items-center justify-center"
                  aria-label="Logout from your account"
                  title="Logout"
                >
                  <span className="sr-only">Logout</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          {/* Mobile Navigation Menu */}
          {isMobileMenuOpen && (
            <div 
              id="mobile-menu" 
              className="sm:hidden border-t border-gray-200"
              role="menu"
              aria-label="Mobile navigation menu"
            >
              <div className="px-2 pt-2 pb-3 space-y-1">
                <Link
                  to="/dashboard"
                  className="block px-3 py-2 rounded-md text-base font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  role="menuitem"
                  aria-current={location.pathname === '/dashboard' ? 'page' : undefined}
                  onClick={closeMobileMenu}
                >
                  Dashboard
                </Link>
                <Link
                  to="/tickets"
                  className="block px-3 py-2 rounded-md text-base font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  role="menuitem"
                  aria-current={location.pathname === '/tickets' ? 'page' : undefined}
                  onClick={closeMobileMenu}
                >
                  My Tickets
                </Link>
                <Link
                  to="/knowledge-base"
                  className="block px-3 py-2 rounded-md text-base font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  role="menuitem"
                  aria-current={location.pathname === '/knowledge-base' ? 'page' : undefined}
                  onClick={closeMobileMenu}
                >
                  Knowledge Base
                </Link>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main 
        id="main-content" 
        className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8"
        role="main"
        aria-label="Main content"
      >
        <div className="px-4 py-6 sm:px-0">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

Layout.propTypes = {
  children: PropTypes.node,
};

Layout.defaultProps = {
  children: null,
};

export default Layout;
