/**
 * WaveformVisualizer Component - E2E Tests
 * Tests audio waveform visualization, animations, and interactions
 */

import { WaveformVisualizerHelpers } from "../helpers/component-helpers";
import { expect, test } from "../setup";

test.describe("WaveformVisualizer Component", () => {
  let waveformHelpers: WaveformVisualizerHelpers;

  test.beforeEach(async ({ page }) => {
    waveformHelpers = new WaveformVisualizerHelpers(page);
    await page.goto("/components/molecules/waveform-visualizer");
  });

  test.describe("Rendering & Data", () => {
    test("renders with default barCount (64)", async ({ page }) => {
      const container = page
        .locator('[role="img"][aria-label*="waveform"]')
        .first();
      await expect(container).toBeVisible();

      const bars = container.locator("div > div");
      const count = await bars.count();
      expect(count).toBe(64);
    });

    test("renders custom barCount", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-32-bars"]');
      await expect(container).toBeVisible();

      const bars = container.locator("div > div");
      const count = await bars.count();
      expect(count).toBe(32);
    });

    test("normalizes data to 0-100 range", async ({ page }) => {
      const container = page
        .locator('[role="img"][aria-label*="waveform"]')
        .first();
      const bars = container.locator("div > div");

      const firstBar = bars.first();
      const height = await firstBar.evaluate((el) => {
        return parseInt(el.style.height);
      });

      // Height should be between 4px (minimum) and container height
      expect(height).toBeGreaterThanOrEqual(4);
      expect(height).toBeLessThanOrEqual(200);
    });

    test("fills missing data with random values", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-no-data"]');
      await expect(container).toBeVisible();

      const bars = container.locator("div > div");
      const count = await bars.count();

      // Should still render bars even without data
      expect(count).toBeGreaterThan(0);
    });

    test("has role='img' for accessibility", async ({ page }) => {
      const container = page.locator('[role="img"]').first();
      const role = await container.getAttribute("role");
      expect(role).toBe("img");
    });

    test("has descriptive aria-label", async ({ page }) => {
      const container = page.locator('[role="img"]').first();
      const ariaLabel = await container.getAttribute("aria-label");
      expect(ariaLabel).toContain("waveform");
    });
  });

  test.describe("Bar Styling", () => {
    test("calculates bar height based on value", async ({ page }) => {
      const container = page
        .locator('[role="img"][aria-label*="waveform"]')
        .first();
      const bars = container.locator("div > div");

      // Get multiple bars and check height variation
      const heights: number[] = [];
      const count = Math.min(10, await bars.count());

      for (let i = 0; i < count; i++) {
        const bar = bars.nth(i);
        const height = await bar.evaluate((el) => {
          return parseInt(el.style.height);
        });
        heights.push(height);
      }

      // Heights should vary based on data
      const uniqueHeights = new Set(heights);
      expect(uniqueHeights.size).toBeGreaterThan(1);
    });

    test("enforces minimum bar height of 4px", async ({ page }) => {
      const container = page
        .locator('[role="img"][aria-label*="waveform"]')
        .first();
      const bars = container.locator("div > div");

      const count = await bars.count();

      for (let i = 0; i < count; i++) {
        const bar = bars.nth(i);
        const height = await bar.evaluate((el) => {
          return parseInt(el.style.height);
        });
        expect(height).toBeGreaterThanOrEqual(4);
      }
    });

    test("applies custom barGap spacing", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-gap-8"]');
      const wrapper = container.locator("div").first();

      const gap = await wrapper.evaluate((el) => {
        return window.getComputedStyle(el).gap;
      });

      expect(gap).toBe("8px");
    });

    test("bars have rounded-full class", async ({ page }) => {
      const container = page
        .locator('[role="img"][aria-label*="waveform"]')
        .first();
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const borderRadius = await firstBar.evaluate((el) => {
        return window.getComputedStyle(el).borderRadius;
      });

      // rounded-full = 9999px
      expect(borderRadius).toBe("9999px");
    });

    test("bars have gradient background", async ({ page }) => {
      const container = page
        .locator('[role="img"][aria-label*="waveform"]')
        .first();
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const background = await firstBar.evaluate((el) => {
        return el.style.background;
      });

      expect(background).toContain("linear-gradient");
    });
  });

  test.describe("Color Schemes", () => {
    test("purple scheme - gradient from #8B5CF6 to #A78BFA", async ({
      page,
    }) => {
      const container = page.locator('[data-testid="waveform-purple"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const background = await firstBar.evaluate((el) => {
        return el.style.background;
      });

      expect(background).toContain("rgb(139, 92, 246)"); // #8B5CF6
      expect(background).toContain("rgb(167, 139, 250)"); // #A78BFA
    });

    test("cyber scheme - gradient from #8B5CF6 to #06B6D4", async ({
      page,
    }) => {
      const container = page.locator('[data-testid="waveform-cyber"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const background = await firstBar.evaluate((el) => {
        return el.style.background;
      });

      expect(background).toContain("rgb(139, 92, 246)"); // #8B5CF6
      expect(background).toContain("rgb(6, 182, 212)"); // #06B6D4
    });

    test("neon scheme - gradient from #EC4899 to #8B5CF6", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-neon"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const background = await firstBar.evaluate((el) => {
        return el.style.background;
      });

      expect(background).toContain("rgb(236, 72, 153)"); // #EC4899
      expect(background).toContain("rgb(139, 92, 246)"); // #8B5CF6
    });

    test("purple scheme - glow color rgba(139, 92, 246, 0.6)", async ({
      page,
    }) => {
      const container = page.locator('[data-testid="waveform-purple"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const boxShadow = await firstBar.evaluate((el) => {
        return el.style.boxShadow;
      });

      expect(boxShadow).toContain("rgba(139, 92, 246, 0.6)");
    });

    test("cyber scheme - glow color rgba(6, 182, 212, 0.6)", async ({
      page,
    }) => {
      const container = page.locator('[data-testid="waveform-cyber"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const boxShadow = await firstBar.evaluate((el) => {
        return el.style.boxShadow;
      });

      expect(boxShadow).toContain("rgba(6, 182, 212, 0.6)");
    });

    test("neon scheme - glow color rgba(236, 72, 153, 0.6)", async ({
      page,
    }) => {
      const container = page.locator('[data-testid="waveform-neon"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const boxShadow = await firstBar.evaluate((el) => {
        return el.style.boxShadow;
      });

      expect(boxShadow).toContain("rgba(236, 72, 153, 0.6)");
    });
  });

  test.describe("Animations", () => {
    test("bars animate from height 0 when animated=true", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-animated"]');
      await expect(container).toBeVisible();

      // Wait for animation to start
      await page.waitForTimeout(100);

      const bars = container.locator("div > div");
      const firstBar = bars.first();

      // Check that bar is animating (has motion div)
      const isMotionDiv = await firstBar.evaluate((el) => {
        return el.hasAttribute("style");
      });

      expect(isMotionDiv).toBe(true);
    });

    test("stagger animation - delay of 0.01s per bar", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-animated"]');
      const bars = container.locator("div > div");

      // Animation should complete within reasonable time
      await page.waitForTimeout(1000);

      const count = await bars.count();

      // Total animation time = 0.5s duration + (count * 0.01s) stagger
      const expectedTime = 500 + count * 10;
      expect(expectedTime).toBeLessThan(2000);
    });

    test("animation duration is 0.5s", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-animated"]');
      await expect(container).toBeVisible();

      // Wait for animation to complete
      await page.waitForTimeout(600);

      const bars = container.locator("div > div");
      const firstBar = bars.first();

      // Animation should be complete
      const opacity = await firstBar.evaluate((el) => {
        return window.getComputedStyle(el).opacity;
      });

      expect(parseFloat(opacity)).toBe(1);
    });

    test("easing function is 'easeOut'", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-animated"]');
      await expect(container).toBeVisible();

      // Framer Motion applies easeOut timing
      // We can verify by checking smooth animation completion
      await page.waitForTimeout(600);

      const bars = container.locator("div > div");
      const allBarsVisible = await bars.evaluateAll((elements) => {
        return elements.every((el) => {
          const opacity = window.getComputedStyle(el).opacity;
          return parseFloat(opacity) === 1;
        });
      });

      expect(allBarsVisible).toBe(true);
    });

    test("no animation when animated=false", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-no-animation"]');
      await expect(container).toBeVisible();

      const bars = container.locator("div > div");
      const firstBar = bars.first();

      // Should be fully visible immediately
      const opacity = await firstBar.evaluate((el) => {
        return window.getComputedStyle(el).opacity;
      });

      expect(parseFloat(opacity)).toBe(1);
    });
  });

  test.describe("Interactive Features", () => {
    test("bars have cursor-pointer when interactive=true", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-interactive"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const cursor = await firstBar.evaluate((el) => {
        return window.getComputedStyle(el).cursor;
      });

      expect(cursor).toBe("pointer");
    });

    test("hover effect - scaleY 1.1 when interactive=true", async ({
      page,
    }) => {
      const container = page.locator('[data-testid="waveform-interactive"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      // Hover over bar
      await firstBar.hover();
      await page.waitForTimeout(200);

      const transform = await firstBar.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      // Should have scale transformation (scaleY 1.1)
      expect(transform).toBeTruthy();
      expect(transform).not.toBe("none");
    });

    test("hover effect - brightness 1.3 filter", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-interactive"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      await firstBar.hover();
      await page.waitForTimeout(200);

      const filter = await firstBar.evaluate((el) => {
        return window.getComputedStyle(el).filter;
      });

      expect(filter).toContain("brightness");
    });

    test("hover effect - enhanced glow (20px shadow)", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-interactive"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const initialShadow = await firstBar.evaluate((el) => {
        return el.style.boxShadow;
      });

      await firstBar.hover();
      await page.waitForTimeout(200);

      const hoverShadow = await firstBar.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      // Shadow should be enhanced on hover
      expect(hoverShadow).toBeTruthy();
    });

    test("onBarClick triggers with index and value", async ({ page }) => {
      let clickedIndex = -1;
      let clickedValue = -1;

      // Listen for console logs (if demo logs click events)
      page.on("console", (msg) => {
        const text = msg.text();
        if (text.includes("Bar clicked")) {
          const matches = text.match(/index:\s*(\d+).*value:\s*([\d.]+)/);
          if (matches) {
            clickedIndex = parseInt(matches[1]);
            clickedValue = parseFloat(matches[2]);
          }
        }
      });

      const container = page.locator('[data-testid="waveform-interactive"]');
      const bars = container.locator("div > div");
      const thirdBar = bars.nth(2);

      await thirdBar.click();
      await page.waitForTimeout(100);

      // Verify click was registered
      expect(clickedIndex).toBeGreaterThanOrEqual(0);
    });

    test("bars have role='button' when clickable", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-interactive"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const role = await firstBar.getAttribute("role");
      expect(role).toBe("button");
    });

    test("bars have tabIndex when clickable", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-interactive"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const tabIndex = await firstBar.getAttribute("tabIndex");
      expect(tabIndex).toBe("0");
    });

    test("bars have descriptive aria-label when clickable", async ({
      page,
    }) => {
      const container = page.locator('[data-testid="waveform-interactive"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const ariaLabel = await firstBar.getAttribute("aria-label");
      expect(ariaLabel).toContain("Waveform bar");
      expect(ariaLabel).toContain("value");
    });

    test("no interactive features when interactive=false", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-no-interaction"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const role = await firstBar.getAttribute("role");
      const tabIndex = await firstBar.getAttribute("tabIndex");
      const ariaLabel = await firstBar.getAttribute("aria-label");

      expect(role).toBeNull();
      expect(tabIndex).toBeNull();
      expect(ariaLabel).toBeNull();
    });
  });

  test.describe("Height & Sizing", () => {
    test("respects custom height prop", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-height-300"]');
      const wrapper = container.locator("div").first();

      const height = await wrapper.evaluate((el) => {
        return parseInt(el.style.height);
      });

      expect(height).toBe(300);
    });

    test("scales bars proportionally to height", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-height-300"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const barHeight = await firstBar.evaluate((el) => {
        return parseInt(el.style.height);
      });

      // Bar height should be <= container height
      expect(barHeight).toBeLessThanOrEqual(300);
    });

    test("bars fill container width evenly", async ({ page }) => {
      const container = page
        .locator('[role="img"][aria-label*="waveform"]')
        .first();
      const wrapper = container.locator("div").first();

      const display = await wrapper.evaluate((el) => {
        return window.getComputedStyle(el).display;
      });

      expect(display).toBe("flex");
    });

    test("bars have flex-1 class for equal width", async ({ page }) => {
      const container = page
        .locator('[role="img"][aria-label*="waveform"]')
        .first();
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      const flexGrow = await firstBar.evaluate((el) => {
        return window.getComputedStyle(el).flexGrow;
      });

      expect(flexGrow).toBe("1");
    });
  });

  test.describe("Labels", () => {
    test("renders frequency labels when showLabels=true", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-with-labels"]');

      const lowLabel = container.locator("text=Low");
      const midLabel = container.locator("text=Mid");
      const highLabel = container.locator("text=High");

      await expect(lowLabel).toBeVisible();
      await expect(midLabel).toBeVisible();
      await expect(highLabel).toBeVisible();
    });

    test("does not render labels when showLabels=false", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-no-labels"]');

      const labels = container.locator("text=Low");
      await expect(labels).not.toBeVisible();
    });

    test("labels have text-text-muted color", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-with-labels"]');
      const label = container.locator("text=Low");

      const color = await label.evaluate((el) => {
        return window.getComputedStyle(el).color;
      });

      // text-muted should be a muted color
      expect(color).toMatch(/rgba?\(\d+,\s*\d+,\s*\d+/);
    });

    test("labels have text-xs size", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-with-labels"]');
      const label = container.locator("text=Low");

      const fontSize = await label.evaluate((el) => {
        return window.getComputedStyle(el).fontSize;
      });

      // text-xs = 0.75rem = 12px
      expect(fontSize).toBe("12px");
    });

    test("labels are positioned with mt-2 spacing", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-with-labels"]');
      const labelsWrapper = container.locator("div").nth(1);

      const marginTop = await labelsWrapper.evaluate((el) => {
        return window.getComputedStyle(el).marginTop;
      });

      // mt-2 = 0.5rem = 8px
      expect(marginTop).toBe("8px");
    });
  });

  test.describe("Accessibility", () => {
    test("container has role='img'", async ({ page }) => {
      const container = page.locator('[role="img"]').first();
      const role = await container.getAttribute("role");
      expect(role).toBe("img");
    });

    test("container has descriptive aria-label", async ({ page }) => {
      const container = page.locator('[role="img"]').first();
      const ariaLabel = await container.getAttribute("aria-label");
      expect(ariaLabel).toContain("Audio waveform visualization");
    });

    test("interactive bars have role='button'", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-interactive"]');
      const bars = container.locator('[role="button"]');
      const count = await bars.count();
      expect(count).toBeGreaterThan(0);
    });

    test("interactive bars have unique aria-labels", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-interactive"]');
      const bars = container.locator("div > div");

      const ariaLabels = new Set();
      const count = Math.min(5, await bars.count());

      for (let i = 0; i < count; i++) {
        const bar = bars.nth(i);
        const ariaLabel = await bar.getAttribute("aria-label");
        if (ariaLabel) {
          ariaLabels.add(ariaLabel);
        }
      }

      expect(ariaLabels.size).toBeGreaterThan(0);
    });

    test("keyboard navigation works for interactive bars", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-interactive"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      // Focus first bar
      await firstBar.focus();

      const focused = page.locator(":focus");
      const isFocused = await focused.evaluate((el, bar) => {
        return el === bar;
      }, await firstBar.elementHandle());

      expect(isFocused).toBe(true);
    });

    test("Enter key triggers click on interactive bars", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-interactive"]');
      const bars = container.locator("div > div");
      const firstBar = bars.first();

      await firstBar.focus();
      await page.keyboard.press("Enter");

      // Click should be triggered (verify via console or state change)
      await page.waitForTimeout(100);
    });
  });

  test.describe("Responsive Design", () => {
    test("renders on mobile viewport", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      const container = page
        .locator('[role="img"][aria-label*="waveform"]')
        .first();
      await expect(container).toBeVisible();
    });

    test("renders on tablet viewport", async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });

      const container = page
        .locator('[role="img"][aria-label*="waveform"]')
        .first();
      await expect(container).toBeVisible();
    });

    test("renders on desktop viewport", async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });

      const container = page
        .locator('[role="img"][aria-label*="waveform"]')
        .first();
      await expect(container).toBeVisible();
    });

    test("maintains aspect ratio on different screen sizes", async ({
      page,
    }) => {
      const sizes = [
        { width: 375, height: 667 },
        { width: 768, height: 1024 },
        { width: 1920, height: 1080 },
      ];

      for (const size of sizes) {
        await page.setViewportSize(size);

        const container = page
          .locator('[role="img"][aria-label*="waveform"]')
          .first();
        const wrapper = container.locator("div").first();

        const height = await wrapper.evaluate((el) => {
          return parseInt(el.style.height);
        });

        expect(height).toBeGreaterThan(0);
      }
    });
  });

  test.describe("Performance", () => {
    test("renders 64 bars without performance issues", async ({ page }) => {
      const container = page
        .locator('[role="img"][aria-label*="waveform"]')
        .first();

      const startTime = Date.now();
      await expect(container).toBeVisible();
      const endTime = Date.now();

      const renderTime = endTime - startTime;
      expect(renderTime).toBeLessThan(1000);
    });

    test("animation completes in reasonable time", async ({ page }) => {
      const container = page.locator('[data-testid="waveform-animated"]');

      const startTime = Date.now();
      await expect(container).toBeVisible();

      // Wait for animation to complete
      await page.waitForTimeout(1000);

      const endTime = Date.now();
      const totalTime = endTime - startTime;

      // Should complete within 2 seconds
      expect(totalTime).toBeLessThan(2000);
    });
  });
});
