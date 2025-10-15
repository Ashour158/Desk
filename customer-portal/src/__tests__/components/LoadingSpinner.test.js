import React from 'react';
import { render, screen } from '@testing-library/react';
import LoadingSpinner from '../../components/LoadingSpinner';

describe('LoadingSpinner', () => {
  it('renders with default props', () => {
    render(<LoadingSpinner />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders with custom text', () => {
    render(<LoadingSpinner text="Custom loading text" />);
    expect(screen.getByText('Custom loading text')).toBeInTheDocument();
  });

  it('applies size classes correctly', () => {
    const { rerender } = render(<LoadingSpinner size="small" />);
    expect(screen.getByTestId('loading-spinner')).toHaveClass('spinner-sm');

    rerender(<LoadingSpinner size="large" />);
    expect(screen.getByTestId('loading-spinner')).toHaveClass('spinner-lg');
  });

  it('applies color classes correctly', () => {
    const { rerender } = render(<LoadingSpinner color="primary" />);
    expect(screen.getByTestId('loading-spinner')).toHaveClass('spinner-primary');

    rerender(<LoadingSpinner color="secondary" />);
    expect(screen.getByTestId('loading-spinner')).toHaveClass('spinner-secondary');
  });

  it('applies custom className', () => {
    render(<LoadingSpinner className="custom-class" />);
    expect(screen.getByTestId('loading-spinner')).toHaveClass('custom-class');
  });

  it('renders without text when text prop is empty', () => {
    render(<LoadingSpinner text="" />);
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
  });

  it('passes through additional props', () => {
    render(<LoadingSpinner data-testid="loading-spinner" />);
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });
});
