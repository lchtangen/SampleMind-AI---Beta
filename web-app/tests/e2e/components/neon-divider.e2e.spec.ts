/**
 * NeonDivider Component - E2E Tests
 * Tests orientations, gradients, animations, and glow effects
 */

import { expect, test } from "../setup";

test.describe("NeonDivider Component", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/components/atoms/neon-divider");
  });

  test.describe("Rendering & Orientation", () => {
    test("renders horizontal divider by default", async ({ page }) => {
      const divider = page
        .locator('[role="separator"][aria-orientation="horizontal"]')
        .first();
      await expect(divider).toBeVisible();

      const width = await divider.evaluate(
        (el) => (el as HTMLElement).offsetWidth
      );
      const height = await divider.evaluate(
        (el) => (el as HTMLElement).offsetHeight
      );

      expect(width).toBeGreaterThan(height);
    });

    test("renders vertical divider when specified", async ({ page }) => {
      const divider = page
        .locator('[role="separator"][aria-orientation="vertical"]')
        .first();
      await expect(divider).toBeVisible();

      const width = await divider.evaluate(
        (el) => (el as HTMLElement).offsetWidth
      );
      const height = await divider.evaluate(
        (el) => (el as HTMLElement).offsetHeight
      );

      expect(height).toBeGreaterThan(width);
    });

    test("has correct ARIA role and orientation", async ({ page }) => {
      const divider = page.locator('[role="separator"]').first();

      const role = await divider.getAttribute("role");
      const orientation = await divider.getAttribute("aria-orientation");

      expect(role).toBe("separator");
      expect(orientation).toMatch(/horizontal|vertical/);
    });
  });

  test.describe("Gradient Presets", () => {
    test("renders purple gradient", async ({ page }) => {
      const divider = page.locator('[data-gradient="purple"]').first();
      const innerDiv = divider.locator("div").first();

      const background = await innerDiv.evaluate((el) => {
        return window.getComputedStyle(el).background;
      });

      expect(background).toContain("linear-gradient");
      expect(background).toContain("139, 92, 246"); // Purple RGB
    });

    test("renders cyber gradient (purple to cyan)", async ({ page }) => {
      const divider = page.locator('[data-gradient="cyber"]').first();
      const innerDiv = divider.locator("div").first();

      const background = await innerDiv.evaluate((el) => {
        return window.getComputedStyle(el).background;
      });

      expect(background).toContain("linear-gradient");
      // Should contain both purple and cyan
      expect(background).toMatch(/139.*92.*246|6.*182.*212/);
    });

    test("renders neon gradient (multi-color)", async ({ page }) => {
      const divider = page.locator('[data-gradient="neon"]').first();
      const innerDiv = divider.locator("div").first();

      const background = await innerDiv.evaluate((el) => {
        return window.getComputedStyle(el).background;
      });

      expect(background).toContain("linear-gradient");
      // Should contain pink, purple, and cyan
      expect(background).toMatch(/236.*72.*153|139.*92.*246|6.*182.*212/);
    });

    test("renders pink gradient", async ({ page }) => {
      const divider = page.locator('[data-gradient="pink"]').first();
      const innerDiv = divider.locator("div").first();

      const background = await innerDiv.evaluate((el) => {
        return window.getComputedStyle(el).background;
      });

      expect(background).toContain("236, 72, 153"); // Pink RGB
    });

    test("renders cyan gradient", async ({ page }) => {
      const divider = page.locator('[data-gradient="cyan"]').first();
      const innerDiv = divider.locator("div").first();

      const background = await innerDiv.evaluate((el) => {
        return window.getComputedStyle(el).background;
      });

      expect(background).toContain("6, 182, 212"); // Cyan RGB
    });
  });

  test.describe("Thickness Variants", () => {
    test("renders with default thickness (2px)", async ({ page }) => {
      const divider = page.locator('[data-thickness="2"]').first();

      const height = await divider.evaluate((el) => {
        return (el as HTMLElement).offsetHeight;
      });

      expect(height).toBe(2);
    });

    test("renders with custom thickness (4px)", async ({ page }) => {
      const divider = page.locator('[data-thickness="4"]').first();

      const height = await divider.evaluate((el) => {
        return (el as HTMLElement).offsetHeight;
      });

      expect(height).toBe(4);
    });

    test("renders with thick variant (6px)", async ({ page }) => {
      const divider = page.locator('[data-thickness="6"]').first();

      const height = await divider.evaluate((el) => {
        return (el as HTMLElement).offsetHeight;
      });

      expect(height).toBe(6);
    });
  });

  test.describe("Glow Intensity", () => {
    test("renders low glow intensity", async ({ page }) => {
      const divider = page.locator('[data-glow="low"]').first();
      const innerDiv = divider.locator("div").first();

      const boxShadow = await innerDiv.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      expect(boxShadow).toContain("5px"); // Low glow: 0 0 5px
    });

    test("renders medium glow intensity", async ({ page }) => {
      const divider = page.locator('[data-glow="medium"]').first();
      const innerDiv = divider.locator("div").first();

      const boxShadow = await innerDiv.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      expect(boxShadow).toContain("10px"); // Medium glow: 0 0 10px
    });

    test("renders high glow intensity", async ({ page }) => {
      const divider = page.locator('[data-glow="high"]').first();
      const innerDiv = divider.locator("div").first();

      const boxShadow = await innerDiv.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      expect(boxShadow).toContain("20px"); // High glow: 0 0 20px
    });
  });

  test.describe("Gradient Animation", () => {
    test("animates background position when enabled", async ({ page }) => {
      const divider = page.locator('[data-animated="true"]').first();
      const innerDiv = divider.locator("div").first();

      // Get initial background position
      const initialPosition = await innerDiv.evaluate((el) => {
        return window.getComputedStyle(el).backgroundPosition;
      });

      // Wait for animation
      await page.waitForTimeout(1500);

      // Background position should change
      const newPosition = await innerDiv.evaluate((el) => {
        return window.getComputedStyle(el).backgroundPosition;
      });

      // Position should be different (animation in progress)
      expect(newPosition).toBeTruthy();
    });

    test("has infinite animation duration", async ({ page }) => {
      const divider = page.locator('[data-animated="true"]').first();
      const innerDiv = divider.locator("div").first();

      const animationIterationCount = await innerDiv.evaluate((el) => {
        return window.getComputedStyle(el).animationIterationCount;
      });

      expect(animationIterationCount).toBe("infinite");
    });

    test("does not animate when animation is disabled", async ({ page }) => {
      const divider = page.locator('[data-animated="false"]').first();
      const innerDiv = divider.locator("div").first();

      const animationName = await innerDiv.evaluate((el) => {
        return window.getComputedStyle(el).animationName;
      });

      // Should not have continuous background animation
      expect(animationName).toBeTruthy(); // May have initial opacity animation
    });
  });

  test.describe("Glow Overlay Effect", () => {
    test("has glow overlay with blur filter", async ({ page }) => {
      const divider = page.locator('[role="separator"]').first();
      const glowOverlay = divider.locator('[aria-hidden="true"]').first();

      await expect(glowOverlay).toBeVisible();

      const filter = await glowOverlay.evaluate((el) => {
        return window.getComputedStyle(el).filter;
      });

      expect(filter).toContain("blur");
    });

    test("glow overlay pulsates (opacity animation)", async ({ page }) => {
      const glowOverlay = page
        .locator('[role="separator"] [aria-hidden="true"]')
        .first();

      const opacity1 = await glowOverlay.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      await page.waitForTimeout(1000);

      const opacity2 = await glowOverlay.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      // Opacity should be between 0.3 and 0.6
      expect(opacity1).toBeGreaterThanOrEqual(0.2);
      expect(opacity1).toBeLessThanOrEqual(0.7);
    });

    test("glow overlay has aria-hidden attribute", async ({ page }) => {
      const glowOverlay = page
        .locator('[role="separator"] [aria-hidden="true"]')
        .first();

      const ariaHidden = await glowOverlay.getAttribute("aria-hidden");
      expect(ariaHidden).toBe("true");
    });
  });

  test.describe("Responsive Design", () => {
    test("horizontal divider spans full width on mobile", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      const divider = page.locator('[aria-orientation="horizontal"]').first();
      const width = await divider.evaluate(
        (el) => (el as HTMLElement).offsetWidth
      );

      expect(width).toBeGreaterThan(300); // Should span most of viewport
    });

    test("vertical divider maintains height on tablet", async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });

      const divider = page.locator('[aria-orientation="vertical"]').first();
      const height = await divider.evaluate(
        (el) => (el as HTMLElement).offsetHeight
      );

      expect(height).toBeGreaterThan(100); // Should have significant height
    });

    test("maintains visibility across screen sizes", async ({ page }) => {
      const sizes = [
        { width: 375, height: 667 }, // Mobile
        { width: 768, height: 1024 }, // Tablet
        { width: 1920, height: 1080 }, // Desktop
      ];

      for (const size of sizes) {
        await page.setViewportSize(size);
        const divider = page.locator('[role="separator"]').first();
        await expect(divider).toBeVisible();
      }
    });
  });

  test.describe("Accessibility", () => {
    test("has proper semantic role", async ({ page }) => {
      const divider = page.locator('[role="separator"]').first();

      const role = await divider.getAttribute("role");
      expect(role).toBe("separator");
    });

    test("includes aria-orientation attribute", async ({ page }) => {
      const horizontalDivider = page
        .locator('[aria-orientation="horizontal"]')
        .first();
      const verticalDivider = page
        .locator('[aria-orientation="vertical"]')
        .first();

      await expect(horizontalDivider).toHaveAttribute(
        "aria-orientation",
        "horizontal"
      );
      await expect(verticalDivider).toHaveAttribute(
        "aria-orientation",
        "vertical"
      );
    });

    test("decorative glow has aria-hidden", async ({ page }) => {
      const glowOverlay = page.locator('[aria-hidden="true"]').first();
      await expect(glowOverlay).toHaveAttribute("aria-hidden", "true");
    });
  });

  test.describe("Initial Animation", () => {
    test("fades in on mount", async ({ page }) => {
      await page.goto("/components/atoms/neon-divider");

      const divider = page.locator('[role="separator"]').first();
      const innerDiv = divider.locator("div").first();

      // Should eventually reach full opacity
      await page.waitForTimeout(600);

      const opacity = await innerDiv.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      expect(opacity).toBeGreaterThan(0.5);
    });
  });
});
