/**
 * Lazy-loaded components for code splitting
 * This file contains all lazy-loaded components to reduce bundle size
 */

import { lazy } from 'react';

// Page components - Lazy loaded for route-based code splitting
export const LazyDashboard = lazy(() => import('../pages/Dashboard'));
export const LazyTickets = lazy(() => import('../pages/Tickets'));
export const LazyTicketDetail = lazy(() => import('../pages/TicketDetail'));
export const LazyNewTicket = lazy(() => import('../pages/NewTicket'));
export const LazyKnowledgeBase = lazy(() => import('../pages/KnowledgeBase'));
export const LazyProfile = lazy(() => import('../pages/Profile'));
export const LazyLogin = lazy(() => import('../pages/Login'));
export const LazyRegister = lazy(() => import('../pages/Register'));

// Heavy components - Lazy loaded for performance
export const LazyPerformanceDashboard = lazy(() => import('./PerformanceDashboard'));
export const LazyVirtualizedTicketList = lazy(() => import('./VirtualizedTicketList'));
export const LazyEnhancedLazyImage = lazy(() => import('./LazyEnhancedLazyImage'));
export const LazyLiveChat = lazy(() => import('./LiveChat'));

// Form components - Lazy loaded when needed
export const LazyTicketForm = lazy(() => import('./TicketForm'));
export const LazyDebouncedSearchInput = lazy(() => import('./DebouncedSearchInput'));

// Utility components - Lazy loaded for specific features
export const LazyErrorBoundary = lazy(() => import('./LazyErrorBoundary'));
export const LazyOptimizedLazyImage = lazy(() => import('./OptimizedLazyImage'));

// Chart and visualization components - Lazy loaded for analytics
// export const LazyMetricsChart = lazy(() => import('./MetricsChart')); // Component not found
// export const LazyPerformanceChart = lazy(() => import('./PerformanceChart')); // Component not found

// Admin components - Lazy loaded for admin features
// export const LazyAdminPanel = lazy(() => import('./AdminPanel')); // Component not found
// export const LazyUserManagement = lazy(() => import('./UserManagement')); // Component not found
// export const LazySystemSettings = lazy(() => import('./SystemSettings')); // Component not found

// Export all lazy components
export default {
  // Pages
  LazyDashboard,
  LazyTickets,
  LazyTicketDetail,
  LazyNewTicket,
  LazyKnowledgeBase,
  LazyProfile,
  LazyLogin,
  LazyRegister,
  
  // Heavy components
  LazyPerformanceDashboard,
  LazyVirtualizedTicketList,
  LazyEnhancedLazyImage,
  LazyLiveChat,
  
  // Form components
  LazyTicketForm,
  LazyDebouncedSearchInput,
  
  // Utility components
  LazyErrorBoundary,
  LazyOptimizedLazyImage,
  
  // Chart components
  // LazyMetricsChart, // Component not found
  // LazyPerformanceChart, // Component not found
  
  // Admin components
  // LazyAdminPanel, // Component not found
  // LazyUserManagement, // Component not found
  // LazySystemSettings // Component not found
};
