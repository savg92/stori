import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useRecentTransactions } from '@/hooks/useApi';
import type { Transaction } from '@/types/api';
import { Loader2, TrendingUp, TrendingDown } from 'lucide-react';
import { format } from 'date-fns';

function TransactionIcon({ type }: { type: string }) {
	return type === 'income' ? (
		<div className='w-8 h-8 bg-green-500/10 rounded-full flex items-center justify-center'>
			<TrendingUp className='h-4 w-4 text-green-500' />
		</div>
	) : (
		<div className='w-8 h-8 bg-red-500/10 rounded-full flex items-center justify-center'>
			<TrendingDown className='h-4 w-4 text-red-500' />
		</div>
	);
}

function formatCategory(category: string) {
	return category
		.split('_')
		.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
		.join(' ');
}

export function RecentTransactions() {
	const {
		data: transactionResponse,
		isLoading,
		error,
	} = useRecentTransactions();
	const transactions = transactionResponse?.items?.slice(0, 5) || [];

	if (isLoading) {
		return (
			<Card className='col-span-4'>
				<CardHeader>
					<CardTitle>Recent Transactions</CardTitle>
					<CardDescription>Your latest financial activity</CardDescription>
				</CardHeader>
				<CardContent className='flex items-center justify-center h-64'>
					<Loader2 className='h-6 w-6 animate-spin' />
				</CardContent>
			</Card>
		);
	}

	if (error || !transactions?.length) {
		return (
			<Card className='col-span-4'>
				<CardHeader>
					<CardTitle>Recent Transactions</CardTitle>
					<CardDescription>Your latest financial activity</CardDescription>
				</CardHeader>
				<CardContent className='flex items-center justify-center h-64 text-muted-foreground'>
					{error ? 'Failed to load transactions' : 'No transactions available'}
				</CardContent>
			</Card>
		);
	}

	return (
		<Card className='col-span-4'>
			<CardHeader>
				<CardTitle>Recent Transactions</CardTitle>
				<CardDescription>Your latest financial activity</CardDescription>
			</CardHeader>
			<CardContent>
				<div className='space-y-3'>
					{transactions.map((transaction: Transaction) => (
						<div
							key={transaction.id}
							className='flex items-center space-x-4 p-2 rounded-lg hover:bg-muted/50 transition-colors'
						>
							<TransactionIcon type={transaction.type} />
							<div className='flex-1 space-y-1'>
								<div className='flex items-center justify-between'>
									<p className='text-sm font-medium leading-none'>
										{transaction.description}
									</p>
									<div
										className={`text-sm font-medium ${
											transaction.type === 'income'
												? 'text-green-600'
												: 'text-red-600'
										}`}
									>
										{transaction.type === 'income' ? '+' : '-'}$
										{transaction.amount.toFixed(2)}
									</div>
								</div>
								<div className='flex items-center space-x-2'>
									<Badge
										variant='secondary'
										className='text-xs'
									>
										{formatCategory(transaction.category)}
									</Badge>
									<p className='text-xs text-muted-foreground'>
										{format(new Date(transaction.date), 'MMM dd, yyyy')}
									</p>
								</div>
							</div>
						</div>
					))}
				</div>
			</CardContent>
		</Card>
	);
}
