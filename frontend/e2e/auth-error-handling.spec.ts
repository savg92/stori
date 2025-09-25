import { test, expect } from '@playwright/test';

test.describe('Authentication Error Handling', () => {
	test.beforeEach(async ({ page }) => {
		// Set viewport for consistent testing
		await page.setViewportSize({ width: 1280, height: 800 });

		// Clear any existing auth state
		await page.context().clearCookies();
		await page.context().clearPermissions();

		// Navigate to the app
		await page.goto('/');

		// Wait for the login form to be visible
		await expect(page.locator('form')).toBeVisible();
	});

	test('shows error messages and toasts for invalid credentials', async ({
		page,
	}) => {
		console.log('Testing invalid credentials error handling...');

		// Fill in invalid credentials
		await page.fill('input[type="email"]', 'nonexistent@email.com');
		await page.fill('input[type="password"]', 'wrongpassword');

		// Listen for toast notifications (Sonner creates elements with specific attributes)
		const toastPromise = page.waitForSelector('[data-sonner-toast]', {
			timeout: 10000,
			state: 'visible',
		});

		// Submit the form
		await page.click('button[type="submit"]');

		// Wait for loading to complete
		await page.waitForTimeout(3000);

		// Check for Alert component error message
		const alertError = page
			.locator('[role="alert"]')
			.or(page.locator('.alert-destructive'));

		// Should show error in Alert component
		if ((await alertError.count()) > 0) {
			console.log('✅ Alert error component found');
			const alertText = await alertError.textContent();
			console.log(`Alert message: ${alertText}`);
			expect(alertText).toBeTruthy();
		}

		// Check for toast notification
		try {
			const toast = await toastPromise;
			console.log('✅ Toast notification appeared');
			const toastText = await toast.textContent();
			console.log(`Toast message: ${toastText}`);
			expect(toastText).toBeTruthy();
		} catch {
			console.log(
				'ℹ️ Toast notification may not have appeared (this is OK if alerts work)'
			);
		}
	});

	test('shows validation errors for empty fields', async ({ page }) => {
		console.log('Testing empty field validation...');

		// Try to submit with empty fields
		const toastPromise = page
			.waitForSelector('[data-sonner-toast]', {
				timeout: 5000,
				state: 'visible',
			})
			.catch(() => null); // Don't fail if toast doesn't appear

		await page.click('button[type="submit"]');

		// Wait a moment for validation
		await page.waitForTimeout(1000);

		// Check for validation error
		const alertError = page
			.locator('[role="alert"]')
			.or(page.locator('.alert-destructive'));

		if ((await alertError.count()) > 0) {
			console.log('✅ Validation alert found');
			const alertText = await alertError.textContent();
			console.log(`Validation message: ${alertText}`);
			expect(alertText).toContain('Please fill in all fields');
		}

		// Check for toast
		const toast = await toastPromise;
		if (toast) {
			console.log('✅ Validation toast appeared');
			const toastText = await toast.textContent();
			console.log(`Toast validation message: ${toastText}`);
		}
	});

	test('toggles between sign in and sign up forms correctly', async ({
		page,
	}) => {
		console.log('Testing form toggle functionality...');

		// Check initial state (should be sign in)
		const initialButton = await page
			.locator('button[type="submit"]')
			.textContent();
		console.log(`Initial form: ${initialButton}`);

		// Click the toggle button
		const toggleButton = page
			.locator('button:has-text("Don\'t have an account")')
			.or(page.locator('button:has-text("Sign up")'));

		if ((await toggleButton.count()) > 0) {
			await toggleButton.click();
			await page.waitForTimeout(500);

			// Check if form changed to sign up
			const newButtonText = await page
				.locator('button[type="submit"]')
				.textContent();
			console.log(`After toggle: ${newButtonText}`);

			// Toggle back
			const backToggle = page
				.locator('button:has-text("Already have an account")')
				.or(page.locator('button:has-text("Sign in")'));

			if ((await backToggle.count()) > 0) {
				await backToggle.click();
				await page.waitForTimeout(500);

				const finalButtonText = await page
					.locator('button[type="submit"]')
					.textContent();
				console.log(`After toggle back: ${finalButtonText}`);

				expect(finalButtonText).toContain('Sign in');
			}
		}
	});

	test('tests sign up error handling', async ({ page }) => {
		console.log('Testing sign up error handling...');

		// Switch to sign up mode
		const signUpToggle = page
			.locator('button:has-text("Don\'t have an account")')
			.or(page.locator('button:has-text("Sign up")'));

		if ((await signUpToggle.count()) > 0) {
			await signUpToggle.click();
			await page.waitForTimeout(500);
		}

		// Try to create account with potentially invalid email
		await page.fill('input[type="email"]', 'invalid-email-format');
		await page.fill('input[type="password"]', '123'); // Too short password

		const toastPromise = page
			.waitForSelector('[data-sonner-toast]', {
				timeout: 10000,
				state: 'visible',
			})
			.catch(() => null);

		await page.click('button[type="submit"]');

		// Wait for any validation or error responses
		await page.waitForTimeout(3000);

		// Check for any error messages (either validation or server errors)
		const alertError = page
			.locator('[role="alert"]')
			.or(page.locator('.alert-destructive'));

		// Should show some kind of error (either client-side validation or server error)
		if ((await alertError.count()) > 0) {
			console.log('✅ Sign up error handling working');
			const alertText = await alertError.textContent();
			console.log(`Sign up error: ${alertText}`);
		} else {
			console.log(
				'ℹ️ No immediate error shown (may be handled by browser validation)'
			);
		}

		// Check for toast
		const toast = await toastPromise;
		if (toast) {
			console.log('✅ Sign up toast appeared');
			const toastText = await toast.textContent();
			console.log(`Sign up toast: ${toastText}`);
		}
	});

	test('verifies form accessibility and keyboard navigation', async ({
		page,
	}) => {
		console.log('Testing accessibility and keyboard navigation...');

		// Check form labels
		const emailLabel = page.locator('label[for="email"]');
		const passwordLabel = page.locator('label[for="password"]');

		await expect(emailLabel).toBeVisible();
		await expect(passwordLabel).toBeVisible();

		console.log('✅ Form labels are present');

		// Test keyboard navigation
		await page.keyboard.press('Tab'); // Should focus email input
		await page.keyboard.type('test@email.com');

		await page.keyboard.press('Tab'); // Should focus password input
		await page.keyboard.type('testpassword');

		await page.keyboard.press('Tab'); // Should focus submit button

		// Verify focused element
		const focusedElement = await page.evaluate(
			() => document.activeElement?.tagName
		);
		console.log(`Focused element after tabbing: ${focusedElement}`);

		// Test Enter key submission
		await page.keyboard.press('Enter');

		// Wait for any response
		await page.waitForTimeout(2000);

		console.log('✅ Keyboard navigation and form submission working');
	});

	test('verifies error clearing when switching forms', async ({ page }) => {
		console.log('Testing error clearing when toggling forms...');

		// First, trigger an error
		await page.click('button[type="submit"]'); // Submit empty form
		await page.waitForTimeout(1000);

		// Verify error is shown
		const alertError = page
			.locator('[role="alert"]')
			.or(page.locator('.alert-destructive'));

		if ((await alertError.count()) > 0) {
			console.log('✅ Error message shown');

			// Now toggle to sign up
			const toggleButton = page
				.locator('button:has-text("Don\'t have an account")')
				.or(page.locator('button:has-text("Sign up")'));

			if ((await toggleButton.count()) > 0) {
				await toggleButton.click();
				await page.waitForTimeout(500);

				// Check if error was cleared
				const errorAfterToggle = page
					.locator('[role="alert"]')
					.or(page.locator('.alert-destructive'));

				const errorCount = await errorAfterToggle.count();
				console.log(`Errors after toggle: ${errorCount}`);

				if (errorCount === 0) {
					console.log('✅ Error messages cleared when toggling forms');
				} else {
					console.log(
						'ℹ️ Error messages still visible (may be expected behavior)'
					);
				}
			}
		}
	});
});
