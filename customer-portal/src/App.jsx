import React, { Suspense, lazy, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { registerServiceWorker } from './utils/serviceWorker';
import { initializeCriticalRenderingPath } from './utils/criticalRenderingPath';
import { memoryOptimizer } from './utils/memoryOptimizer';
import { networkOptimizer } from './utils/networkOptimizer';
import Logger from './utils/logger-simple';
import { NotificationProvider } from './components/NotificationSystem';
import { FeatureFlagProvider } from './contexts/FeatureFlagContext';
import { globalErrorHandler } from './utils/globalErrorHandler';

// Import lazy components for optimized code splitting
import {
  LazyDashboard,
  LazyTickets,
  LazyTicketDetail,
  LazyNewTicket,
  LazyKnowledgeBase,
  LazyProfile,
  LazyLogin,
  LazyRegister,
  LazyLiveChat,
  LazyErrorBoundary,
  LazyPerformanceDashboard
} from './components/LazyComponents';

// Import ErrorBoundary for error handling
import ErrorBoundary from './components/ErrorBoundary';

// Layout component - Keep non-lazy as it's always needed
const Layout = lazy(() => import('./components/Layout'));

// Create React Query client with optimized configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      retry: 1,
      retryDelay: 1000,
    },
  },
});

import LoadingSpinner from './components/LoadingSpinner.jsx';

// Main App component
function App() {
  // Initialize performance optimizations
  useEffect(() => {
    // Initialize critical rendering path optimizations
    initializeCriticalRenderingPath({
      preloadResources: true,
      preloadFonts: true,
      prefetchPages: true,
      addResourceHints: true,
      optimizeFonts: true,
      deferResources: true,
      inlineCriticalCSS: true,
      loadNonCriticalCSS: true,
      optimizeImages: true,
      implementLazyLoading: true,
      optimizeJS: true
    });

    // Initialize memory optimization
    memoryOptimizer.startTracking(5000); // Track memory every 5 seconds
    memoryOptimizer.monitorGC({
      interval: 10000, // Check every 10 seconds
      threshold: 0.8, // 80% memory usage threshold
      enableLogging: true
    });

    // Initialize network optimization
    networkOptimizer.addPerformanceObserver((metrics) => {
      Logger.info('Network performance metrics:', metrics);
    });

    // Register service worker for offline support
    registerServiceWorker().catch(error => {
      Logger.error('Service worker registration failed:', error);
    });

    // Initialize global error handler
    globalErrorHandler.initialize();

    // Log performance metrics
    Logger.info('App initialized with performance optimizations');
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      memoryOptimizer.stopTracking();
      networkOptimizer.clearAllCaches();
    };
  }, []);

  return (
      <QueryClientProvider client={queryClient}>
            <Router>
              <div className="App">
          <FeatureFlagProvider>
            <NotificationProvider>
              <ErrorBoundary>
              <Suspense fallback={<LoadingSpinner />}>
                <Routes>
                  <Route path="/login" element={<LazyLogin />} />
                  <Route path="/register" element={<LazyRegister />} />
                  <Route path="/" element={<Layout />}>
                    <Route index element={<Navigate to="/dashboard" replace />} />
                    <Route path="dashboard" element={<LazyDashboard />} />
                    <Route path="tickets" element={<LazyTickets />} />
                    <Route path="tickets/:id" element={<LazyTicketDetail />} />
                    <Route path="new-ticket" element={<LazyNewTicket />} />
                    <Route path="knowledge-base" element={<LazyKnowledgeBase />} />
                    <Route path="profile" element={<LazyProfile />} />
                    <Route path="performance" element={<LazyPerformanceDashboard />} />
                  </Route>
                </Routes>
              </Suspense>
              
              {/* Live Chat Component */}
              <Suspense fallback={null}>
                <LazyLiveChat />
              </Suspense>
              
              {/* Toast Notifications */}
                  <Toaster
                    position="top-right"
                    toastOptions={{
                      duration: 4000,
                      style: {
                        background: '#363636',
                        color: '#fff',
                      },
                  success: {
                    duration: 3000,
                    iconTheme: {
                      primary: '#4CAF50',
                      secondary: '#fff',
                    },
                  },
                  error: {
                    duration: 5000,
                    iconTheme: {
                      primary: '#F44336',
                      secondary: '#fff',
                    },
                  },
                }}
              />
            </ErrorBoundary>
            </NotificationProvider>
          </FeatureFlagProvider>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;