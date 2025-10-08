/**
 * Component-specific test helpers
 * Reusable functions for testing cyberpunk components
 */

import { Page } from "@playwright/test";

/**
 * NeonButton Test Helpers
 */
export class NeonButtonHelpers {
  constructor(private page: Page) {}

  async findButton(text: string) {
    return this.page.locator("button", { hasText: text }).first();
  }

  async clickButton(text: string) {
    const button = await this.findButton(text);
    await button.click();
  }

  async hasVariant(
    selector: string,
    variant: "primary" | "secondary" | "ghost" | "danger"
  ): Promise<boolean> {
    const classList = await this.page.evaluate((sel: string) => {
      const element = document.querySelector(sel);
      return element ? Array.from(element.classList) : [];
    }, selector);

    return classList.some((cls) => cls.includes(variant));
  }

  async isPulseAnimating(selector: string): Promise<boolean> {
    const boxShadow = await this.page.evaluate((sel: string) => {
      const element = document.querySelector(sel);
      return element ? window.getComputedStyle(element).boxShadow : "";
    }, selector);

    return boxShadow.includes("rgba(139, 92, 246"); // Purple glow
  }

  async isLoading(selector: string): Promise<boolean> {
    const isDisabled = await this.page.evaluate((sel: string) => {
      const element = document.querySelector(sel) as HTMLButtonElement;
      return element ? element.disabled : false;
    }, selector);

    // Check for spinner presence
    const hasSpinner = (await this.page.locator(`${selector} svg`).count()) > 0;

    return isDisabled && hasSpinner;
  }
}

/**
 * CyberpunkInput Test Helpers
 */
export class CyberpunkInputHelpers {
  constructor(private page: Page) {}

  async findInput(label: string) {
    return this.page
      .locator(`input[aria-label="${label}"], input[placeholder="${label}"]`)
      .first();
  }

  async typeInInput(label: string, text: string) {
    const input = await this.findInput(label);
    await input.fill(text);
  }

  async isFocused(selector: string): Promise<boolean> {
    return await this.page.evaluate((sel: string) => {
      const element = document.querySelector(sel);
      return element === document.activeElement;
    }, selector);
  }

  async hasValidationState(
    selector: string,
    state: "default" | "success" | "error" | "warning"
  ): Promise<boolean> {
    const borderColor = await this.page.evaluate((sel: string) => {
      const element = document.querySelector(sel);
      return element ? window.getComputedStyle(element).borderColor : "";
    }, selector);

    const stateColors = {
      default: "rgba(139, 92, 246", // Purple
      success: "rgba(34, 197, 94", // Green
      error: "rgba(239, 68, 68", // Red
      warning: "rgba(251, 191, 36", // Amber
    };

    return borderColor.includes(stateColors[state]);
  }

  async getHelperText(selector: string): Promise<string> {
    return await this.page.evaluate((sel: string) => {
      const inputContainer = document.querySelector(sel)?.closest("div");
      const helperText = inputContainer?.querySelector('[class*="helper"]');
      return helperText ? helperText.textContent || "" : "";
    }, selector);
  }
}

/**
 * GlassmorphicCard Test Helpers
 */
export class GlassmorphicCardHelpers {
  constructor(private page: Page) {}

  async findCard(title: string) {
    return this.page
      .locator('[role="article"], [role="button"]', {
        has: this.page.locator(`h3:has-text("${title}")`),
      })
      .first();
  }

  async clickCard(title: string) {
    const card = await this.findCard(title);
    await card.click();
  }

  async hasGlassmorphism(selector: string): Promise<boolean> {
    const backdropFilter = await this.page.evaluate((sel: string) => {
      const element = document.querySelector(sel);
      return element ? window.getComputedStyle(element).backdropFilter : "";
    }, selector);

    return backdropFilter.includes("blur");
  }

