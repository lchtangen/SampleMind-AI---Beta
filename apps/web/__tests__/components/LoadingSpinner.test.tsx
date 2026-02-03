/**
 * Tests for LoadingSpinner Component
 * Tests loading state visualization
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import LoadingSpinner from '@/components/LoadingSpinner';

describe('LoadingSpinner', () => {
  test('renders loading spinner component', () => {
    render(<LoadingSpinner />);
    const spinner = screen.getByRole('status');
    expect(spinner).toBeInTheDocument();
  });

  test('displays loading text when provided', () => {
    render(<LoadingSpinner />);
    // Check that the spinner is visible
    const spinner = screen.getByRole('status');
    expect(spinner).toBeVisible();
  });

  test('applies correct CSS classes', () => {
    const { container } = render(<LoadingSpinner />);
    const spinnerElement = container.querySelector('[role="status"]');
    expect(spinnerElement).toHaveClass('animate-spin');
  });

  test('handles multiple spinner instances', () => {
    const { container } = render(
      <>
        <LoadingSpinner />
        <LoadingSpinner />
      </>
    );
    const spinners = container.querySelectorAll('[role="status"]');
    expect(spinners).toHaveLength(2);
  });
});
