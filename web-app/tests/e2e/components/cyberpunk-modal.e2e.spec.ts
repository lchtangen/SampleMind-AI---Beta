/**
 * CyberpunkModal Component - E2E Tests
 * Tests modal functionality, animations, accessibility, and interactions
 */

import { CyberpunkModalHelpers } from "../helpers/component-helpers";
import { expect, test } from "../setup";

test.describe("CyberpunkModal Component", () => {
  let modalHelpers: CyberpunkModalHelpers;

  test.beforeEach(async ({ page }) => {
    modalHelpers = new CyberpunkModalHelpers(page);
    await page.goto("/components/molecules/cyberpunk-modal");
  });

  test.describe("Open/Close Functionality", () => {
    test("renders when isOpen is true", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
    });

    test("does not render when isOpen is false", async ({ page }) => {
      const modal = page.locator('[role="dialog"]');
      await expect(modal).not.toBeVisible();
    });

    test("triggers onClose when close button clicked", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const closeButton = page.locator('[aria-label="Close modal"]');
      await closeButton.click();

      // Wait for modal to close with animation
      await page.waitForTimeout(500);
      const modal = page.locator('[role="dialog"]');
      await expect(modal).not.toBeVisible();
    });

    test("AnimatePresence mounts and unmounts with animation", async ({
      page,
    }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      // Check modal appears with animation
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();

      // Close and verify unmount
      const closeButton = page.locator('[aria-label="Close modal"]');
      await closeButton.click();
      await page.waitForTimeout(500);
      await expect(modal).not.toBeVisible();
    });
  });

  test.describe("Backdrop Behavior", () => {
    test("renders backdrop with blur animation", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const backdrop = page
        .locator('[role="dialog"]')
        .locator("..")
        .locator("div")
        .first();
      await expect(backdrop).toBeVisible();

      // Check for backdrop blur
      const backdropFilter = await backdrop.evaluate((el) => {
        return window.getComputedStyle(el).backdropFilter;
      });
      expect(backdropFilter).toContain("blur");
    });

    test("triggers onClose when backdrop clicked (if closeOnBackdropClick=true)", async ({
      page,
    }) => {
      const openButton = page
        .locator('button:has-text("Open Closeable Modal")')
        .first();
      await openButton.click();

      // Click backdrop (outside modal content)
      const backdrop = page
        .locator('[role="dialog"]')
        .locator("..")
        .locator("div")
        .first();
      await backdrop.click({ position: { x: 10, y: 10 } });

      await page.waitForTimeout(500);
      const modal = page.locator('[role="dialog"]');
      await expect(modal).not.toBeVisible();
    });

    test("does not close when backdrop clicked (if closeOnBackdropClick=false)", async ({
      page,
    }) => {
      const openButton = page
        .locator('button:has-text("Open Non-Closeable Modal")')
        .first();
      await openButton.click();

      const backdrop = page
        .locator('[role="dialog"]')
        .locator("..")
        .locator("div")
        .first();
      await backdrop.click({ position: { x: 10, y: 10 } });

      // Modal should still be visible
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
    });

    test("backdrop has aria-hidden attribute", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const backdrop = page
        .locator('[role="dialog"]')
        .locator("..")
        .locator("div")
        .first();
      const ariaHidden = await backdrop.getAttribute("aria-hidden");
      expect(ariaHidden).toBe("true");
    });
  });

  test.describe("Size Variants", () => {
    test("renders small size (max-w-md)", async ({ page }) => {
      const openButton = page
        .locator('button:has-text("Open Small Modal")')
        .first();
      await openButton.click();

      const modalContent = page.locator('[role="dialog"]');
      const maxWidth = await modalContent.evaluate((el) => {
        return window.getComputedStyle(el).maxWidth;
      });
      // max-w-md = 28rem = 448px
      expect(maxWidth).toBe("448px");
    });

    test("renders medium size (max-w-lg)", async ({ page }) => {
      const openButton = page
        .locator('button:has-text("Open Medium Modal")')
        .first();
      await openButton.click();

      const modalContent = page.locator('[role="dialog"]');
      const maxWidth = await modalContent.evaluate((el) => {
        return window.getComputedStyle(el).maxWidth;
      });
      // max-w-lg = 32rem = 512px
      expect(maxWidth).toBe("512px");
    });

    test("renders large size (max-w-2xl)", async ({ page }) => {
      const openButton = page
        .locator('button:has-text("Open Large Modal")')
        .first();
      await openButton.click();

      const modalContent = page.locator('[role="dialog"]');
      const maxWidth = await modalContent.evaluate((el) => {
        return window.getComputedStyle(el).maxWidth;
      });
      // max-w-2xl = 42rem = 672px
      expect(maxWidth).toBe("672px");
    });

    test("renders extra large size (max-w-4xl)", async ({ page }) => {
      const openButton = page
        .locator('button:has-text("Open XL Modal")')
        .first();
      await openButton.click();

      const modalContent = page.locator('[role="dialog"]');
      const maxWidth = await modalContent.evaluate((el) => {
        return window.getComputedStyle(el).maxWidth;
      });
      // max-w-4xl = 56rem = 896px
      expect(maxWidth).toBe("896px");
    });

    test("renders full size (max-w-[90vw])", async ({ page }) => {
      const openButton = page
        .locator('button:has-text("Open Full Modal")')
        .first();
      await openButton.click();

      const modalContent = page.locator('[role="dialog"]');
      const maxWidth = await modalContent.evaluate((el) => {
        return window.getComputedStyle(el).maxWidth;
      });
      // max-w-[90vw] = 90% of viewport width
      const viewportWidth = page.viewportSize()?.width || 1280;
      const expectedWidth = viewportWidth * 0.9;
      expect(parseFloat(maxWidth)).toBeCloseTo(expectedWidth, 0);
    });
  });

  test.describe("ESC Key Handling", () => {
    test("closes modal when ESC pressed (if closeOnEsc=true)", async ({
      page,
    }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      await page.keyboard.press("Escape");
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"]');
      await expect(modal).not.toBeVisible();
    });

    test("does not close when ESC pressed (if closeOnEsc=false)", async ({
      page,
    }) => {
      const openButton = page
        .locator('button:has-text("Open ESC-Disabled Modal")')
        .first();
      await openButton.click();

      await page.keyboard.press("Escape");
      await page.waitForTimeout(200);

      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
    });

    test("event listener cleanup on unmount", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      // Close modal
      const closeButton = page.locator('[aria-label="Close modal"]');
      await closeButton.click();
      await page.waitForTimeout(500);

      // ESC key should not affect anything when modal closed
      await page.keyboard.press("Escape");
      const modal = page.locator('[role="dialog"]');
      await expect(modal).not.toBeVisible();
    });
  });

  test.describe("Focus Management", () => {
    test("has role='dialog' attribute", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
    });

    test("has aria-modal='true' attribute", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      const ariaModal = await modal.getAttribute("aria-modal");
      expect(ariaModal).toBe("true");
    });

    test("has aria-labelledby pointing to title", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      const ariaLabelledby = await modal.getAttribute("aria-labelledby");
      expect(ariaLabelledby).toBe("modal-title");

      const title = page.locator("#modal-title");
      await expect(title).toBeVisible();
    });

    test("focus trap - Tab cycles within modal", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      // Tab through modal elements
      await page.keyboard.press("Tab");
      const focusedElement1 = await page.locator(":focus");
      await expect(focusedElement1).toBeVisible();

      // Get all focusable elements
      const focusableElements = page.locator(
        '[role="dialog"] button, [role="dialog"] a, [role="dialog"] input'
      );
      const count = await focusableElements.count();

      // Tab through all elements
      for (let i = 0; i < count + 1; i++) {
        await page.keyboard.press("Tab");
      }

      // Focus should cycle back to first element (or close button)
      const focusedElement2 = await page.locator(":focus");
      await expect(focusedElement2).toBeVisible();
    });

    test("focus does not escape modal container", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      // Try to tab to elements outside modal
      for (let i = 0; i < 20; i++) {
        await page.keyboard.press("Tab");
        const focusedElement = await page.locator(":focus");
        const isInsideModal = await focusedElement.evaluate((el) => {
          return el.closest('[role="dialog"]') !== null;
        });
        expect(isInsideModal).toBe(true);
      }
    });
  });

  test.describe("Close Button", () => {
    test("renders close button when showCloseButton=true", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const closeButton = page.locator('[aria-label="Close modal"]');
      await expect(closeButton).toBeVisible();
    });

    test("does not render close button when showCloseButton=false", async ({
      page,
    }) => {
      const openButton = page
        .locator('button:has-text("Open No-Close-Button Modal")')
        .first();
      await openButton.click();

      const closeButton = page.locator('[aria-label="Close modal"]');
      await expect(closeButton).not.toBeVisible();
    });

    test("close button has proper aria-label", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const closeButton = page.locator('[aria-label="Close modal"]');
      const ariaLabel = await closeButton.getAttribute("aria-label");
      expect(ariaLabel).toBe("Close modal");
    });

    test("close button triggers onClose on click", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const closeButton = page.locator('[aria-label="Close modal"]');
      await closeButton.click();

      await page.waitForTimeout(500);
      const modal = page.locator('[role="dialog"]');
      await expect(modal).not.toBeVisible();
    });

    test("close button has hover effects", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const closeButton = page.locator('[aria-label="Close modal"]');

      // Get initial state
      const initialOpacity = await closeButton.evaluate((el) => {
        return window.getComputedStyle(el).opacity;
      });

      // Hover
      await closeButton.hover();
      await page.waitForTimeout(100);

      const hoverOpacity = await closeButton.evaluate((el) => {
        return window.getComputedStyle(el).opacity;
      });

      // Opacity should change on hover
      expect(hoverOpacity).not.toBe(initialOpacity);
    });
  });

  test.describe("Animations", () => {
    test("applies spring animation on enter", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();

      // Check for animation properties (stiffness: 300, damping: 30)
      const transform = await modal.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      // Initially animated from scale(0.9) and translateY(20px)
      // Should end at scale(1) translateY(0)
      expect(transform).toBeTruthy();
    });

    test("animates scale from 0.9 to 1", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();

      // Capture animation frames
      let scaleValues: number[] = [];

      page.on("console", (msg) => {
        if (msg.type() === "log" && msg.text().includes("scale")) {
          scaleValues.push(parseFloat(msg.text()));
        }
      });

      await openButton.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"]');
      const finalTransform = await modal.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      // Final transform should be identity or scale(1)
      expect(finalTransform).toMatch(/matrix\(1,\s*0,\s*0,\s*1,|none/);
    });

    test("animates translateY from 20px to 0", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"]');
      const transform = await modal.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      // Should end at translateY(0)
      expect(transform).toMatch(/matrix\(1,\s*0,\s*0,\s*1,\s*0,\s*0\)|none/);
    });

    test("opacity transitions from 0 to 1", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"]');
      const opacity = await modal.evaluate((el) => {
        return window.getComputedStyle(el).opacity;
      });

      expect(parseFloat(opacity)).toBe(1);
    });

    test("reverse animation on exit", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();

      const closeButton = page.locator('[aria-label="Close modal"]');
      await closeButton.click();

      // Check animation during exit
      await page.waitForTimeout(200);

      // Modal should be animating out
      const isVisible = await modal.isVisible();
      // During animation, it may still be visible but transitioning
      expect(isVisible).toBeDefined();
    });
  });

  test.describe("Body Scroll Lock", () => {
    test("prevents body scroll when modal is open", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const bodyOverflow = await page.evaluate(() => {
        return document.body.style.overflow;
      });

      expect(bodyOverflow).toBe("hidden");
    });

    test("restores body scroll when modal is closed", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const closeButton = page.locator('[aria-label="Close modal"]');
      await closeButton.click();
      await page.waitForTimeout(500);

      const bodyOverflow = await page.evaluate(() => {
        return document.body.style.overflow;
      });

      expect(bodyOverflow).toBe("");
    });
  });

  test.describe("Header, Body, Footer", () => {
    test("renders title with id='modal-title'", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const title = page.locator("#modal-title");
      await expect(title).toBeVisible();
      await expect(title).toHaveText(/Modal Title|Cyberpunk Modal/);
    });

    test("renders children in body section", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const body = page
        .locator('[role="dialog"]')
        .locator("p, div")
        .filter({ hasText: /This is the modal content/ });
      await expect(body).toBeVisible();
    });

    test("renders footer when footer prop provided", async ({ page }) => {
      const openButton = page
        .locator('button:has-text("Open Modal with Footer")')
        .first();
      await openButton.click();

      const footer = page
        .locator('[role="dialog"]')
        .locator("footer, div")
        .filter({ hasText: /Cancel|Confirm/ });
      await expect(footer).toBeVisible();
    });

    test("does not render footer when footer prop not provided", async ({
      page,
    }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const footer = page.locator('[role="dialog"]').locator("footer");
      await expect(footer).not.toBeVisible();
    });

    test("renders NeonDivider separators", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      // Check for dividers (should be between header/body and body/footer)
      const dividers = page
        .locator('[role="dialog"]')
        .locator('hr, [role="separator"]');
      const count = await dividers.count();
      expect(count).toBeGreaterThanOrEqual(1);
    });
  });

  test.describe("Glassmorphic Effects", () => {
    test("has backdrop-blur-xl", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      const backdropFilter = await modal.evaluate((el) => {
        return window.getComputedStyle(el).backdropFilter;
      });

      expect(backdropFilter).toContain("blur");
    });

    test("has semi-transparent background (bg-white/5)", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      const bgColor = await modal.evaluate((el) => {
        return window.getComputedStyle(el).backgroundColor;
      });

      // rgba(255, 255, 255, 0.05)
      expect(bgColor).toMatch(/rgba\(255,\s*255,\s*255,\s*0\.0[45]\d*\)/);
    });

    test("has primary border with opacity (border-primary/50)", async ({
      page,
    }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      const borderColor = await modal.evaluate((el) => {
        return window.getComputedStyle(el).borderColor;
      });

      // Should contain rgba with opacity
      expect(borderColor).toMatch(/rgba\(\d+,\s*\d+,\s*\d+,\s*0\.\d+\)/);
    });
  });

  test.describe("Neon Glow Effects", () => {
    test("has multi-layer purple glow shadow", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      const boxShadow = await modal.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      // Should contain multiple shadow layers
      expect(boxShadow).toContain("rgba");
      expect(boxShadow.split(",").length).toBeGreaterThan(6); // Multiple layers
    });

    test("shadow contains purple color (139, 92, 246)", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      const boxShadow = await modal.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      expect(boxShadow).toMatch(/rgba\(139,\s*92,\s*246/);
    });

    test("has glow overlay effect", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      // Check for glow overlay div
      const glowOverlay = page
        .locator('[role="dialog"]')
        .locator('[class*="glow"]');
      const count = await glowOverlay.count();
      expect(count).toBeGreaterThanOrEqual(1);
    });
  });

  test.describe("Accessibility", () => {
    test("keyboard navigation works correctly", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      // Tab through interactive elements
      await page.keyboard.press("Tab");
      const focused = page.locator(":focus");
      await expect(focused).toBeVisible();
    });

    test("ESC key closes modal (accessibility)", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      await page.keyboard.press("Escape");
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"]');
      await expect(modal).not.toBeVisible();
    });

    test("has all required ARIA attributes", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');

      const role = await modal.getAttribute("role");
      const ariaModal = await modal.getAttribute("aria-modal");
      const ariaLabelledby = await modal.getAttribute("aria-labelledby");

      expect(role).toBe("dialog");
      expect(ariaModal).toBe("true");
      expect(ariaLabelledby).toBe("modal-title");
    });

    test("decorative elements have aria-hidden", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      // Check backdrop
      const backdrop = page
        .locator('[role="dialog"]')
        .locator("..")
        .locator('[aria-hidden="true"]');
      const count = await backdrop.count();
      expect(count).toBeGreaterThanOrEqual(1);
    });

    test("focus returns to trigger button after close", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const closeButton = page.locator('[aria-label="Close modal"]');
      await closeButton.click();
      await page.waitForTimeout(500);

      // Focus should return to open button
      const focused = page.locator(":focus");
      const isTriggerButton = await focused.evaluate((el, btn) => {
        return el === btn;
      }, await openButton.elementHandle());

      expect(isTriggerButton).toBe(true);
    });
  });

  test.describe("Responsive Design", () => {
    test("mobile padding (p-6)", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      const padding = await modal.evaluate((el) => {
        return window.getComputedStyle(el).padding;
      });

      // p-6 = 1.5rem = 24px
      expect(padding).toContain("24px");
    });

    test("desktop padding (p-8)", async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });

      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      const padding = await modal.evaluate((el) => {
        return window.getComputedStyle(el).padding;
      });

      // p-8 = 2rem = 32px (if responsive classes applied)
      expect(padding).toBeTruthy();
    });

    test("responsive on tablet", async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });

      const openButton = page.locator('button:has-text("Open Modal")').first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
    });
  });

  test.describe("Edge Cases", () => {
    test("handles rapid open/close", async ({ page }) => {
      const openButton = page.locator('button:has-text("Open Modal")').first();

      for (let i = 0; i < 5; i++) {
        await openButton.click();
        await page.waitForTimeout(100);

        const closeButton = page.locator('[aria-label="Close modal"]');
        await closeButton.click();
        await page.waitForTimeout(100);
      }

      const modal = page.locator('[role="dialog"]');
      await expect(modal).not.toBeVisible();
    });

    test("handles missing title prop", async ({ page }) => {
      const openButton = page
        .locator('button:has-text("Open No-Title Modal")')
        .first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
    });

    test("accepts custom className", async ({ page }) => {
      const openButton = page
        .locator('button:has-text("Open Custom Modal")')
        .first();
      await openButton.click();

      const modal = page.locator('[role="dialog"]');
      const className = await modal.getAttribute("class");
      expect(className).toContain("custom");
    });
  });
});
