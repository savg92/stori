// API Data Test Component - for debugging and verification
import {
	useCurrentMonthSummary,
	useExpenseSummary,
	useTimelineData,
} from '@/hooks/useApi';
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from '@/components/ui/card';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';

export function APIDataTest() {
	const {
		data: currentMonthData,
		isLoading: isCurrentMonthLoading,
		error: currentMonthError,
	} = useCurrentMonthSummary();
	const {
		data: expenseData,
		isLoading: isExpenseLoading,
		error: expenseError,
	} = useExpenseSummary();
	const {
		data: timelineData,
		isLoading: isTimelineLoading,
		error: timelineError,
	} = useTimelineData();

	const StatusIcon = ({
		isLoading,
		error,
		hasData,
	}: {
		isLoading: boolean;
		error: unknown;
		hasData: boolean;
	}) => {
		if (isLoading)
			return <Loader2 className='h-4 w-4 animate-spin text-blue-500' />;
		if (error) return <XCircle className='h-4 w-4 text-red-500' />;
		if (hasData) return <CheckCircle className='h-4 w-4 text-green-500' />;
		return <XCircle className='h-4 w-4 text-gray-400' />;
	};

	return (
		<Card className='w-full max-w-4xl'>
			<CardHeader>
				<CardTitle>API Data Flow Test</CardTitle>
				<CardDescription>
					Verify that charts are receiving real data from backend API
				</CardDescription>
			</CardHeader>
			<CardContent className='space-y-4'>
				{/* Current Month Summary Test */}
				<div className='flex items-center justify-between p-3 border rounded'>
					<div>
						<h4 className='font-medium'>Current Month Summary API</h4>
						<p className='text-sm text-muted-foreground'>
							{currentMonthData
								? `Net: $${currentMonthData.net_amount}, Expenses: $${currentMonthData.total_expenses}`
								: 'No data'}
						</p>
						{currentMonthError && (
							<p className='text-sm text-red-500'>
								Error: {currentMonthError.message}
							</p>
						)}
					</div>
					<StatusIcon
						isLoading={isCurrentMonthLoading}
						error={currentMonthError}
						hasData={!!currentMonthData}
					/>
				</div>

				{/* Expense Summary Test */}
				<div className='flex items-center justify-between p-3 border rounded'>
					<div>
						<h4 className='font-medium'>Expense Summary API (Chart Data)</h4>
						<p className='text-sm text-muted-foreground'>
							{expenseData
								? `${expenseData.category_breakdown.length} categories`
								: 'No data'}
						</p>
						{(expenseData?.category_breakdown?.length || 0) > 0 && (
							<p className='text-xs text-muted-foreground'>
								Categories:{' '}
								{expenseData?.category_breakdown
									?.map((cat) => cat.category)
									.join(', ')}
							</p>
						)}
						{expenseError && (
							<p className='text-sm text-red-500'>
								Error: {expenseError.message}
							</p>
						)}
					</div>
					<StatusIcon
						isLoading={isExpenseLoading}
						error={expenseError}
						hasData={!!expenseData?.category_breakdown?.length}
					/>
				</div>

				{/* Timeline Data Test */}
				<div className='flex items-center justify-between p-3 border rounded'>
					<div>
						<h4 className='font-medium'>Timeline Data API (Chart Data)</h4>
						<p className='text-sm text-muted-foreground'>
							{timelineData
								? `${timelineData.data_points.length} data points`
								: 'No data'}
						</p>
						{(timelineData?.data_points?.length || 0) > 0 && (
							<p className='text-xs text-muted-foreground'>
								Latest:{' '}
								{
									timelineData?.data_points?.[
										timelineData.data_points.length - 1
									]?.date
								}{' '}
								- Income: $
								{
									timelineData?.data_points?.[
										timelineData.data_points.length - 1
									]?.total_income
								}
							</p>
						)}
						{timelineError && (
							<p className='text-sm text-red-500'>
								Error: {timelineError.message}
							</p>
						)}
					</div>
					<StatusIcon
						isLoading={isTimelineLoading}
						error={timelineError}
						hasData={!!timelineData?.data_points?.length}
					/>
				</div>

				{/* Raw Backend Test */}
				<div className='p-3 border rounded bg-muted/50'>
					<h4 className='font-medium text-sm'>Backend API Raw Data Sample</h4>
					<p className='text-xs text-muted-foreground mt-1'>
						Backend Mock API: User 1 has $56,000 income, -$19,557 expenses, net
						$75,557
					</p>
					<p className='text-xs text-muted-foreground'>
						Categories: rent (-$12,000), groceries (-$2,198), dining (-$1,450),
						etc.
					</p>
				</div>
			</CardContent>
		</Card>
	);
}
