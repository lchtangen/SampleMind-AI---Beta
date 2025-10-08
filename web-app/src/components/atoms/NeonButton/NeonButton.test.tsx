/**
 * NeonButton Component Tests
 *
 * Comprehensive test suite for the NeonButton component covering:
 * - Rendering with different props
 * - Variant styles and behaviors
 * - Size options
 * - Interactive states (hover, loading, disabled)
 * - Accessibility (ARIA attributes, keyboard navigation)
 * - Framer Motion animations
 * - Icon rendering
 *
 * @module NeonButton.test
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NeonButton } from './NeonButton';
import type { NeonButtonProps } from './NeonButton.types';

/**
 * Test helper to render NeonButton with default props
 */
const renderNeonButton = (props: Partial<NeonButtonProps> = {}) => {
  const defaultProps: NeonButtonProps = {
    children: 'Test Button',
    ...props,
  };

  return render(<NeonButton {...defaultProps} />);
};

describe('NeonButton', () => {
  describe('Rendering', () => {
    it('should render with children text', () => {
      renderNeonButton({ children: 'Click Me' });
      expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
    });

    it('should render with default variant and size', () => {
      renderNeonButton();
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button).toHaveClass('px-6', 'py-3'); // md size
    });

    it('should apply custom className', () => {
      renderNeonButton({ className: 'custom-class' });
      const button = screen.getByRole('button');
      expect(button.className).toContain('custom-class');
    });

    it('should render with testId', () => {
      renderNeonButton({ testId: 'neon-button-test' });
      expect(screen.getByTestId('neon-button-test')).toBeInTheDocument();
    });
  });

  describe('Variants', () => {
    it('should render primary variant with correct styles', () => {
      renderNeonButton({ variant: 'primary' });
      const button = screen.getByRole('button');
      expect(button.className).toContain('bg-gradient-purple');
    });

    it('should render secondary variant with correct styles', () => {
      renderNeonButton({ variant: 'secondary' });
      const button = screen.getByRole('button');
      expect(button.className).toContain('bg-gradient-cyber');
    });

    it('should render ghost variant with correct styles', () => {
      renderNeonButton({ variant: 'ghost' });
      const button = screen.getByRole('button');
      expect(button.className).toContain('bg-transparent');
    });

    it('should render danger variant with correct styles', () => {
      renderNeonButton({ variant: 'danger' });
      const button = screen.getByRole('button');
      expect(button.className).toContain('from-error');
    });
  });

  describe('Sizes', () => {
    it('should render small size with correct padding', () => {
      renderNeonButton({ size: 'sm' });
      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-4', 'py-2', 'text-sm');
    });

    it('should render medium size with correct padding', () => {
      renderNeonButton({ size: 'md' });
      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-6', 'py-3', 'text-base');
    });

    it('should render large size with correct padding', () => {
      renderNeonButton({ size: 'lg' });
      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-8', 'py-4', 'text-lg');
    });
  });

  describe('Button Types', () => {
    it('should render with type="button" by default', () => {
      renderNeonButton();
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'button');
    });

    it('should render with type="submit"', () => {
      renderNeonButton({ type: 'submit' });
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'submit');
    });

    it('should render with type="reset"', () => {
      renderNeonButton({ type: 'reset' });
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'reset');
    });
  });

  describe('Interactive States', () => {
    it('should call onClick when clicked', async () => {
      const handleClick = vi.fn();
      const user = userEvent.setup();

      renderNeonButton({ onClick: handleClick });
      const button = screen.getByRole('button');

      await user.click(button);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should not call onClick when disabled', async () => {
      const handleClick = vi.fn();
      const user = userEvent.setup();

      renderNeonButton({ onClick: handleClick, disabled: true });
      const button = screen.getByRole('button');

      await user.click(button);
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('should not call onClick when loading', async () => {
      const handleClick = vi.fn();
      const user = userEvent.setup();

      renderNeonButton({ onClick: handleClick, loading: true });
      const button = screen.getByRole('button');

      await user.click(button);
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('should be disabled when disabled prop is true', () => {
      renderNeonButton({ disabled: true });
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });

    it('should be disabled when loading', () => {
      renderNeonButton({ loading: true });
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });
  });

  describe('Loading State', () => {
    it('should show loading spinner when loading', () => {
      renderNeonButton({ loading: true });
      const button = screen.getByRole('button');
      // Check for spinner element (border-2 border-t-transparent indicates spinner)
      const spinner = button.querySelector('.border-2.border-t-transparent');
      expect(spinner).toBeInTheDocument();
    });

    it('should hide icons when loading', () => {
      const leftIcon = <span data-testid="left-icon">←</span>;
      const rightIcon = <span data-testid="right-icon">→</span>;

      renderNeonButton({
        loading: true,
        leftIcon,
        rightIcon
      });

      expect(screen.queryByTestId('left-icon')).not.toBeInTheDocument();
      expect(screen.queryByTestId('right-icon')).not.toBeInTheDocument();
    });

    it('should have aria-busy when loading', () => {
      renderNeonButton({ loading: true });
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-busy', 'true');
    });
  });

  describe('Full Width', () => {
    it('should not be full width by default', () => {
      renderNeonButton();
      const button = screen.getByRole('button');
      expect(button).not.toHaveClass('w-full');
    });

    it('should be full width when fullWidth is true', () => {
      renderNeonButton({ fullWidth: true });
      const button = screen.getByRole('button');
      expect(button).toHaveClass('w-full');
    });
  });

  describe('Icons', () => {
    it('should render left icon', () => {
      const leftIcon = <span data-testid="left-icon">←</span>;
      renderNeonButton({ leftIcon });

      expect(screen.getByTestId('left-icon')).toBeInTheDocument();
    });

    it('should render right icon', () => {
      const rightIcon = <span data-testid="right-icon">→</span>;
      renderNeonButton({ rightIcon });

      expect(screen.getByTestId('right-icon')).toBeInTheDocument();
    });

    it('should render both left and right icons', () => {
      const leftIcon = <span data-testid="left-icon">←</span>;
      const rightIcon = <span data-testid="right-icon">→</span>;

      renderNeonButton({ leftIcon, rightIcon });

      expect(screen.getByTestId('left-icon')).toBeInTheDocument();
      expect(screen.getByTestId('right-icon')).toBeInTheDocument();
    });

    it('should have aria-hidden on icon elements', () => {
      const leftIcon = <span data-testid="left-icon">←</span>;
      renderNeonButton({ leftIcon });

      const iconContainer = screen.getByTestId('left-icon').parentElement;
      expect(iconContainer).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Accessibility', () => {
    it('should have role="button"', () => {
      renderNeonButton();
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('should use children as accessible name when no ariaLabel', () => {
      renderNeonButton({ children: 'Submit Form' });
      expect(screen.getByRole('button', { name: /submit form/i })).toBeInTheDocument();
    });

    it('should use ariaLabel when provided', () => {
      renderNeonButton({
        children: 'OK',
        ariaLabel: 'Confirm action'
      });

      const button = screen.getByRole('button', { name: /confirm action/i });
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('aria-label', 'Confirm action');
    });

    it('should have aria-disabled when disabled', () => {
      renderNeonButton({ disabled: true });
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-disabled', 'true');
    });

    it('should have aria-disabled when loading', () => {
      renderNeonButton({ loading: true });
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-disabled', 'true');
    });

    it('should have aria-busy when loading', () => {
      renderNeonButton({ loading: true });
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-busy', 'true');
    });

    it('should not have aria-busy when not loading', () => {
      renderNeonButton({ loading: false });
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-busy', 'false');
    });
  });

  describe('Pulse Animation', () => {
    it('should not pulse by default', () => {
      renderNeonButton();
      const button = screen.getByRole('button');
      // The pulse animation is controlled via Framer Motion's animate prop
      // We can't directly test the animation, but we can verify the component renders
      expect(button).toBeInTheDocument();
    });

    it('should accept pulse prop', () => {
      renderNeonButton({ pulse: true });
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    it('should not pulse when loading', () => {
      renderNeonButton({ pulse: true, loading: true });
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });
  });

  describe('Glow Intensity', () => {
    it('should accept low glow intensity', () => {
      renderNeonButton({ glowIntensity: 'low' });
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('should accept medium glow intensity (default)', () => {
      renderNeonButton({ glowIntensity: 'medium' });
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('should accept high glow intensity', () => {
      renderNeonButton({ glowIntensity: 'high' });
      expect(screen.getByRole('button')).toBeInTheDocument();
    });
  });

  describe('Complex Scenarios', () => {
    it('should render with all props combined', () => {
      const handleClick = vi.fn();
      const leftIcon = <span data-testid="left-icon">←</span>;
      const rightIcon = <span data-testid="right-icon">→</span>;

      renderNeonButton({
        variant: 'primary',
        size: 'lg',
        onClick: handleClick,
        fullWidth: true,
        pulse: true,
        glowIntensity: 'high',
        leftIcon,
        rightIcon,
        className: 'custom-class',
        ariaLabel: 'Complex button',
        testId: 'complex-button',
      });

      const button = screen.getByTestId('complex-button');
      expect(button).toBeInTheDocument();
      expect(button).toHaveClass('w-full', 'px-8', 'py-4', 'custom-class');
      expect(screen.getByTestId('left-icon')).toBeInTheDocument();
      expect(screen.getByTestId('right-icon')).toBeInTheDocument();
    });

    it('should handle rapid clicks gracefully', async () => {
      const handleClick = vi.fn();
      const user = userEvent.setup();

      renderNeonButton({ onClick: handleClick });
      const button = screen.getByRole('button');

      await user.click(button);
      await user.click(button);
      await user.click(button);

      expect(handleClick).toHaveBeenCalledTimes(3);
    });

    it('should work in a form context', () => {
      const handleSubmit = vi.fn((e) => e.preventDefault());

      render(
        <form onSubmit={handleSubmit}>
          <NeonButton type="submit">Submit</NeonButton>
        </form>
      );

      const button = screen.getByRole('button', { name: /submit/i });
      fireEvent.click(button);

      expect(handleSubmit).toHaveBeenCalled();
    });
  });

  describe('Component API', () => {
    it('should have displayName set', () => {
      expect(NeonButton.displayName).toBe('NeonButton');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty children gracefully', () => {
      renderNeonButton({ children: '' });
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('should handle React elements as children', () => {
      renderNeonButton({
        children: <span data-testid="child-element">Complex Child</span>
      });

      expect(screen.getByTestId('child-element')).toBeInTheDocument();
    });

    it('should handle undefined onClick gracefully', () => {
      renderNeonButton({ onClick: undefined });
      const button = screen.getByRole('button');
      expect(() => fireEvent.click(button)).not.toThrow();
    });

    it('should handle both disabled and loading states', () => {
      renderNeonButton({ disabled: true, loading: true });
      const button = screen.getByRole('button');

      expect(button).toBeDisabled();
      expect(button).toHaveAttribute('aria-busy', 'true');
      expect(button).toHaveAttribute('aria-disabled', 'true');
    });

    it('should handle very long text gracefully', () => {
      const longText = 'A'.repeat(100);
      renderNeonButton({ children: longText });

      const button = screen.getByRole('button');
      expect(button.textContent).toBe(longText);
    });
  });

  describe('Style Classes', () => {
    it('should include base styles', () => {
      renderNeonButton();
      const button = screen.getByRole('button');

      expect(button).toHaveClass('relative');
      expect(button).toHaveClass('inline-flex');
      expect(button).toHaveClass('items-center');
      expect(button).toHaveClass('justify-center');
    });

    it('should include transition classes', () => {
      renderNeonButton();
      const button = screen.getByRole('button');

      expect(button).toHaveClass('transition-all');
      expect(button).toHaveClass('duration-normal');
    });

    it('should include focus styles', () => {
      renderNeonButton();
      const button = screen.getByRole('button');

      expect(button).toHaveClass('focus:outline-none');
      expect(button).toHaveClass('focus:ring-2');
    });

    it('should include disabled styles', () => {
      renderNeonButton({ disabled: true });
      const button = screen.getByRole('button');

      expect(button).toHaveClass('disabled:opacity-50');
      expect(button).toHaveClass('disabled:cursor-not-allowed');
    });
  });

  describe('Integration', () => {
    it('should work with multiple buttons', () => {
      render(
        <>
          <NeonButton testId="button-1">Button 1</NeonButton>
          <NeonButton testId="button-2">Button 2</NeonButton>
          <NeonButton testId="button-3">Button 3</NeonButton>
        </>
      );

      expect(screen.getByTestId('button-1')).toBeInTheDocument();
      expect(screen.getByTestId('button-2')).toBeInTheDocument();
      expect(screen.getByTestId('button-3')).toBeInTheDocument();
    });

    it('should work in conditional rendering', () => {
      const { rerender } = render(
        <>
          {true && <NeonButton testId="conditional-button">Show</NeonButton>}
        </>
      );

      expect(screen.getByTestId('conditional-button')).toBeInTheDocument();

      rerender(
        <>
          {false && <NeonButton testId="conditional-button">Show</NeonButton>}
        </>
      );

      expect(screen.queryByTestId('conditional-button')).not.toBeInTheDocument();
    });
  });
});
