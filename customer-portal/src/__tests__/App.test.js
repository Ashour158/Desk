import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import App from '../App';

// Mock the lazy components
jest.mock('../components/LazyComponents', () => ({
  LazyDashboard: () => <div data-testid="dashboard">Dashboard</div>,
  LazyTickets: () => <div data-testid="tickets">Tickets</div>,
  LazyTicketDetail: () => <div data-testid="ticket-detail">Ticket Detail</div>,
  LazyNewTicket: () => <div data-testid="new-ticket">New Ticket</div>,
  LazyKnowledgeBase: () => <div data-testid="knowledge-base">Knowledge Base</div>,
  LazyProfile: () => <div data-testid="profile">Profile</div>,
  LazyLogin: () => <div data-testid="login">Login</div>,
  LazyRegister: () => <div data-testid="register">Register</div>,
  LazyLiveChat: () => <div data-testid="live-chat">Live Chat</div>,
  LazyErrorBoundary: ({ children }) => <div data-testid="error-boundary">{children}</div>,
  LazyPerformanceDashboard: () => <div data-testid="performance-dashboard">Performance Dashboard</div>
}));

// Mock the Layout component
jest.mock('../components/Layout', () => {
  return function MockLayout({ children }) {
    return <div data-testid="layout">{children}</div>;
  };
});

// Mock the LoadingSpinner component
jest.mock('../components/LoadingSpinner', () => {
  return function MockLoadingSpinner() {
    return <div data-testid="loading-spinner">Loading...</div>;
  };
});

// Mock utility functions
jest.mock('../utils/serviceWorker', () => ({
  registerServiceWorker: jest.fn()
}));

jest.mock('../utils/criticalRenderingPath', () => ({
  initializeCriticalRenderingPath: jest.fn()
}));

jest.mock('../utils/memoryOptimizer', () => ({
  memoryOptimizer: {
    startMonitoring: jest.fn(),
    stopMonitoring: jest.fn()
  }
}));

jest.mock('../utils/networkOptimizer', () => ({
  networkOptimizer: {
    startMonitoring: jest.fn(),
    stopMonitoring: jest.fn()
  }
}));

jest.mock('../utils/logger-simple', () => ({
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
}));

describe('App', () => {
  let queryClient;

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
  });

  afterEach(() => {
    // Clean up query client
    queryClient.clear();
    
    // Clean up any global state
    jest.clearAllMocks();
    
    // Clean up DOM
    document.body.innerHTML = '';
  });

  it('renders application without crashing', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    );
  });

  it('renders error boundary component for error handling', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    );

    expect(screen.getByTestId('error-boundary')).toBeInTheDocument();
  });

  it('renders main layout component for application structure', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    );

    expect(screen.getByTestId('layout')).toBeInTheDocument();
  });

  it('renders live chat component for customer support', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    );

    expect(screen.getByTestId('live-chat')).toBeInTheDocument();
  });

  it('renders toast notification container for user feedback', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    );

    // Toast container should be present
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('handles route navigation and redirects to dashboard by default', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    );

    // Should redirect to dashboard by default with proper timeout
    await waitFor(() => {
      expect(screen.getByTestId('dashboard')).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('initializes performance monitoring systems on application mount', () => {
    const { initializeCriticalRenderingPath } = require('../utils/criticalRenderingPath');
    const { memoryOptimizer } = require('../utils/memoryOptimizer');
    const { networkOptimizer } = require('../utils/networkOptimizer');

    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    );

    expect(initializeCriticalRenderingPath).toHaveBeenCalled();
    expect(memoryOptimizer.startMonitoring).toHaveBeenCalled();
    expect(networkOptimizer.startMonitoring).toHaveBeenCalled();
  });

  it('cleans up performance monitoring systems on application unmount', () => {
    const { memoryOptimizer } = require('../utils/memoryOptimizer');
    const { networkOptimizer } = require('../utils/networkOptimizer');

    const { unmount } = render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    );

    unmount();

    expect(memoryOptimizer.stopMonitoring).toHaveBeenCalled();
    expect(networkOptimizer.stopMonitoring).toHaveBeenCalled();
  });
});
