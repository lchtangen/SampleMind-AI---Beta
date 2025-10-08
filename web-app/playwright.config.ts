import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration for E2E and Visual Regression Testing
 *
 * Supports:
 * - End-to-end testing of user flows
 * - Visual regression testing of components
 * - Cross-browser and responsive testing
 * - Accessibility testing integration
 */
export default defineConfig({
  // Test directories - both E2E and visual tests
  testDir: './tests',

  // Test match patterns
  testMatch: ['**/*.spec.ts', '**/*.e2e.spec.ts', '**/*.visual.spec.ts'],

  // Test timeout
  timeout: 30000,

  // Expect timeout for assertions
  expect: {
    timeout: 5000,
    toHaveScreenshot: {
      // Maximum pixel diff percentage
      maxDiffPixels: 100,
      // Threshold for pixel comparison (0-1)
      threshold: 0.2,
    },
  },

  // Run tests in files in parallel
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Parallel workers
  workers: process.env.CI ? 1 : undefined,

  // Reporter configuration
  reporter: process.env.CI
    ? [
        ['html', { outputFolder: 'playwright-report' }],
        ['json', { outputFile: 'playwright-report/results.json' }],
        ['junit', { outputFile: 'playwright-report/junit.xml' }],
        ['list'],
      ]
    : [
        ['html', { outputFolder: 'playwright-report' }],
        ['json', { outputFile: 'playwright-report/results.json' }],
        ['list'],
      ],

  // Shared settings for all projects
  use: {
    // Base URL for E2E tests
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',

    // Collect trace on failure
    trace: 'on-first-retry',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Video on failure
    video: 'retain-on-failure',

    // Viewport size for desktop tests
    viewport: { width: 1280, height: 720 },

    // Permissions
    permissions: [],

    // Locale
    locale: 'en-US',

    // Timezone
    timezoneId: 'America/New_York',

    // Color scheme
    colorScheme: 'dark', // Match cyberpunk theme

    // Action timeout
    actionTimeout: 10000,

    // Navigation timeout
    navigationTimeout: 30000,
  },

  // Web server configuration for E2E tests
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
    stdout: 'ignore',
    stderr: 'pipe',
  },

  // Configure projects for major browsers and test types
  projects: [
    // ========================================
    // E2E Tests - Desktop Browsers
    // ========================================
    {
      name: 'e2e-chromium',
      testMatch: '**/*.e2e.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
      },
    },

    {
      name: 'e2e-firefox',
      testMatch: '**/*.e2e.spec.ts',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'e2e-webkit',
      testMatch: '**/*.e2e.spec.ts',
      use: { ...devices['Desktop Safari'] },
    },

    // ========================================
    // E2E Tests - Mobile Devices
    // ========================================
    {
      name: 'e2e-mobile-chrome',
      testMatch: '**/*.e2e.spec.ts',
      use: { ...devices['Pixel 5'] },
    },

    {
      name: 'e2e-mobile-safari',
      testMatch: '**/*.e2e.spec.ts',
      use: { ...devices['iPhone 12'] },
    },

    // ========================================
    // Visual Regression Tests
    // ========================================
    {
      name: 'visual-chromium',
      testMatch: '**/*.visual.spec.ts',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'visual-firefox',
      testMatch: '**/*.visual.spec.ts',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'visual-webkit',
      testMatch: '**/*.visual.spec.ts',
      use: { ...devices['Desktop Safari'] },
    },

    // Mobile visual tests
    {
      name: 'visual-mobile-chrome',
      testMatch: '**/*.visual.spec.ts',
      use: { ...devices['Pixel 5'] },
    },

    {
      name: 'visual-mobile-safari',
      testMatch: '**/*.visual.spec.ts',
      use: { ...devices['iPhone 12'] },
    },

    // Tablet visual tests
    {
      name: 'visual-ipad',
      testMatch: '**/*.visual.spec.ts',
      use: { ...devices['iPad Pro'] },
    },

    // ========================================
    // Accessibility Tests
    // ========================================
    {
      name: 'a11y-chromium',
      testMatch: '**/*.a11y.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
      },
    },
  ],

  // Output folder for test artifacts
  outputDir: 'test-results/',

  // Global setup and teardown
  // globalSetup: require.resolve('./tests/global-setup.ts'),
  // globalTeardown: require.resolve('./tests/global-teardown.ts'),
});
