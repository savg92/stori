import { test, expect } from '@playwright/test';

test.describe('Basic Debug Test', () => {
	test('Check if app loads and what we see', async ({ page }) => {
		console.log('Starting test...');

		// Go to the app
		await page.goto('/');

		// Wait a bit for the app to load
		await page.waitForTimeout(3000);

		// Take a screenshot
		await page.screenshot({ path: 'debug-homepage.png' });

		// Get page info
		console.log('Page title:', await page.title());
		console.log('Page URL:', page.url());
		console.log(
			'Page content preview:',
			(await page.textContent('body'))?.slice(0, 500)
		);

		// Check what elements exist
		const form = page.locator('form');
		const formCount = await form.count();
		console.log('Forms found:', formCount);

		if (formCount > 0) {
			console.log('Form content:', await form.first().textContent());
		}

		const headings = page.locator('h1, h2, h3, h4, h5, h6');
		const headingCount = await headings.count();
		console.log('Headings found:', headingCount);

		for (let i = 0; i < Math.min(headingCount, 5); i++) {
			console.log(`Heading ${i + 1}:`, await headings.nth(i).textContent());
		}

		const inputs = page.locator('input');
		const inputCount = await inputs.count();
		console.log('Inputs found:', inputCount);

		for (let i = 0; i < Math.min(inputCount, 3); i++) {
			const input = inputs.nth(i);
			console.log(`Input ${i + 1} type:`, await input.getAttribute('type'));
			console.log(
				`Input ${i + 1} placeholder:`,
				await input.getAttribute('placeholder')
			);
		}

		const buttons = page.locator('button');
		const buttonCount = await buttons.count();
		console.log('Buttons found:', buttonCount);

		for (let i = 0; i < Math.min(buttonCount, 3); i++) {
			console.log(`Button ${i + 1}:`, await buttons.nth(i).textContent());
		}

		// Basic assertion - the page should have some content
		await expect(page.locator('body')).not.toBeEmpty();
	});
});
