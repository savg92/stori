import { test, expect } from '@playwright/test';

test.describe('Basic App Loading', () => {
	test('should load the homepage', async ({ page }) => {
		await page.goto('/');

		// Check that the page loads (using the current title)
		await expect(page).toHaveTitle(/Vite \+ React \+ TS/);

		// Check for basic page elements
		await expect(page.locator('body')).toBeVisible();
	});

	test('should have proper viewport and responsive design', async ({
		page,
	}) => {
		await page.goto('/');

		// Check mobile viewport
		await page.setViewportSize({ width: 375, height: 667 });
		await expect(page.locator('body')).toBeVisible();

		// Check desktop viewport
		await page.setViewportSize({ width: 1920, height: 1080 });
		await expect(page.locator('body')).toBeVisible();
	});
});
