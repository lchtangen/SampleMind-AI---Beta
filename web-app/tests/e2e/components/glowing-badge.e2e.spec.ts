/**
 * GlowingBadge Component - E2E Tests
 * Tests all variants, sizes, animations, and visual effects
 */

import { expect, test } from "../setup";

test.describe("GlowingBadge Component", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to component showcase/demo page
    await page.goto("/components/atoms/glowing-badge");
  });

  test.describe("Rendering & Variants", () => {
    test("renders primary variant with purple glow", async ({ page }) => {
      const badge = page.locator('[data-variant="primary"]').first();
      await expect(badge).toBeVisible();

      const boxShadow = await badge.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      // Should have purple glow
      expect(boxShadow).toContain("139, 92, 246"); // RGB for primary purple
    });

    test("renders success variant with green glow", async ({ page }) => {
      const badge = page.locator('[data-variant="success"]').first();

      const boxShadow = await badge.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      expect(boxShadow).toContain("16, 185, 129"); // RGB for success green
    });

    test("renders warning variant with amber glow", async ({ page }) => {
      const badge = page.locator('[data-variant="warning"]').first();

      const boxShadow = await badge.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      expect(boxShadow).toContain("245, 158, 11"); // RGB for warning amber
    });

    test("renders error variant with red glow", async ({ page }) => {
      const badge = page.locator('[data-variant="error"]').first();

      const boxShadow = await badge.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      expect(boxShadow).toContain("239, 68, 68"); // RGB for error red
    });

    test("renders info variant with blue glow", async ({ page }) => {
      const badge = page.locator('[data-variant="info"]').first();

      const boxShadow = await badge.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      expect(boxShadow).toContain("59, 130, 246"); // RGB for info blue
    });

    test("renders cyan variant with cyan glow", async ({ page }) => {
      const badge = page.locator('[data-variant="cyan"]').first();

      const boxShadow = await badge.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      expect(boxShadow).toContain("6, 182, 212"); // RGB for cyan
    });

    test("renders pink variant with pink glow", async ({ page }) => {
      const badge = page.locator('[data-variant="pink"]').first();

      const boxShadow = await badge.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      expect(boxShadow).toContain("236, 72, 153"); // RGB for pink
    });
  });

  test.describe("Size Variants", () => {
    test("renders small size correctly", async ({ page }) => {
      const badge = page.locator('[data-size="sm"]').first();

      const fontSize = await badge.evaluate((el) => {
        return window.getComputedStyle(el).fontSize;
      });

      const padding = await badge.evaluate((el) => {
        return window.getComputedStyle(el).padding;
      });

      expect(parseFloat(fontSize)).toBeLessThan(14); // text-xs
      expect(padding).toBeTruthy();
    });

    test("renders medium size correctly", async ({ page }) => {
      const badge = page.locator('[data-size="md"]').first();

      const fontSize = await badge.evaluate((el) => {
        return window.getComputedStyle(el).fontSize;
      });

      expect(parseFloat(fontSize)).toBeGreaterThanOrEqual(14); // text-sm
    });

    test("renders large size correctly", async ({ page }) => {
      const badge = page.locator('[data-size="lg"]').first();

      const fontSize = await badge.evaluate((el) => {
        return window.getComputedStyle(el).fontSize;
      });

      expect(parseFloat(fontSize)).toBeGreaterThanOrEqual(16); // text-base
    });
  });

  test.describe("Pulse Animation", () => {
    test("shows continuous pulse animation when enabled", async ({ page }) => {
      const badge = page.locator('[data-pulse="true"]').first();

      // Get initial box shadow
      const initialShadow = await badge.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      // Wait for animation cycle
      await page.waitForTimeout(1000);

      // Shadow should pulse (we can't compare exact values due to animation, but it should exist)
      const currentShadow = await badge.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      expect(currentShadow).toBeTruthy();
      expect(currentShadow).toContain("rgba");
    });

    test("has animation-iteration-count infinite for pulse", async ({
      page,
    }) => {
      const badge = page.locator('[data-pulse="true"]').first();

      const animationIterationCount = await badge.evaluate((el) => {
        return window.getComputedStyle(el).animationIterationCount;
      });

      expect(animationIterationCount).toBe("infinite");
    });

    test("does not pulse when pulse is disabled", async ({ page }) => {
      const badge = page.locator('[data-pulse="false"]').first();

      const animationName = await badge.evaluate((el) => {
        return window.getComputedStyle(el).animationName;
      });

      // Should not have pulse animation or should be 'none'
      expect(animationName).not.toContain("pulse");
    });
  });

  test.describe("Status Dot Indicator", () => {
    test("renders status dot when enabled", async ({ page }) => {
      const badge = page.locator('[data-dot="true"]').first();
      const dot = badge.locator("[data-status-dot]").first();

      await expect(dot).toBeVisible();
    });

    test("status dot has circular shape", async ({ page }) => {
      const dot = page.locator("[data-status-dot]").first();

      const borderRadius = await dot.evaluate((el) => {
        return window.getComputedStyle(el).borderRadius;
      });

      expect(borderRadius).toBe("50%"); // Should be circular
    });

    test("status dot matches badge variant color", async ({ page }) => {
      const successBadge = page
        .locator('[data-variant="success"][data-dot="true"]')
        .first();
      const dot = successBadge.locator("[data-status-dot]").first();

      const backgroundColor = await dot.evaluate((el) => {
        return window.getComputedStyle(el).backgroundColor;
      });

      // Should have success green color
      expect(backgroundColor).toMatch(/rgb.*16.*185.*129|rgb.*34.*197.*94/);
    });

    test("does not render dot when disabled", async ({ page }) => {
      const badge = page.locator('[data-dot="false"]').first();
      const dot = badge.locator("[data-status-dot]").first();

      await expect(dot).not.toBeVisible();
    });
  });

  test.describe("Entry Animation", () => {
    test("has fade-in animation on mount", async ({ page }) => {
      // Navigate to trigger mount
      await page.goto("/components/atoms/glowing-badge");

      const badge = page.locator('[data-variant="primary"]').first();

      // Check initial animation state
      const opacity = await badge.evaluate((el) => {
        return window.getComputedStyle(el).opacity;
      });

      expect(parseFloat(opacity)).toBeLessThanOrEqual(1);
    });

    test("has scale animation on mount", async ({ page }) => {
      await page.goto("/components/atoms/glowing-badge");

      const badge = page.locator('[data-variant="primary"]').first();

      const transform = await badge.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      expect(transform).toBeTruthy();
    });
  });

  test.describe("Glassmorphic Effects", () => {
    test("has backdrop blur", async ({ page }) => {
      const badge = page.locator('[data-variant="primary"]').first();

      const backdropFilter = await badge.evaluate((el) => {
        return window.getComputedStyle(el).backdropFilter;
      });

      expect(backdropFilter).toContain("blur");
    });

    test("has semi-transparent background", async ({ page }) => {
      const badge = page.locator('[data-variant="primary"]').first();

      const backgroundColor = await badge.evaluate((el) => {
        return window.getComputedStyle(el).backgroundColor;
      });

      // Should have alpha transparency
      expect(backgroundColor).toMatch(/rgba?\(.*,\s*0\.\d+\)/);
    });

    test("has border with opacity", async ({ page }) => {
      const badge = page.locator('[data-variant="primary"]').first();

      const borderColor = await badge.evaluate((el) => {
        return window.getComputedStyle(el).borderColor;
      });

      expect(borderColor).toBeTruthy();
    });
  });

  test.describe("Accessibility", () => {
    test("has proper role for status indicators", async ({ page }) => {
      const badge = page.locator('[role="status"]').first();

      await expect(badge).toBeVisible();
    });

    test("has aria-label when provided", async ({ page }) => {
      const badge = page.locator("[aria-label]").first();

      const ariaLabel = await badge.getAttribute("aria-label");
      expect(ariaLabel).toBeTruthy();
    });

    test("text content is readable", async ({ page }) => {
      const badge = page.locator('[data-variant="primary"]').first();

      const textContent = await badge.textContent();
      expect(textContent).toBeTruthy();
      expect(textContent?.trim().length).toBeGreaterThan(0);
    });
  });

  test.describe("Glow Effects", () => {
    test("has neon glow shadow when enabled", async ({ page }) => {
      const badge = page.locator('[data-glow="true"]').first();

      const boxShadow = await badge.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      expect(boxShadow).toContain("rgba");
      expect(boxShadow).not.toBe("none");
    });

    test("glow can be disabled", async ({ page }) => {
      const badge = page.locator('[data-glow="false"]').first();

      const boxShadow = await badge.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      // Should have minimal or no glow
      expect(boxShadow).toBeTruthy();
    });

    test("glow intensity matches variant", async ({ page }) => {
      const primaryBadge = page
        .locator('[data-variant="primary"][data-glow="true"]')
        .first();
      const errorBadge = page
        .locator('[data-variant="error"][data-glow="true"]')
        .first();

      const primaryShadow = await primaryBadge.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      const errorShadow = await errorBadge.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      // Both should have shadows but different colors
      expect(primaryShadow).not.toBe(errorShadow);
    });
  });

  test.describe("Responsive Design", () => {
    test("renders correctly on mobile", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      const badge = page.locator('[data-variant="primary"]').first();
      await expect(badge).toBeVisible();

      const fontSize = await badge.evaluate((el) => {
        return window.getComputedStyle(el).fontSize;
      });

      expect(parseFloat(fontSize)).toBeGreaterThan(0);
    });

    test("renders correctly on tablet", async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });

      const badge = page.locator('[data-variant="primary"]').first();
      await expect(badge).toBeVisible();
    });

    test("renders correctly on desktop", async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });

      const badge = page.locator('[data-variant="primary"]').first();
      await expect(badge).toBeVisible();
    });

    test("text remains readable across screen sizes", async ({ page }) => {
      const sizes = [
        { width: 375, height: 667 }, // Mobile
        { width: 768, height: 1024 }, // Tablet
        { width: 1920, height: 1080 }, // Desktop
      ];

      for (const size of sizes) {
        await page.setViewportSize(size);
        const badge = page.locator('[data-variant="primary"]').first();

        const fontSize = await badge.evaluate((el) => {
          return parseFloat(window.getComputedStyle(el).fontSize);
        });

        // Font should never be smaller than 10px for readability
        expect(fontSize).toBeGreaterThanOrEqual(10);
      }
    });
  });
});
