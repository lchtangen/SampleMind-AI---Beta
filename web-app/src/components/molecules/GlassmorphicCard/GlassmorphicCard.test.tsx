/**
 * GlassmorphicCard Component Tests
 *
 * Comprehensive test suite covering rendering, props, accessibility,
 * and user interactions.
 *
 * @module GlassmorphicCard.test
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { GlassmorphicCard } from './GlassmorphicCard';
import type { GlassmorphicCardProps } from './GlassmorphicCard.types';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

/**
 * Default props for testing
 */
const defaultProps: GlassmorphicCardProps = {
  title: 'Test Card Title',
  description: 'Test card description with some content',
};

/**
 * Helper function to render component with default props
 */
const renderCard = (props: Partial<GlassmorphicCardProps> = {}) => {
  return render(<GlassmorphicCard {...defaultProps} {...props} />);
};

describe('GlassmorphicCard', () => {
  describe('Rendering', () => {
    it('renders with required props', () => {
      renderCard();

      expect(screen.getByText(defaultProps.title)).toBeInTheDocument();
      expect(screen.getByText(defaultProps.description)).toBeInTheDocument();
    });

    it('renders as article element when not interactive', () => {
      const { container } = renderCard();

      const article = container.querySelector('article');
      expect(article).toBeInTheDocument();
    });

    it('renders as div with role=button when interactive', () => {
      const onClick = vi.fn();
      renderCard({ onClick });

      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button.tagName).toBe('DIV');
    });

    it('applies custom className', () => {
      const customClass = 'custom-test-class';
      const { container } = renderCard({ className: customClass });

      const card = container.firstChild as HTMLElement;
      expect(card.className).toContain(customClass);
    });

    it('renders with testId', () => {
      const testId = 'test-card-id';
      renderCard({ testId });

      expect(screen.getByTestId(testId)).toBeInTheDocument();
    });
  });

  describe('Icon Rendering', () => {
    it('renders without icon when not provided', () => {
      const { container } = renderCard();

      // Check that no icon is rendered by looking for the icon container with flex-shrink-0 class
      const iconContainer = container.querySelector('.flex-shrink-0');
      expect(iconContainer).not.toBeInTheDocument();
    });

    it('renders with icon when provided', () => {
      const IconComponent = () => <svg data-testid="test-icon" />;
      renderCard({ icon: <IconComponent /> });

      expect(screen.getByTestId('test-icon')).toBeInTheDocument();
    });

    it('marks icon as aria-hidden', () => {
      const IconComponent = () => <svg data-testid="test-icon" />;
      const { container } = renderCard({ icon: <IconComponent /> });

      const iconContainer = screen.getByTestId('test-icon').parentElement;
      expect(iconContainer).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Accessibility', () => {
    it('has no accessibility violations in default state', async () => {
      const { container } = renderCard();
      const results = await axe(container);

      expect(results).toHaveNoViolations();
    });

    it('has no accessibility violations in interactive state', async () => {
      const onClick = vi.fn();
      const { container } = renderCard({ onClick });
      const results = await axe(container);

      expect(results).toHaveNoViolations();
    });

    it('uses title as aria-label when ariaLabel not provided', () => {
      renderCard();

      const card = screen.getByLabelText(defaultProps.title);
      expect(card).toBeInTheDocument();
    });

    it('uses custom ariaLabel when provided', () => {
      const ariaLabel = 'Custom accessibility label';
      renderCard({ ariaLabel });

      const card = screen.getByLabelText(ariaLabel);
      expect(card).toBeInTheDocument();
    });

    it('has role=button when interactive', () => {
      const onClick = vi.fn();
      renderCard({ onClick });

      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('is keyboard accessible when interactive', () => {
      const onClick = vi.fn();
      renderCard({ onClick });

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('tabIndex', '0');
    });

    it('has aria-pressed attribute when interactive', () => {
      const onClick = vi.fn();
      renderCard({ onClick });

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-pressed', 'false');
    });
  });

  describe('User Interactions - Mouse', () => {
    it('calls onClick when clicked', () => {
      const onClick = vi.fn();
      renderCard({ onClick });

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(onClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when not interactive', () => {
      const onClick = vi.fn();
      // Render without onClick to make it non-interactive
      const { container } = renderCard();

      const card = container.firstChild as HTMLElement;
      fireEvent.click(card);

      expect(onClick).not.toHaveBeenCalled();
    });

    it('applies cursor-pointer class when interactive', () => {
      const onClick = vi.fn();
      const { container } = renderCard({ onClick });

      const button = container.firstChild as HTMLElement;
      expect(button.className).toContain('cursor-pointer');
    });

    it('does not apply cursor-pointer when not interactive', () => {
      const { container } = renderCard();

      const card = container.firstChild as HTMLElement;
      expect(card.className).not.toContain('cursor-pointer');
    });
  });

  describe('User Interactions - Keyboard', () => {
    it('calls onClick when Enter key is pressed', async () => {
      const onClick = vi.fn();
      const user = userEvent.setup();
      renderCard({ onClick });

      const button = screen.getByRole('button');
      button.focus();
      await user.keyboard('{Enter}');

      expect(onClick).toHaveBeenCalledTimes(1);
    });

    it('calls onClick when Space key is pressed', async () => {
      const onClick = vi.fn();
      const user = userEvent.setup();
      renderCard({ onClick });

      const button = screen.getByRole('button');
      button.focus();
      await user.keyboard(' ');

      expect(onClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick for other keys', async () => {
      const onClick = vi.fn();
      const user = userEvent.setup();
      renderCard({ onClick });

      const button = screen.getByRole('button');
      button.focus();
      await user.keyboard('{Escape}');
      await user.keyboard('a');

      expect(onClick).not.toHaveBeenCalled();
    });

    it('prevents default behavior on Space key', () => {
      const onClick = vi.fn();
      renderCard({ onClick });

      const button = screen.getByRole('button');
      const event = new KeyboardEvent('keydown', {
        key: ' ',
        bubbles: true,
        cancelable: true,
      });

      const preventDefaultSpy = vi.spyOn(event, 'preventDefault');
      button.dispatchEvent(event);

      expect(preventDefaultSpy).toHaveBeenCalled();
    });

    it('prevents default behavior on Enter key', () => {
      const onClick = vi.fn();
      renderCard({ onClick });

      const button = screen.getByRole('button');
      const event = new KeyboardEvent('keydown', {
        key: 'Enter',
        bubbles: true,
        cancelable: true,
      });

      const preventDefaultSpy = vi.spyOn(event, 'preventDefault');
      button.dispatchEvent(event);

      expect(preventDefaultSpy).toHaveBeenCalled();
    });
  });

  describe('Styling and Visual Effects', () => {
    it('applies glassmorphism styles', () => {
      const { container } = renderCard();
      const card = container.firstChild as HTMLElement;

      expect(card.className).toContain('backdrop-blur-xl');
      expect(card.className).toContain('bg-white/5');
      expect(card.className).toContain('border');
      expect(card.className).toContain('rounded-xl');
    });

    it('applies responsive padding classes', () => {
      const { container } = renderCard();
      const card = container.firstChild as HTMLElement;

      expect(card.className).toContain('p-6');
      expect(card.className).toContain('md:p-8');
    });

    it('applies transition classes', () => {
      const { container } = renderCard();
      const card = container.firstChild as HTMLElement;

      expect(card.className).toContain('transition-all');
      expect(card.className).toContain('duration-slow');
      expect(card.className).toContain('ease-out');
    });

    it('applies hover classes when interactive', () => {
      const onClick = vi.fn();
      const { container } = renderCard({ onClick });
      const card = container.firstChild as HTMLElement;

      expect(card.className).toContain('hover:scale-105');
      expect(card.className).toContain('active:scale-[1.02]');
    });

    it('does not apply hover classes when not interactive', () => {
      const { container } = renderCard();
      const card = container.firstChild as HTMLElement;

      expect(card.className).not.toContain('hover:scale-105');
    });

    it('applies focus styles when interactive', () => {
      const onClick = vi.fn();
      const { container } = renderCard({ onClick });
      const card = container.firstChild as HTMLElement;

      expect(card.className).toContain('focus:outline-none');
      expect(card.className).toContain('focus:ring-2');
      expect(card.className).toContain('focus:ring-primary');
    });

    it('renders interactive indicator when clickable', () => {
      const onClick = vi.fn();
      const { container } = renderCard({ onClick });

      // Check for SVG arrow indicator
      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });

    it('does not render interactive indicator when not clickable', () => {
      const { container } = renderCard();

      const article = container.querySelector('article');
      const svg = article?.querySelector('svg');
      expect(svg).not.toBeInTheDocument();
    });
  });

  describe('Typography', () => {
    it('applies correct heading styles to title', () => {
      renderCard();

      const title = screen.getByText(defaultProps.title);
      expect(title.tagName).toBe('H3');
      expect(title.className).toContain('font-heading');
      expect(title.className).toContain('font-semibold');
      expect(title.className).toContain('text-text-primary');
    });

    it('applies responsive text sizes to title', () => {
      renderCard();

      const title = screen.getByText(defaultProps.title);
      expect(title.className).toContain('text-xl');
      expect(title.className).toContain('md:text-2xl');
    });

    it('applies correct body styles to description', () => {
      renderCard();

      const description = screen.getByText(defaultProps.description);
      expect(description.tagName).toBe('P');
      expect(description.className).toContain('font-body');
      expect(description.className).toContain('text-text-secondary');
    });

    it('applies responsive text sizes to description', () => {
      renderCard();

      const description = screen.getByText(defaultProps.description);
      expect(description.className).toContain('text-base');
      expect(description.className).toContain('md:text-lg');
    });
  });

  describe('Edge Cases', () => {
    it('handles empty title gracefully', () => {
      renderCard({ title: '' });

      const title = screen.queryByRole('heading');
      expect(title).toBeInTheDocument();
      expect(title?.textContent).toBe('');
    });

    it('handles empty description gracefully', () => {
      const { container } = renderCard({ description: '' });

      // Find the paragraph element by its class instead of text content
      const description = container.querySelector('.font-body.text-base.md\\:text-lg');
      expect(description).toBeInTheDocument();
      expect(description?.textContent).toBe('');
    });

    it('handles long title text', () => {
      const longTitle = 'A'.repeat(200);
      renderCard({ title: longTitle });

      expect(screen.getByText(longTitle)).toBeInTheDocument();
    });

    it('handles long description text', () => {
      const longDescription = 'B'.repeat(500);
      renderCard({ description: longDescription });

      expect(screen.getByText(longDescription)).toBeInTheDocument();
    });

    it('handles special characters in title', () => {
      const specialTitle = '<script>alert("xss")</script>';
      renderCard({ title: specialTitle });

      expect(screen.getByText(specialTitle)).toBeInTheDocument();
    });

    it('handles special characters in description', () => {
      const specialDescription = '& < > " \' ™ © ®';
      renderCard({ description: specialDescription });

      expect(screen.getByText(specialDescription)).toBeInTheDocument();
    });

    it('handles multiple clicks rapidly', () => {
      const onClick = vi.fn();
      renderCard({ onClick });

      const button = screen.getByRole('button');

      // Simulate rapid clicks
      fireEvent.click(button);
      fireEvent.click(button);
      fireEvent.click(button);

      expect(onClick).toHaveBeenCalledTimes(3);
    });

    it('does not break with undefined className', () => {
      renderCard({ className: undefined });

      const { container } = renderCard({ className: undefined });
      const card = container.firstChild as HTMLElement;

      expect(card).toBeInTheDocument();
    });
  });

  describe('Component Display Name', () => {
    it('has correct display name', () => {
      expect(GlassmorphicCard.displayName).toBe('GlassmorphicCard');
    });
  });
});
