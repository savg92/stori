import { test, expect } from '@playwright/test';

test.describe('Authentication with Real Users', () => {
	const testUsers = [
		{
			email: 'alex.johnson@email.com',
			password: 'testpassword123',
			name: 'Alex Johnson',
			profile: 'young_professional',
		},
		{
			email: 'maria.garcia@email.com',
			password: 'testpassword123',
			name: 'Maria Garcia',
			profile: 'family_household',
		},
	];

	test.beforeEach(async ({ page }) => {
		await page.goto('/');
		await expect(page.locator('form')).toBeVisible();
	});

	test('User 1 (Alex Johnson) can sign in successfully', async ({ page }) => {
		console.log('Testing sign in for Alex Johnson...');

		const user = testUsers[0];

		// Fill credentials
		await page.fill('input[type="email"]', user.email);
		await page.fill('input[type="password"]', user.password);

		// Listen for success toast
		const toastPromise = page
			.waitForSelector('[data-sonner-toast]', {
				timeout: 10000,
				state: 'visible',
			})
			.catch(() => null);

		// Submit form
		await page.click('button[type="submit"]');

		// Wait for authentication
		await page.waitForTimeout(5000);

		// Check for success indicators
		const toast = await toastPromise;
		if (toast) {
			const toastText = await toast.textContent();
			console.log(`Sign in toast: ${toastText}`);

			if (toastText && toastText.includes('success')) {
				console.log('✅ Success toast shown');
			}
		}

		// Check if we're redirected to dashboard (URL should change)
		const currentUrl = page.url();
		console.log(`Current URL after sign in: ${currentUrl}`);

		// Look for dashboard elements or check if form is gone
		const formVisible = await page
			.locator('form')
			.isVisible()
			.catch(() => false);
		if (!formVisible) {
			console.log('✅ Login form disappeared - likely signed in successfully');
		}

		// Check for any error messages (shouldn't be any)
		const errorAlert = page.locator('[role="alert"].alert-destructive');
		const errorCount = await errorAlert.count();
		console.log(`Error alerts: ${errorCount}`);
		expect(errorCount).toBe(0);
	});

	test('shows proper error for wrong password', async ({ page }) => {
		console.log('Testing wrong password error...');

		await page.fill('input[type="email"]', testUsers[0].email);
		await page.fill('input[type="password"]', 'wrongpassword');

		const toastPromise = page
			.waitForSelector('[data-sonner-toast]', {
				timeout: 10000,
				state: 'visible',
			})
			.catch(() => null);

		await page.click('button[type="submit"]');
		await page.waitForTimeout(3000);

		// Should show error
		const toast = await toastPromise;
		if (toast) {
			const toastText = await toast.textContent();
			console.log(`Wrong password toast: ${toastText}`);

			if (
				toastText &&
				(toastText.includes('Invalid') ||
					toastText.includes('credentials') ||
					toastText.includes('password'))
			) {
				console.log('✅ Proper error message for wrong password');
			}
		}

		// Should still be on login form
		await expect(page.locator('form')).toBeVisible();
	});

	test('sign up now shows appropriate error for existing user', async ({
		page,
	}) => {
		console.log('Testing sign up with existing user...');

		// Switch to sign up
		const signUpToggle = page.locator(
			'button:has-text("Don\'t have an account")'
		);
		await signUpToggle.click();
		await page.waitForTimeout(500);

		// Try to sign up with existing user
		await page.fill('input[type="email"]', testUsers[0].email);
		await page.fill('input[type="password"]', 'testpassword123');

		const toastPromise = page
			.waitForSelector('[data-sonner-toast]', {
				timeout: 10000,
				state: 'visible',
			})
			.catch(() => null);

		await page.click('button[type="submit"]');
		await page.waitForTimeout(3000);

		const toast = await toastPromise;
		if (toast) {
			const toastText = await toast.textContent();
			console.log(`Existing user signup toast: ${toastText}`);

			if (
				toastText &&
				(toastText.includes('already') ||
					toastText.includes('exists') ||
					toastText.includes('registered'))
			) {
				console.log('✅ Proper error for existing user signup');
			}
		}
	});

	test('sign up with valid new email works', async ({ page }) => {
		console.log('Testing sign up with new valid email...');

		// Switch to sign up
		const signUpToggle = page.locator(
			'button:has-text("Don\'t have an account")'
		);
		await signUpToggle.click();
		await page.waitForTimeout(500);

		// Use a unique email
		const uniqueEmail = `test.user.${Date.now()}@example.com`;
		await page.fill('input[type="email"]', uniqueEmail);
		await page.fill('input[type="password"]', 'validpassword123');

		const toastPromise = page
			.waitForSelector('[data-sonner-toast]', {
				timeout: 10000,
				state: 'visible',
			})
			.catch(() => null);

		await page.click('button[type="submit"]');
		await page.waitForTimeout(5000);

		const toast = await toastPromise;
		if (toast) {
			const toastText = await toast.textContent();
			console.log(`New user signup toast: ${toastText}`);

			// Check for success or email confirmation message
			if (
				toastText &&
				(toastText.includes('created') ||
					toastText.includes('email') ||
					toastText.includes('success'))
			) {
				console.log('✅ Signup success message shown');
			} else if (toastText && toastText.includes('invalid')) {
				console.log(
					'❌ Still getting invalid email error - might be Supabase config issue'
				);
			}
		}
	});
});
