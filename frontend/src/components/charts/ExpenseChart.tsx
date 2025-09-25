import { useMemo, useState } from 'react';
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
import { Loader2, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';

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

// Format category names for display
const formatCategoryName = (category: string): string => {
	return category
		.split('_')
		.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
		.join(' ');
};

interface ChartDataItem {
	name: string;
	value: number;
	amount: number;
	percentage: number;
	color: string;
	transactionCount?: number;
}

interface CustomTooltipProps {
	active?: boolean;
	payload?: Array<{
		name: string;
		value: number;
		payload: ChartDataItem;
	}>;
}

interface BarClickData {
	payload?: ChartDataItem;
	name?: string;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
	if (active && payload && payload[0]) {
		const data = payload[0].payload;
		return (
			<div className='bg-background border rounded-lg p-4 shadow-lg max-w-xs'>
				<div className='flex items-center gap-2 mb-2'>
					<div
						className='w-3 h-3 rounded-full'
						style={{ backgroundColor: data.color }}
					/>
					<p className='font-semibold text-sm'>{data.name}</p>
				</div>
				<div className='space-y-1'>
					<p className='text-lg font-bold text-primary'>
						$
						{data.amount.toLocaleString('en-US', {
							minimumFractionDigits: 2,
							maximumFractionDigits: 2,
						})}
					</p>
					<p className='text-sm text-muted-foreground'>
						{data.percentage.toFixed(1)}% of total expenses
					</p>
					{data.transactionCount && (
						<p className='text-xs text-muted-foreground'>
							{data.transactionCount} transactions
						</p>
					)}
				</div>
			</div>
		);
	}
	return null;
}

export function ExpenseChart() {
	const { data: expenseData, isLoading, error } = useExpenseSummary();
	const [activeIndex, setActiveIndex] = useState<number | null>(null);
	const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

	const chartData = useMemo(() => {
		if (!expenseData?.expense_categories) return [];

		const total = expenseData.expense_categories.reduce(
			(sum: number, cat) => sum + cat.total_amount,
			0
		);

		return expenseData.expense_categories.map((category, index: number) => ({
			name: formatCategoryName(category.category),
			value: category.total_amount,
			amount: category.total_amount,
			percentage: total > 0 ? (category.total_amount / total) * 100 : 0,
			color: COLORS[index % COLORS.length],
			transactionCount: category.transaction_count,
		}));
	}, [expenseData]);

	// Event handlers for interactivity
	const handlePieClick = (data: ChartDataItem, index: number) => {
		setActiveIndex(activeIndex === index ? null : index);
		setSelectedCategory(selectedCategory === data.name ? null : data.name);
	};

	const handleBarClick = (data: BarClickData) => {
		const categoryName = data?.payload?.name || data?.name;
		if (categoryName) {
			setSelectedCategory(
				selectedCategory === categoryName ? null : categoryName
			);
		}
	};

	const handleMouseEnter = (_data: unknown, index: number) => {
		setActiveIndex(index);
	};

	const handleMouseLeave = () => {
		if (selectedCategory === null) {
			setActiveIndex(null);
		}
	};

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
				{selectedCategory && (
					<div className='mb-4 p-4 bg-primary/10 border border-primary/20 rounded-lg'>
						<div className='flex items-center justify-between'>
							<div>
								<h3 className='font-semibold text-primary'>
									{selectedCategory}
								</h3>
								{chartData.find((item) => item.name === selectedCategory) && (
									<div className='mt-2 grid grid-cols-2 gap-4 text-sm'>
										<div>
											<p className='text-muted-foreground'>Total Amount</p>
											<p className='font-medium'>
												$
												{chartData
													.find((item) => item.name === selectedCategory)
													?.amount.toLocaleString('en-US', {
														minimumFractionDigits: 2,
														maximumFractionDigits: 2,
													})}
											</p>
										</div>
										<div>
											<p className='text-muted-foreground'>Transactions</p>
											<p className='font-medium'>
												{
													chartData.find(
														(item) => item.name === selectedCategory
													)?.transactionCount
												}
											</p>
										</div>
									</div>
								)}
							</div>
							<Button
								variant='ghost'
								size='sm'
								onClick={() => {
									setSelectedCategory(null);
									setActiveIndex(null);
								}}
								className='shrink-0'
							>
								<Eye className='h-4 w-4' />
								Clear
							</Button>
						</div>
					</div>
				)}

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
						<div className='h-64 sm:h-80 touch-manipulation'>
							<ResponsiveContainer
								width='100%'
								height='100%'
								minHeight={200}
							>
								<PieChart>
									<Pie
										data={chartData}
										cx='50%'
										cy='50%'
										innerRadius={30}
										outerRadius={activeIndex !== null ? 85 : 75}
										paddingAngle={2}
										dataKey='value'
										onClick={handlePieClick}
										onMouseEnter={handleMouseEnter}
										onMouseLeave={handleMouseLeave}
										animationBegin={0}
										animationDuration={800}
									>
										{chartData.map((entry, index: number) => (
											<Cell
												key={`cell-${index}`}
												fill={entry.color}
												stroke={activeIndex === index ? '#ffffff' : 'none'}
												strokeWidth={activeIndex === index ? 2 : 0}
												style={{
													filter:
														activeIndex !== null && activeIndex !== index
															? 'opacity(0.6)'
															: 'opacity(1)',
													cursor: 'pointer',
													transition: 'all 0.3s ease',
												}}
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
						<div className='h-64 sm:h-80 touch-manipulation'>
							<ResponsiveContainer
								width='100%'
								height='100%'
								minHeight={200}
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
										radius={[4, 4, 0, 0]}
										animationDuration={800}
										animationBegin={0}
										onClick={(data) => handleBarClick(data)}
									>
										{chartData.map((entry, index: number) => (
											<Cell
												key={`cell-${index}`}
												fill={
													selectedCategory === entry.name
														? entry.color
														: '#0088FE'
												}
												style={{
													filter:
														selectedCategory && selectedCategory !== entry.name
															? 'opacity(0.6)'
															: 'opacity(1)',
													cursor: 'pointer',
													transition: 'all 0.3s ease',
												}}
											/>
										))}
									</Bar>
								</BarChart>
							</ResponsiveContainer>
						</div>
					</TabsContent>
				</Tabs>
			</CardContent>
		</Card>
	);
}
