import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Component Interactions
 *
 * Tests user interactions with UI components including:
 * - Modal dialogs
 * - Forms and inputs
 * - Buttons and actions
 * - Cards and selections
 * - Navigation and routing
 * - Animations and transitions
 */

test.describe('Component Interactions', () => {
  test.beforeEach(async ({ page }) => {
    // Start from the home page
    await page.goto('/');
  });

  test.describe('Modal Interactions', () => {
    test('should open and close modal with button click', async ({ page }) => {
      // Click button to open modal
      await page.getByRole('button', { name: /open modal/i }).click();

      // Modal should be visible
      const modal = page.getByRole('dialog');
      await expect(modal).toBeVisible();

      // Check for backdrop
      await expect(page.locator('[data-testid="modal-backdrop"]')).toBeVisible();

      // Close with X button
      await page.getByRole('button', { name: /close/i }).click();

      // Modal should be hidden
      await expect(modal).not.toBeVisible();
    });

    test('should close modal with Escape key', async ({ page }) => {
      await page.getByRole('button', { name: /open modal/i }).click();

      const modal = page.getByRole('dialog');
      await expect(modal).toBeVisible();

      // Press Escape
      await page.keyboard.press('Escape');

      // Modal should close
      await expect(modal).not.toBeVisible();
    });

    test('should close modal by clicking backdrop', async ({ page }) => {
      await page.getByRole('button', { name: /open modal/i }).click();

      const modal = page.getByRole('dialog');
      await expect(modal).toBeVisible();

      // Click on backdrop (outside modal content)
      await page.locator('[data-testid="modal-backdrop"]').click({ position: { x: 10, y: 10 } });

      // Modal should close
      await expect(modal).not.toBeVisible();
    });

    test('should trap focus within modal', async ({ page }) => {
      await page.getByRole('button', { name: /open modal/i }).click();

      const modal = page.getByRole('dialog');
      await expect(modal).toBeVisible();

      // Get focusable elements in modal
      const firstButton = modal.getByRole('button').first();
      const lastButton = modal.getByRole('button').last();

      // Focus should start on first element
      await expect(firstButton).toBeFocused();

      // Tab to last element
      while (!(await lastButton.evaluate(el => el === document.activeElement))) {
        await page.keyboard.press('Tab');
      }

      // Tab should wrap to first element
      await page.keyboard.press('Tab');
      await expect(firstButton).toBeFocused();

      // Shift+Tab should wrap to last element
      await page.keyboard.press('Shift+Tab');
      await expect(lastButton).toBeFocused();
    });

    test('should animate modal entrance and exit', async ({ page }) => {
      await page.getByRole('button', { name: /open modal/i }).click();

      const modal = page.getByRole('dialog');

      // Check for entrance animation class
      await expect(modal).toHaveClass(/fade-in|slide-up|animate/);

      // Wait for animation to complete
      await page.waitForTimeout(500);

      // Close modal
      await page.getByRole('button', { name: /close/i }).click();

      // Check for exit animation
      await expect(modal).toHaveClass(/fade-out|slide-down|animate/);
    });

    test('should handle multiple modals', async ({ page }) => {
      // Open first modal
      await page.getByRole('button', { name: /open modal/i }).first().click();
      const firstModal = page.getByRole('dialog').first();
      await expect(firstModal).toBeVisible();

      // Open second modal from within first
      await firstModal.getByRole('button', { name: /open another/i }).click();
      const secondModal = page.getByRole('dialog').nth(1);
      await expect(secondModal).toBeVisible();

      // Both modals should be visible
      await expect(firstModal).toBeVisible();
      await expect(secondModal).toBeVisible();

      // Close second modal
      await secondModal.getByRole('button', { name: /close/i }).click();
      await expect(secondModal).not.toBeVisible();
      await expect(firstModal).toBeVisible();

      // Close first modal
      await firstModal.getByRole('button', { name: /close/i }).click();
      await expect(firstModal).not.toBeVisible();
    });
  });

  test.describe('Form Interactions', () => {
    test('should fill and submit a form', async ({ page }) => {
      await page.goto('/form-page');

      // Fill form fields
      await page.getByLabel(/name/i).fill('John Doe');
      await page.getByLabel(/email/i).fill('john@example.com');
      await page.getByLabel(/message/i).fill('This is a test message');

      // Select from dropdown
      await page.getByLabel(/category/i).selectOption('feedback');

      // Check checkbox
      await page.getByLabel(/agree/i).check();

      // Submit form
      await page.getByRole('button', { name: /submit/i }).click();

      // Check for success message
      await expect(page.getByText(/success/i)).toBeVisible();
    });

    test('should validate form fields in real-time', async ({ page }) => {
      await page.goto('/form-page');

      const emailInput = page.getByLabel(/email/i);

      // Enter invalid email
      await emailInput.fill('invalid-email');
      await emailInput.blur();

      // Should show validation error
      await expect(page.getByText(/valid email/i)).toBeVisible();

      // Enter valid email
      await emailInput.fill('valid@example.com');
      await emailInput.blur();

      // Error should disappear
      await expect(page.getByText(/valid email/i)).not.toBeVisible();
    });

    test('should handle file upload', async ({ page }) => {
      await page.goto('/upload-page');

      // Set up file chooser listener
      const fileChooserPromise = page.waitForEvent('filechooser');
      await page.getByLabel(/upload file/i).click();
      const fileChooser = await fileChooserPromise;

      // Upload a file
      await fileChooser.setFiles({
        name: 'test.mp3',
        mimeType: 'audio/mpeg',
        buffer: Buffer.from('test audio content'),
      });

      // Check that file is displayed
      await expect(page.getByText(/test\.mp3/i)).toBeVisible();

      // Check for upload progress
      await expect(page.getByRole('progressbar')).toBeVisible();

      // Wait for upload to complete
      await expect(page.getByText(/upload complete/i)).toBeVisible({ timeout: 10000 });
    });

    test('should auto-save form progress', async ({ page }) => {
      await page.goto('/form-page');

      // Fill some fields
      await page.getByLabel(/name/i).fill('John Doe');
      await page.getByLabel(/email/i).fill('john@example.com');

      // Wait for auto-save indicator
      await expect(page.getByText(/saved/i)).toBeVisible({ timeout: 3000 });

      // Reload page
      await page.reload();

      // Data should be restored
      await expect(page.getByLabel(/name/i)).toHaveValue('John Doe');
      await expect(page.getByLabel(/email/i)).toHaveValue('john@example.com');
    });
  });

  test.describe('Button Interactions', () => {
    test('should show hover effects on buttons', async ({ page }) => {
      const button = page.getByRole('button', { name: /click me/i });

      // Get initial styles
      const initialBg = await button.evaluate(el => getComputedStyle(el).backgroundColor);

      // Hover over button
      await button.hover();

      // Wait for animation
      await page.waitForTimeout(200);

      // Check for style change
      const hoverBg = await button.evaluate(el => getComputedStyle(el).backgroundColor);
      expect(hoverBg).not.toBe(initialBg);

      // Check for scale transform
      const transform = await button.evaluate(el => getComputedStyle(el).transform);
      expect(transform).toContain('scale');
    });

    test('should handle button loading states', async ({ page }) => {
      const button = page.getByRole('button', { name: /submit/i });

      // Click button
      await button.click();

      // Button should show loading state
      await expect(button).toHaveAttribute('disabled');
      await expect(button).toHaveText(/loading/i);
      await expect(button.locator('[data-testid="spinner"]')).toBeVisible();

      // Wait for completion
      await expect(button).not.toHaveAttribute('disabled', { timeout: 5000 });
      await expect(button).toHaveText(/submit/i);
    });

    test('should handle disabled buttons', async ({ page }) => {
      const button = page.getByRole('button', { name: /disabled/i });

      // Button should be disabled
      await expect(button).toBeDisabled();

      // Click should not work
      await button.click({ force: true });

      // No action should occur
      await expect(page.getByText(/action completed/i)).not.toBeVisible();
    });

    test('should show pulse animation on interactive buttons', async ({ page }) => {
      const button = page.getByRole('button', { name: /action/i });

      // Check for pulse animation class
      await expect(button).toHaveClass(/pulse|animate/);

      // Animation should be applied
      const animation = await button.evaluate(el => getComputedStyle(el).animation);
      expect(animation).toBeTruthy();
    });
  });

  test.describe('Card Interactions', () => {
    test('should display cards in grid layout', async ({ page }) => {
      await page.goto('/dashboard');

      // Check for cards
      const cards = page.locator('[data-testid="card"]');
      await expect(cards).toHaveCount(6);

      // Cards should have glassmorphic effect
      const firstCard = cards.first();
      const backdrop = await firstCard.evaluate(el =>
        getComputedStyle(el).getPropertyValue('backdrop-filter')
      );
      expect(backdrop).toContain('blur');
    });

    test('should navigate on card click', async ({ page }) => {
      await page.goto('/dashboard');

      // Click on a card
      await page.locator('[data-testid="card"]').first().click();

      // Should navigate to detail page
      await expect(page).toHaveURL(/\/detail/);
    });

    test('should show card hover effects', async ({ page }) => {
      await page.goto('/dashboard');

      const card = page.locator('[data-testid="card"]').first();

      // Hover over card
      await card.hover();

      // Wait for animation
      await page.waitForTimeout(200);

      // Check for glow effect
      const boxShadow = await card.evaluate(el => getComputedStyle(el).boxShadow);
      expect(boxShadow).toBeTruthy();
      expect(boxShadow).not.toBe('none');
    });

    test('should handle card selection', async ({ page }) => {
      await page.goto('/select-page');

      const cards = page.locator('[data-testid="selectable-card"]');

      // Click first card
      await cards.first().click();
      await expect(cards.first()).toHaveAttribute('data-selected', 'true');

      // Click second card
      await cards.nth(1).click();
      await expect(cards.nth(1)).toHaveAttribute('data-selected', 'true');

      // First card should be deselected (if single selection)
      // Or both selected (if multiple selection)
      // Adjust based on your implementation
    });
  });

  test.describe('Navigation Interactions', () => {
    test('should navigate between pages', async ({ page }) => {
      // Start at home
      await expect(page).toHaveURL('/');

      // Navigate to dashboard
      await page.getByRole('link', { name: /dashboard/i }).click();
      await expect(page).toHaveURL(/\/dashboard/);

      // Navigate to profile
      await page.getByRole('link', { name: /profile/i }).click();
      await expect(page).toHaveURL(/\/profile/);

      // Use browser back button
      await page.goBack();
      await expect(page).toHaveURL(/\/dashboard/);
    });

    test('should show page transition animations', async ({ page }) => {
      await page.goto('/');

      // Navigate to another page
      await page.getByRole('link', { name: /dashboard/i }).click();

      // Check for page transition
      const pageContainer = page.locator('[data-testid="page-container"]');
      await expect(pageContainer).toHaveClass(/fade|slide|animate/);

      // Wait for transition to complete
      await page.waitForTimeout(500);
      await expect(pageContainer).toBeVisible();
    });

    test('should highlight active navigation item', async ({ page }) => {
      await page.goto('/dashboard');

      // Dashboard link should be active
      const dashboardLink = page.getByRole('link', { name: /dashboard/i });
      await expect(dashboardLink).toHaveClass(/active|current/);

      // Navigate to profile
      await page.getByRole('link', { name: /profile/i }).click();

      // Profile link should be active
      const profileLink = page.getByRole('link', { name: /profile/i });
      await expect(profileLink).toHaveClass(/active|current/);

      // Dashboard link should not be active
      await expect(dashboardLink).not.toHaveClass(/active|current/);
    });

    test('should handle mobile navigation menu', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      // Menu should be hidden initially
      const menu = page.locator('[data-testid="mobile-menu"]');
      await expect(menu).not.toBeVisible();

      // Click menu button
      await page.getByRole('button', { name: /menu/i }).click();

      // Menu should be visible
      await expect(menu).toBeVisible();

      // Click a link
      await menu.getByRole('link', { name: /dashboard/i }).click();

      // Menu should close and navigate
      await expect(menu).not.toBeVisible();
      await expect(page).toHaveURL(/\/dashboard/);
    });
  });

  test.describe('Scroll Animations', () => {
    test('should trigger animations on scroll into view', async ({ page }) => {
      await page.goto('/long-page');

      // Element should be outside viewport initially
      const element = page.locator('[data-testid="scroll-animated"]').first();
      const isInViewport = await element.evaluate(el => {
        const rect = el.getBoundingClientRect();
        return rect.top >= 0 && rect.top <= window.innerHeight;
      });
      expect(isInViewport).toBe(false);

      // Scroll to element
      await element.scrollIntoViewIfNeeded();

      // Animation class should be applied
      await expect(element).toHaveClass(/fade-in|slide-up|visible/);

      // Element should be visible
      await expect(element).toBeVisible();
    });

    test('should stagger list animations', async ({ page }) => {
      await page.goto('/list-page');

      // Scroll to list
      const list = page.locator('[data-testid="stagger-list"]');
      await list.scrollIntoViewIfNeeded();

      // Items should animate in with delay
      const items = list.locator('[data-testid="list-item"]');
      const itemCount = await items.count();

      for (let i = 0; i < itemCount; i++) {
        const item = items.nth(i);
        await expect(item).toHaveClass(/visible|animated/, { timeout: (i + 1) * 200 });
      }
    });
  });

  test.describe('Loading States', () => {
    test('should show skeleton loaders', async ({ page }) => {
      await page.goto('/loading-page');

      // Check for skeleton elements
      const skeletons = page.locator('[data-testid="skeleton"]');
      await expect(skeletons).toHaveCount(3);

      // Skeletons should have shimmer animation
      const firstSkeleton = skeletons.first();
      await expect(firstSkeleton).toHaveClass(/shimmer|pulse|animate/);

      // Wait for content to load
      await expect(page.getByText(/loaded content/i)).toBeVisible({ timeout: 5000 });

      // Skeletons should be replaced
      await expect(skeletons).toHaveCount(0);
    });

    test('should show loading spinners', async ({ page }) => {
      await page.goto('/async-page');

      // Check for spinner
      const spinner = page.locator('[data-testid="spinner"]');
      await expect(spinner).toBeVisible();

      // Spinner should animate
      await expect(spinner).toHaveClass(/spin|rotate|animate/);

      // Wait for content
      await expect(page.getByText(/content loaded/i)).toBeVisible({ timeout: 5000 });
      await expect(spinner).not.toBeVisible();
    });
  });

  test.describe('Accessibility', () => {
    test('should be fully keyboard navigable', async ({ page }) => {
      await page.goto('/');

      // Tab through interactive elements
      await page.keyboard.press('Tab');
      let focusedElement = await page.evaluate(() => document.activeElement?.tagName);
      expect(['A', 'BUTTON', 'INPUT']).toContain(focusedElement);

      // Continue tabbing
      for (let i = 0; i < 5; i++) {
        await page.keyboard.press('Tab');
        focusedElement = await page.evaluate(() => document.activeElement?.tagName);
        expect(['A', 'BUTTON', 'INPUT', 'TEXTAREA']).toContain(focusedElement);
      }
    });

    test('should have proper focus indicators', async ({ page }) => {
      await page.goto('/');

      const button = page.getByRole('button').first();

      // Focus the button
      await button.focus();

      // Check for focus ring
      const outline = await button.evaluate(el => getComputedStyle(el).outline);
      expect(outline).not.toBe('none');
    });
  });
});
