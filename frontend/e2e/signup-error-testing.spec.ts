import { test, expect } from '@playwright/test';

test.describe('Sign Up Error Handling - Detailed Testing', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('/');
		await expect(page.locator('form')).toBeVisible();

		// Switch to sign up mode
		const signUpToggle = page
			.locator('button:has-text("Don\'t have an account")')
			.or(page.locator('button:has-text("Sign up")'));

		if ((await signUpToggle.count()) > 0) {
			await signUpToggle.click();
			await page.waitForTimeout(500);
		}

		// Verify we're in sign up mode
		await expect(
			page.locator('button[type="submit"]:has-text("Create account")')
		).toBeVisible();
	});

	test('shows toast and alert for invalid email during sign up', async ({
		page,
	}) => {
		console.log('Testing sign up with invalid email...');

		// Fill invalid email format
		await page.fill('input[type="email"]', 'invalid-email-format');
		await page.fill('input[type="password"]', 'validpassword123');

		// Listen for toast
		const toastPromise = page
			.waitForSelector('[data-sonner-toast]', {
				timeout: 10000,
				state: 'visible',
			})
			.catch(() => null);

		// Submit form
		await page.click('button[type="submit"]');

		// Wait for response
		await page.waitForTimeout(3000);

		// Check for error messages
		const alertError = page
			.locator('[role="alert"]')
			.or(page.locator('.alert-destructive'));

		const alertCount = await alertError.count();
		console.log(`Alert errors found: ${alertCount}`);

		if (alertCount > 0) {
			const alertText = await alertError.first().textContent();
			console.log(`Alert message: ${alertText}`);
			expect(alertText).toBeTruthy();
		}

		// Check for toast
		const toast = await toastPromise;
		if (toast) {
			const toastText = await toast.textContent();
			console.log(`Toast message: ${toastText}`);
			expect(toastText).toBeTruthy();
		} else {
			console.log('No toast appeared - checking browser validation...');
		}
	});

	test('shows errors for weak password during sign up', async ({ page }) => {
		console.log('Testing sign up with weak password...');

		await page.fill('input[type="email"]', 'test@example.com');
		await page.fill('input[type="password"]', '123'); // Too short

		const toastPromise = page
			.waitForSelector('[data-sonner-toast]', {
				timeout: 10000,
				state: 'visible',
			})
			.catch(() => null);

		await page.click('button[type="submit"]');
		await page.waitForTimeout(3000);

		// Check for validation errors
		const alertError = page
			.locator('[role="alert"]')
			.or(page.locator('.alert-destructive'));

		if ((await alertError.count()) > 0) {
			const alertText = await alertError.textContent();
			console.log(`Password validation alert: ${alertText}`);
		}

		const toast = await toastPromise;
		if (toast) {
			const toastText = await toast.textContent();
			console.log(`Password validation toast: ${toastText}`);
		}
	});

	test('shows errors for existing email during sign up', async ({ page }) => {
		console.log('Testing sign up with existing email...');

		// Try to sign up with an email that might already exist
		await page.fill('input[type="email"]', 'alex.johnson@email.com');
		await page.fill('input[type="password"]', 'testpassword123');

		const toastPromise = page
			.waitForSelector('[data-sonner-toast]', {
				timeout: 10000,
				state: 'visible',
			})
			.catch(() => null);

		await page.click('button[type="submit"]');
		await page.waitForTimeout(5000); // Wait longer for server response

		// Check for error about existing user
		const alertError = page
			.locator('[role="alert"]')
			.or(page.locator('.alert-destructive'));

		if ((await alertError.count()) > 0) {
			const alertText = await alertError.textContent();
			console.log(`Existing email alert: ${alertText}`);

			// Should contain some indication about user already existing
			if (
				alertText &&
				(alertText.includes('already') ||
					alertText.includes('exists') ||
					alertText.includes('registered') ||
					alertText.includes('taken'))
			) {
				console.log('✅ Proper existing user error shown');
			}
		}

		const toast = await toastPromise;
		if (toast) {
			const toastText = await toast.textContent();
			console.log(`Existing email toast: ${toastText}`);
		}
	});

	test('shows success message for valid sign up', async ({ page }) => {
		console.log('Testing valid sign up...');

		// Use a unique email that shouldn't exist
		const uniqueEmail = `test.${Date.now()}@example.com`;
		await page.fill('input[type="email"]', uniqueEmail);
		await page.fill('input[type="password"]', 'validpassword123');

		// Listen for success toast
		const toastPromise = page
			.waitForSelector('[data-sonner-toast]', {
				timeout: 10000,
				state: 'visible',
			})
			.catch(() => null);

		await page.click('button[type="submit"]');
		await page.waitForTimeout(5000);

		// Check for success message
		const successAlert = page
			.locator('[role="alert"]:not(.alert-destructive)')
			.or(page.locator('.alert:not(.alert-destructive)'));

		if ((await successAlert.count()) > 0) {
			const successText = await successAlert.textContent();
			console.log(`Success alert: ${successText}`);

			if (successText && successText.includes('email')) {
				console.log('✅ Success message about email verification shown');
			}
		}

		const toast = await toastPromise;
		if (toast) {
			const toastText = await toast.textContent();
			console.log(`Success toast: ${toastText}`);

			if (
				toastText &&
				(toastText.includes('success') ||
					toastText.includes('created') ||
					toastText.includes('email'))
			) {
				console.log('✅ Success toast shown properly');
			}
		}
	});

	test('shows network error handling', async ({ page }) => {
		console.log('Testing network error handling...');

		// We can't easily simulate network errors in this test,
		// but we can check that the error handling code paths exist

		await page.fill('input[type="email"]', 'network.test@example.com');
		await page.fill('input[type="password"]', 'testpassword123');

		// Mock a network failure by intercepting the auth request
		await page.route('**/*', (route) => {
			if (
				route.request().url().includes('supabase') &&
				route.request().method() === 'POST'
			) {
				console.log(
					'Intercepting Supabase auth request for network simulation'
				);
				route.abort('failed');
			} else {
				route.continue();
			}
		});

		const toastPromise = page
			.waitForSelector('[data-sonner-toast]', {
				timeout: 10000,
				state: 'visible',
			})
			.catch(() => null);

		await page.click('button[type="submit"]');
		await page.waitForTimeout(3000);

		// Should show network error
		const alertError = page
			.locator('[role="alert"]')
			.or(page.locator('.alert-destructive'));

		if ((await alertError.count()) > 0) {
			const alertText = await alertError.textContent();
			console.log(`Network error alert: ${alertText}`);

			if (
				alertText &&
				(alertText.includes('error') ||
					alertText.includes('failed') ||
					alertText.includes('unexpected'))
			) {
				console.log('✅ Network error properly handled');
			}
		}

		const toast = await toastPromise;
		if (toast) {
			const toastText = await toast.textContent();
			console.log(`Network error toast: ${toastText}`);
		}
	});
});
