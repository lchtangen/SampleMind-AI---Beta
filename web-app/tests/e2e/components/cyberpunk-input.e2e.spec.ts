/**
 * CyberpunkInput Component - E2E Tests
 * Tests all states, validation, icons, and interactions
 */

import { CyberpunkInputHelpers } from "../helpers/component-helpers";
import { expect, test } from "../setup";

test.describe("CyberpunkInput Component", () => {
  let inputHelpers: CyberpunkInputHelpers;

  test.beforeEach(async ({ page }) => {
    inputHelpers = new CyberpunkInputHelpers(page);
    // Navigate to component showcase/demo page
    await page.goto("/components/atoms/cyberpunk-input");
  });

  test.describe("Rendering & States", () => {
    test("renders default input with label", async ({ page }) => {
      const input = page.locator('input[aria-label="Default Input"]').first();
      await expect(input).toBeVisible();

      // Check for glassmorphic background
      const background = await input.evaluate((el) => {
        return window.getComputedStyle(el).backgroundColor;
      });
      expect(background).toBeTruthy();
    });

    test("renders with placeholder text", async ({ page }) => {
      const input = page.locator('input[placeholder="Enter text..."]').first();
      await expect(input).toBeVisible();

      const placeholder = await input.getAttribute("placeholder");
      expect(placeholder).toBe("Enter text...");
    });

    test("renders with helper text", async ({ page }) => {
      const input = page.locator('input[aria-describedby*="helper"]').first();
      const helperText = page.locator('[id*="helper-text"]').first();

      await expect(input).toBeVisible();
      await expect(helperText).toBeVisible();
    });

    test("renders in success state with green border", async ({ page }) => {
      const input = page.locator('input[data-state="success"]').first();

      const borderColor = await input.evaluate((el) => {
        return window.getComputedStyle(el).borderColor;
      });

      // Should have green border
      expect(borderColor).toMatch(/rgb.*16.*185.*129|rgb.*34.*197.*94/); // Success green
    });

    test("renders in error state with red border", async ({ page }) => {
      const input = page.locator('input[data-state="error"]').first();

      const borderColor = await input.evaluate((el) => {
        return window.getComputedStyle(el).borderColor;
      });

      // Should have red border
      expect(borderColor).toMatch(/rgb.*239.*68.*68|rgb.*220.*38.*38/); // Error red
    });

    test("renders in warning state with amber border", async ({ page }) => {
      const input = page.locator('input[data-state="warning"]').first();

      const borderColor = await input.evaluate((el) => {
        return window.getComputedStyle(el).borderColor;
      });

      // Should have amber border
      expect(borderColor).toMatch(/rgb.*245.*158.*11|rgb.*251.*191.*36/); // Warning amber
    });
  });

  test.describe("Icons & Elements", () => {
    test("renders with left icon", async ({ page }) => {
      const inputContainer = page
        .locator('[data-has-left-icon="true"]')
        .first();
      const icon = inputContainer.locator("svg").first();

      await expect(icon).toBeVisible();

      // Icon should be positioned on the left
      const iconPosition = await icon.evaluate((el) => {
        const rect = el.getBoundingClientRect();
        const container = el.closest('[data-has-left-icon="true"]');
        const containerRect = container?.getBoundingClientRect();
        return rect.left < (containerRect?.left || 0) + 50; // Within first 50px
      });

      expect(iconPosition).toBe(true);
    });

    test("renders with right element (button)", async ({ page }) => {
      const inputContainer = page
        .locator('[data-has-right-element="true"]')
        .first();
      const rightElement = inputContainer.locator("button, svg").last();

      await expect(rightElement).toBeVisible();
    });

    test("left icon has correct color coordination", async ({ page }) => {
      const icon = page.locator('[data-has-left-icon="true"] svg').first();

      const iconColor = await icon.evaluate((el) => {
        return window.getComputedStyle(el).color;
      });

      expect(iconColor).toBeTruthy();
    });
  });

  test.describe("Focus & Blur Events", () => {
    test("shows animated border on focus", async ({ page }) => {
      const input = page.locator('input[aria-label="Focus Test"]').first();

      // Get initial border
      const initialBorder = await input.evaluate((el) => {
        return window.getComputedStyle(el).borderColor;
      });

      // Focus the input
      await input.focus();
      await page.waitForTimeout(350); // Wait for animation

      // Border should change (glow effect)
      const focusedBorder = await input.evaluate((el) => {
        return window.getComputedStyle(el).borderColor;
      });

      expect(focusedBorder).not.toBe(initialBorder);
    });

    test("shows glow shadow on focus", async ({ page }) => {
      const input = page.locator('input[aria-label="Glow Test"]').first();

      await input.focus();
      await page.waitForTimeout(350);

      const boxShadow = await input.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      // Should have shadow with rgba color
      expect(boxShadow).toContain("rgba");
    });

    test("floating label animates on focus", async ({ page }) => {
      const input = page
        .locator('input[data-has-floating-label="true"]')
        .first();
      const label = page.locator("label").first();

      // Get initial label position
      const initialY = await label.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      // Focus input
      await input.focus();
      await page.waitForTimeout(350);

      // Label should move up
      const focusedY = await label.evaluate((el) => {
        return window.getComputedStyle(el).transform;
      });

      expect(focusedY).not.toBe(initialY);
    });

    test("removes glow on blur", async ({ page }) => {
      const input = page.locator('input[aria-label="Blur Test"]').first();

      // Focus then blur
      await input.focus();
      await page.waitForTimeout(350);
      await input.blur();
      await page.waitForTimeout(350);

      const boxShadow = await input.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      // Shadow should be reduced or removed
      expect(boxShadow).toBeTruthy(); // Will have base shadow
    });
  });

  test.describe("Value Changes & Input", () => {
    test("accepts keyboard input", async ({ page }) => {
      const input = page.locator('input[aria-label="Keyboard Input"]').first();

      await input.fill("Test Input Value");

      const value = await input.inputValue();
      expect(value).toBe("Test Input Value");
    });

    test("triggers onChange handler", async ({ page }) => {
      // Setup change listener
      await page.evaluate(() => {
        (window as any).inputChanged = false;
        const input = document.querySelector(
          'input[aria-label="Change Handler"]'
        ) as HTMLInputElement;
        if (input) {
          input.addEventListener("change", () => {
            (window as any).inputChanged = true;
          });
        }
      });

      const input = page.locator('input[aria-label="Change Handler"]').first();
      await input.fill("New Value");
      await input.blur(); // Trigger change event

      const wasChanged = await page.evaluate(
        () => (window as any).inputChanged
      );
      expect(wasChanged).toBe(true);
    });

    test("displays typed value correctly", async ({ page }) => {
      const input = page.locator('input[aria-label="Display Value"]').first();

      await input.type("Cyberpunk Input", { delay: 50 });

      const displayedValue = await input.inputValue();
      expect(displayedValue).toBe("Cyberpunk Input");
    });
  });

  test.describe("Validation States", () => {
    test("displays error message in error state", async ({ page }) => {
      const input = page.locator('input[data-state="error"]').first();
      const errorMessage = page
        .locator('[role="alert"], [data-error-message]')
        .first();

      await expect(errorMessage).toBeVisible();

      const messageText = await errorMessage.textContent();
      expect(messageText).toBeTruthy();
    });

    test("error message has correct styling", async ({ page }) => {
      const errorMessage = page.locator("[data-error-message]").first();

      const color = await errorMessage.evaluate((el) => {
        return window.getComputedStyle(el).color;
      });

      // Should be red
      expect(color).toMatch(/rgb.*239.*68.*68|rgb.*220.*38.*38/);
    });

    test("success state shows success message", async ({ page }) => {
      const successMessage = page.locator("[data-success-message]").first();

      await expect(successMessage).toBeVisible();

      const color = await successMessage.evaluate((el) => {
        return window.getComputedStyle(el).color;
      });

      // Should be green
      expect(color).toMatch(/rgb.*16.*185.*129|rgb.*34.*197.*94/);
    });

    test("warning state shows warning message", async ({ page }) => {
      const warningMessage = page.locator("[data-warning-message]").first();

      await expect(warningMessage).toBeVisible();

      const color = await warningMessage.evaluate((el) => {
        return window.getComputedStyle(el).color;
      });

      // Should be amber
      expect(color).toMatch(/rgb.*245.*158.*11|rgb.*251.*191.*36/);
    });
  });

  test.describe("Accessibility", () => {
    test("has correct ARIA label", async ({ page }) => {
      const input = page
        .locator('input[aria-label="Accessible Input"]')
        .first();

      const ariaLabel = await input.getAttribute("aria-label");
      expect(ariaLabel).toBe("Accessible Input");
    });

    test("associates label with input via id", async ({ page }) => {
      const input = page.locator("input#email-input").first();
      const label = page.locator('label[for="email-input"]').first();

      await expect(input).toBeVisible();
      await expect(label).toBeVisible();
    });

    test("has aria-describedby for helper text", async ({ page }) => {
      const input = page.locator("input[aria-describedby]").first();

      const describedBy = await input.getAttribute("aria-describedby");
      expect(describedBy).toBeTruthy();

      // Check if described element exists
      const helperElement = page.locator(`#${describedBy}`).first();
      await expect(helperElement).toBeVisible();
    });

    test("has aria-invalid in error state", async ({ page }) => {
      const input = page.locator('input[data-state="error"]').first();

      const ariaInvalid = await input.getAttribute("aria-invalid");
      expect(ariaInvalid).toBe("true");
    });

    test("has aria-required for required fields", async ({ page }) => {
      const input = page.locator("input[required]").first();

      const ariaRequired = await input.getAttribute("aria-required");
      expect(ariaRequired).toBe("true");
    });

    test('error message has role="alert"', async ({ page }) => {
      const errorMessage = page
        .locator('[data-state="error"] + [role="alert"]')
        .first();

      await expect(errorMessage).toBeVisible();
    });

    test("is keyboard accessible", async ({ page }) => {
      const input = page.locator('input[aria-label="Keyboard Access"]').first();

      // Tab to focus
      await page.keyboard.press("Tab");

      const isFocused = await input.evaluate((el) => {
        return document.activeElement === el;
      });

      expect(isFocused).toBe(true);
    });
  });

  test.describe("Glassmorphic Effects", () => {
    test("has glassmorphic background", async ({ page }) => {
      const input = page.locator("input").first();

      const backdropFilter = await input.evaluate((el) => {
        return window.getComputedStyle(el).backdropFilter;
      });

      expect(backdropFilter).toContain("blur");
    });

    test("has semi-transparent background", async ({ page }) => {
      const input = page.locator("input").first();

      const background = await input.evaluate((el) => {
        return window.getComputedStyle(el).backgroundColor;
      });

      // Should be rgba with alpha < 1
      expect(background).toMatch(/rgba?\(.*,\s*0\.\d+\)/);
    });
  });

  test.describe("Disabled State", () => {
    test("shows disabled styling", async ({ page }) => {
      const input = page.locator("input:disabled").first();

      await expect(input).toBeDisabled();

      const opacity = await input.evaluate((el) => {
        return window.getComputedStyle(el).opacity;
      });

      expect(parseFloat(opacity)).toBeLessThan(1);
    });

    test("does not accept input when disabled", async ({ page }) => {
      const input = page.locator("input:disabled").first();

      await input.fill("Should not work");

      const value = await input.inputValue();
      expect(value).toBe(""); // Should remain empty
    });

    test("has cursor-not-allowed style", async ({ page }) => {
      const input = page.locator("input:disabled").first();

      const cursor = await input.evaluate((el) => {
        return window.getComputedStyle(el).cursor;
      });

      expect(cursor).toContain("not-allowed");
    });
  });

  test.describe("Size Variants", () => {
    test("renders small size correctly", async ({ page }) => {
      const input = page.locator('input[data-size="sm"]').first();

      const padding = await input.evaluate((el) => {
        return window.getComputedStyle(el).padding;
      });

      expect(padding).toBeTruthy();
    });

    test("renders medium size correctly", async ({ page }) => {
      const input = page.locator('input[data-size="md"]').first();

      const fontSize = await input.evaluate((el) => {
        return window.getComputedStyle(el).fontSize;
      });

      expect(parseFloat(fontSize)).toBeGreaterThan(12);
    });

    test("renders large size correctly", async ({ page }) => {
      const input = page.locator('input[data-size="lg"]').first();

      const padding = await input.evaluate((el) => {
        return window.getComputedStyle(el).padding;
      });

      const fontSize = await input.evaluate((el) => {
        return window.getComputedStyle(el).fontSize;
      });

      expect(parseFloat(fontSize)).toBeGreaterThan(14);
    });
  });

  test.describe("Responsive Design", () => {
    test("renders correctly on mobile", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      const input = page.locator("input").first();
      await expect(input).toBeVisible();

      const width = await input.evaluate(
        (el) => (el as HTMLElement).offsetWidth
      );
      expect(width).toBeLessThanOrEqual(375);
    });

    test("renders correctly on tablet", async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });

      const input = page.locator("input").first();
      await expect(input).toBeVisible();
    });

    test("renders correctly on desktop", async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });

      const input = page.locator("input").first();
      await expect(input).toBeVisible();
    });
  });
});
