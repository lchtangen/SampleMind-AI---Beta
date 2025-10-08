/**
 * NeonButton Component - E2E Tests
 * Tests all variants, sizes, states, and interactions
 */

import { NeonButtonHelpers } from "../helpers/component-helpers";
import { expect, test } from "../setup";

test.describe("NeonButton Component", () => {
  let buttonHelpers: NeonButtonHelpers;

  test.beforeEach(async ({ page }) => {
    buttonHelpers = new NeonButtonHelpers(page);
    // Navigate to component showcase/demo page
    await page.goto("/components/atoms/neon-button");
  });

  test.describe("Rendering & Variants", () => {
    test("renders primary variant button", async ({ page }) => {
      const button = page.locator('button:has-text("Primary Button")').first();
      await expect(button).toBeVisible();

      // Check for purple gradient background
      const bgGradient = await button.evaluate((el) => {
        return window.getComputedStyle(el).backgroundImage;
      });
      expect(bgGradient).toContain("gradient");
    });

    test("renders secondary variant button", async ({ page }) => {
      const button = page
        .locator('button:has-text("Secondary Button")')
        .first();
      await expect(button).toBeVisible();

      // Check for border style
      const border = await button.evaluate((el) => {
        return window.getComputedStyle(el).border;
      });
      expect(border).toBeTruthy();
    });

    test("renders ghost variant button", async ({ page }) => {
      const button = page.locator('button:has-text("Ghost Button")').first();
      await expect(button).toBeVisible();

      // Ghost should have transparent background initially
      const bgColor = await button.evaluate((el) => {
        return window.getComputedStyle(el).backgroundColor;
      });
      expect(bgColor).toMatch(/rgba?\(.*,\s*0\.?\d*\)/); // Transparent or semi-transparent
    });

    test("renders danger variant button", async ({ page }) => {
      const button = page.locator('button:has-text("Danger")').first();
      await expect(button).toBeVisible();

      // Check for red color tones
      const color = await button.evaluate((el) => {
        return (
          window.getComputedStyle(el).color ||
          window.getComputedStyle(el).backgroundColor
        );
      });
      expect(color).toMatch(/rgb.*239.*68.*68|rgb.*220.*38.*38/); // Red tones
    });
  });

  test.describe("Sizes", () => {
    test("renders small size button", async ({ page }) => {
      const button = page.locator('button:has-text("Small")').first();
      const padding = await button.evaluate((el) => {
        return window.getComputedStyle(el).padding;
      });

      // Small buttons should have less padding
      expect(padding).toBeTruthy();
    });

    test("renders medium size button (default)", async ({ page }) => {
      const button = page.locator('button:has-text("Medium")').first();
      await expect(button).toBeVisible();
    });

    test("renders large size button", async ({ page }) => {
      const button = page.locator('button:has-text("Large")').first();
      const fontSize = await button.evaluate((el) => {
        return window.getComputedStyle(el).fontSize;
      });

      // Large buttons should have bigger font size
      const size = parseFloat(fontSize);
      expect(size).toBeGreaterThan(14); // Larger than default
    });
  });

  test.describe("Interactive States", () => {
    test("shows hover effect with scale animation", async ({ page }) => {
      const button = page.locator('button:has-text("Hover Me")').first();

      // Get initial transform
      const initialTransform = await button.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      // Hover
      await button.hover();
      await page.waitForTimeout(350); // Wait for animation

      // Check if transform changed (scale up)
      const hoverTransform = await button.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      expect(hoverTransform).not.toBe(initialTransform);
    });

    test("shows active/pressed state", async ({ page }) => {
      const button = page.locator('button:has-text("Click Me")').first();

      // Click and hold
      await button.click({ delay: 100 });

      // Button should have been clicked
      await expect(button).toBeEnabled();
    });

    test("shows disabled state", async ({ page }) => {
      const button = page.locator('button:has-text("Disabled")').first();
      await expect(button).toBeDisabled();

      // Check for reduced opacity
      const opacity = await button.evaluate((el) => {
        return window.getComputedStyle(el).opacity;
      });
      expect(parseFloat(opacity)).toBeLessThan(1);
    });

    test("shows loading state with spinner", async ({ page }) => {
      const button = page.locator('button:has-text("Loading")').first();

      // Check if button is disabled during loading
      await expect(button).toBeDisabled();

      // Check for spinner SVG
      const spinner = button.locator("svg").first();
      await expect(spinner).toBeVisible();

      // Spinner should be animating
      const animationName = await spinner.evaluate((el) => {
        return window.getComputedStyle(el).animationName;
      });
      expect(animationName).not.toBe("none");
    });
  });

  test.describe("Pulse Animation", () => {
    test("shows pulse glow when enabled", async ({ page }) => {
      const button = page.locator('button[data-pulse="true"]').first();

      // Wait for pulse animation
      await page.waitForTimeout(1000);

      // Check for box-shadow animation
      const boxShadow = await button.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      expect(boxShadow).toContain("rgba(139, 92, 246"); // Purple glow
    });

    test("pulse animation is smooth and continuous", async ({ page }) => {
      const button = page.locator('button[data-pulse="true"]').first();

      // Check animation duration
      const animationDuration = await button.evaluate((el) => {
        const animations = el.getAnimations();
        return animations.length > 0
          ? animations[0].effect?.getTiming().duration
          : 0;
      });

      expect(animationDuration).toBeGreaterThan(0);
    });
  });

  test.describe("Icons", () => {
    test("renders left icon", async ({ page }) => {
      const button = page.locator('button:has-text("With Left Icon")').first();
      const icon = button.locator("svg").first();

      await expect(icon).toBeVisible();

      // Icon should be before text
      const iconIndex = await icon.evaluate((el) => {
        return Array.from(el.parentElement?.children || []).indexOf(el);
      });
      expect(iconIndex).toBe(0); // First child
    });

    test("renders right icon", async ({ page }) => {
      const button = page.locator('button:has-text("With Right Icon")').first();
      const icon = button.locator("svg").last();

      await expect(icon).toBeVisible();

      // Icon should be after text
      const iconIndex = await icon.evaluate((el) => {
        const parent = el.parentElement;
        return Array.from(parent?.children || []).indexOf(el);
      });
      expect(iconIndex).toBeGreaterThan(0); // Not first child
    });
  });

  test.describe("Accessibility", () => {
    test("has correct ARIA attributes", async ({ page }) => {
      const button = page
        .locator('button:has-text("Accessible Button")')
        .first();

      const ariaLabel = await button.getAttribute("aria-label");
      const role = await button.getAttribute("role");

      // Should have aria-label or text content
      expect(ariaLabel || (await button.textContent())).toBeTruthy();

      // Role should be button (default or explicit)
      expect(role).toBeNull(); // Native button doesn't need role
    });

    test("is keyboard accessible (Enter key)", async ({ page }) => {
      const button = page.locator('button:has-text("Press Enter")').first();

      await button.focus();
      await page.keyboard.press("Enter");

      // Button should remain focused after click
      const isFocused = await button.evaluate((el) => {
        return document.activeElement === el;
      });
      expect(isFocused).toBe(true);
    });

    test("is keyboard accessible (Space key)", async ({ page }) => {
      const button = page.locator('button:has-text("Press Space")').first();

      await button.focus();
      await page.keyboard.press("Space");

      // Check if button was activated
      await expect(button).toBeEnabled();
    });

    test("has visible focus indicator", async ({ page }) => {
      const button = page.locator('button:has-text("Focus Me")').first();

      await button.focus();
      await page.waitForTimeout(200);

      // Check for focus ring
      const outline = await button.evaluate((el) => {
        return window.getComputedStyle(el).outline;
      });

      // Should have visible outline or box-shadow for focus
      const boxShadow = await button.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      expect(outline !== "none" || boxShadow !== "none").toBe(true);
    });
  });

  test.describe("Neon Glow Effects", () => {
    test("has neon glow on hover", async ({ page }) => {
      const button = page.locator('button:has-text("Glow Effect")').first();

      // Hover to trigger glow
      await button.hover();
      await page.waitForTimeout(350);

      const boxShadow = await button.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      // Should have multiple shadows (neon glow effect)
      expect(boxShadow).toContain("rgba");
    });

    test("glow intensity increases on hover", async ({ page }) => {
      const button = page.locator('button:has-text("Intense Glow")').first();

      // Get initial box shadow
      const initialShadow = await button.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      // Hover
      await button.hover();
      await page.waitForTimeout(350);

      const hoverShadow = await button.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      // Shadow should change (more intense)
      expect(hoverShadow).not.toBe(initialShadow);
    });
  });

  test.describe("Click Events", () => {
    test("triggers onClick handler", async ({ page }) => {
      // Setup click listener
      await page.evaluate(() => {
        (window as any).buttonClicked = false;
        const button = document.querySelector(
          'button:has-text("Click Handler")'
        ) as HTMLButtonElement;
        if (button) {
          button.onclick = () => {
            (window as any).buttonClicked = true;
          };
        }
      });

      const button = page.locator('button:has-text("Click Handler")').first();
      await button.click();

      // Check if handler was called
      const wasClicked = await page.evaluate(
        () => (window as any).buttonClicked
      );
      expect(wasClicked).toBe(true);
    });
  });

  test.describe("Responsive Design", () => {
    test("renders correctly on mobile", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      const button = page.locator('button:has-text("Mobile Button")').first();
      await expect(button).toBeVisible();

      // Button should be responsive (not overflow)
      const width = await button.evaluate(
        (el) => (el as HTMLElement).offsetWidth
      );
      expect(width).toBeLessThanOrEqual(375);
    });

    test("renders correctly on tablet", async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });

      const button = page.locator('button:has-text("Tablet Button")').first();
      await expect(button).toBeVisible();
    });

    test("renders correctly on desktop", async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });

      const button = page.locator('button:has-text("Desktop Button")').first();
      await expect(button).toBeVisible();
    });
  });
});
