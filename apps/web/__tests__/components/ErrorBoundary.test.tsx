/**
 * Tests for ErrorBoundary Component
 * Tests error handling and recovery
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import ErrorBoundary from '@/components/ErrorBoundary';

// Component that throws an error
const ThrowError = () => {
  throw new Error('Test error');
};

// Safe component
const SafeComponent = () => <div>Safe content</div>;

describe('ErrorBoundary', () => {
  // Suppress console.error for these tests
  beforeEach(() => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <SafeComponent />
      </ErrorBoundary>
    );
    expect(screen.getByText('Safe content')).toBeInTheDocument();
  });

  test('renders error UI when child component throws', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );
    // Error boundary should display error message
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
  });

  test('displays error details', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );
    const errorText = screen.getByText(/Test error/i);
    expect(errorText).toBeInTheDocument();
  });

  test('provides recovery button', () => {
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );
    expect(screen.getByText(/reset/i)).toBeInTheDocument();
  });

  test('recovers from error when reset', () => {
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    // Rerender with safe component
    rerender(
      <ErrorBoundary>
        <SafeComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText('Safe content')).toBeInTheDocument();
  });
});
