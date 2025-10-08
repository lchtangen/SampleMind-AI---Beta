/**
 * GlassmorphicCard Visual Regression Tests
 *
 * Tests visual appearance across browsers, viewports, and states
 * using Playwright's screenshot comparison capabilities.
 *
 * @module GlassmorphicCard.visual.spec
 */

import { test, expect } from '@playwright/test';

/**
 * Test page setup
 * Creates a minimal HTML page with the component for visual testing
 */
const setupTestPage = async (page: any, cardHTML: string) => {
  await page.setContent(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Glassmorphic Card Test</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <style>
        body {
          margin: 0;
          padding: 40px;
          background: linear-gradient(135deg, #0A0A0F 0%, #131318 100%);
          min-height: 100vh;
        }
        .test-container {
          max-width: 600px;
          margin: 0 auto;
        }
      </style>
    </head>
    <body>
      <div class="test-container">
        ${cardHTML}
      </div>
    </body>
    </html>
  `);
};

test.describe('GlassmorphicCard - Visual Regression', () => {
  test.describe('Default State', () => {
    test('renders with glassmorphism effects', async ({ page }) => {
      await setupTestPage(page, `
        <article
          class="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-6 md:p-8 transition-all duration-slow ease-out relative overflow-hidden shadow-[0_0_20px_rgba(139,92,246,0.5),0_0_40px_rgba(139,92,246,0.3),0_0_60px_rgba(6,182,212,0.2),0_8px_32px_rgba(0,0,0,0.37)]"
          aria-label="Audio Waveform"
        >
          <div class="relative z-10 flex flex-col gap-4">
            <div class="flex items-start gap-4">
              <div class="flex-1 min-w-0">
                <h3 class="font-heading text-xl md:text-2xl font-semibold text-white mb-2 leading-tight">
                  Audio Waveform
                </h3>
                <p class="font-body text-base md:text-lg text-gray-400 leading-relaxed">
                  View detailed spectral analysis of your audio files
                </p>
              </div>
            </div>
          </div>
        </article>
      `);

      // Wait for styles to load
      await page.waitForTimeout(500);

      // Take screenshot
      await expect(page).toHaveScreenshot('glassmorphic-card-default.png');
    });

    test('renders with icon', async ({ page }) => {
      await setupTestPage(page, `
        <article
          class="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-6 md:p-8 transition-all duration-slow ease-out relative overflow-hidden shadow-[0_0_20px_rgba(139,92,246,0.5),0_0_40px_rgba(139,92,246,0.3),0_0_60px_rgba(6,182,212,0.2),0_8px_32px_rgba(0,0,0,0.37)]"
          aria-label="Audio Waveform"
        >
          <div class="relative z-10 flex flex-col gap-4">
            <div class="flex items-start gap-4">
              <div class="flex-shrink-0 text-purple-500" aria-hidden="true">
                <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z"/>
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="font-heading text-xl md:text-2xl font-semibold text-white mb-2 leading-tight">
                  Audio Waveform
                </h3>
                <p class="font-body text-base md:text-lg text-gray-400 leading-relaxed">
                  View detailed spectral analysis
                </p>
              </div>
            </div>
          </div>
        </article>
      `);

      await page.waitForTimeout(500);
      await expect(page).toHaveScreenshot('glassmorphic-card-with-icon.png');
    });
  });

  test.describe('Interactive State', () => {
    test('renders interactive card with hover indicator', async ({ page }) => {
      await setupTestPage(page, `
        <div
          class="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-6 md:p-8 transition-all duration-slow ease-out relative overflow-hidden shadow-[0_0_20px_rgba(139,92,246,0.5),0_0_40px_rgba(139,92,246,0.3),0_0_60px_rgba(6,182,212,0.2),0_8px_32px_rgba(0,0,0,0.37)] hover:shadow-[0_0_30px_rgba(139,92,246,0.75),0_0_60px_rgba(139,92,246,0.45),0_0_90px_rgba(6,182,212,0.3),0_8px_32px_rgba(0,0,0,0.37)] hover:scale-105 hover:border-purple-500/30 cursor-pointer active:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-gray-900"
          role="button"
          tabindex="0"
          aria-label="Open Audio Waveform"
        >
          <div class="relative z-10 flex flex-col gap-4">
            <div class="flex items-start gap-4">
              <div class="flex-1 min-w-0">
                <h3 class="font-heading text-xl md:text-2xl font-semibold text-white mb-2 leading-tight">
                  Audio Waveform
                </h3>
                <p class="font-body text-base md:text-lg text-gray-400 leading-relaxed">
                  Click to view analysis
                </p>
              </div>
            </div>
            <div class="absolute bottom-4 right-4 text-purple-500 opacity-50 transition-opacity duration-normal" aria-hidden="true">
              <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
              </svg>
            </div>
          </div>
        </div>
      `);

      await page.waitForTimeout(500);
      await expect(page).toHaveScreenshot('glassmorphic-card-interactive.png');
    });

    test('captures hover state with intensified glow', async ({ page }) => {
      await setupTestPage(page, `
        <div
          id="test-card"
          class="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-6 md:p-8 transition-all duration-slow ease-out relative overflow-hidden shadow-[0_0_20px_rgba(139,92,246,0.5),0_0_40px_rgba(139,92,246,0.3),0_0_60px_rgba(6,182,212,0.2),0_8px_32px_rgba(0,0,0,0.37)] hover:shadow-[0_0_30px_rgba(139,92,246,0.75),0_0_60px_rgba(139,92,246,0.45),0_0_90px_rgba(6,182,212,0.3),0_8px_32px_rgba(0,0,0,0.37)] hover:scale-105 cursor-pointer"
          role="button"
          tabindex="0"
        >
          <div class="relative z-10 flex flex-col gap-4">
            <div class="flex items-start gap-4">
              <div class="flex-1 min-w-0">
                <h3 class="font-heading text-xl md:text-2xl font-semibold text-white mb-2 leading-tight">
                  Audio Waveform
                </h3>
                <p class="font-body text-base md:text-lg text-gray-400 leading-relaxed">
                  Hover to see glow effect
                </p>
              </div>
            </div>
          </div>
        </div>
      `);

      // Hover over the card
      const card = page.locator('#test-card');
      await card.hover();

      // Wait for transition
      await page.waitForTimeout(600);

      await expect(page).toHaveScreenshot('glassmorphic-card-hover.png');
    });

    test('captures focus state', async ({ page }) => {
      await setupTestPage(page, `
        <div
          id="test-card"
          class="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-6 md:p-8 transition-all duration-slow ease-out relative overflow-hidden shadow-[0_0_20px_rgba(139,92,246,0.5),0_0_40px_rgba(139,92,246,0.3),0_0_60px_rgba(6,182,212,0.2),0_8px_32px_rgba(0,0,0,0.37)] focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-gray-900 cursor-pointer"
          role="button"
          tabindex="0"
        >
          <div class="relative z-10 flex flex-col gap-4">
            <div class="flex items-start gap-4">
              <div class="flex-1 min-w-0">
                <h3 class="font-heading text-xl md:text-2xl font-semibold text-white mb-2 leading-tight">
                  Audio Waveform
                </h3>
                <p class="font-body text-base md:text-lg text-gray-400 leading-relaxed">
                  Focus state with ring
                </p>
              </div>
            </div>
          </div>
        </div>
      `);

      // Focus the card
      const card = page.locator('#test-card');
      await card.focus();

      // Wait for transition
      await page.waitForTimeout(300);

      await expect(page).toHaveScreenshot('glassmorphic-card-focus.png');
    });
  });

  test.describe('Responsive Behavior', () => {
    test('mobile viewport (375px)', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      await setupTestPage(page, `
        <article
          class="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-6 md:p-8 transition-all duration-slow ease-out relative overflow-hidden shadow-[0_0_20px_rgba(139,92,246,0.5),0_0_40px_rgba(139,92,246,0.3),0_0_60px_rgba(6,182,212,0.2),0_8px_32px_rgba(0,0,0,0.37)]"
        >
          <div class="relative z-10 flex flex-col gap-4">
            <div class="flex items-start gap-4">
              <div class="flex-1 min-w-0">
                <h3 class="font-heading text-xl md:text-2xl font-semibold text-white mb-2 leading-tight">
                  Audio Analysis
                </h3>
                <p class="font-body text-base md:text-lg text-gray-400 leading-relaxed">
                  Mobile responsive view
                </p>
              </div>
            </div>
          </div>
        </article>
      `);

      await page.waitForTimeout(500);
      await expect(page).toHaveScreenshot('glassmorphic-card-mobile.png');
    });

    test('tablet viewport (768px)', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });

      await setupTestPage(page, `
        <article
          class="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-6 md:p-8 transition-all duration-slow ease-out relative overflow-hidden shadow-[0_0_20px_rgba(139,92,246,0.5),0_0_40px_rgba(139,92,246,0.3),0_0_60px_rgba(6,182,212,0.2),0_8px_32px_rgba(0,0,0,0.37)]"
        >
          <div class="relative z-10 flex flex-col gap-4">
            <div class="flex items-start gap-4">
              <div class="flex-1 min-w-0">
                <h3 class="font-heading text-xl md:text-2xl font-semibold text-white mb-2 leading-tight">
                  Audio Analysis
                </h3>
                <p class="font-body text-base md:text-lg text-gray-400 leading-relaxed">
                  Tablet responsive view with increased padding
                </p>
              </div>
            </div>
          </div>
        </article>
      `);

      await page.waitForTimeout(500);
      await expect(page).toHaveScreenshot('glassmorphic-card-tablet.png');
    });

    test('desktop viewport (1920px)', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });

      await setupTestPage(page, `
        <article
          class="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-6 md:p-8 transition-all duration-slow ease-out relative overflow-hidden shadow-[0_0_20px_rgba(139,92,246,0.5),0_0_40px_rgba(139,92,246,0.3),0_0_60px_rgba(6,182,212,0.2),0_8px_32px_rgba(0,0,0,0.37)]"
        >
          <div class="relative z-10 flex flex-col gap-4">
            <div class="flex items-start gap-4">
              <div class="flex-1 min-w-0">
                <h3 class="font-heading text-xl md:text-2xl font-semibold text-white mb-2 leading-tight">
                  Audio Analysis
                </h3>
                <p class="font-body text-base md:text-lg text-gray-400 leading-relaxed">
                  Desktop responsive view with full styling
                </p>
              </div>
            </div>
          </div>
        </article>
      `);

      await page.waitForTimeout(500);
      await expect(page).toHaveScreenshot('glassmorphic-card-desktop.png');
    });
  });

  test.describe('Dark Mode', () => {
    test('light background variation', async ({ page }) => {
      await page.setContent(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Glassmorphic Card Test - Light</title>
          <script src="https://cdn.tailwindcss.com"></script>
          <style>
            body {
              margin: 0;
              padding: 40px;
              background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
              min-height: 100vh;
            }
            .test-container {
              max-width: 600px;
              margin: 0 auto;
            }
          </style>
        </head>
        <body>
          <div class="test-container">
            <article
              class="backdrop-blur-xl bg-black/5 border border-black/10 rounded-xl p-6 md:p-8 transition-all duration-slow ease-out relative overflow-hidden shadow-[0_0_20px_rgba(139,92,246,0.5),0_0_40px_rgba(139,92,246,0.3),0_0_60px_rgba(6,182,212,0.2),0_8px_32px_rgba(0,0,0,0.37)]"
            >
              <div class="relative z-10 flex flex-col gap-4">
                <div class="flex items-start gap-4">
                  <div class="flex-1 min-w-0">
                    <h3 class="font-heading text-xl md:text-2xl font-semibold text-gray-900 mb-2 leading-tight">
                      Audio Analysis
                    </h3>
                    <p class="font-body text-base md:text-lg text-gray-600 leading-relaxed">
                      Light mode adaptation
                    </p>
                  </div>
                </div>
              </div>
            </article>
          </div>
        </body>
        </html>
      `);

      await page.waitForTimeout(500);
      await expect(page).toHaveScreenshot('glassmorphic-card-light-mode.png');
    });
  });
});
