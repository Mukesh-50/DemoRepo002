import { test, expect } from '@playwright/test';

test('TC_LOGOUT_004 Verify a logged-in user can sign out', async ({ page }) => {
  // Step 1: Navigate to login page
  await page.goto('https://freelance-learn-automation.vercel.app/login');
  await expect(page).toHaveURL(/login/);
  await expect(page.getByRole('heading', { name: 'Learn Automation Courses' })).toBeVisible();
  await expect(page.getByRole('img', { name: 'Login' })).toBeVisible();

  // Step 2: Enter valid email address
  await expect(page.getByPlaceholder('Enter email')).toBeVisible();
  await page.getByPlaceholder('Enter email').fill('admin@email.com');

  // Step 3: Enter valid password
  await expect(page.getByPlaceholder('Enter password')).toBeVisible();
  await page.getByPlaceholder('Enter password').fill('admin@123');

  // Step 4: Click the Sign in button
  await expect(page.getByRole('button', { name: 'Sign in' })).toBeVisible();
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('button', { name: 'Sign out' })).toBeVisible();

  // Step 5: If menu icon is present, click it, otherwise proceed
  const menuButton = page.getByRole('img', { name: 'menu' });
  if (await menuButton.isVisible().catch(() => false)) {
    await menuButton.click();
  }

  // Step 6: Click the "Sign out" button
  await expect(page.getByRole('button', { name: 'Sign out' })).toBeVisible();
  await page.getByRole('button', { name: 'Sign out' }).click();

  // Step 7: Verify user is on login page
  await expect(page).toHaveURL(/login/);
  await expect(page.getByRole('button', { name: 'Sign in' })).toBeVisible();
});
