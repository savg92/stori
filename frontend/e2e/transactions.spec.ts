import { test, expect } from '@playwright/test';

test.describe('Transaction Management', () => {
	// Mock login before each test
	test.beforeEach(async ({ page }) => {
		// Mock successful authentication
		await page.addInitScript(() => {
			// Mock Supabase auth state
			window.localStorage.setItem(
				'sb-auth-token',
				JSON.stringify({
					access_token: 'mock-token',
					user: { id: 'user-123', email: 'test@example.com' },
				})
			);
		});

		await page.goto('/');
		// Wait for app to load authenticated state
		await page.waitForSelector('[data-testid="dashboard"]', { timeout: 10000 });
	});

	test('should display add transaction button', async ({ page }) => {
		await expect(
			page.getByRole('button', { name: /add transaction/i })
		).toBeVisible();
	});

	test('should open add transaction modal', async ({ page }) => {
		await page.getByRole('button', { name: /add transaction/i }).click();

		// Check modal is visible
		await expect(page.getByRole('dialog')).toBeVisible();
		await expect(page.getByText(/add transaction/i)).toBeVisible();

		// Check form fields
		await expect(page.locator('select[name="type"]')).toBeVisible();
		await expect(page.locator('input[name="amount"]')).toBeVisible();
		await expect(page.locator('select[name="category"]')).toBeVisible();
		await expect(page.locator('input[name="description"]')).toBeVisible();
		await expect(page.locator('input[name="date"]')).toBeVisible();
	});

	test('should validate required fields', async ({ page }) => {
		// Open modal
		await page.getByRole('button', { name: /add transaction/i }).click();

		// Try to submit without filling required fields
		await page.getByRole('button', { name: /save transaction/i }).click();

		// Check for validation errors
		await expect(page.getByText(/amount is required/i)).toBeVisible();
		await expect(page.getByText(/category is required/i)).toBeVisible();
	});

	test('should add expense transaction successfully', async ({ page }) => {
		// Mock API response for adding transaction
		await page.route('**/api/transactions', async (route) => {
			if (route.request().method() === 'POST') {
				await route.fulfill({
					status: 201,
					contentType: 'application/json',
					body: JSON.stringify({
						id: 'txn-123',
						type: 'expense',
						amount: -50.0,
						category: 'Food',
						description: 'Lunch',
						date: '2024-01-15',
					}),
				});
			} else {
				await route.continue();
			}
		});

		// Open modal and fill form
		await page.getByRole('button', { name: /add transaction/i }).click();

		await page.selectOption('select[name="type"]', 'expense');
		await page.fill('input[name="amount"]', '50.00');
		await page.selectOption('select[name="category"]', 'Food');
		await page.fill('input[name="description"]', 'Lunch');
		await page.fill('input[name="date"]', '2024-01-15');

		// Submit form
		await page.getByRole('button', { name: /save transaction/i }).click();

		// Check modal closes
		await expect(page.getByRole('dialog')).not.toBeVisible();

		// Check success message
		await expect(
			page.getByText(/transaction added successfully/i)
		).toBeVisible();
	});

	test('should add income transaction successfully', async ({ page }) => {
		// Mock API response
		await page.route('**/api/transactions', async (route) => {
			if (route.request().method() === 'POST') {
				await route.fulfill({
					status: 201,
					contentType: 'application/json',
					body: JSON.stringify({
						id: 'txn-124',
						type: 'income',
						amount: 3000.0,
						category: 'Salary',
						description: 'Monthly salary',
						date: '2024-01-01',
					}),
				});
			} else {
				await route.continue();
			}
		});

		// Open modal and fill form
		await page.getByRole('button', { name: /add transaction/i }).click();

		await page.selectOption('select[name="type"]', 'income');
		await page.fill('input[name="amount"]', '3000.00');
		await page.selectOption('select[name="category"]', 'Salary');
		await page.fill('input[name="description"]', 'Monthly salary');
		await page.fill('input[name="date"]', '2024-01-01');

		// Submit form
		await page.getByRole('button', { name: /save transaction/i }).click();

		// Check success
		await expect(page.getByRole('dialog')).not.toBeVisible();
		await expect(
			page.getByText(/transaction added successfully/i)
		).toBeVisible();
	});

	test('should display transactions in timeline', async ({ page }) => {
		// Mock API response for transactions list
		await page.route('**/api/transactions*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify([
					{
						id: 'txn-1',
						type: 'expense',
						amount: -50.0,
						category: 'Food',
						description: 'Lunch',
						date: '2024-01-15',
					},
					{
						id: 'txn-2',
						type: 'income',
						amount: 3000.0,
						category: 'Salary',
						description: 'Monthly salary',
						date: '2024-01-01',
					},
				]),
			});
		});

		// Navigate to timeline
		await page.getByRole('link', { name: /timeline/i }).click();

		// Check transactions are displayed
		await expect(page.getByText('Lunch')).toBeVisible();
		await expect(page.getByText('Monthly salary')).toBeVisible();
		await expect(page.getByText('-$50.00')).toBeVisible();
		await expect(page.getByText('+$3,000.00')).toBeVisible();
	});

	test('should edit transaction', async ({ page }) => {
		// Mock transactions list
		await page.route('**/api/transactions*', async (route) => {
			if (route.request().method() === 'GET') {
				await route.fulfill({
					status: 200,
					contentType: 'application/json',
					body: JSON.stringify([
						{
							id: 'txn-1',
							type: 'expense',
							amount: -50.0,
							category: 'Food',
							description: 'Lunch',
							date: '2024-01-15',
						},
					]),
				});
			} else {
				await route.continue();
			}
		});

		// Mock update response
		await page.route('**/api/transactions/txn-1', async (route) => {
			if (route.request().method() === 'PUT') {
				await route.fulfill({
					status: 200,
					contentType: 'application/json',
					body: JSON.stringify({
						id: 'txn-1',
						type: 'expense',
						amount: -75.0,
						category: 'Food',
						description: 'Dinner',
						date: '2024-01-15',
					}),
				});
			} else {
				await route.continue();
			}
		});

		// Navigate to timeline and edit transaction
		await page.getByRole('link', { name: /timeline/i }).click();
		await page.getByRole('button', { name: /edit/i }).first().click();

		// Update fields
		await page.fill('input[name="amount"]', '75.00');
		await page.fill('input[name="description"]', 'Dinner');

		// Submit
		await page.getByRole('button', { name: /save/i }).click();

		// Check success
		await expect(page.getByText(/transaction updated/i)).toBeVisible();
	});

	test('should delete transaction', async ({ page }) => {
		// Mock transactions list
		await page.route('**/api/transactions*', async (route) => {
			if (route.request().method() === 'GET') {
				await route.fulfill({
					status: 200,
					contentType: 'application/json',
					body: JSON.stringify([
						{
							id: 'txn-1',
							type: 'expense',
							amount: -50.0,
							category: 'Food',
							description: 'Lunch',
							date: '2024-01-15',
						},
					]),
				});
			} else {
				await route.continue();
			}
		});

		// Mock delete response
		await page.route('**/api/transactions/txn-1', async (route) => {
			if (route.request().method() === 'DELETE') {
				await route.fulfill({ status: 204 });
			} else {
				await route.continue();
			}
		});

		// Navigate to timeline and delete transaction
		await page.getByRole('link', { name: /timeline/i }).click();
		await page
			.getByRole('button', { name: /delete/i })
			.first()
			.click();

		// Confirm deletion
		await page.getByRole('button', { name: /confirm/i }).click();

		// Check success
		await expect(page.getByText(/transaction deleted/i)).toBeVisible();
	});
});
