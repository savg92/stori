import { useState, useEffect } from 'react';
import { Button } from './button';
import { Calendar, ChevronDown } from 'lucide-react';
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from './dropdown-menu';

export interface DateRange {
	start: string;
	end: string;
	label: string;
}

interface DateRangePickerProps {
	onRangeChange: (range: DateRange) => void;
	defaultRange?: DateRange;
}

const presetRanges: DateRange[] = [
	{
		start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
			.toISOString()
			.split('T')[0],
		end: new Date().toISOString().split('T')[0],
		label: 'Last 30 days',
	},
	{
		start: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000)
			.toISOString()
			.split('T')[0],
		end: new Date().toISOString().split('T')[0],
		label: 'Last 3 months',
	},
	{
		start: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000)
			.toISOString()
			.split('T')[0],
		end: new Date().toISOString().split('T')[0],
		label: 'Last 6 months',
	},
	{
		start: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000)
			.toISOString()
			.split('T')[0],
		end: new Date().toISOString().split('T')[0],
		label: 'Last year',
	},
	{
		start: '2024-01-01',
		end: '2024-12-31',
		label: 'All 2024 data',
	},
];

export function DateRangePicker({
	onRangeChange,
	defaultRange,
}: DateRangePickerProps) {
	const [selectedRange, setSelectedRange] = useState<DateRange>(
		defaultRange || presetRanges[4] // Default to "All 2024 data"
	);

	// Update selected range when defaultRange prop changes (e.g., from smart detection)
	useEffect(() => {
		if (defaultRange) {
			setSelectedRange(defaultRange);
		}
	}, [defaultRange]);

	const handleRangeSelect = (range: DateRange) => {
		setSelectedRange(range);
		onRangeChange(range);
	};

	return (
		<DropdownMenu>
			<DropdownMenuTrigger asChild>
				<Button
					variant='outline'
					className='w-auto justify-between'
				>
					<Calendar className='mr-2 h-4 w-4' />
					{selectedRange.label}
					<ChevronDown className='ml-2 h-4 w-4' />
				</Button>
			</DropdownMenuTrigger>
			<DropdownMenuContent
				align='end'
				className='w-56'
			>
				{presetRanges.map((range) => (
					<DropdownMenuItem
						key={range.label}
						onSelect={() => handleRangeSelect(range)}
						className={selectedRange.label === range.label ? 'bg-accent' : ''}
					>
						{range.label}
					</DropdownMenuItem>
				))}
			</DropdownMenuContent>
		</DropdownMenu>
	);
}
