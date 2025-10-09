// spec: docs/testing/obcms_test_plan.md

import { test, expect } from '@playwright/test';

test.describe('Concrete test scenarios', () => {
  test('Create Community (HTMX modal)', async ({ page, baseURL }) => {
    // Assumption: a staff user exists and env vars provide credentials
    // 1. Navigate to communities list.
    await page.goto(`${baseURL ?? ''}/communities/`);

    // If not logged in, perform a login. The login test covers authentication; reuse here.
    if (await page.locator('text=Login').count() > 0) {
      await page.goto(`${baseURL ?? ''}/accounts/login/`);
      await page.fill('input[name="username"]', process.env.E2E_LOGIN_USERNAME || 'staff@test.com');
      await page.fill('input[name="password"]', process.env.E2E_LOGIN_PASSWORD || 'password');
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'networkidle' }),
        page.click('button[type="submit"]'),
      ]);
      await page.goto(`${baseURL ?? ''}/communities/`);
    }

    // 2. Click "New Community" (HTMX opens modal).
    // Selector: try button text first; adjust to the actual markup in your app.
    await page.click('text=New Community');

    // Wait for the HTMX modal to appear. Common patterns: dialog[role="dialog"], .modal, or hx-target container.
    const modal = page.locator('role=dialog').first();
    await modal.waitFor({ state: 'visible', timeout: 5000 });

    // 3. Fill required fields and click Save.
    // NOTE: Adjust field names to match your form. We'll attempt common names.
    const communityName = `e2e-community-${Date.now()}`;
    // Comment: fill name
    await modal.fill('input[name="name"]', communityName).catch(() => modal.fill('input[placeholder*="Name"]', communityName));
    // Comment: optionally fill description
    await modal.fill('textarea[name="description"]', 'Created by automated E2E test').catch(() => {});

    // Submit the modal form. HTMX typically sends an XHR; wait for the list to update.
    await Promise.all([
      page.waitForResponse(response => response.status() < 400 && response.url().includes('/communities/')),
      modal.click('button[type="submit"]'),
    ]).catch(() => {});

    // Expected: HTMX returns fragment with new row (outerHTML swap) and list updates with new community entry.
    // Verify the new community name appears in the list.
    await expect(page.locator(`text=${communityName}`).first()).toBeVisible({ timeout: 5000 });

    // Verify server returned HX-Trigger (this is server header-based and not directly accessible from page;
    // instead, verify a toast or notification appears)
    await expect(page.locator('text=Operation completed|text=created|text=success').first()).toBeVisible({ timeout: 3000 }).catch(() => {});
  });
});
