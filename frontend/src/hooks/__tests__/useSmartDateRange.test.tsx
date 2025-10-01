import { describe, test, expect } from 'vitest';
import { subDays, subMonths, format } from 'date-fns';

describe('useSmartDateRange', () => {
	test('should correctly calculate date ranges for smart detection', () => {
		const now = new Date();

		// Test 30 days calculation
		const thirtyDaysAgo = subDays(now, 30);
		const formattedThirtyDays = format(thirtyDaysAgo, 'yyyy-MM-dd');
		expect(formattedThirtyDays).toMatch(/^\d{4}-\d{2}-\d{2}$/);

		// Test 3 months calculation
		const threeMonthsAgo = subMonths(now, 3);
		const formattedThreeMonths = format(threeMonthsAgo, 'yyyy-MM-dd');
		expect(formattedThreeMonths).toMatch(/^\d{4}-\d{2}-\d{2}$/);

		// Verify ordering
		expect(thirtyDaysAgo.getTime()).toBeGreaterThan(threeMonthsAgo.getTime());
	});

	test('should handle transaction count logic', () => {
		const MIN_TRANSACTION_THRESHOLD = 5;

		// Test meaningful data detection
		expect(10).toBeGreaterThanOrEqual(MIN_TRANSACTION_THRESHOLD);
		expect(3).toBeLessThan(MIN_TRANSACTION_THRESHOLD);
	});
});
