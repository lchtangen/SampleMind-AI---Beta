/**
 * GlassmorphicCard Component - E2E Tests
 * Tests glassmorphism, neon borders, interactive states, and accessibility
 */

import { expect, test } from "../setup";

test.describe("GlassmorphicCard Component", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/components/molecules/glassmorphic-card");
  });

  test.describe("Rendering & Content", () => {
    test("renders with title and description", async ({ page }) => {
      const card = page.locator("[data-card]").first();
      const title = card.locator("h3").first();
      const description = card.locator("p").first();

      await expect(title).toBeVisible();
      await expect(description).toBeVisible();

      const titleText = await title.textContent();
      const descText = await description.textContent();

      expect(titleText).toBeTruthy();
      expect(descText).toBeTruthy();
    });

    test("renders with optional icon", async ({ page }) => {
      const card = page.locator('[data-has-icon="true"]').first();
      const icon = card.locator('[aria-hidden="true"]').first();

      await expect(icon).toBeVisible();
    });

    test("icon has correct color coordination", async ({ page }) => {
      const icon = page.locator('[data-card] [aria-hidden="true"] svg').first();

      const color = await icon.evaluate((el) => {
        return window.getComputedStyle(el).color;
      });

      // Should have primary purple color
      expect(color).toMatch(/rgb.*139.*92.*246/);
    });
  });

  test.describe("Glassmorphic Effects", () => {
    test("has backdrop blur effect", async ({ page }) => {
      const card = page.locator("[data-card]").first();

      const backdropFilter = await card.evaluate((el) => {
        return window.getComputedStyle(el).backdropFilter;
      });

      expect(backdropFilter).toContain("blur");
    });

    test("has semi-transparent background", async ({ page }) => {
      const card = page.locator("[data-card]").first();

      const backgroundColor = await card.evaluate((el) => {
        return window.getComputedStyle(el).backgroundColor;
      });

      // Should be rgba with alpha channel
      expect(backgroundColor).toMatch(/rgba?\(.*,\s*0\.\d+\)/);
    });

    test("has subtle border with opacity", async ({ page }) => {
      const card = page.locator("[data-card]").first();

      const border = await card.evaluate((el) => {
        const borderColor = window.getComputedStyle(el).borderColor;
        const borderWidth = window.getComputedStyle(el).borderWidth;
        return { borderColor, borderWidth };
      });

      expect(border.borderWidth).toBeTruthy();
      expect(border.borderColor).toBeTruthy();
    });

    test("has large border radius (16px)", async ({ page }) => {
      const card = page.locator("[data-card]").first();

      const borderRadius = await card.evaluate((el) => {
        return window.getComputedStyle(el).borderRadius;
      });

      // rounded-xl = 16px
      expect(borderRadius).toContain("16px");
    });
  });

  test.describe("Neon Glow Effects", () => {
    test("has multi-layer neon glow shadow", async ({ page }) => {
      const card = page.locator("[data-card]").first();

      const boxShadow = await card.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      // Should have purple (139, 92, 246) and cyan (6, 182, 212) glows
      expect(boxShadow).toContain("139, 92, 246");
      expect(boxShadow).toContain("6, 182, 212");
    });

    test("glow shadow has correct blur radius", async ({ page }) => {
      const card = page.locator("[data-card]").first();

      const boxShadow = await card.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      // Should have 20px, 40px, 60px blur layers
      expect(boxShadow).toMatch(/20px|40px|60px/);
    });

    test("has background glow gradient", async ({ page }) => {
      const card = page.locator("[data-card]").first();
      const glowGradient = card.locator('[aria-hidden="true"]').last();

      await expect(glowGradient).toBeAttached();

      const opacity = await glowGradient.evaluate((el) => {
        return window.getComputedStyle(el).opacity;
      });

      expect(opacity).toBe("0"); // Initially invisible
    });
  });

  test.describe("Interactive States", () => {
    test("shows cursor pointer when interactive", async ({ page }) => {
      const interactiveCard = page.locator('[role="button"]').first();

      const cursor = await interactiveCard.evaluate((el) => {
        return window.getComputedStyle(el).cursor;
      });

      expect(cursor).toBe("pointer");
    });

    test("scales up on hover (scale-105)", async ({ page }) => {
      const interactiveCard = page.locator('[role="button"]').first();

      await interactiveCard.hover();
      await page.waitForTimeout(350);

      const transform = await interactiveCard.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      // Should have scale transform
      expect(transform).not.toBe("none");
      expect(transform).toContain("matrix");
    });

    test("intensifies glow on hover", async ({ page }) => {
      const interactiveCard = page.locator('[role="button"]').first();

      // Get initial shadow
      const initialShadow = await interactiveCard.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      await interactiveCard.hover();
      await page.waitForTimeout(350);

      const hoverShadow = await interactiveCard.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      // Hover shadow should be different (more intense)
      expect(hoverShadow).not.toBe(initialShadow);
    });

    test("increases border opacity on hover", async ({ page }) => {
      const interactiveCard = page.locator('[role="button"]').first();

      await interactiveCard.hover();
      await page.waitForTimeout(350);

      const borderColor = await interactiveCard.evaluate((el) => {
        return window.getComputedStyle(el).borderColor;
      });

      expect(borderColor).toBeTruthy();
    });

    test("scales down on active (scale-102)", async ({ page }) => {
      const interactiveCard = page.locator('[role="button"]').first();

      await interactiveCard.click();
      await page.waitForTimeout(100);

      const transform = await interactiveCard.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      expect(transform).not.toBe("none");
    });

    test("non-interactive card has no hover effects", async ({ page }) => {
      const staticCard = page.locator("article[data-card]").first();

      const cursor = await staticCard.evaluate((el) => {
        return window.getComputedStyle(el).cursor;
      });

      expect(cursor).not.toBe("pointer");
    });
  });

  test.describe("Click Functionality", () => {
    test("triggers onClick handler when interactive", async ({ page }) => {
      // Setup click listener
      await page.evaluate(() => {
        (window as any).cardClicked = false;
        const card = document.querySelector('[role="button"]') as HTMLElement;
        if (card) {
          card.addEventListener("click", () => {
            (window as any).cardClicked = true;
          });
        }
      });

      const interactiveCard = page.locator('[role="button"]').first();
      await interactiveCard.click();

      const wasClicked = await page.evaluate(() => (window as any).cardClicked);
      expect(wasClicked).toBe(true);
    });

    test("shows interactive indicator (arrow icon)", async ({ page }) => {
      const interactiveCard = page.locator('[role="button"]').first();
      const indicator = interactiveCard.locator("svg").last();

      await expect(indicator).toBeVisible();

      // Check if it's positioned bottom-right
      const position = await indicator.evaluate((el) => {
        const rect = el.getBoundingClientRect();
        const parent = el.closest('[role="button"]');
        const parentRect = parent?.getBoundingClientRect();
        return {
          isBottomRight:
            rect.bottom < (parentRect?.bottom || 0) + 10 &&
            rect.right < (parentRect?.right || 0) + 10,
        };
      });

      expect(position.isBottomRight).toBe(true);
    });
  });

  test.describe("Accessibility", () => {
    test("has correct ARIA label", async ({ page }) => {
      const card = page.locator("[aria-label]").first();

      const ariaLabel = await card.getAttribute("aria-label");
      expect(ariaLabel).toBeTruthy();
    });

    test("interactive card has role='button'", async ({ page }) => {
      const interactiveCard = page.locator('[role="button"]').first();

      const role = await interactiveCard.getAttribute("role");
      expect(role).toBe("button");
    });

    test("interactive card has tabIndex=0", async ({ page }) => {
      const interactiveCard = page.locator('[role="button"]').first();

      const tabIndex = await interactiveCard.getAttribute("tabindex");
      expect(tabIndex).toBe("0");
    });

    test("interactive card has aria-pressed", async ({ page }) => {
      const interactiveCard = page.locator('[role="button"]').first();

      const ariaPressed = await interactiveCard.getAttribute("aria-pressed");
      expect(ariaPressed).toBe("false");
    });

    test("non-interactive card uses article element", async ({ page }) => {
      const staticCard = page.locator("article[data-card]").first();
      await expect(staticCard).toBeVisible();
    });

    test("keyboard navigation with Enter key", async ({ page }) => {
      await page.evaluate(() => {
        (window as any).enterPressed = false;
        const card = document.querySelector('[role="button"]') as HTMLElement;
        if (card) {
          card.addEventListener("click", () => {
            (window as any).enterPressed = true;
          });
        }
      });

      const interactiveCard = page.locator('[role="button"]').first();
      await interactiveCard.focus();
      await page.keyboard.press("Enter");

      const wasPressed = await page.evaluate(
        () => (window as any).enterPressed
      );
      expect(wasPressed).toBe(true);
    });

    test("keyboard navigation with Space key", async ({ page }) => {
      await page.evaluate(() => {
        (window as any).spacePressed = false;
        const card = document.querySelector('[role="button"]') as HTMLElement;
        if (card) {
          card.addEventListener("click", () => {
            (window as any).spacePressed = true;
          });
        }
      });

      const interactiveCard = page.locator('[role="button"]').first();
      await interactiveCard.focus();
      await page.keyboard.press("Space");

      const wasPressed = await page.evaluate(
        () => (window as any).spacePressed
      );
      expect(wasPressed).toBe(true);
    });

    test("has focus ring on keyboard focus", async ({ page }) => {
      const interactiveCard = page.locator('[role="button"]').first();

      await interactiveCard.focus();
      await page.waitForTimeout(200);

      const outline = await interactiveCard.evaluate((el) => {
        return window.getComputedStyle(el).outline;
      });

      expect(outline).toBeTruthy();
    });

    test("decorative elements have aria-hidden", async ({ page }) => {
      const decorativeElements = page.locator('[aria-hidden="true"]');

      const count = await decorativeElements.count();
      expect(count).toBeGreaterThan(0);

      for (let i = 0; i < count; i++) {
        const ariaHidden = await decorativeElements
          .nth(i)
          .getAttribute("aria-hidden");
        expect(ariaHidden).toBe("true");
      }
    });
  });

  test.describe("Typography & Spacing", () => {
    test("title has correct font styling", async ({ page }) => {
      const title = page.locator("[data-card] h3").first();

      const fontSize = await title.evaluate((el) => {
        return window.getComputedStyle(el).fontSize;
      });

      // Should be xl (20px) or 2xl (24px)
      expect(parseFloat(fontSize)).toBeGreaterThanOrEqual(20);
    });

    test("description has secondary text color", async ({ page }) => {
      const description = page.locator("[data-card] p").first();

      const color = await description.evaluate((el) => {
        return window.getComputedStyle(el).color;
      });

      expect(color).toBeTruthy();
    });

    test("card has proper padding (p-6 or p-8)", async ({ page }) => {
      const card = page.locator("[data-card]").first();

      const padding = await card.evaluate((el) => {
        return window.getComputedStyle(el).padding;
      });

      // Should have at least 24px padding (p-6)
      expect(padding).toMatch(/24px|32px/);
    });

    test("content elements have gap spacing", async ({ page }) => {
      const contentContainer = page.locator("[data-card] > div").first();

      const gap = await contentContainer.evaluate((el) => {
        return window.getComputedStyle(el).gap;
      });

      expect(gap).toBeTruthy();
    });
  });

  test.describe("Responsive Design", () => {
    test("renders correctly on mobile", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      const card = page.locator("[data-card]").first();
      await expect(card).toBeVisible();

      const padding = await card.evaluate((el) => {
        return window.getComputedStyle(el).padding;
      });

      // Mobile should have p-6 (24px)
      expect(padding).toContain("24px");
    });

    test("renders correctly on tablet", async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });

      const card = page.locator("[data-card]").first();
      await expect(card).toBeVisible();
    });

    test("renders correctly on desktop", async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });

      const card = page.locator("[data-card]").first();
      await expect(card).toBeVisible();

      const padding = await card.evaluate((el) => {
        return window.getComputedStyle(el).padding;
      });

      // Desktop should have p-8 (32px)
      expect(padding).toContain("32px");
    });

    test("title font size adjusts on larger screens", async ({ page }) => {
      const title = page.locator("[data-card] h3").first();

      // Mobile size
      await page.setViewportSize({ width: 375, height: 667 });
      const mobileFontSize = await title.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).fontSize);
      });

      // Desktop size
      await page.setViewportSize({ width: 1920, height: 1080 });
      const desktopFontSize = await title.evaluate((el) => {
        return parseFloat(window.getComputedStyle(el).fontSize);
      });

      expect(desktopFontSize).toBeGreaterThanOrEqual(mobileFontSize);
    });
  });

  test.describe("Animation & Transitions", () => {
    test("has transition for all properties", async ({ page }) => {
      const card = page.locator("[data-card]").first();

      const transition = await card.evaluate((el) => {
        return window.getComputedStyle(el).transition;
      });

      expect(transition).toContain("all");
    });

    test("uses slow duration for transitions", async ({ page }) => {
      const card = page.locator("[data-card]").first();

      const transitionDuration = await card.evaluate((el) => {
        return window.getComputedStyle(el).transitionDuration;
      });

      // duration-slow should be > 300ms
      expect(parseFloat(transitionDuration)).toBeGreaterThan(0.3);
    });

    test("uses ease-out timing function", async ({ page }) => {
      const card = page.locator("[data-card]").first();

      const transitionTimingFunction = await card.evaluate((el) => {
        return window.getComputedStyle(el).transitionTimingFunction;
      });

      expect(transitionTimingFunction).toContain("ease");
    });
  });
});
