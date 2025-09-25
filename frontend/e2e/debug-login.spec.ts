import { test, expect } from '@playwright/test';

test('Debug login page content', async ({ page }) => {
	console.log('🔍 Debugging login page content...');

	await page.goto('http://localhost:5173');

	// Take a screenshot to see what we're working with
	await page.screenshot({ path: 'debug-login-page.png', fullPage: true });

	// Get all text content to see what's actually on the page
	const bodyText = await page.textContent('body');
	console.log('Page content:', bodyText);

	// Check for various possible headings
	const headings = await page
		.locator('h1, h2, h3, h4, h5, h6')
		.allTextContents();
	console.log('Headings found:', headings);

	// Check for forms
	const forms = await page.locator('form').count();
	console.log('Forms found:', forms);

	// Check for buttons
	const buttons = await page.locator('button').allTextContents();
	console.log('Buttons found:', buttons);

	console.log('✅ Debug complete');
});
