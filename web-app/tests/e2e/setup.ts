/**
 * Playwright E2E Test Setup
 * Global configuration and utilities for end-to-end testing
 */

import { test as base, expect } from "@playwright/test";

/**
 * Custom test fixture with additional utilities
 */
export const test = base.extend({
  /**
   * Custom page fixture with cyberpunk theme verification
   */
  page: async ({ page }, use) => {
    // Navigate to base URL before each test
    await page.goto("/");

    // Wait for app to be ready (check for root element)
    await page.waitForSelector("#root", { state: "attached" });

    // Verify design system CSS is loaded
    const bodyBackground = await page.evaluate(() => {
      return window.getComputedStyle(document.body).backgroundColor;
    });

    // Ensure cyberpunk theme is active (dark background)
    expect(bodyBackground).toBeTruthy();

    await use(page);
  },
});

/**
 * Custom expect with additional matchers for cyberpunk components
 */
export { expect };

/**
 * Test utilities
 */
export const testUtils = {
  /**
   * Wait for animations to complete
   */
  async waitForAnimations(page: any, selector: string) {
    await page.waitForSelector(selector);
    await page.waitForTimeout(500); // Allow Framer Motion animations to complete
  },

  /**
   * Check if element has neon glow effect
   */
  async hasNeonGlow(page: any, selector: string): Promise<boolean> {
    const boxShadow = await page.evaluate((sel: string) => {
      const element = document.querySelector(sel);
      return element ? window.getComputedStyle(element).boxShadow : "";
    }, selector);

    return boxShadow.includes("rgba");
  },

  /**
   * Check if element has glassmorphic background
   */
  async hasGlassmorphism(page: any, selector: string): Promise<boolean> {
    const backdropFilter = await page.evaluate((sel: string) => {
      const element = document.querySelector(sel);
      return element ? window.getComputedStyle(element).backdropFilter : "";
    }, selector);

    return backdropFilter.includes("blur");
  },

  /**
   * Get computed color (handles rgba/rgb/hex)
   */
  async getComputedColor(
    page: any,
    selector: string,
    property: string = "color"
  ): Promise<string> {
    return await page.evaluate(
      (args: { sel: string; prop: string }) => {
        const element = document.querySelector(args.sel);
        return element
          ? window.getComputedStyle(element)[args.prop as any]
          : "";
      },
      { sel: selector, prop: property }
    );
  },

  /**
   * Trigger keyboard navigation
   */
  async navigateWithKeyboard(
    page: any,
    key: "Enter" | "Space" | "Tab" | "Escape"
  ) {
    await page.keyboard.press(key);
    await page.waitForTimeout(100); // Allow event handlers to process
  },

  /**
   * Check accessibility (aria attributes)
   */
  async checkAriaAttributes(page: any, selector: string) {
    return await page.evaluate((sel: string) => {
      const element = document.querySelector(sel);
      if (!element) return null;

      return {
        role: element.getAttribute("role"),
        ariaLabel: element.getAttribute("aria-label"),
        ariaPressed: element.getAttribute("aria-pressed"),
        ariaDisabled: element.getAttribute("aria-disabled"),
        tabIndex: element.getAttribute("tabindex"),
      };
    }, selector);
  },

  /**
   * Simulate hover effect
   */
  async hoverElement(page: any, selector: string) {
    await page.hover(selector);
    await page.waitForTimeout(300); // Allow CSS transitions
  },

  /**
   * Get animation state
   */
  async getAnimationState(page: any, selector: string): Promise<string> {
    return await page.evaluate((sel: string) => {
      const element = document.querySelector(sel);
      const animations = element?.getAnimations() || [];
      return animations.length > 0 ? animations[0].playState : "idle";
    }, selector);
  },
};
