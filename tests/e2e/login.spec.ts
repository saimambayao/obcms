// spec: docs/testing/obcms_test_plan.md

import { test, expect } from '@playwright/test';

test.describe('Concrete test scenarios', () => {
  test('User login happy path', async ({ page, baseURL }) => {
    // 1. Open login page (`/accounts/login/`).
    await page.goto(`${baseURL ?? ''}/accounts/login/`);

    // 2. Enter valid username & password.
    // Note: selectors below assume a typical Django auth form. Adjust selectors to match your app.
    // input[name="username"] and input[name="password"] are common defaults.
    await page.fill('input[name="username"]', process.env.E2E_LOGIN_USERNAME || 'admin@test.com');
    await page.fill('input[name="password"]', process.env.E2E_LOGIN_PASSWORD || 'password');

    // 3. Submit form.
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle' }),
      page.click('button[type="submit"]'),
    ]);

    // Expected: Redirect to dashboard (HTTP 302 -> `/` or configured landing).
    // Verify we landed somewhere other than login page and that a logout link or user menu is visible.
    expect(page.url()).not.toContain('/accounts/login');

    // Session cookie set - look for a session cookie (Django default name is 'sessionid')
    const cookies = await page.context().cookies();
    expect(cookies.some(c => c.name.includes('session'))).toBeTruthy();

    // Also assert some visible, user-specific UI (adjust selector as needed)
    // Prefer robust checks like presence of user's email or a logout button.
    await expect(page.locator('text=Logout').first()).toBeVisible({ timeout: 5_000 }).catch(async () => {
      // Fallback: look for a username label
      await expect(page.locator(`text=${process.env.E2E_LOGIN_USERNAME || 'admin@test.com'}`).first()).toBeVisible();
    });
  });
});
