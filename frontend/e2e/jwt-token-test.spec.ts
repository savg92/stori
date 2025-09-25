import { test, expect } from '@playwright/test';

test.describe('JWT Token Extraction for API Testing', () => {
	test('extract JWT token after login and test API', async ({ page }) => {
		console.log('🧪 Testing JWT token extraction and API calls...');

		// Navigate to login page
		await page.goto('http://localhost:5173/login');

		// Sign in with User 1
		await page.fill('input[type="email"]', 'alex.johnson+test@example.com');
		await page.fill('input[type="password"]', 'securepass123');
		await page.click('button[type="submit"]');

		// Wait for redirect to dashboard (successful login)
		await page.waitForURL('http://localhost:5173/', { timeout: 10000 });
		console.log('✅ Successfully redirected to dashboard after login');

		// Extract the JWT token from localStorage
		const token = await page.evaluate(() => {
			// Get all localStorage keys to find the auth token
			const keys = Object.keys(localStorage);
			const authKey = keys.find((key) => key.includes('auth-token'));
			if (!authKey) return null;

			const auth = JSON.parse(localStorage.getItem(authKey) || '{}');
			return auth.access_token;
		});

		console.log(
			'🔑 JWT Token extracted:',
			token ? 'Token found!' : 'No token found'
		);
		expect(token).toBeTruthy();

		// Test API call with the token
		const apiResponse = await page.evaluate(async (token) => {
			try {
				const response = await fetch(
					'http://localhost:8000/api/transactions/',
					{
						headers: {
							Authorization: `Bearer ${token}`,
							'Content-Type': 'application/json',
						},
					}
				);

				let responseData;
				try {
					responseData = await response.json();
				} catch {
					responseData = await response.text();
				}

				return {
					status: response.status,
					statusText: response.statusText,
					data: responseData,
				};
			} catch (error) {
				return {
					status: 0,
					statusText: 'Network Error',
					error: error.message,
				};
			}
		}, token);

		console.log('📊 API Response:', {
			status: apiResponse.status,
			statusText: apiResponse.statusText,
			dataPreview:
				typeof apiResponse.data === 'string'
					? apiResponse.data.substring(0, 100)
					: apiResponse.data,
		});

		// Check if we're getting proper authentication
		if (apiResponse.status === 401) {
			console.log('❌ Still getting authentication error:', apiResponse.data);
		} else if (apiResponse.status === 200) {
			console.log('✅ API call successful with authentication!');
		} else {
			console.log(
				'⚠️ Unexpected API response:',
				apiResponse.status,
				apiResponse.data
			);
		}
	});
});
