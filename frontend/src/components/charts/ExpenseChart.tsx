import { useMemo } from 'react';
import {
	PieChart,
	Pie,
	Cell,
	ResponsiveContainer,
	BarChart,
	Bar,
	XAxis,
	YAxis,
	CartesianGrid,
	Tooltip,
	Legend,
} from 'recharts';
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useExpenseSummary } from '@/hooks/useApi';
import { Loader2 } from 'lucide-react';

const COLORS = [
	'#0088FE',
	'#00C49F',
	'#FFBB28',
	'#FF8042',
	'#8884D8',
	'#82CA9D',
	'#FFC658',
	'#FF7C7C',
];

interface ChartDataItem {
	name: string;
	value: number;
	amount: number;
	percentage: number;
}

interface CustomTooltipProps {
	active?: boolean;
	payload?: Array<{
		name: string;
		value: number;
		payload: ChartDataItem;
	}>;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
	if (active && payload && payload[0]) {
		const data = payload[0].payload;
		return (
			<div className='bg-background border rounded-lg p-3 shadow-lg'>
				<p className='font-medium'>{data.name}</p>
				<p className='text-primary'>${data.amount.toFixed(2)}</p>
				<p className='text-muted-foreground text-sm'>
					{data.percentage.toFixed(1)}%
				</p>
			</div>
		);
	}
	return null;
}

export function ExpenseChart() {
	const { data: expenseData, isLoading, error } = useExpenseSummary();

	const chartData = useMemo(() => {
		if (!expenseData?.expense_categories) return [];

		const total = expenseData.expense_categories.reduce(
			(sum: number, cat) => sum + cat.total_amount,
			0
		);

		return expenseData.expense_categories.map((category, index: number) => ({
			name: category.category,
			value: category.total_amount,
			amount: category.total_amount,
			percentage: total > 0 ? (category.total_amount / total) * 100 : 0,
			color: COLORS[index % COLORS.length],
		}));
	}, [expenseData]);

	if (isLoading) {
		return (
			<Card className='col-span-3'>
				<CardHeader>
					<CardTitle>Expense Analytics</CardTitle>
					<CardDescription>
						Breakdown of your expenses by category
					</CardDescription>
				</CardHeader>
				<CardContent className='flex items-center justify-center h-64'>
					<Loader2 className='h-6 w-6 animate-spin' />
				</CardContent>
			</Card>
		);
	}

	if (error || !chartData.length) {
		return (
			<Card className='col-span-3'>
				<CardHeader>
					<CardTitle>Expense Analytics</CardTitle>
					<CardDescription>
						Breakdown of your expenses by category
					</CardDescription>
				</CardHeader>
				<CardContent className='flex items-center justify-center h-64 text-muted-foreground'>
					{error ? 'Failed to load expense data' : 'No expense data available'}
				</CardContent>
			</Card>
		);
	}

	return (
		<Card className='col-span-3'>
			<CardHeader>
				<CardTitle>Expense Analytics</CardTitle>
				<CardDescription>
					Breakdown of your expenses by category
				</CardDescription>
			</CardHeader>
			<CardContent>
				<Tabs
					defaultValue='pie'
					className='w-full'
				>
					<TabsList className='grid w-full grid-cols-2'>
						<TabsTrigger value='pie'>Pie Chart</TabsTrigger>
						<TabsTrigger value='bar'>Bar Chart</TabsTrigger>
					</TabsList>

					<TabsContent
						value='pie'
						className='mt-4'
					>
						<div className='h-64'>
							<ResponsiveContainer
								width='100%'
								height='100%'
							>
								<PieChart>
									<Pie
										data={chartData}
										cx='50%'
										cy='50%'
										innerRadius={40}
										outerRadius={80}
										paddingAngle={2}
										dataKey='value'
									>
										{chartData.map((_, index: number) => (
											<Cell
												key={`cell-${index}`}
												fill={COLORS[index % COLORS.length]}
											/>
										))}
									</Pie>
									<Tooltip content={<CustomTooltip />} />
									<Legend />
								</PieChart>
							</ResponsiveContainer>
						</div>
					</TabsContent>

					<TabsContent
						value='bar'
						className='mt-4'
					>
						<div className='h-64'>
							<ResponsiveContainer
								width='100%'
								height='100%'
							>
								<BarChart data={chartData}>
									<CartesianGrid strokeDasharray='3 3' />
									<XAxis
										dataKey='name'
										fontSize={12}
										angle={-45}
										textAnchor='end'
										height={80}
									/>
									<YAxis
										fontSize={12}
										tickFormatter={(value) => `$${value}`}
									/>
									<Tooltip content={<CustomTooltip />} />
									<Bar
										dataKey='value'
										fill='#0088FE'
										radius={[4, 4, 0, 0]}
									/>
								</BarChart>
							</ResponsiveContainer>
						</div>
					</TabsContent>
				</Tabs>
			</CardContent>
		</Card>
	);
}
