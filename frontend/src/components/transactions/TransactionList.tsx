import { useState } from 'react';
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from '../ui/select';
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { TransactionForm } from './TransactionForm';
import {
	Search,
	MoreVertical,
	Edit,
	Trash2,
	TrendingUp,
	TrendingDown,
	Loader2,
} from 'lucide-react';
import {
	useTransactionFilters,
	useDeleteTransaction,
} from '../../hooks/useApi';
import type { TransactionFilters } from '../../types/api';

export function TransactionList() {
	const [searchTerm, setSearchTerm] = useState('');
	const [typeFilter, setTypeFilter] = useState<'all' | 'income' | 'expense'>(
		'all'
	);
	const [categoryFilter, setCategoryFilter] = useState<string>('all');

	// Build filters object for API
	const filters: TransactionFilters = {
		type: typeFilter !== 'all' ? typeFilter : undefined,
		category: categoryFilter !== 'all' ? categoryFilter : undefined,
		search: searchTerm || undefined,
	};

	// API hooks
	const {
		data: transactionData,
		isLoading,
		error,
	} = useTransactionFilters(filters);
	const deleteTransaction = useDeleteTransaction();

	const transactions = transactionData?.items || [];

	const handleDelete = async (id: string) => {
		if (window.confirm('Are you sure you want to delete this transaction?')) {
			await deleteTransaction.mutateAsync(id);
		}
	};

	// Get unique categories from current transactions
	const allCategories = [...new Set(transactions.map((t) => t.category))];

	const formatAmount = (amount: number, type: 'income' | 'expense') => {
		const value = type === 'income' ? amount : -amount;
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
		}).format(value);
	};

	const formatDate = (dateString: string) => {
		return new Date(dateString).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric',
		});
	};

	if (error) {
		return (
			<Card>
				<CardHeader>
					<CardTitle>Error Loading Transactions</CardTitle>
					<CardDescription>
						There was an error loading your transactions. Please try again.
					</CardDescription>
				</CardHeader>
			</Card>
		);
	}

	return (
		<div className='space-y-6'>
			<div className='flex items-center justify-between'>
				<div>
					<h1 className='text-3xl font-bold tracking-tight'>Transactions</h1>
					<p className='text-muted-foreground'>
						Manage your income and expenses
					</p>
				</div>
				<TransactionForm />
			</div>

			<Card>
				<CardHeader>
					<CardTitle>Recent Transactions</CardTitle>
					<CardDescription>
						A list of your recent financial transactions
					</CardDescription>
				</CardHeader>
				<CardContent>
					{/* Filters */}
					<div className='flex flex-col sm:flex-row gap-4 mb-6'>
						<div className='relative flex-1'>
							<Search className='absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground' />
							<Input
								placeholder='Search transactions...'
								value={searchTerm}
								onChange={(e) => setSearchTerm(e.target.value)}
								className='pl-10'
							/>
						</div>
						<Select
							value={typeFilter}
							onValueChange={(value: string) =>
								setTypeFilter(value as 'all' | 'income' | 'expense')
							}
						>
							<SelectTrigger className='w-[140px]'>
								<SelectValue placeholder='Type' />
							</SelectTrigger>
							<SelectContent>
								<SelectItem value='all'>All Types</SelectItem>
								<SelectItem value='income'>Income</SelectItem>
								<SelectItem value='expense'>Expense</SelectItem>
							</SelectContent>
						</Select>
						<Select
							value={categoryFilter}
							onValueChange={setCategoryFilter}
						>
							<SelectTrigger className='w-[140px]'>
								<SelectValue placeholder='Category' />
							</SelectTrigger>
							<SelectContent>
								<SelectItem value='all'>All Categories</SelectItem>
								{allCategories.map((category) => (
									<SelectItem
										key={category}
										value={category}
									>
										{category}
									</SelectItem>
								))}
							</SelectContent>
						</Select>
					</div>

					{/* Loading State */}
					{isLoading && (
						<div className='flex items-center justify-center py-8'>
							<Loader2 className='h-8 w-8 animate-spin' />
							<span className='ml-2'>Loading transactions...</span>
						</div>
					)}

					{/* Transaction List */}
					{!isLoading && (
						<div className='space-y-3'>
							{transactions.length === 0 ? (
								<div className='text-center py-8'>
									<p className='text-muted-foreground'>No transactions found</p>
									<p className='text-sm text-muted-foreground mt-2'>
										Try adjusting your filters or add your first transaction
									</p>
								</div>
							) : (
								transactions.map((transaction) => (
									<div
										key={transaction.id}
										className='flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors'
									>
										<div className='flex items-center space-x-4'>
											<div
												className={`w-10 h-10 rounded-full flex items-center justify-center ${
													transaction.type === 'income'
														? 'bg-green-100 dark:bg-green-900/20'
														: 'bg-red-100 dark:bg-red-900/20'
												}`}
											>
												{transaction.type === 'income' ? (
													<TrendingUp className='h-5 w-5 text-green-600 dark:text-green-400' />
												) : (
													<TrendingDown className='h-5 w-5 text-red-600 dark:text-red-400' />
												)}
											</div>
											<div className='flex-1'>
												<div className='flex items-center space-x-2'>
													<p className='font-medium'>{transaction.category}</p>
													<span className='text-xs bg-secondary px-2 py-1 rounded'>
														{transaction.type}
													</span>
												</div>
												<p className='text-sm text-muted-foreground'>
													{transaction.description || 'No description'}
												</p>
												<p className='text-xs text-muted-foreground'>
													{formatDate(transaction.date)}
												</p>
											</div>
										</div>
										<div className='flex items-center space-x-2'>
											<span
												className={`font-semibold ${
													transaction.type === 'income'
														? 'text-green-600'
														: 'text-red-600'
												}`}
											>
												{formatAmount(transaction.amount, transaction.type)}
											</span>
											<DropdownMenu>
												<DropdownMenuTrigger asChild>
													<Button
														variant='ghost'
														size='icon'
													>
														<MoreVertical className='h-4 w-4' />
													</Button>
												</DropdownMenuTrigger>
												<DropdownMenuContent align='end'>
													<DropdownMenuItem>
														<Edit className='mr-2 h-4 w-4' />
														Edit
													</DropdownMenuItem>
													<DropdownMenuItem
														onClick={() => handleDelete(transaction.id)}
														className='text-destructive'
													>
														<Trash2 className='mr-2 h-4 w-4' />
														Delete
													</DropdownMenuItem>
												</DropdownMenuContent>
											</DropdownMenu>
										</div>
									</div>
								))
							)}
						</div>
					)}
				</CardContent>
			</Card>
		</div>
	);
}