  async hasNeonBorder(selector: string): Promise<boolean> {
    const borderColor = await this.page.evaluate((sel: string) => {
      const element = document.querySelector(sel);
      return element ? window.getComputedStyle(element).borderColor : "";
    }, selector);

    return borderColor.includes("rgba");
  }

  async getCardContent(selector: string) {
    return await this.page.evaluate((sel: string) => {
      const card = document.querySelector(sel);
      const title = card?.querySelector("h3")?.textContent || "";
      const description = card?.querySelector("p")?.textContent || "";
      const hasIcon = card?.querySelector("svg") !== null;

      return { title, description, hasIcon };
    }, selector);
  }
}

/**
 * AnimatedCard Test Helpers
 */
export class AnimatedCardHelpers {
  constructor(private page: Page) {}

  async findCard(title: string) {
    return this.page
      .locator('[role="article"], [role="button"]', {
        has: this.page.locator(`h3:has-text("${title}")`),
      })
      .first();
  }

  async getAnimationPreset(selector: string): Promise<string> {
    return await this.page.evaluate((sel: string) => {
      const card = document.querySelector(sel);
      return card?.getAttribute("data-animation-preset") || "fadeIn";
    }, selector);
  }

  async hasAnimationCompleted(selector: string): Promise<boolean> {
    const opacity = await this.page.evaluate((sel: string) => {
      const element = document.querySelector(sel);
      return element ? parseFloat(window.getComputedStyle(element).opacity) : 0;
    }, selector);

    return opacity === 1;
  }
}

/**
 * Modal Test Helpers
 */
export class CyberpunkModalHelpers {
  constructor(private page: Page) {}

  async isModalOpen(): Promise<boolean> {
    const modal = this.page.locator('[role="dialog"]');
    return await modal.isVisible();
  }

  async openModal(triggerSelector: string) {
    await this.page.click(triggerSelector);
    await this.page.waitForSelector('[role="dialog"]', { state: "visible" });
  }

  async closeModal() {
    // Try Escape key first
    await this.page.keyboard.press("Escape");
    await this.page.waitForTimeout(300);

    // If still visible, click backdrop
    if (await this.isModalOpen()) {
      await this.page.click('[role="dialog"]', { position: { x: 0, y: 0 } });
    }
  }

  async getModalTitle(): Promise<string> {
    return (
      (await this.page
        .locator('[role="dialog"] h2, [role="dialog"] h3')
        .textContent()) || ""
    );
  }

  async hasBackdropBlur(): Promise<boolean> {
    const backdrop = this.page.locator('[role="dialog"]').locator("..").first();
    const backdropFilter = await backdrop.evaluate((el: any) => {
      return window.getComputedStyle(el).backdropFilter;
    });

    return backdropFilter.includes("blur");
  }
}

/**
 * Waveform Test Helpers
 */
export class WaveformVisualizerHelpers {
  constructor(private page: Page) {}

  async getWaveformBars(selector: string): Promise<number> {
    return await this.page.locator(`${selector} > div`).count();
  }

  async areWaveformBarsAnimated(selector: string): Promise<boolean> {
    const hasGradient = await this.page.evaluate((sel: string) => {
      const firstBar = document.querySelector(`${sel} > div:first-child`);
      if (!firstBar) return false;

      const background = window.getComputedStyle(firstBar).background;
      return background.includes("gradient");
    }, selector);

    return hasGradient;
  }

  async getWaveformHeight(selector: string): Promise<number> {
    return await this.page.evaluate((sel: string) => {
      const container = document.querySelector(sel);
      return container ? container.clientHeight : 0;
    }, selector);
  }
}

/**
 * Export all helpers
 */
export const componentHelpers = {
  NeonButton: NeonButtonHelpers,
  CyberpunkInput: CyberpunkInputHelpers,
  GlassmorphicCard: GlassmorphicCardHelpers,
  AnimatedCard: AnimatedCardHelpers,
  CyberpunkModal: CyberpunkModalHelpers,
  WaveformVisualizer: WaveformVisualizerHelpers,
};
