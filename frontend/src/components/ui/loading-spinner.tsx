import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
	className?: string;
	size?: 'sm' | 'md' | 'lg';
	text?: string;
}

export function LoadingSpinner({
	className,
	size = 'md',
	text,
}: LoadingSpinnerProps) {
	const sizeClasses = {
		sm: 'h-4 w-4',
		md: 'h-8 w-8',
		lg: 'h-12 w-12',
	};

	return (
		<div
			className={cn(
				'flex flex-col items-center justify-center gap-2',
				className
			)}
		>
			<Loader2 className={cn('animate-spin text-primary', sizeClasses[size])} />
			{text && (
				<p className='text-sm text-muted-foreground animate-pulse'>{text}</p>
			)}
		</div>
	);
}

// Full page loading spinner
export function PageLoadingSpinner() {
	return (
		<div className='flex items-center justify-center min-h-[400px] w-full'>
			<LoadingSpinner
				size='lg'
				text='Loading...'
			/>
		</div>
	);
}
