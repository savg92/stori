import { useMemo, useState } from 'react';
import {
	LineChart,
	Line,
	XAxis,
	YAxis,
	CartesianGrid,
	Tooltip,
	Legend,
	ResponsiveContainer,
	AreaChart,
	Area,
} from 'recharts';
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useTimelineData } from '@/hooks/useApi';
import type { TimelinePoint } from '@/types/api';
import { Loader2, TrendingUp, TrendingDown, Calendar } from 'lucide-react';
import { format } from 'date-fns';
import { Button } from '@/components/ui/button';

interface CustomTimelineTooltipProps {
	active?: boolean;
	payload?: Array<{
		name: string;
		value: number;
		color: string;
	}>;
	label?: string;
}

interface ChartDataPoint {
	date: string;
	dateFormatted: string;
	income: number;
	expenses: number;
	net: number;
}

function CustomTimelineTooltip({
	active,
	payload,
	label,
}: CustomTimelineTooltipProps) {
	if (active && payload && payload.length) {
		const incomeData = payload.find((item) => item.name === 'Income');
		const expensesData = payload.find((item) => item.name === 'Expenses');
		const netData = payload.find((item) => item.name === 'Net Income');

		return (
			<div className='bg-background border rounded-lg p-4 shadow-lg max-w-xs'>
				<div className='flex items-center gap-2 mb-3'>
					<Calendar className='h-4 w-4 text-muted-foreground' />
					<p className='font-semibold text-sm'>{label}</p>
				</div>
				<div className='space-y-2'>
					{incomeData && (
						<div className='flex items-center justify-between'>
							<div className='flex items-center gap-2'>
								<div className='w-3 h-3 rounded-full bg-green-500' />
								<span className='text-sm'>Income:</span>
							</div>
							<span className='font-medium text-green-600'>
								$
								{incomeData.value.toLocaleString('en-US', {
									minimumFractionDigits: 2,
									maximumFractionDigits: 2,
								})}
							</span>
						</div>
					)}
					{expensesData && (
						<div className='flex items-center justify-between'>
							<div className='flex items-center gap-2'>
								<div className='w-3 h-3 rounded-full bg-red-500' />
								<span className='text-sm'>Expenses:</span>
							</div>
							<span className='font-medium text-red-600'>
								$
								{expensesData.value.toLocaleString('en-US', {
									minimumFractionDigits: 2,
									maximumFractionDigits: 2,
								})}
							</span>
						</div>
					)}
					{netData && (
						<div className='flex items-center justify-between pt-1 border-t'>
							<div className='flex items-center gap-2'>
								<div className='w-3 h-3 rounded-full bg-blue-500' />
								<span className='text-sm font-medium'>Net:</span>
							</div>
							<div className='flex items-center gap-1'>
								{netData.value > 0 ? (
									<TrendingUp className='h-3 w-3 text-green-500' />
								) : (
									<TrendingDown className='h-3 w-3 text-red-500' />
								)}
								<span
									className={`font-bold ${
										netData.value > 0 ? 'text-green-600' : 'text-red-600'
									}`}
								>
									$
									{Math.abs(netData.value).toLocaleString('en-US', {
										minimumFractionDigits: 2,
										maximumFractionDigits: 2,
									})}
								</span>
							</div>
						</div>
					)}
				</div>
			</div>
		);
	}
	return null;
}

