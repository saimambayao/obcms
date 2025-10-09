import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: 'tests/e2e',
  timeout: 60_000,
  expect: { timeout: 5_000 },
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.PW_BASE_URL || 'http://localhost:8000',
    headless: true,
    viewport: { width: 1280, height: 800 },
    actionTimeout: 15_000,
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    // add firefox or webkit if you want cross-browser coverage in CI
    // { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
});
