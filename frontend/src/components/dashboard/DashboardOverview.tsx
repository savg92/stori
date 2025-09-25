import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { TrendingUp, TrendingDown, DollarSign, CreditCard } from 'lucide-react';
import { ExpenseChart } from '@/components/charts/ExpenseChart';
import { TimelineChart } from '@/components/charts/TimelineChart';
import { RecentTransactions } from './RecentTransactions';
import { DateRangePicker } from '@/components/ui/date-range-picker';
import { useExpenseSummary } from '@/hooks/useApi';

interface StatCardProps {
	title: string;
	value: string;
	description: string;
	icon: React.ComponentType<{ className?: string }>;
	trend?: 'up' | 'down' | 'neutral';
	trendValue?: string;
}

function StatCard({
	title,
	value,
	description,
	icon: Icon,
	trend,
	trendValue,
}: StatCardProps) {
	const getTrendIcon = () => {
		if (trend === 'up')
			return <TrendingUp className='h-4 w-4 text-green-500' />;
		if (trend === 'down')
			return <TrendingDown className='h-4 w-4 text-red-500' />;
		return null;
	};

	const getTrendColor = () => {
		if (trend === 'up') return 'text-green-500';
		if (trend === 'down') return 'text-red-500';
		return 'text-muted-foreground';
	};

	return (
		<Card>
			<CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
				<CardTitle className='text-sm font-medium'>{title}</CardTitle>
				<Icon className='h-4 w-4 text-muted-foreground' />
			</CardHeader>
			<CardContent>
				<div className='text-2xl font-bold'>{value}</div>
				<div className='flex items-center space-x-1 text-xs'>
					{getTrendIcon()}
					<span className={getTrendColor()}>
						{trendValue && `${trendValue} `}
						{description}
					</span>
				</div>
			</CardContent>
		</Card>
	);
}

export function DashboardOverview() {
	// Date filtering state
	const [dateRange, setDateRange] = useState<{
		startDate?: string;
		endDate?: string;
		label: string;
	}>({
		label: 'All 2024 data',
	});

	const { data: summaryData } = useExpenseSummary(
		dateRange.startDate,
		dateRange.endDate
	);

	// Handle date range changes from DateRangePicker
	const handleRangeChange = (range: { start: string; end: string; label: string }) => {
		setDateRange({
			startDate: range.start,
			endDate: range.end,
			label: range.label,
		});
	};

	// Use API data when available, fallback to demo data
	const stats = summaryData
		? [
				{
					title: 'Total Balance',
					value: `$${summaryData.net_amount.toFixed(2)}`,
					description: 'available data',
					icon: DollarSign,
					trend:
						summaryData.net_amount > 0 ? ('up' as const) : ('down' as const),
				},
				{
					title: 'Monthly Income',
					value: `$${summaryData.total_income.toFixed(2)}`,
					description: 'available data',
					icon: TrendingUp,
					trend: 'up' as const,
				},
				{
					title: 'Monthly Expenses',
					value: `$${summaryData.total_expenses.toFixed(2)}`,
					description: 'available data',
					icon: TrendingDown,
					trend: 'down' as const,
				},
				{
					title: 'Transaction Count',
					value: summaryData.category_breakdown
						.reduce((sum, cat) => sum + cat.transaction_count, 0)
						.toString(),
					description: 'available data',
					icon: CreditCard,
					trend: 'up' as const,
				},
		  ]
		: [
				{
					title: 'Total Balance',
					value: '$12,453.20',
					description: 'from last month',
					icon: DollarSign,
					trend: 'up' as const,
					trendValue: '+12%',
				},
				{
					title: 'Monthly Income',
					value: '$5,420.00',
					description: 'this month',
					icon: TrendingUp,
					trend: 'up' as const,
					trendValue: '+8%',
				},
				{
					title: 'Monthly Expenses',
					value: '$2,134.50',
					description: 'this month',
					icon: TrendingDown,
					trend: 'down' as const,
					trendValue: '-3%',
				},
				{
					title: 'Transactions',
					value: '127',
					description: 'this month',
					icon: CreditCard,
					trend: 'up' as const,
					trendValue: '+15',
				},
		  ];

	return (
		<div className='space-y-6'>
			<div className='flex items-center justify-between'>
				<div>
					<h1 className='text-3xl font-bold tracking-tight'>Dashboard</h1>
					<p className='text-muted-foreground'>
						Welcome back! Here's an overview of your financial activity.
					</p>
				</div>
				<DateRangePicker
					onRangeChange={handleRangeChange}
				/>
			</div>

			<div className='grid gap-4 md:grid-cols-2 lg:grid-cols-4'>
				{stats.map((stat) => (
					<StatCard
						key={stat.title}
						{...stat}
					/>
				))}
			</div>

			<div className='grid gap-4 md:grid-cols-2 lg:grid-cols-7'>
				<RecentTransactions />
				<ExpenseChart 
					startDate={dateRange.startDate}
					endDate={dateRange.endDate}
				/>
			</div>

			<div className='grid gap-4'>
				<TimelineChart 
					startDate={dateRange.startDate}
					endDate={dateRange.endDate}
				/>
			</div>
		</div>
	);
}
