import { test, expect } from '@playwright/test';

test.describe('AI Financial Advisor', () => {
	test.beforeEach(async ({ page }) => {
		// Mock authentication
		await page.addInitScript(() => {
			window.localStorage.setItem(
				'sb-auth-token',
				JSON.stringify({
					access_token: 'mock-token',
					user: { id: 'user-123', email: 'test@example.com' },
				})
			);
		});

		await page.goto('/');
		await page.waitForSelector('[data-testid="dashboard"]', { timeout: 10000 });

		// Navigate to AI advisor
		await page.getByRole('link', { name: /ai advisor/i }).click();
	});

	test('should display AI chat interface', async ({ page }) => {
		// Check chat interface elements
		await expect(page.getByTestId('chat-container')).toBeVisible();
		await expect(page.getByTestId('chat-input')).toBeVisible();
		await expect(page.getByRole('button', { name: /send/i })).toBeVisible();

		// Check welcome message
		await expect(
			page.getByText(/hello! i'm your ai financial advisor/i)
		).toBeVisible();
	});

	test('should send message and receive AI response', async ({ page }) => {
		// Mock AI advice API
		await page.route('**/api/ai/advice', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					response:
						"Based on your spending patterns, I notice you're spending quite a bit on food ($450 this month). Consider meal planning to reduce expenses by 20-30%. You're doing well with your savings rate of 75%!",
					suggestions: [
						'Create a weekly meal plan',
						'Set a food budget of $350/month',
						'Track grocery vs dining out expenses',
					],
					confidence: 0.85,
				}),
			});
		});

		const chatInput = page.getByTestId('chat-input');

		// Type and send message
		await chatInput.fill('How can I reduce my food expenses?');
		await page.getByRole('button', { name: /send/i }).click();

		// Check message appears in chat
		await expect(
			page.getByText('How can I reduce my food expenses?')
		).toBeVisible();

		// Check AI response
		await expect(
			page.getByText(/based on your spending patterns/i)
		).toBeVisible();
		await expect(page.getByText(/meal planning/i)).toBeVisible();

		// Check suggestions are displayed
		await expect(page.getByText('Create a weekly meal plan')).toBeVisible();
		await expect(
			page.getByText('Set a food budget of $350/month')
		).toBeVisible();
	});

	test('should handle multiple conversation turns', async ({ page }) => {
		// Mock multiple AI responses
		let messageCount = 0;
		await page.route('**/api/ai/advice', async (route) => {
			messageCount++;
			const responses = [
				"I can help you create a budget! Let's start by analyzing your current spending patterns.",
				"Great! Based on your data, I recommend the 50/30/20 rule: 50% needs, 30% wants, 20% savings. You're currently at 75% savings rate which is excellent!",
			];

			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					response: responses[messageCount - 1] || responses[1],
					suggestions:
						messageCount === 1
							? ['Track all expenses for a week', 'Categorize spending']
							: ['Maintain current savings rate', 'Consider investing excess'],
					confidence: 0.9,
				}),
			});
		});

		const chatInput = page.getByTestId('chat-input');

		// First message
		await chatInput.fill('Can you help me create a budget?');
		await page.getByRole('button', { name: /send/i }).click();

		await expect(page.getByText(/help you create a budget/i)).toBeVisible();

		// Second message
		await chatInput.fill('Yes, please analyze my spending');
		await page.getByRole('button', { name: /send/i }).click();

		await expect(page.getByText(/50\/30\/20 rule/i)).toBeVisible();

		// Check both messages are in conversation history
		await expect(
			page.getByText('Can you help me create a budget?')
		).toBeVisible();
		await expect(
			page.getByText('Yes, please analyze my spending')
		).toBeVisible();
	});

	test('should display suggested questions', async ({ page }) => {
		// Check predefined question suggestions
		await expect(page.getByText(/suggested questions/i)).toBeVisible();
		await expect(
			page.getByRole('button', { name: /how can i save more money/i })
		).toBeVisible();
		await expect(
			page.getByRole('button', { name: /analyze my spending habits/i })
		).toBeVisible();
		await expect(
			page.getByRole('button', { name: /help me create a budget/i })
		).toBeVisible();
	});

	test('should use suggested question', async ({ page }) => {
		// Mock AI response for suggested question
		await page.route('**/api/ai/advice', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					response:
						"Looking at your expenses, you're already doing great with a 75% savings rate! To save even more, consider reducing your food expenses by meal planning.",
					suggestions: [
						'Meal prep on Sundays',
						'Use grocery store apps for discounts',
						'Set dining out budget limit',
					],
					confidence: 0.88,
				}),
			});
		});

		// Click suggested question
		await page
			.getByRole('button', { name: /how can i save more money/i })
			.click();

		// Check question appears in chat
		await expect(page.getByText('How can I save more money?')).toBeVisible();

		// Check AI response
		await expect(
			page.getByText(/already doing great with a 75% savings rate/i)
		).toBeVisible();
	});

	test('should handle empty message', async ({ page }) => {
		// Try to send empty message
		await page.getByRole('button', { name: /send/i }).click();

		// Check validation or no action
		const chatMessages = page.locator('[data-testid="chat-message"]');
		const messageCount = await chatMessages.count();

		// Should only have welcome message, no empty message sent
		expect(messageCount).toBeLessThanOrEqual(1);
	});

	test('should handle API errors gracefully', async ({ page }) => {
		// Mock API error
		await page.route('**/api/ai/advice', async (route) => {
			await route.fulfill({
				status: 500,
				contentType: 'application/json',
				body: JSON.stringify({ error: 'AI service temporarily unavailable' }),
			});
		});

		const chatInput = page.getByTestId('chat-input');

		// Send message
		await chatInput.fill('Help me with my budget');
		await page.getByRole('button', { name: /send/i }).click();

		// Check error message
		await expect(page.getByText(/sorry, i'm having trouble/i)).toBeVisible();
		await expect(
			page.getByRole('button', { name: /try again/i })
		).toBeVisible();
	});

	test('should display loading state during AI response', async ({ page }) => {
		// Mock slow AI response
		await page.route('**/api/ai/advice', async (route) => {
			await new Promise((resolve) => setTimeout(resolve, 2000));
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					response: "Here's my advice...",
					suggestions: [],
					confidence: 0.8,
				}),
			});
		});

		const chatInput = page.getByTestId('chat-input');

		// Send message
		await chatInput.fill('Give me advice');
		await page.getByRole('button', { name: /send/i }).click();

		// Check loading state
		await expect(page.getByTestId('ai-thinking')).toBeVisible();
		await expect(page.getByText(/thinking/i)).toBeVisible();

		// Wait for response
		await expect(page.getByText("Here's my advice...")).toBeVisible({
			timeout: 3000,
		});
		await expect(page.getByTestId('ai-thinking')).not.toBeVisible();
	});

	test('should clear conversation', async ({ page }) => {
		// Send a message first
		await page.route('**/api/ai/advice', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					response: 'Test response',
					suggestions: [],
					confidence: 0.8,
				}),
			});
		});

		const chatInput = page.getByTestId('chat-input');
		await chatInput.fill('Test message');
		await page.getByRole('button', { name: /send/i }).click();

		await expect(page.getByText('Test message')).toBeVisible();

		// Clear conversation
		await page.getByRole('button', { name: /clear conversation/i }).click();

		// Check conversation is cleared
		await expect(page.getByText('Test message')).not.toBeVisible();
		await expect(page.getByText('Test response')).not.toBeVisible();

		// Welcome message should still be there
		await expect(
			page.getByText(/hello! i'm your ai financial advisor/i)
		).toBeVisible();
	});

	test('should export conversation', async ({ page }) => {
		// Send a message to have conversation history
		await page.route('**/api/ai/advice', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					response: 'Export test response',
					suggestions: [],
					confidence: 0.8,
				}),
			});
		});

		const chatInput = page.getByTestId('chat-input');
		await chatInput.fill('Export test message');
		await page.getByRole('button', { name: /send/i }).click();

		await expect(page.getByText('Export test message')).toBeVisible();

		// Export conversation
		const downloadPromise = page.waitForEvent('download');
		await page.getByRole('button', { name: /export conversation/i }).click();

		const download = await downloadPromise;
		expect(download.suggestedFilename()).toMatch(/conversation.*\.txt/);
	});
});
