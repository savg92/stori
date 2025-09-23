import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from '../ui/card';
import { TrendingUp, TrendingDown, DollarSign, CreditCard } from 'lucide-react';

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
	// TODO: Replace with real data from API
	const stats = [
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
			<div>
				<h1 className='text-3xl font-bold tracking-tight'>Dashboard</h1>
				<p className='text-muted-foreground'>
					Welcome back! Here's an overview of your financial activity.
				</p>
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
				<Card className='col-span-4'>
					<CardHeader>
						<CardTitle>Recent Transactions</CardTitle>
						<CardDescription>Your latest financial activity</CardDescription>
					</CardHeader>
					<CardContent>
						<div className='space-y-3'>
							{/* TODO: Replace with real transaction data */}
							{[1, 2, 3, 4, 5].map((i) => (
								<div
									key={i}
									className='flex items-center space-x-4'
								>
									<div className='w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center'>
										<CreditCard className='h-4 w-4' />
									</div>
									<div className='flex-1 space-y-1'>
										<p className='text-sm font-medium leading-none'>
											Transaction #{i}
										</p>
										<p className='text-xs text-muted-foreground'>
											Category • 2 hours ago
										</p>
									</div>
									<div className='text-sm font-medium'>
										${(Math.random() * 200 + 10).toFixed(2)}
									</div>
								</div>
							))}
						</div>
					</CardContent>
				</Card>

				<Card className='col-span-3'>
					<CardHeader>
						<CardTitle>Spending Categories</CardTitle>
						<CardDescription>Top categories this month</CardDescription>
					</CardHeader>
					<CardContent>
						<div className='space-y-3'>
							{/* TODO: Replace with real category data */}
							{[
								{ name: 'Food & Dining', amount: 450, percentage: 35 },
								{ name: 'Transportation', amount: 320, percentage: 25 },
								{ name: 'Entertainment', amount: 180, percentage: 15 },
								{ name: 'Shopping', amount: 150, percentage: 12 },
								{ name: 'Bills', amount: 100, percentage: 8 },
							].map((category) => (
								<div
									key={category.name}
									className='space-y-2'
								>
									<div className='flex items-center justify-between text-sm'>
										<span className='font-medium'>{category.name}</span>
										<span>${category.amount}</span>
									</div>
									<div className='w-full bg-secondary rounded-full h-2'>
										<div
											className='bg-primary h-2 rounded-full'
											style={{ width: `${category.percentage}%` }}
										/>
									</div>
								</div>
							))}
						</div>
					</CardContent>
				</Card>
			</div>
		</div>
	);
}
