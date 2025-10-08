/**
 * Skeleton Component - E2E Tests
 * Tests loading placeholders, variants, animations, and accessibility
 */

import { expect, test } from "../setup";

test.describe("Skeleton Component", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/components/atoms/skeleton");
  });

  test.describe("Rendering & Variants", () => {
    test("renders rectangular variant by default", async ({ page }) => {
      const skeleton = page
        .locator('[role="status"][data-variant="rectangular"]')
        .first();
      await expect(skeleton).toBeVisible();

      const borderRadius = await skeleton.evaluate((el) => {
        return window.getComputedStyle(el).borderRadius;
      });

      // Should have medium border radius (rounded-md)
      expect(parseFloat(borderRadius)).toBeLessThan(16); // Not fully rounded
    });

    test("renders circular variant", async ({ page }) => {
      const skeleton = page.locator('[data-variant="circular"]').first();

      const borderRadius = await skeleton.evaluate((el) => {
        return window.getComputedStyle(el).borderRadius;
      });

      // Should be fully circular (50%)
      expect(borderRadius).toContain("50%");
    });

    test("renders rounded variant", async ({ page }) => {
      const skeleton = page.locator('[data-variant="rounded"]').first();

      const borderRadius = await skeleton.evaluate((el) => {
        return window.getComputedStyle(el).borderRadius;
      });

      // Should have large border radius (rounded-lg)
      expect(parseFloat(borderRadius)).toBeGreaterThan(6);
    });

    test("renders text variant", async ({ page }) => {
      const skeleton = page.locator('[data-variant="text"]').first();
      await expect(skeleton).toBeVisible();

      const height = await skeleton.evaluate((el) => {
        return (el as HTMLElement).offsetHeight;
      });

      // Text variant should have text-like height
      expect(height).toBeLessThan(30);
    });
  });

  test.describe("Size Customization", () => {
    test("accepts custom width in pixels", async ({ page }) => {
      const skeleton = page.locator('[data-width="200"]').first();

      const width = await skeleton.evaluate((el) => {
        return (el as HTMLElement).offsetWidth;
      });

      expect(width).toBe(200);
    });

    test("accepts custom height in pixels", async ({ page }) => {
      const skeleton = page.locator('[data-height="100"]').first();

      const height = await skeleton.evaluate((el) => {
        return (el as HTMLElement).offsetHeight;
      });

      expect(height).toBe(100);
    });

    test("accepts percentage width", async ({ page }) => {
      const skeleton = page.locator('[data-width="50%"]').first();

      const computedWidth = await skeleton.evaluate((el) => {
        return window.getComputedStyle(el).width;
      });

      expect(computedWidth).toContain("%");
    });
  });

  test.describe("Shimmer Animation", () => {
    test("has shimmer animation by default", async ({ page }) => {
      const skeleton = page.locator('[data-animate="true"]').first();

      const animationName = await skeleton.evaluate((el) => {
        return window.getComputedStyle(el).animationName;
      });

      expect(animationName).not.toBe("none");
    });

    test("shimmer animation is infinite", async ({ page }) => {
      const skeleton = page.locator('[data-animate="true"]').first();

      const animationIterationCount = await skeleton.evaluate((el) => {
        return window.getComputedStyle(el).animationIterationCount;
      });

      expect(animationIterationCount).toBe("infinite");
    });

    test("has gradient overlay for shimmer effect", async ({ page }) => {
      const skeleton = page.locator('[data-animate="true"]').first();

      const background = await skeleton.evaluate((el) => {
        const beforeEl = window.getComputedStyle(el, "::before");
        return beforeEl.background;
      });

      expect(background).toBeTruthy();
    });

    test("can disable animation", async ({ page }) => {
      const skeleton = page.locator('[data-animate="false"]').first();

      const animationName = await skeleton.evaluate((el) => {
        return window.getComputedStyle(el).animationName;
      });

      expect(animationName).toBe("none");
    });
  });

  test.describe("Text Variant with Multiple Lines", () => {
    test("renders multiple lines for text variant", async ({ page }) => {
      const textSkeleton = page
        .locator('[data-variant="text"][data-lines="3"]')
        .first();
      const lines = textSkeleton.locator("div");

      const lineCount = await lines.count();
      expect(lineCount).toBe(3);
    });

    test("last line is shorter (80% width)", async ({ page }) => {
      const textSkeleton = page
        .locator('[data-variant="text"][data-lines="3"]')
        .first();
      const lastLine = textSkeleton.locator("div").last();

      const width = await lastLine.evaluate((el) => {
        return window.getComputedStyle(el).width;
      });

      expect(width).toContain("80%");
    });

    test("lines have consistent spacing", async ({ page }) => {
      const textSkeleton = page
        .locator('[data-variant="text"][data-lines="3"]')
        .first();

      const marginBottom = await textSkeleton.evaluate((el) => {
        return window.getComputedStyle(el).marginBottom;
      });

      expect(marginBottom).toBeTruthy();
    });
  });

  test.describe("Glassmorphic Effects", () => {
    test("has semi-transparent background", async ({ page }) => {
      const skeleton = page.locator('[role="status"]').first();

      const backgroundColor = await skeleton.evaluate((el) => {
        return window.getComputedStyle(el).backgroundColor;
      });

      // Should be rgba with alpha < 1
      expect(backgroundColor).toMatch(/rgba?\(.*,\s*0\.\d+\)/);
    });

    test("has backdrop blur effect", async ({ page }) => {
      const skeleton = page.locator('[role="status"]').first();

      const backdropFilter = await skeleton.evaluate((el) => {
        return window.getComputedStyle(el).backdropFilter;
      });

      expect(backdropFilter).toContain("blur");
    });
  });

  test.describe("Accessibility", () => {
    test("has role='status' for loading state", async ({ page }) => {
      const skeleton = page.locator('[role="status"]').first();
      await expect(skeleton).toHaveAttribute("role", "status");
    });

    test("has aria-live='polite' for updates", async ({ page }) => {
      const skeleton = page.locator('[aria-live="polite"]').first();
      await expect(skeleton).toHaveAttribute("aria-live", "polite");
    });

    test("has aria-busy='true' during loading", async ({ page }) => {
      const skeleton = page.locator('[aria-busy="true"]').first();
      await expect(skeleton).toHaveAttribute("aria-busy", "true");
    });
  });
});