export function TimelineChart({
	startDate,
	endDate,
}: {
	startDate?: string;
	endDate?: string;
} = {}) {
	const {
		data: timelineData,
		isLoading,
		error,
	} = useTimelineData(startDate, endDate);
	const [selectedDataPoint, setSelectedDataPoint] =
		useState<ChartDataPoint | null>(null);
	const [focusedLine, setFocusedLine] = useState<string | null>(null);

	const chartData = useMemo(() => {
		if (!timelineData?.data_points) return [];

		return timelineData.data_points.map((point: TimelinePoint) => ({
			date: point.date,
			dateFormatted: format(new Date(point.date), 'MMM dd'),
			income: point.total_income, // Fixed: use total_income from backend
			expenses: point.total_expenses, // Fixed: use total_expenses from backend
			net: point.net_amount,
		}));
	}, [timelineData]);

	// Interactive handlers
	const handleDataPointClick = (data: ChartDataPoint) => {
		setSelectedDataPoint(selectedDataPoint?.date === data.date ? null : data);
	};

	const handleLineHover = (lineName: string) => {
		setFocusedLine(lineName);
	};

	const handleChartLeave = () => {
		setFocusedLine(null);
	};

	if (isLoading) {
		return (
			<Card className='col-span-4'>
				<CardHeader>
					<CardTitle>Financial Timeline</CardTitle>
					<CardDescription>Income vs Expenses over time</CardDescription>
				</CardHeader>
				<CardContent className='flex items-center justify-center h-80'>
					<Loader2 className='h-6 w-6 animate-spin' />
				</CardContent>
			</Card>
		);
	}

	if (error || !chartData.length) {
		return (
			<Card className='col-span-4'>
				<CardHeader>
					<CardTitle>Financial Timeline</CardTitle>
					<CardDescription>Income vs Expenses over time</CardDescription>
				</CardHeader>
				<CardContent className='flex items-center justify-center h-80 text-muted-foreground'>
					{error
						? 'Failed to load timeline data'
						: 'No timeline data available'}
				</CardContent>
			</Card>
		);
	}

	return (
		<Card className='col-span-4'>
			<CardHeader>
				<CardTitle>Financial Timeline</CardTitle>
				<CardDescription>Income vs Expenses over time</CardDescription>
			</CardHeader>
			<CardContent>
				{selectedDataPoint && (
					<div className='mb-4 p-4 bg-primary/10 border border-primary/20 rounded-lg'>
						<div className='flex items-center justify-between'>
							<div className='flex-1'>
								<h3 className='font-semibold text-primary flex items-center gap-2'>
									<Calendar className='h-4 w-4' />
									{format(new Date(selectedDataPoint.date), 'MMMM dd, yyyy')}
								</h3>
								<div className='mt-3 grid grid-cols-3 gap-4 text-sm'>
									<div className='space-y-1'>
										<p className='text-muted-foreground'>Income</p>
										<p className='font-medium text-green-600'>
											$
											{selectedDataPoint?.income?.toLocaleString('en-US', {
												minimumFractionDigits: 2,
												maximumFractionDigits: 2,
											}) ?? '0.00'}
										</p>
									</div>
									<div className='space-y-1'>
										<p className='text-muted-foreground'>Expenses</p>
										<p className='font-medium text-red-600'>
											$
											{selectedDataPoint?.expenses?.toLocaleString('en-US', {
												minimumFractionDigits: 2,
												maximumFractionDigits: 2,
											}) ?? '0.00'}
										</p>
									</div>
									<div className='space-y-1'>
										<p className='text-muted-foreground'>Net Income</p>
										<div className='flex items-center gap-1'>
											{(selectedDataPoint?.net ?? 0) > 0 ? (
												<TrendingUp className='h-3 w-3 text-green-500' />
											) : (
												<TrendingDown className='h-3 w-3 text-red-500' />
											)}
											<p
												className={`font-bold ${
													(selectedDataPoint?.net ?? 0) > 0
														? 'text-green-600'
														: 'text-red-600'
												}`}
											>
												$
												{Math.abs(selectedDataPoint?.net ?? 0).toLocaleString(
													'en-US',
													{
														minimumFractionDigits: 2,
														maximumFractionDigits: 2,
													}
												)}
											</p>
										</div>
									</div>
								</div>
							</div>
							<Button
								variant='ghost'
								size='sm'
								onClick={() => setSelectedDataPoint(null)}
								className='shrink-0'
							>
								Clear
							</Button>
						</div>
					</div>
				)}

				<Tabs
					defaultValue='line'
					className='w-full'
				>
					<TabsList className='grid w-full grid-cols-2'>
						<TabsTrigger value='line'>Line Chart</TabsTrigger>
						<TabsTrigger value='area'>Area Chart</TabsTrigger>
					</TabsList>

					<TabsContent
						value='line'
						className='mt-4'
					>
						<div className='h-80 sm:h-96 touch-manipulation'>
							<ResponsiveContainer
								width='100%'
								height='100%'
								minHeight={300}
							>
								<LineChart
									data={chartData}
									onClick={(data) =>
										data?.activeLabel &&
										handleDataPointClick(
											chartData.find(
												(point) => point.dateFormatted === data.activeLabel
											) as ChartDataPoint
										)
									}
									onMouseLeave={handleChartLeave}
								>
									<CartesianGrid strokeDasharray='3 3' />
									<XAxis
										dataKey='dateFormatted'
										fontSize={12}
									/>
									<YAxis
										fontSize={12}
										tickFormatter={(value) => `$${value}`}
									/>
									<Tooltip content={<CustomTimelineTooltip />} />
									<Legend />
									<Line
										type='monotone'
										dataKey='income'
										stroke='#22c55e'
										strokeWidth={focusedLine === 'Income' ? 4 : 2}
										name='Income'
										dot={{
											r: focusedLine === 'Income' ? 6 : 4,
											strokeWidth: 2,
											fill: '#22c55e',
										}}
										activeDot={{
											r: 8,
											stroke: '#22c55e',
											strokeWidth: 3,
											fill: '#ffffff',
										}}
										onMouseEnter={() => handleLineHover('Income')}
										style={{
											filter:
												focusedLine && focusedLine !== 'Income'
													? 'opacity(0.3)'
													: 'opacity(1)',
											transition: 'all 0.3s ease',
											cursor: 'pointer',
										}}
									/>
									<Line
										type='monotone'
										dataKey='expenses'
										stroke='#ef4444'
										strokeWidth={focusedLine === 'Expenses' ? 4 : 2}
										name='Expenses'
										dot={{
											r: focusedLine === 'Expenses' ? 6 : 4,
											strokeWidth: 2,
											fill: '#ef4444',
										}}
										activeDot={{
											r: 8,
											stroke: '#ef4444',
											strokeWidth: 3,
											fill: '#ffffff',
										}}
										onMouseEnter={() => handleLineHover('Expenses')}
										style={{
											filter:
												focusedLine && focusedLine !== 'Expenses'
													? 'opacity(0.3)'
													: 'opacity(1)',
											transition: 'all 0.3s ease',
											cursor: 'pointer',
										}}
									/>
									<Line
										type='monotone'
										dataKey='net'
										stroke='#3b82f6'
										strokeWidth={focusedLine === 'Net Income' ? 4 : 2}
										name='Net Income'
										dot={{
											r: focusedLine === 'Net Income' ? 6 : 4,
											strokeWidth: 2,
											fill: '#3b82f6',
										}}
										activeDot={{
											r: 8,
											stroke: '#3b82f6',
											strokeWidth: 3,
											fill: '#ffffff',
										}}
										onMouseEnter={() => handleLineHover('Net Income')}
										style={{
											filter:
												focusedLine && focusedLine !== 'Net Income'
													? 'opacity(0.3)'
													: 'opacity(1)',
											transition: 'all 0.3s ease',
											cursor: 'pointer',
										}}
									/>
								</LineChart>
							</ResponsiveContainer>
						</div>
					</TabsContent>

					<TabsContent
						value='area'
						className='mt-4'
					>
						<div className='h-80 sm:h-96 touch-manipulation'>
							<ResponsiveContainer
								width='100%'
								height='100%'
								minHeight={300}
							>
								<AreaChart
									data={chartData}
									onClick={(data) =>
										data?.activeLabel &&
										handleDataPointClick(
											chartData.find(
												(point) => point.dateFormatted === data.activeLabel
											) as ChartDataPoint
										)
									}
									onMouseLeave={handleChartLeave}
								>
									<CartesianGrid strokeDasharray='3 3' />
									<XAxis
										dataKey='dateFormatted'
										fontSize={12}
									/>
									<YAxis
										fontSize={12}
										tickFormatter={(value) => `$${value}`}
									/>
									<Tooltip content={<CustomTimelineTooltip />} />
									<Legend />
									<Area
										type='monotone'
										dataKey='income'
										stackId='1'
										stroke='#22c55e'
										fill='#22c55e'
										fillOpacity={focusedLine === 'Income' ? 0.6 : 0.3}
										strokeWidth={focusedLine === 'Income' ? 3 : 2}
										name='Income'
										onMouseEnter={() => handleLineHover('Income')}
										style={{
											filter:
												focusedLine && focusedLine !== 'Income'
													? 'opacity(0.4)'
													: 'opacity(1)',
											transition: 'all 0.3s ease',
											cursor: 'pointer',
										}}
									/>
									<Area
										type='monotone'
										dataKey='expenses'
										stackId='2'
										stroke='#ef4444'
										fill='#ef4444'
										fillOpacity={focusedLine === 'Expenses' ? 0.6 : 0.3}
										strokeWidth={focusedLine === 'Expenses' ? 3 : 2}
										name='Expenses'
										onMouseEnter={() => handleLineHover('Expenses')}
										style={{
											filter:
												focusedLine && focusedLine !== 'Expenses'
													? 'opacity(0.4)'
													: 'opacity(1)',
											transition: 'all 0.3s ease',
											cursor: 'pointer',
										}}
									/>
								</AreaChart>
							</ResponsiveContainer>
						</div>
					</TabsContent>
				</Tabs>
			</CardContent>
		</Card>
	);
}
