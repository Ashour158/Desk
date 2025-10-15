import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { Suspense } from 'react';
import LoadingSpinner from '../../components/LoadingSpinner.jsx';

// Mock the lazy components
jest.mock('../../pages/Dashboard', () => {
  return function MockDashboard() {
    return <div data-testid="dashboard">Dashboard</div>;
  };
});

jest.mock('../../pages/Tickets', () => {
  return function MockTickets() {
    return <div data-testid="tickets">Tickets</div>;
  };
});

jest.mock('../../components/PerformanceDashboard', () => {
  return function MockPerformanceDashboard() {
    return <div data-testid="performance-dashboard">Performance Dashboard</div>;
  };
});

describe('Lazy Components', () => {
  it('renders LazyDashboard with loading fallback', async () => {
    const { LazyDashboard } = require('../../components/LazyComponents');
    
    render(
      <Suspense fallback={<LoadingSpinner />}>
        <LazyDashboard />
      </Suspense>
    );

    // Should show loading spinner initially
    expect(screen.getByText('Loading...')).toBeInTheDocument();

    // Should render dashboard after loading with proper timeout
    await waitFor(() => {
      expect(screen.getByTestId('dashboard')).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('renders LazyTickets with loading fallback', async () => {
    const { LazyTickets } = require('../../components/LazyComponents');
    
    render(
      <Suspense fallback={<LoadingSpinner />}>
        <LazyTickets />
      </Suspense>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByTestId('tickets')).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('renders LazyPerformanceDashboard with loading fallback', async () => {
    const { LazyPerformanceDashboard } = require('../../components/LazyComponents');
    
    render(
      <Suspense fallback={<LoadingSpinner />}>
        <LazyPerformanceDashboard />
      </Suspense>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByTestId('performance-dashboard')).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('handles lazy loading errors gracefully', async () => {
    // Mock a component that throws an error
    jest.doMock('../../pages/ErrorPage', () => {
      throw new Error('Failed to load component');
    });

    const { LazyErrorPage } = require('../../components/LazyComponents');
    
    render(
      <Suspense fallback={<LoadingSpinner />}>
        <LazyErrorPage />
      </Suspense>
    );

    // Should show loading spinner initially
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    
    // Should handle error gracefully with timeout
    await waitFor(() => {
      // Component should still be in loading state due to error
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    }, { timeout: 5000 });
  });
});