test.describe("SkeletonCard Component", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/components/atoms/skeleton-card");
  });

  test.describe("Avatar Display", () => {
    test("shows avatar when enabled", async ({ page }) => {
      const card = page.locator('[data-show-avatar="true"]').first();
      const avatar = card.locator('[data-variant="circular"]').first();

      await expect(avatar).toBeVisible();
    });

    test("avatar has correct size (48x48)", async ({ page }) => {
      const avatar = page
        .locator('[data-variant="circular"][data-avatar]')
        .first();

      const width = await avatar.evaluate(
        (el) => (el as HTMLElement).offsetWidth
      );
      const height = await avatar.evaluate(
        (el) => (el as HTMLElement).offsetHeight
      );

      expect(width).toBe(48);
      expect(height).toBe(48);
    });

    test("shows title and subtitle skeletons with avatar", async ({ page }) => {
      const card = page.locator('[data-show-avatar="true"]').first();
      const title = card.locator('[data-skeleton="title"]').first();
      const subtitle = card.locator('[data-skeleton="subtitle"]').first();

      await expect(title).toBeVisible();
      await expect(subtitle).toBeVisible();
    });

    test("hides avatar when disabled", async ({ page }) => {
      const card = page.locator('[data-show-avatar="false"]').first();
      const avatar = card.locator('[data-variant="circular"]');

      const count = await avatar.count();
      expect(count).toBe(0);
    });
  });

  test.describe("Text Lines", () => {
    test("renders specified number of text lines", async ({ page }) => {
      const card = page.locator('[data-lines="4"]').first();
      const textLines = card.locator('[data-variant="text"] div');

      const lineCount = await textLines.count();
      expect(lineCount).toBe(4);
    });

    test("default to 3 lines", async ({ page }) => {
      const card = page.locator("[data-card-default]").first();
      const textLines = card.locator('[data-variant="text"] div');

      const lineCount = await textLines.count();
      expect(lineCount).toBe(3);
    });
  });

  test.describe("Card Layout", () => {
    test("has proper spacing (p-6)", async ({ page }) => {
      const card = page.locator("[data-skeleton-card]").first();

      const padding = await card.evaluate((el) => {
        return window.getComputedStyle(el).padding;
      });

      expect(padding).toContain("24px"); // p-6 = 1.5rem = 24px
    });

    test("elements have gap spacing", async ({ page }) => {
      const card = page.locator("[data-skeleton-card]").first();

      const gap = await card.evaluate((el) => {
        return window.getComputedStyle(el).gap;
      });

      expect(gap).toBeTruthy();
    });
  });
});

test.describe("SkeletonImage Component", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/components/atoms/skeleton-image");
  });

  test.describe("Rendering & Sizing", () => {
    test("renders with custom dimensions", async ({ page }) => {
      const imageSkeleton = page
        .locator('[data-skeleton-image][data-width="300"][data-height="200"]')
        .first();

      const width = await imageSkeleton.evaluate(
        (el) => (el as HTMLElement).offsetWidth
      );
      const height = await imageSkeleton.evaluate(
        (el) => (el as HTMLElement).offsetHeight
      );

      expect(width).toBe(300);
      expect(height).toBe(200);
    });

    test("maintains aspect ratio container", async ({ page }) => {
      const imageSkeleton = page.locator("[data-skeleton-image]").first();

      const aspectRatio = await imageSkeleton.evaluate((el) => {
        const width = (el as HTMLElement).offsetWidth;
        const height = (el as HTMLElement).offsetHeight;
        return width / height;
      });

      expect(aspectRatio).toBeGreaterThan(0);
    });
  });
});

test.describe("Skeleton - Responsive Design", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/components/atoms/skeleton");
  });

  test.describe("Cross-Device Rendering", () => {
    test("renders correctly on mobile", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      const skeleton = page.locator('[role="status"]').first();
      await expect(skeleton).toBeVisible();
    });

    test("renders correctly on tablet", async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });

      const skeleton = page.locator('[role="status"]').first();
      await expect(skeleton).toBeVisible();
    });

    test("renders correctly on desktop", async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });

      const skeleton = page.locator('[role="status"]').first();
      await expect(skeleton).toBeVisible();
    });

    test("percentage widths adapt to viewport", async ({ page }) => {
      const skeleton = page.locator('[data-width="100%"]').first();

      // Mobile
      await page.setViewportSize({ width: 375, height: 667 });
      const mobileWidth = await skeleton.evaluate(
        (el) => (el as HTMLElement).offsetWidth
      );

      // Desktop
      await page.setViewportSize({ width: 1920, height: 1080 });
      const desktopWidth = await skeleton.evaluate(
        (el) => (el as HTMLElement).offsetWidth
      );

      expect(desktopWidth).toBeGreaterThan(mobileWidth);
    });
  });
});
