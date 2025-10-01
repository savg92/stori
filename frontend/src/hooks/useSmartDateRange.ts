import { useMemo } from 'react';
import { subDays, subMonths, format } from 'date-fns';
import { useTransactions } from './useApi';
import type { Transaction } from '../types/api';

interface DateRangeOption {
	startDate: string;
	endDate: string;
	label: string;
	transactionCount: number;
}

interface SmartDateRangeResult {
	optimalRange: DateRangeOption;
	isLoading: boolean;
	availableRanges: DateRangeOption[];
}

export function useSmartDateRange(): SmartDateRangeResult {
	const { data: transactions, isLoading } = useTransactions();

	const result = useMemo(() => {
		if (
			!transactions ||
			!transactions.items ||
			transactions.items.length === 0
		) {
			// Default to current month when no data
			const now = new Date();
			const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
			return {
				optimalRange: {
					startDate: format(startOfMonth, 'yyyy-MM-dd'),
					endDate: format(now, 'yyyy-MM-dd'),
					label: 'Current Month',
					transactionCount: 0,
				},
				availableRanges: [],
			};
		}

		// Find the actual date range of user's transaction data
		const transactionDates = transactions.items.map((t) => new Date(t.date));
		const earliestDate = new Date(
			Math.min(...transactionDates.map((d) => d.getTime()))
		);
		const latestDate = new Date(
			Math.max(...transactionDates.map((d) => d.getTime()))
		);
		const now = new Date();

		// Create smart ranges based on actual data span
		const rangeOptions = [];

		// Add "All Data" option covering the entire transaction range
		rangeOptions.push({
			label:
				earliestDate.getFullYear() === latestDate.getFullYear()
					? `All ${earliestDate.getFullYear()} data`
					: 'All Data',
			startDate: format(earliestDate, 'yyyy-MM-dd'),
			endDate: format(latestDate, 'yyyy-MM-dd'),
		});

		// Add time-based ranges only if they make sense with the data
		const thirtyDaysAgo = subDays(now, 30);
		const threeMonthsAgo = subMonths(now, 3);
		const sixMonthsAgo = subMonths(now, 6);
		const twelveMonthsAgo = subMonths(now, 12);

		// Only add ranges that would include some of the user's data
		if (latestDate >= thirtyDaysAgo) {
			rangeOptions.push({
				label: 'Last 30 Days',
				startDate: format(
					Math.max(thirtyDaysAgo.getTime(), earliestDate.getTime()),
					'yyyy-MM-dd'
				),
				endDate: format(
					Math.min(now.getTime(), latestDate.getTime()),
					'yyyy-MM-dd'
				),
			});
		}

		if (latestDate >= threeMonthsAgo) {
			rangeOptions.push({
				label: 'Last 3 Months',
				startDate: format(
					Math.max(threeMonthsAgo.getTime(), earliestDate.getTime()),
					'yyyy-MM-dd'
				),
				endDate: format(
					Math.min(now.getTime(), latestDate.getTime()),
					'yyyy-MM-dd'
				),
			});
		}

		if (latestDate >= sixMonthsAgo) {
			rangeOptions.push({
				label: 'Last 6 Months',
				startDate: format(
					Math.max(sixMonthsAgo.getTime(), earliestDate.getTime()),
					'yyyy-MM-dd'
				),
				endDate: format(
					Math.min(now.getTime(), latestDate.getTime()),
					'yyyy-MM-dd'
				),
			});
		}

		if (latestDate >= twelveMonthsAgo) {
			rangeOptions.push({
				label: 'Last 12 Months',
				startDate: format(
					Math.max(twelveMonthsAgo.getTime(), earliestDate.getTime()),
					'yyyy-MM-dd'
				),
				endDate: format(
					Math.min(now.getTime(), latestDate.getTime()),
					'yyyy-MM-dd'
				),
			});
		}

		// Count transactions in each range
		const rangesWithCounts: DateRangeOption[] = rangeOptions.map((range) => {
			const rangeStart = new Date(range.startDate);
			const rangeEnd = new Date(range.endDate);

			const transactionCount = transactions.items.filter(
				(transaction: Transaction) => {
					const transactionDate = new Date(transaction.date);
					return transactionDate >= rangeStart && transactionDate <= rangeEnd;
				}
			).length;

			return {
				...range,
				transactionCount,
			};
		});

		// Find the optimal range - prefer comprehensive view for financial data
		const MIN_TRANSACTION_THRESHOLD = 5; // Minimum transactions to consider meaningful

		// Always prefer "All Data" if it has meaningful transactions
		let optimalRange = rangesWithCounts[0]; // "All Data" is always first

		// If "All Data" doesn't have enough transactions, find the best alternative
		if (
			optimalRange.transactionCount < MIN_TRANSACTION_THRESHOLD &&
			rangesWithCounts.length > 1
		) {
			const alternativeRange = rangesWithCounts
				.slice(1)
				.find((range) => range.transactionCount >= MIN_TRANSACTION_THRESHOLD);

			if (alternativeRange) {
				optimalRange = alternativeRange;
			}
		}

		// Final fallback - use the range with the most transactions
		if (!optimalRange || optimalRange.transactionCount === 0) {
			optimalRange = rangesWithCounts.reduce((best, current) =>
				current.transactionCount > best.transactionCount ? current : best
			);
		}

		return {
			optimalRange,
			availableRanges: rangesWithCounts.filter(
				(range) => range.transactionCount > 0
			),
		};
	}, [transactions]);

	return {
		...result,
		isLoading,
	};
}
