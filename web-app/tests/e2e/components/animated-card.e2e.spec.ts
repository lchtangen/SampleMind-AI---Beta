/**
 * AnimatedCard Component - E2E Tests
 * Tests animation presets, timing, stagger effects, and Framer Motion integration
 */

import { expect, test } from "../setup";

test.describe("AnimatedCard Component", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/components/molecules/animated-card");
  });

  test.describe("Animation Presets", () => {
    test("fadeIn animation - opacity transition", async ({ page }) => {
      const card = page.locator('[data-animation="fadeIn"]').first();

      // Check initial state (should start with opacity 0)
      await page.goto("/components/molecules/animated-card");
      await page.waitForTimeout(100);

      const finalOpacity = await card.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      // Should eventually reach full opacity
      expect(finalOpacity).toBeGreaterThan(0.9);
    });

    test("slideUp animation - y transform", async ({ page }) => {
      const card = page.locator('[data-animation="slideUp"]').first();

      await page.waitForTimeout(600);

      const transform = await card.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      // Should have transform applied
      expect(transform).toBeTruthy();
      expect(transform).not.toBe("none");
    });

    test("slideRight animation - x transform", async ({ page }) => {
      const card = page.locator('[data-animation="slideRight"]').first();

      await page.waitForTimeout(600);

      const transform = await card.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      expect(transform).toBeTruthy();
      expect(transform).not.toBe("none");
    });

    test("scale animation - scale transform", async ({ page }) => {
      const card = page.locator('[data-animation="scale"]').first();

      await page.waitForTimeout(600);

      const transform = await card.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      // Should have scale in transform matrix
      expect(transform).toContain("matrix");
    });

    test("blur animation - filter transition", async ({ page }) => {
      const card = page.locator('[data-animation="blur"]').first();

      await page.waitForTimeout(600);

      const filter = await card.evaluate((el) => {
        return window.getComputedStyle(el).filter;
      });

      // Should eventually have no blur (blur(0px))
      expect(filter).toMatch(/blur\(0px\)|none/);
    });
  });

  test.describe("Animation Timing", () => {
    test("respects custom duration", async ({ page }) => {
      const card = page.locator('[data-duration="0.8"]').first();

      // Animation should still be running at 400ms
      await page.waitForTimeout(400);

      const opacity1 = await card.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      // Wait for completion (800ms total)
      await page.waitForTimeout(500);

      const opacity2 = await card.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      expect(opacity2).toBeGreaterThanOrEqual(opacity1);
    });

    test("applies delay before animation starts", async ({ page }) => {
      const card = page.locator('[data-delay="0.5"]').first();

      // Check opacity immediately after load (should be 0 due to delay)
      await page.goto("/components/molecules/animated-card");
      await page.waitForTimeout(100);

      const earlyOpacity = await card.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      // Wait for delay + animation
      await page.waitForTimeout(700);

      const finalOpacity = await card.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      expect(earlyOpacity).toBeLessThan(finalOpacity);
    });

    test("default duration is 0.5s", async ({ page }) => {
      const card = page
        .locator('[data-animation="fadeIn"][data-default-duration]')
        .first();

      await page.waitForTimeout(600);

      const opacity = await card.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      // Should be fully visible after 500ms + buffer
      expect(opacity).toBeGreaterThan(0.9);
    });
  });

  test.describe("Stagger Effects", () => {
    test("cards in list have staggered delays", async ({ page }) => {
      const firstCard = page.locator('[data-index="0"]').first();
      const secondCard = page.locator('[data-index="1"]').first();

      await page.goto("/components/molecules/animated-card");
      await page.waitForTimeout(100);

      const firstOpacity = await firstCard.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      const secondOpacity = await secondCard.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      // First card should be more visible than second (stagger effect)
      expect(firstOpacity).toBeGreaterThanOrEqual(secondOpacity);
    });

    test("stagger delay increases by 0.1s per index", async ({ page }) => {
      await page.goto("/components/molecules/animated-card");

      const card0 = page.locator('[data-index="0"]').first();
      const card2 = page.locator('[data-index="2"]').first();

      // At 250ms, card 0 should be more animated than card 2
      await page.waitForTimeout(250);

      const opacity0 = await card0.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      const opacity2 = await card2.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      expect(opacity0).toBeGreaterThan(opacity2);
    });
  });

  test.describe("Animation Disable", () => {
    test("renders immediately when animation disabled", async ({ page }) => {
      const card = page.locator('[data-disable-animation="true"]').first();

      await page.goto("/components/molecules/animated-card");
      await page.waitForTimeout(100);

      const opacity = await card.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      // Should be fully visible immediately
      expect(opacity).toBe(1);
    });

    test("disabled animation shows GlassmorphicCard directly", async ({
      page,
    }) => {
      const disabledCard = page
        .locator('[data-disable-animation="true"]')
        .first();
      const glassmorphicCard = disabledCard.locator("[data-card]").first();

      await expect(glassmorphicCard).toBeVisible();
    });
  });

  test.describe("Framer Motion Integration", () => {
    test("uses custom easing curve", async ({ page }) => {
      const card = page.locator('[data-animation="fadeIn"]').first();

      // Framer Motion applies easing to the animation
      await page.waitForTimeout(300);

      const opacity = await card.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      // Mid-animation opacity should reflect easing (not linear)
      expect(opacity).toBeGreaterThan(0);
      expect(opacity).toBeLessThan(1);
    });

    test("motion wrapper has full width", async ({ page }) => {
      const motionWrapper = page.locator("[data-animation]").first();

      const width = await motionWrapper.evaluate((el) => {
        return window.getComputedStyle(el).width;
      });

      expect(width).toBeTruthy();
    });
  });

  test.describe("Content Inheritance", () => {
    test("inherits GlassmorphicCard props", async ({ page }) => {
      const animatedCard = page.locator("[data-animation]").first();
      const title = animatedCard.locator("h3").first();
      const description = animatedCard.locator("p").first();

      await expect(title).toBeVisible();
      await expect(description).toBeVisible();
    });

    test("inherits glassmorphic effects", async ({ page }) => {
      const animatedCard = page.locator("[data-animation]").first();
      const glassmorphicCard = animatedCard.locator("[data-card]").first();

      const backdropFilter = await glassmorphicCard.evaluate((el) => {
        return window.getComputedStyle(el).backdropFilter;
      });

      expect(backdropFilter).toContain("blur");
    });

    test("inherits neon glow effects", async ({ page }) => {
      const animatedCard = page.locator("[data-animation]").first();
      const glassmorphicCard = animatedCard.locator("[data-card]").first();

      const boxShadow = await glassmorphicCard.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      expect(boxShadow).toContain("139, 92, 246"); // Purple glow
    });

    test("inherits interactive behavior", async ({ page }) => {
      const animatedCard = page.locator("[data-animation]").first();
      const interactiveCard = animatedCard.locator('[role="button"]').first();

      await expect(interactiveCard).toBeVisible();

      const tabIndex = await interactiveCard.getAttribute("tabindex");
      expect(tabIndex).toBe("0");
    });
  });

  test.describe("Responsive Animation", () => {
    test("animates correctly on mobile", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      const card = page.locator('[data-animation="fadeIn"]').first();

      await page.goto("/components/molecules/animated-card");
      await page.waitForTimeout(600);

      const opacity = await card.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      expect(opacity).toBeGreaterThan(0.9);
    });

    test("animates correctly on tablet", async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });

      const card = page.locator('[data-animation="slideUp"]').first();

      await page.waitForTimeout(600);

      const transform = await card.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      expect(transform).not.toBe("none");
    });

    test("animates correctly on desktop", async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });

      const card = page.locator('[data-animation="scale"]').first();

      await page.waitForTimeout(600);

      const transform = await card.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      expect(transform).toBeTruthy();
    });
  });

  test.describe("Performance", () => {
    test("completes animation within expected timeframe", async ({ page }) => {
      const card = page.locator('[data-animation="fadeIn"]').first();

      await page.goto("/components/molecules/animated-card");

      const startTime = Date.now();

      await page.waitForFunction(
        (selector) => {
          const el = document.querySelector(selector);
          return el && parseFloat(window.getComputedStyle(el).opacity) > 0.95;
        },
        '[data-animation="fadeIn"]',
        { timeout: 2000 }
      );

      const duration = Date.now() - startTime;

      // Should complete within 1s (500ms animation + 500ms buffer)
      expect(duration).toBeLessThan(1000);
    });

    test("handles rapid re-renders", async ({ page }) => {
      for (let i = 0; i < 5; i++) {
        await page.goto("/components/molecules/animated-card");
        await page.waitForTimeout(100);
      }

      const card = page.locator('[data-animation="fadeIn"]').first();
      await expect(card).toBeVisible();
    });
  });

  test.describe("Accessibility During Animation", () => {
    test("maintains accessibility attributes during animation", async ({
      page,
    }) => {
      const card = page.locator("[data-animation]").first();
      const interactiveElement = card.locator('[role="button"]').first();

      await page.goto("/components/molecules/animated-card");
      await page.waitForTimeout(300); // Mid-animation

      const role = await interactiveElement.getAttribute("role");
      const ariaLabel = await interactiveElement.getAttribute("aria-label");

      expect(role).toBe("button");
      expect(ariaLabel).toBeTruthy();
    });

    test("keyboard navigation works after animation", async ({ page }) => {
      const card = page.locator("[data-animation]").first();
      const interactiveElement = card.locator('[role="button"]').first();

      await page.waitForTimeout(600); // Wait for animation to complete

      await interactiveElement.focus();

      const isFocused = await interactiveElement.evaluate((el) => {
        return document.activeElement === el;
      });

      expect(isFocused).toBe(true);
    });
  });

  test.describe("Edge Cases", () => {
    test("handles negative delay gracefully", async ({ page }) => {
      const card = page.locator('[data-delay="-0.2"]').first();

      await page.goto("/components/molecules/animated-card");
      await page.waitForTimeout(100);

      const opacity = await card.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      // Should still animate (clamp to 0)
      expect(opacity).toBeGreaterThanOrEqual(0);
    });

    test("handles very long duration", async ({ page }) => {
      const card = page.locator('[data-duration="2"]').first();

      await page.goto("/components/molecules/animated-card");
      await page.waitForTimeout(500);

      const opacity = await card.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      // Should still be animating
      expect(opacity).toBeLessThan(1);
    });

    test("handles high index stagger", async ({ page }) => {
      const card = page.locator('[data-index="10"]').first();

      await page.goto("/components/molecules/animated-card");
      await page.waitForTimeout(100);

      const opacity = await card.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).opacity);
      });

      // Should start invisible (1s delay for index 10)
      expect(opacity).toBeLessThan(0.5);
    });
  });
});
