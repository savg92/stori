import { useMemo } from 'react';
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
import { Loader2 } from 'lucide-react';
import { format } from 'date-fns';

interface CustomTimelineTooltipProps {
	active?: boolean;
	payload?: Array<{
		name: string;
		value: number;
		color: string;
	}>;
	label?: string;
}

function CustomTimelineTooltip({
	active,
	payload,
	label,
}: CustomTimelineTooltipProps) {
	if (active && payload && payload.length) {
		return (
			<div className='bg-background border rounded-lg p-3 shadow-lg'>
				<p className='font-medium mb-2'>{label}</p>
				{payload.map((entry, index) => (
					<p
						key={index}
						style={{ color: entry.color }}
						className='text-sm'
					>
						{entry.name}: ${entry.value.toFixed(2)}
					</p>
				))}
			</div>
		);
	}
	return null;
}

export function TimelineChart() {
	const { data: timelineData, isLoading, error } = useTimelineData();

	const chartData = useMemo(() => {
		if (!timelineData?.data_points) return [];

		return timelineData.data_points.map((point: TimelinePoint) => ({
			date: point.date,
			dateFormatted: format(new Date(point.date), 'MMM dd'),
			income: point.income,
			expenses: point.expenses,
			net: point.net_income,
		}));
	}, [timelineData]);

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
						<div className='h-80'>
							<ResponsiveContainer
								width='100%'
								height='100%'
							>
								<LineChart data={chartData}>
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
										strokeWidth={2}
										name='Income'
										dot={{ r: 4 }}
									/>
									<Line
										type='monotone'
										dataKey='expenses'
										stroke='#ef4444'
										strokeWidth={2}
										name='Expenses'
										dot={{ r: 4 }}
									/>
									<Line
										type='monotone'
										dataKey='net'
										stroke='#3b82f6'
										strokeWidth={2}
										name='Net Income'
										dot={{ r: 4 }}
									/>
								</LineChart>
							</ResponsiveContainer>
						</div>
					</TabsContent>

					<TabsContent
						value='area'
						className='mt-4'
					>
						<div className='h-80'>
							<ResponsiveContainer
								width='100%'
								height='100%'
							>
								<AreaChart data={chartData}>
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
										fillOpacity={0.3}
										name='Income'
									/>
									<Area
										type='monotone'
										dataKey='expenses'
										stackId='2'
										stroke='#ef4444'
										fill='#ef4444'
										fillOpacity={0.3}
										name='Expenses'
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
