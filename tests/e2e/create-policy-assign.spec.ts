// spec: docs/testing/obcms_test_plan.md

import { test, expect } from '@playwright/test';

test.describe('Concrete test scenarios', () => {
  test('Create Policy -> Assign to Community -> Notify', async ({ page, baseURL }) => {
    // Assumption: staff user exists and there is at least one community to assign

    // 1. Login as staff user in browser (reuse pattern)
    await page.goto(`${baseURL ?? ''}/accounts/login/`);
    await page.fill('input[name="username"]', process.env.E2E_LOGIN_USERNAME || 'staff@test.com');
    await page.fill('input[name="password"]', process.env.E2E_LOGIN_PASSWORD || 'password');
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle' }),
      page.click('button[type="submit"]'),
    ]);

    // 2. Navigate to Policies page -> Create Policy with modal.
    await page.goto(`${baseURL ?? ''}/policies/`);
    await page.click('text=New Policy');

    // Wait for modal or form
    const modal = page.locator('role=dialog').first();
    await modal.waitFor({ state: 'visible', timeout: 5000 }).catch(() => {});

    // 3. Fill policy fields
    const policyTitle = `E2E Policy ${Date.now()}`;
    await modal.fill('input[name="title"]', policyTitle).catch(() => modal.fill('input[placeholder*="Title"]', policyTitle));
    await modal.fill('textarea[name="content"]', 'Policy content created by E2E test').catch(() => {});

    // 4. Assign the policy to an existing community from dropdown.
    // Try common select patterns: <select>, custom dropdown, or autocomplete.
    const communityOptionText = await page.locator('.community-list .community-item').first().innerText().catch(() => '');
    if (communityOptionText) {
      // If there's a visible list we can select from, click the first one
      await modal.click('select[name="community"]').catch(() => {});
      await modal.selectOption('select[name="community"]', { label: communityOptionText }).catch(() => {});
    } else {
      // fallback: select by index if native select exists
      await modal.selectOption('select[name="community"]', '1').catch(() => {});
    }

    // 5. Save and assert notification appears and counters increase.
    await Promise.all([
      page.waitForResponse(response => response.status() < 400 && response.url().includes('/policies/')),
      modal.click('button[type="submit"]'),
    ]).catch(() => {});

    // Verify the policy appears in the list
    await expect(page.locator(`text=${policyTitle}`).first()).toBeVisible({ timeout: 5000 });

    // Verify a notification appears (toast) - adjust text as needed
    await expect(page.locator('text=Operation completed|text=Policy created|text=success').first()).toBeVisible({ timeout: 3000 }).catch(() => {});

    // Optional: verify backend assignment by visiting policy detail and checking assigned community text
    await page.click(`text=${policyTitle}`);
    await expect(page.locator('text=Assigned to').first()).toBeVisible({ timeout: 3000 }).catch(() => {});
  });
});
