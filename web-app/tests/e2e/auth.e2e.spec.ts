import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Authentication Flow
 *
 * Tests user authentication including:
 * - Login process
 * - Logout process
 * - Session persistence
 * - Error handling
 * - Protected route access
 */

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
  });

  test.describe('Login', () => {
    test('should display login form', async ({ page }) => {
      // Navigate to login page
      await page.goto('/login');

      // Check for login form elements
      await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
      await expect(page.getByLabel(/email/i)).toBeVisible();
      await expect(page.getByLabel(/password/i)).toBeVisible();
      await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
    });

    test('should successfully log in with valid credentials', async ({ page }) => {
      await page.goto('/login');

      // Fill in login form
      await page.getByLabel(/email/i).fill('test@example.com');
      await page.getByLabel(/password/i).fill('password123');

      // Submit form
      await page.getByRole('button', { name: /sign in/i }).click();

      // Wait for navigation to dashboard
      await page.waitForURL('**/dashboard');

      // Verify user is logged in
      await expect(page.getByText(/welcome/i)).toBeVisible();
      await expect(page.getByRole('button', { name: /sign out/i })).toBeVisible();
    });

    test('should show error with invalid credentials', async ({ page }) => {
      await page.goto('/login');

      // Fill in with invalid credentials
      await page.getByLabel(/email/i).fill('invalid@example.com');
      await page.getByLabel(/password/i).fill('wrongpassword');

      // Submit form
      await page.getByRole('button', { name: /sign in/i }).click();

      // Check for error message
      await expect(page.getByText(/invalid credentials/i)).toBeVisible();

      // User should still be on login page
      await expect(page).toHaveURL(/\/login/);
    });

    test('should validate required fields', async ({ page }) => {
      await page.goto('/login');

      // Try to submit empty form
      await page.getByRole('button', { name: /sign in/i }).click();

      // Check for validation messages
      await expect(page.getByText(/email is required/i)).toBeVisible();
      await expect(page.getByText(/password is required/i)).toBeVisible();
    });

    test('should validate email format', async ({ page }) => {
      await page.goto('/login');

      // Enter invalid email format
      await page.getByLabel(/email/i).fill('notanemail');
      await page.getByLabel(/password/i).fill('password123');
      await page.getByRole('button', { name: /sign in/i }).click();

      // Check for email validation error
      await expect(page.getByText(/valid email/i)).toBeVisible();
    });

    test('should toggle password visibility', async ({ page }) => {
      await page.goto('/login');

      const passwordInput = page.getByLabel(/password/i);
      const toggleButton = page.getByRole('button', { name: /show password/i });

      // Password should be hidden by default
      await expect(passwordInput).toHaveAttribute('type', 'password');

      // Click toggle to show password
      await toggleButton.click();
      await expect(passwordInput).toHaveAttribute('type', 'text');

      // Click toggle to hide password again
      await toggleButton.click();
      await expect(passwordInput).toHaveAttribute('type', 'password');
    });

    test('should handle Enter key submission', async ({ page }) => {
      await page.goto('/login');

      await page.getByLabel(/email/i).fill('test@example.com');
      await page.getByLabel(/password/i).fill('password123');

      // Press Enter to submit
      await page.getByLabel(/password/i).press('Enter');

      // Should navigate to dashboard
      await page.waitForURL('**/dashboard');
      await expect(page.getByText(/welcome/i)).toBeVisible();
    });
  });

  test.describe('Logout', () => {
    test.beforeEach(async ({ page }) => {
      // Log in before each logout test
      await page.goto('/login');
      await page.getByLabel(/email/i).fill('test@example.com');
      await page.getByLabel(/password/i).fill('password123');
      await page.getByRole('button', { name: /sign in/i }).click();
      await page.waitForURL('**/dashboard');
    });

    test('should successfully log out', async ({ page }) => {
      // Click sign out button
      await page.getByRole('button', { name: /sign out/i }).click();

      // Should redirect to login page
      await page.waitForURL('**/login');

      // Verify user is logged out
      await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
    });

    test('should clear user session on logout', async ({ page, context }) => {
      // Get cookies before logout
      const cookiesBefore = await context.cookies();
      expect(cookiesBefore.length).toBeGreaterThan(0);

      // Log out
      await page.getByRole('button', { name: /sign out/i }).click();
      await page.waitForURL('**/login');

      // Check that auth cookies are cleared
      const cookiesAfter = await context.cookies();
      const authCookie = cookiesAfter.find(c => c.name === 'auth_token');
      expect(authCookie).toBeUndefined();
    });

    test('should prevent access to protected routes after logout', async ({ page }) => {
      // Log out
      await page.getByRole('button', { name: /sign out/i }).click();
      await page.waitForURL('**/login');

      // Try to access protected route
      await page.goto('/dashboard');

      // Should redirect back to login
      await page.waitForURL('**/login');
      await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
    });
  });

  test.describe('Session Management', () => {
    test('should persist session across page reloads', async ({ page }) => {
      // Log in
      await page.goto('/login');
      await page.getByLabel(/email/i).fill('test@example.com');
      await page.getByLabel(/password/i).fill('password123');
      await page.getByRole('button', { name: /sign in/i }).click();
      await page.waitForURL('**/dashboard');

      // Reload the page
      await page.reload();

      // User should still be logged in
      await expect(page.getByText(/welcome/i)).toBeVisible();
      await expect(page.getByRole('button', { name: /sign out/i })).toBeVisible();
    });

    test('should maintain session across navigation', async ({ page }) => {
      // Log in
      await page.goto('/login');
      await page.getByLabel(/email/i).fill('test@example.com');
      await page.getByLabel(/password/i).fill('password123');
      await page.getByRole('button', { name: /sign in/i }).click();
      await page.waitForURL('**/dashboard');

      // Navigate to different pages
      await page.goto('/profile');
      await expect(page.getByRole('button', { name: /sign out/i })).toBeVisible();

      await page.goto('/settings');
      await expect(page.getByRole('button', { name: /sign out/i })).toBeVisible();

      // Return to dashboard
      await page.goto('/dashboard');
      await expect(page.getByText(/welcome/i)).toBeVisible();
    });

    test('should handle expired session', async ({ page, context }) => {
      // Log in
      await page.goto('/login');
      await page.getByLabel(/email/i).fill('test@example.com');
      await page.getByLabel(/password/i).fill('password123');
      await page.getByRole('button', { name: /sign in/i }).click();
      await page.waitForURL('**/dashboard');

      // Manually expire the session by clearing cookies
      await context.clearCookies();

      // Try to access a protected route
      await page.goto('/profile');

      // Should redirect to login
      await page.waitForURL('**/login');
      await expect(page.getByText(/session expired/i)).toBeVisible();
    });
  });

  test.describe('Protected Routes', () => {
    test('should redirect unauthenticated users to login', async ({ page }) => {
      // Try to access protected routes without logging in
      await page.goto('/dashboard');
      await page.waitForURL('**/login');

      await page.goto('/profile');
      await page.waitForURL('**/login');

      await page.goto('/settings');
      await page.waitForURL('**/login');
    });

    test('should allow authenticated users to access protected routes', async ({ page }) => {
      // Log in first
      await page.goto('/login');
      await page.getByLabel(/email/i).fill('test@example.com');
      await page.getByLabel(/password/i).fill('password123');
      await page.getByRole('button', { name: /sign in/i }).click();
      await page.waitForURL('**/dashboard');

      // Access protected routes
      await page.goto('/profile');
      await expect(page).toHaveURL(/\/profile/);

      await page.goto('/settings');
      await expect(page).toHaveURL(/\/settings/);
    });
  });

  test.describe('Remember Me', () => {
    test('should save session with remember me checked', async ({ page, context }) => {
      await page.goto('/login');

      // Fill in credentials and check remember me
      await page.getByLabel(/email/i).fill('test@example.com');
      await page.getByLabel(/password/i).fill('password123');
      await page.getByLabel(/remember me/i).check();
      await page.getByRole('button', { name: /sign in/i }).click();

      await page.waitForURL('**/dashboard');

      // Check that persistent cookie is set
      const cookies = await context.cookies();
      const persistentCookie = cookies.find(c => c.name === 'remember_token');
      expect(persistentCookie).toBeDefined();
      expect(persistentCookie?.expires).toBeGreaterThan(Date.now() / 1000 + 86400); // More than 1 day
    });

    test('should use session cookie without remember me', async ({ page, context }) => {
      await page.goto('/login');

      // Fill in credentials without checking remember me
      await page.getByLabel(/email/i).fill('test@example.com');
      await page.getByLabel(/password/i).fill('password123');
      await page.getByRole('button', { name: /sign in/i }).click();

      await page.waitForURL('**/dashboard');

      // Check that session cookie is set (expires when browser closes)
      const cookies = await context.cookies();
      const sessionCookie = cookies.find(c => c.name === 'auth_token');
      expect(sessionCookie).toBeDefined();
      expect(sessionCookie?.expires).toBe(-1); // Session cookie
    });
  });

  test.describe('Loading States', () => {
    test('should show loading state during login', async ({ page }) => {
      await page.goto('/login');

      await page.getByLabel(/email/i).fill('test@example.com');
      await page.getByLabel(/password/i).fill('password123');

      // Click submit and immediately check for loading state
      await page.getByRole('button', { name: /sign in/i }).click();

      // Check for loading indicator
      await expect(page.getByTestId('login-loading')).toBeVisible();

      // Loading should disappear after completion
      await page.waitForURL('**/dashboard');
      await expect(page.getByTestId('login-loading')).not.toBeVisible();
    });
  });

  test.describe('Accessibility', () => {
    test('should be keyboard navigable', async ({ page }) => {
      await page.goto('/login');

      // Tab through form elements
      await page.keyboard.press('Tab'); // Focus email
      await expect(page.getByLabel(/email/i)).toBeFocused();

      await page.keyboard.press('Tab'); // Focus password
      await expect(page.getByLabel(/password/i)).toBeFocused();

      await page.keyboard.press('Tab'); // Focus remember me
      await expect(page.getByLabel(/remember me/i)).toBeFocused();

      await page.keyboard.press('Tab'); // Focus submit button
      await expect(page.getByRole('button', { name: /sign in/i })).toBeFocused();
    });

    test('should have proper ARIA labels', async ({ page }) => {
      await page.goto('/login');

      // Check for proper labels
      const emailInput = page.getByLabel(/email/i);
      await expect(emailInput).toHaveAttribute('aria-label', /email/i);

      const passwordInput = page.getByLabel(/password/i);
      await expect(passwordInput).toHaveAttribute('aria-label', /password/i);
    });

    test('should announce errors to screen readers', async ({ page }) => {
      await page.goto('/login');

      // Submit invalid form
      await page.getByRole('button', { name: /sign in/i }).click();

      // Check for ARIA live region with error
      const errorRegion = page.getByRole('alert');
      await expect(errorRegion).toBeVisible();
      await expect(errorRegion).toHaveAttribute('aria-live', 'polite');
    });
  });
});
