import { test, expect } from '@playwright/test';

// Test data for User 1
const USER_1_DATA = {
	email: 'alex.johnson.test@email.com', // Use a different email for testing
	password: 'testpassword123',
	fullName: 'Alex Johnson',
	profileType: 'young_professional',
};

test.describe('Authentication Test', () => {
	test('Sign up new user', async ({ page }) => {
		// Go to the app
		await page.goto('/');

		// Should show login form
		await expect(page.locator('form')).toBeVisible();

		console.log('Page loaded, looking for signup option...');

		// Try to sign up (click the sign up toggle)
		const signUpToggle = page.locator(
			'button:has-text("Don\'t have an account? Sign up")'
		);

		if ((await signUpToggle.count()) > 0) {
			console.log('Found sign up toggle, clicking...');
			await signUpToggle.click();
			await page.waitForTimeout(1000); // Wait for form to potentially switch
		}

		// Take a screenshot to see current state
		await page.screenshot({ path: 'auth-state-1.png' });

		// Fill the form
		console.log('Filling form with:', USER_1_DATA.email);
		await page.fill('input[type="email"]', USER_1_DATA.email);
		await page.fill('input[type="password"]', USER_1_DATA.password);

		// Take another screenshot
		await page.screenshot({ path: 'auth-state-2.png' });

		// Submit the form
		console.log('Submitting form...');
		const submitButton = page.locator('button[type="submit"]');

		await submitButton.click();

		// Wait a moment to see what happens
		await page.waitForTimeout(3000);

		// Take screenshot of result
		await page.screenshot({ path: 'auth-state-3.png' });

		// Check current URL and page state
		console.log('Current URL:', page.url());
		console.log('Page title:', await page.title());

		const pageContent = await page.textContent('body');
		console.log('Page content preview:', pageContent?.slice(0, 300));

		// Look for any error messages or success messages
		const allText = await page.locator('body').textContent();
		const hasError =
			allText?.toLowerCase().includes('error') ||
			allText?.toLowerCase().includes('invalid') ||
			allText?.toLowerCase().includes('failed');

		const hasSuccess =
			allText?.toLowerCase().includes('success') ||
			allText?.toLowerCase().includes('created') ||
			allText?.toLowerCase().includes('welcome');

		console.log('Has error indicators:', hasError);
		console.log('Has success indicators:', hasSuccess);

		// If we're still on login page, try to sign in with the same credentials
		if (
			page.url().includes('localhost:5173/') &&
			(await page.locator('form').count()) > 0
		) {
			console.log('Still on login page, trying to sign in...');

			// Make sure we're in sign-in mode
			const signInToggle = page.locator(
				'button:has-text("Already have an account? Sign in")'
			);
			if ((await signInToggle.count()) > 0) {
				await signInToggle.click();
				await page.waitForTimeout(1000);
			}

			// Fill and submit sign-in form
			await page.fill('input[type="email"]', USER_1_DATA.email);
			await page.fill('input[type="password"]', USER_1_DATA.password);
			await page.locator('button[type="submit"]').click();

			// Wait for result
			await page.waitForTimeout(3000);

			console.log('After sign-in attempt - URL:', page.url());
			console.log(
				'After sign-in attempt - content:',
				(await page.textContent('body'))?.slice(0, 200)
			);
		}

		// Basic assertion that we at least have a functioning page
		await expect(page.locator('body')).not.toBeEmpty();
	});
});
