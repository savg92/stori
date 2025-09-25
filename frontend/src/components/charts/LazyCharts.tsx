import React, { Suspense } from 'react';
import { Loader2 } from 'lucide-react';
import { Card, CardContent } from '../ui/card';

// Lazy load chart components to reduce initial bundle size
const ExpenseChart = React.lazy(() =>
	import('./ExpenseChart').then((module) => ({ default: module.ExpenseChart }))
);

const TimelineChart = React.lazy(() =>
	import('./TimelineChart').then((module) => ({
		default: module.TimelineChart,
	}))
);

// Chart loading fallback component
function ChartLoading() {
	return (
		<Card className='w-full'>
			<CardContent className='flex items-center justify-center h-80'>
				<div className='flex flex-col items-center space-y-2 text-muted-foreground'>
					<Loader2 className='h-8 w-8 animate-spin' />
					<p className='text-sm'>Loading chart...</p>
				</div>
			</CardContent>
		</Card>
	);
}

// Lazy-loaded expense chart with suspense boundary
interface LazyChartProps {
	[key: string]: unknown;
}

export function LazyExpenseChart(props: LazyChartProps) {
	return (
		<Suspense fallback={<ChartLoading />}>
			<ExpenseChart {...props} />
		</Suspense>
	);
}

// Lazy-loaded timeline chart with suspense boundary
export function LazyTimelineChart(props: LazyChartProps) {
	return (
		<Suspense fallback={<ChartLoading />}>
			<TimelineChart {...props} />
		</Suspense>
	);
}
